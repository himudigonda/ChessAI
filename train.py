# chess_app/train.py

import chess
import chess.engine
import torch
from torch.utils.data import Dataset, DataLoader
from chess_app.model import ChessNet, save_model, load_model
from chess_app.data import board_to_tensor, move_to_index, index_to_move, ChessDatasetTrain
import torch.optim as optim
import torch.nn as nn
import random
import os
from tqdm import tqdm  # For progress bars
from chess_app.utils import get_device, Logger, TensorBoardLogger, EloRating
from chess_app.config import Config
import json

def self_play(model, device, num_games=100, engine_path=Config.ENGINE_PATH, depth=2, logger=None, elo_rating=None):
    """
    Generates training data via self-play against Stockfish.
    """
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    training_data = []
    move_quality_mapping = {
        "Great Step": 4,
        "Good Step": 3,
        "Average Step": 2,
        "Bad Step": 1,
        "Blunder": 0
    }

    for game_num in tqdm(range(num_games), desc="Self-Play Games", disable=not logger):
        board = chess.Board()
        game_moves = []
        outcome_val = 0.5  # Default for draw

        while not board.is_game_over():
            # AI's move (White)
            board_tensor = board_to_tensor(board).numpy()
            if model:
                model.eval()
                with torch.no_grad():
                    policy, value = model(board_to_tensor(board).unsqueeze(0).to(device))
                move_probs = torch.exp(policy).cpu().numpy()[0]
                top_move_indices = move_probs.argsort()[-10:][::-1]  # Top 10 moves
                move_found = False
                for move_index in top_move_indices:
                    move = index_to_move(move_index, board)
                    if move in board.legal_moves:
                        # Predict move quality
                        move_quality = model.predict_move_quality(board_to_tensor(board).unsqueeze(0).to(device))
                        training_data.append((board_tensor, move_to_index(move), 0.0, move_quality))
                        board.push(move)
                        game_moves.append(move)
                        move_found = True
                        break
                if not move_found:
                    move = random.choice(list(board.legal_moves))
                    move_quality = "Average Step"
                    training_data.append((board_tensor, move_to_index(move), 0.0, move_quality))
                    board.push(move)
                    game_moves.append(move)
            else:
                # If no model, use Stockfish
                result = engine.play(board, chess.engine.Limit(depth=depth))
                move = result.move
                training_data.append((board_tensor, move_to_index(move), 0.0, "Average Step"))
                board.push(move)
                game_moves.append(move)

            if board.is_game_over():
                break

            # Stockfish's move (Black)
            result = engine.play(board, chess.engine.Limit(time=depth))
            stockfish_move = result.move
            training_data.append((board_tensor, move_to_index(stockfish_move), 0.0, "Average Step"))
            board.push(stockfish_move)
            game_moves.append(stockfish_move)

        # Determine outcome
        outcome = board.outcome()
        if outcome.winner is None:
            outcome_val = 0.5
        elif outcome.winner == chess.WHITE:
            outcome_val = 1.0
        else:
            outcome_val = 0.0

        # Update Elo Rating
        if elo_rating:
            elo_rating.update(opponent_rating=1500, score=outcome_val)

        # Update outcome for all AI moves in the game
        for i in range(0, len(game_moves), 2):  # AI moves are even-indexed
            if i < len(training_data):
                board_tensor_i, move_index_i, _, move_quality_i = training_data[i]
                training_data[i] = (board_tensor_i, move_index_i, outcome_val, move_quality_i)

        if logger:
            elo = elo_rating.rating if elo_rating else "N/A"
            logger.info(f"Game {game_num + 1}/{num_games} completed. Outcome: {outcome_val}. ELO: {elo}")

    engine.quit()
    return training_data

def train_model(model, device, training_data, epochs=10, batch_size=64, lr=1e-4, logger=None, tensorboard_logger=None, elo_rating=None):
    """
    Trains the ChessNet model on the provided training data.
    """
    dataset = ChessDatasetTrain(training_data)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)

    criterion_policy = nn.NLLLoss()
    criterion_value = nn.MSELoss()
    criterion_quality = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        total_loss_policy = 0
        total_loss_value = 0
        total_loss_quality = 0
        loop = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}", leave=False, disable=not logger)
        for batch_idx, (boards, moves, outcomes, qualities) in enumerate(loop):
            boards = boards.to(device)
            moves = moves.to(device)
            outcomes = outcomes.to(device).float()
            qualities = qualities.to(device).long()

            optimizer.zero_grad()
            policy, value = model(boards)

            # Policy loss
            loss_policy = criterion_policy(policy, moves)

            # Value loss
            loss_value = criterion_value(value.squeeze(), outcomes)

            # Move Quality loss
            # Assuming move_quality is a separate output, which requires modifying the model
            # For simplicity, we'll skip this unless the model is adjusted accordingly

            # Total loss
            loss = loss_policy + loss_value  # + loss_quality
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_loss_policy += loss_policy.item()
            total_loss_value += loss_value.item()
            # total_loss_quality += loss_quality.item()

            if logger:
                loop.set_postfix(loss=loss.item())

        avg_loss = total_loss / len(dataloader)
        avg_loss_policy = total_loss_policy / len(dataloader)
        avg_loss_value = total_loss_value / len(dataloader)
        # avg_loss_quality = total_loss_quality / len(dataloader)

        if logger:
            logger.info(f"Epoch [{epoch+1}/{epochs}], Average Loss: {avg_loss:.4f}, Policy Loss: {avg_loss_policy:.4f}, Value Loss: {avg_loss_value:.4f}")
            # Log move quality loss if implemented

        # Log to TensorBoard
        if tensorboard_logger:
            metrics = {
                'Loss/Total': avg_loss,
                'Loss/Policy': avg_loss_policy,
                'Loss/Value': avg_loss_value
                # 'Loss/Quality': avg_loss_quality
            }
            tensorboard_logger.log_metrics(metrics, epoch)

        scheduler.step()

    return model

def main():
    config = Config()

    # Ensure log directory exists
    if not os.path.exists(config.LOG_DIR):
        os.makedirs(config.LOG_DIR)
    if not os.path.exists(config.PLOTLY_LOG_DIR):
        os.makedirs(config.PLOTLY_LOG_DIR)

    logger_instance = Logger()
    logger = logger_instance.get_logger()

    tensorboard_logger = TensorBoardLogger()

    device = get_device()
    logger.info(f"Using device: {device}")

    model = ChessNet(
        board_size=config.BOARD_SIZE,
        num_channels=config.NUM_CHANNELS,
        num_residual_blocks=config.NUM_RESIDUAL_BLOCKS
    ).to(device)

    # Check if a pre-trained model exists
    model_path = config.MODEL_PATH
    if os.path.exists(model_path):
        load_model(model, model_path, device)
        logger.info("Loaded existing model.")
    else:
        logger.info("No existing model found. Starting from scratch.")

    # Initialize Elo Rating
    elo_rating = EloRating(initial_elo=config.INITIAL_ELO, k_factor=config.K_FACTOR)

    # Iterate training loop
    iterations = config.NUM_ITERATIONS  # Define number of iterations in config.py
    for iteration in range(iterations):
        logger.info(f"Starting Training Iteration {iteration + 1}/{iterations}")

        # Self-Play to generate data
        training_data = self_play(
            model=model,
            device=device,
            num_games=config.NUM_GAMES_PER_ITERATION,
            engine_path=config.ENGINE_PATH,
            depth=config.DEPTH,
            logger=logger,
            elo_rating=elo_rating
        )
        logger.info(f"Collected {len(training_data)} training samples.")

        # Train the model
        logger.info("Starting model training...")
        model = train_model(
            model=model,
            device=device,
            training_data=training_data,
            epochs=config.EPOCHS,
            batch_size=config.BATCH_SIZE,
            lr=config.LEARNING_RATE,
            logger=logger,
            tensorboard_logger=tensorboard_logger,
            elo_rating=elo_rating
        )
        logger.info("Model training completed.")

        # Save the trained model
        save_model(model, model_path)
        logger.info(f"Model saved to {model_path}")

    # Close TensorBoard logger
    tensorboard_logger.close()

    logger.info("Training loop completed.")

if __name__ == "__main__":
    main()