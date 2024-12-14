# chess_app/evaluate.py

import chess
import chess.engine
from chess_app.utils import AIPlayer
import torch
from chess_app.config import Config

def evaluate_model(model_path, device, num_games=10, engine_path="/opt/homebrew/bin/stockfish", depth=2):
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
                result = engine.play(board, chess.engine.Limit(time=depth))
                move = result.move
            board.push(move)

        outcome = board.outcome()
        if outcome.winner is None:
            results["Draws"] += 1
        elif outcome.winner == ai_player.side:
            results["AI_Wins"] += 1
        else:
            results["Stockfish_Wins"] += 1

    engine.quit()
    ai_player.close()
    return results

def main():
    config = None
    try:
        from chess_app.config import Config
        config = Config()
    except ImportError:
        config = None  # Use default values if config.py is missing

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = config.MODEL_PATH if config and hasattr(config, 'MODEL_PATH') else "chess_model.pth"
    engine_path = config.ENGINE_PATH if config and hasattr(config, 'ENGINE_PATH') else "/opt/homebrew/bin/stockfish"
    num_games = config.NUM_GAMES // 100 if config and hasattr(config, 'NUM_GAMES') else 10

    results = evaluate_model(
        model_path=model_path,
        device=device,
        num_games=num_games,
        engine_path=engine_path,
        depth=2
    )
    print("Evaluation Results:")
    print(f"AI Wins: {results['AI_Wins']}")
    print(f"Stockfish Wins: {results['Stockfish_Wins']}")
    print(f"Draws: {results['Draws']}")

if __name__ == "__main__":
    main()