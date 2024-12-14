# chess_app/evaluate.py

import chess
import chess.engine
import torch
from chess_app.model import ChessNet, load_model, save_model
from chess_app.data import board_to_tensor, move_to_index, index_to_move
import random
import os
from tqdm import tqdm  # For progress bars
from chess_app.utils import get_device, Logger, TensorBoardLogger, EloRating, AIPlayer
from chess_app.config import Config
import json

def evaluate_model(model_path, device, num_games=10, engine_path=Config.ENGINE_PATH, depth=2, logger=None, tensorboard_logger=None):
    """
    Evaluates the Chess AI model by playing against Stockfish.

    :param model_path: Path to the trained model.
    :param device: Torch device to run the model on.
    :param num_games: Number of games to play for evaluation.
    :param engine_path: Path to the Stockfish engine executable.
    :param depth: Search depth for Stockfish.
    :param logger: Logger instance for logging.
    :param tensorboard_logger: TensorBoardLogger instance for logging to TensorBoard.
    :return: Tuple (results dictionary, final Elo rating)
    """
    # Initialize AIPlayer with the model
    ai_player = AIPlayer(model_path=model_path, device=device, side=chess.WHITE)
    # Initialize Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    # Initialize Elo Rating
    elo_rating = EloRating(initial_elo=Config.INITIAL_ELO, k_factor=Config.K_FACTOR)

    results = {"AI_Wins": 0, "Stockfish_Wins": 0, "Draws": 0}

    for game_num in tqdm(range(num_games), desc="Self-Play Games", disable=not logger):
        board = chess.Board()
        while not board.is_game_over():
            if board.turn == ai_player.side:
                # AI's turn
                move = ai_player.get_best_move(board)
            else:
                # Stockfish's turn
                result = engine.play(board, chess.engine.Limit(depth=depth))
                move = result.move
            board.push(move)

        outcome = board.outcome()
        if outcome.winner is None:
            results["Draws"] += 1
            outcome_val = 0.5
        elif outcome.winner == ai_player.side:
            results["AI_Wins"] += 1
            outcome_val = 1.0
        else:
            results["Stockfish_Wins"] += 1
            outcome_val = 0.0

        # Update Elo Rating
        elo_rating.update(opponent_rating=1500, score=outcome_val)

        # Log the outcome
        if logger:
            elo = elo_rating.rating if elo_rating else "N/A"
            logger.info(f"Game {game_num + 1}/{num_games} completed. Outcome: {outcome_val}. ELO: {elo}")

        # Log to TensorBoard
        if tensorboard_logger:
            metrics = {
                'Evaluation/Game_Result': outcome_val,
                'Evaluation/Elo': elo_rating.rating
            }
            tensorboard_logger.log_metrics(metrics, epoch=game_num)  # Use game_num as epoch for uniqueness

    engine.quit()
    ai_player.close()
    return results, elo_rating.rating

def main():
    """
    Main function to run the evaluation of the Chess AI model.
    """
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

    model_path = config.MODEL_PATH
    num_games = config.NUM_GAMES_EVAL  # Define in config.py

    logger.info(f"Evaluating model on {num_games} games against Stockfish.")

    results, final_elo = evaluate_model(
        model_path=model_path,
        device=device,
        num_games=num_games,
        engine_path=config.ENGINE_PATH,
        depth=2,
        logger=logger,
        tensorboard_logger=tensorboard_logger
    )

    logger.info("Evaluation Results:")
    logger.info(f"AI Wins: {results['AI_Wins']}")
    logger.info(f"Stockfish Wins: {results['Stockfish_Wins']}")
    logger.info(f"Draws: {results['Draws']}")
    logger.info(f"Final Elo Rating: {final_elo:.0f}")

    # Log results to TensorBoard
    if tensorboard_logger:
        metrics = {
            'Evaluation/AI_Wins': results['AI_Wins'],
            'Evaluation/Stockfish_Wins': results['Stockfish_Wins'],
            'Evaluation/Draws': results['Draws'],
            'Evaluation/Final_Elo': final_elo
        }
        tensorboard_logger.log_metrics(metrics, epoch=num_games)

    tensorboard_logger.close()

if __name__ == "__main__":
    main()