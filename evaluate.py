# chess_app/evaluate.py

import chess
import chess.engine
from chess_app.utils import AIPlayer, Logger, TensorBoardLogger
import torch
from chess_app.config import Config
import os

def evaluate_model(model_path, device, num_games=10, engine_path=Config.ENGINE_PATH, depth=2, logger=None, tensorboard_logger=None):
    ai_player = AIPlayer(model_path=model_path, device=device, side=chess.WHITE)
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    results = {"AI_Wins": 0, "Stockfish_Wins": 0, "Draws": 0}

    for game_num in range(num_games):
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

        if logger:
            logger.info(f"Evaluation Game {game_num + 1}/{num_games}: Outcome = {outcome_val}")

        if tensorboard_logger:
            metrics = {
                'Evaluation/Game_Result': outcome_val
            }
            tensorboard_logger.log_metrics(metrics, epoch=0)  # Epoch can be modified as needed

    engine.quit()
    ai_player.close()
    return results

def main():
    config = Config()

    # Ensure log directory exists
    if not os.path.exists(config.LOG_DIR):
        os.makedirs(config.LOG_DIR)
    if not os.path.exists(config.TENSORBOARD_LOG_DIR):
        os.makedirs(config.TENSORBOARD_LOG_DIR)

    logger_instance = Logger()
    logger = logger_instance.get_logger()

    tensorboard_logger = TensorBoardLogger()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    model_path = config.MODEL_PATH
    num_games = config.NUM_GAMES // 100 if config and hasattr(config, 'NUM_GAMES') else 10

    logger.info(f"Evaluating model on {num_games} games against Stockfish.")

    results = evaluate_model(
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

    # Log results to TensorBoard
    if tensorboard_logger:
        metrics = {
            'Evaluation/AI_Wins': results['AI_Wins'],
            'Evaluation/Stockfish_Wins': results['Stockfish_Wins'],
            'Evaluation/Draws': results['Draws']
        }
        tensorboard_logger.log_metrics(metrics, epoch=0)

    tensorboard_logger.close()

if __name__ == "__main__":
    main()