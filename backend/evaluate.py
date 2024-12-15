# evaluate.py

import chess
import chess.engine
import torch
from chess_app.model import ChessNet, load_model
from chess_app.data import board_to_tensor, move_to_index, index_to_move
import random
import os
from tqdm import tqdm
from chess_app.utils import get_device, Logger, TensorBoardLogger, EloRating, AIPlayer
from chess_app.config import Config


def evaluate_model(
    model_path,
    device,
    num_games=10,
    engine_path=Config.ENGINE_PATH,
    depth=2,
    logger=None,
    tensorboard_logger=None,
):
    ai_player = AIPlayer(model_path=model_path, device=device, side=chess.WHITE)
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    elo_rating = EloRating(initial_elo=Config.INITIAL_ELO, k_factor=Config.K_FACTOR)

    results = {"AI_Wins": 0, "Stockfish_Wins": 0, "Draws": 0}

    for game_num in tqdm(
        range(num_games), desc="Self-Play Games", disable=(logger is None)
    ):
        board = chess.Board()
        while not board.is_game_over():
            if board.turn == ai_player.side:
                move = ai_player.get_best_move(board)
            else:
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

        elo_rating.update(opponent_rating=1500, score=outcome_val)

        if logger:
            elo = elo_rating.rating
            logger.info(
                f"Game {game_num + 1}/{num_games} completed. Outcome: {outcome_val}. ELO: {elo}"
            )

        if tensorboard_logger:
            metrics = {
                "Evaluation/Game_Result": outcome_val,
                "Evaluation/Elo": elo_rating.rating,
            }
            tensorboard_logger.log_metrics(metrics, epoch=game_num)

    engine.quit()
    ai_player.close()
    return results, elo_rating.rating


def main():
    config = Config()
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
    num_games = config.NUM_GAMES_EVAL

    logger.info(f"Evaluating model on {num_games} games against Stockfish.")
    results, final_elo = evaluate_model(
        model_path=model_path,
        device=device,
        num_games=num_games,
        engine_path=config.ENGINE_PATH,
        depth=2,
        logger=logger,
        tensorboard_logger=tensorboard_logger,
    )

    logger.info("Evaluation Results:")
    logger.info(f"AI Wins: {results['AI_Wins']}")
    logger.info(f"Stockfish Wins: {results['Stockfish_Wins']}")
    logger.info(f"Draws: {results['Draws']}")
    logger.info(f"Final Elo Rating: {final_elo:.0f}")

    if tensorboard_logger:
        metrics = {
            "Evaluation/AI_Wins": results["AI_Wins"],
            "Evaluation/Stockfish_Wins": results["Stockfish_Wins"],
            "Evaluation/Draws": results["Draws"],
            "Evaluation/Final_Elo": final_elo,
        }
        tensorboard_logger.log_metrics(metrics, epoch=num_games)

    tensorboard_logger.close()


if __name__ == "__main__":
    main()
