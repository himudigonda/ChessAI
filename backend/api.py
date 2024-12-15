from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import chess
from chess_app.utils import AIPlayer, get_device
from chess_app.data import move_to_index
from chess_app.config import Config
import os
import time
import traceback


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# Global variable to hold game state
current_board = chess.Board()
ai_player = None
opponent_ai = None
engine_path = Config.ENGINE_PATH


def initialize_ai():
    # Initialize AI players
    pass


initialize_ai()


def board_to_fen(board):
    return board.fen()


def get_legal_moves(board):
    return [move.uci() for move in board.legal_moves]


def get_moves_san(board):
    san_moves = []
    temp_board = chess.Board()
    for move in board.move_stack:
        try:
            san = temp_board.san(move)
            san_moves.append(san)
            temp_board.push(move)
        except Exception as e:
            print(f"Error generating SAN for move {move}: {e}")
            san_moves.append("Invalid Move")
    return san_moves


@app.route("/api/start_game/<mode>", methods=["POST"])
@cross_origin()
def start_game(mode):
    global current_board, ai_player, opponent_ai
    timestamp = time.time()
    print(f"[{timestamp}] Starting game in mode: {mode}")
    current_board.reset()
    ai_player = None
    opponent_ai = None

    if mode == "user_vs_stockfish":
        print(f"[{timestamp}] Initializing against stockfish")
        ai_player = AIPlayer(
            model_path=None,
            device=get_device(),
            side=chess.BLACK,
            engine_path=engine_path,
        )
    elif mode == "user_vs_cai":
        print(f"[{timestamp}] Initializing against cAI")
        ai_player = AIPlayer(
            model_path=Config.MODEL_PATH, device=get_device(), side=chess.BLACK
        )
    elif mode == "watch_cai_vs_stockfish":
        print(f"[{timestamp}] Initializing cAI vs stockfish")
        ai_player = AIPlayer(
            model_path=Config.MODEL_PATH, device=get_device(), side=chess.WHITE
        )
        opponent_ai = AIPlayer(
            model_path=None,
            device=get_device(),
            side=chess.BLACK,
            engine_path=engine_path,
        )

    return jsonify({"message": "Game started", "mode": mode})


@app.route("/api/get_board", methods=["GET"])
@cross_origin()
def get_board():
    global current_board
    return jsonify(
        {
            "fen": board_to_fen(current_board),
            "legalMoves": get_legal_moves(current_board),
            "moves": get_moves_san(current_board),
            "gameOver": current_board.is_game_over(),
            "turn": "white" if current_board.turn == chess.WHITE else "black",
        }
    )


@app.route("/api/make_move", methods=["POST"])
@cross_origin()
def make_move():
    global current_board
    timestamp = time.time()
    data = request.get_json()
    move_uci = data.get("move")
    print(f"[{timestamp}] Making move: {move_uci}")
    if not move_uci:
        print(f"[{timestamp}] Error: Move not provided")
        return jsonify({"error": "Move not provided"}), 400

    try:
        move = chess.Move.from_uci(move_uci)
        if move in current_board.legal_moves:
            current_board.push(move)
            print(f"[{timestamp}] Move made: {move_uci}")

            if current_board.is_game_over():
                print(f"[{timestamp}] Game over detected")
                return jsonify(
                    {
                        "fen": board_to_fen(current_board),
                        "legalMoves": get_legal_moves(current_board),
                        "moves": get_moves_san(current_board),
                        "gameOver": True,
                        "winner": (
                            str(current_board.outcome().winner)
                            if current_board.outcome()
                            else None
                        ),
                    }
                )
            captured_pieces = {
                "white": [],
                "black": [],
            }
            temp_board = chess.Board()
            for move_in_stack in current_board.move_stack:
                if temp_board.is_capture(move_in_stack):
                    captured_piece = temp_board.piece_at(move_in_stack.to_square)
                    if captured_piece:
                        symbol = captured_piece.symbol()
                        if captured_piece.color == chess.WHITE:
                            captured_pieces["white"].append(symbol.upper())
                        else:
                            captured_pieces["black"].append(symbol.lower())
                temp_board.push(move_in_stack)

            return jsonify(
                {
                    "fen": board_to_fen(current_board),
                    "legalMoves": get_legal_moves(current_board),
                    "moves": get_moves_san(current_board),
                    "gameOver": False,
                    "capturedPieces": captured_pieces,
                }
            )
        else:
            print(f"[{timestamp}] Invalid move attempted: {move_uci}")
            print(f"Current board FEN: {current_board.fen()}")
            return jsonify({"error": "Invalid move"}), 400

    except ValueError as e:
        print(f"[{timestamp}] Invalid move format: {e}")
        traceback.print_exc()
        return jsonify({"error": "Invalid move format"}), 400
    except Exception as e:
        print(f"[{timestamp}] Error making move: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error making move"}), 500


@app.route("/api/undo_move", methods=["POST"])
@cross_origin()
def undo_move():
    global current_board
    timestamp = time.time()
    print(f"[{timestamp}] Undoing move")
    if len(current_board.move_stack) > 0:
        try:
            current_board.pop()
            print(f"[{timestamp}] Move undone")
            return jsonify(
                {
                    "fen": board_to_fen(current_board),
                    "legalMoves": get_legal_moves(current_board),
                    "moves": get_moves_san(current_board),
                    "gameOver": False,
                }
            )
        except Exception as e:
            print(f"[{timestamp}] Error undoing move: {e}")
            traceback.print_exc()
            return jsonify({"error": "Error undoing move"}), 500
    else:
        print(f"[{timestamp}] No moves to undo.")
        return jsonify({"error": "No moves to undo."}), 400


@app.route("/api/redo_move", methods=["POST"])
@cross_origin()
def redo_move():
    global current_board
    timestamp = time.time()
    print(f"[{timestamp}] Redoing move")
    try:
        # We cannot redo without a way to track moves.
        return jsonify({"error": "Redo move is not yet implemented."}), 400
    except Exception as e:
        print(f"[{timestamp}] Error redoing move: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error redoing move"}), 500


@app.route("/api/validate_move", methods=["POST"])
@cross_origin()
def validate_move():
    timestamp = time.time()
    data = request.get_json()
    move_uci = data.get("move")
    print(f"[{timestamp}] Validating move: {move_uci}")
    if not move_uci:
        print(f"[{timestamp}] Error: Move not provided")
        return jsonify({"error": "Move not provided"}), 400

    try:
        move = chess.Move.from_uci(move_uci)
        is_legal = move in current_board.legal_moves
        print(f"[{timestamp}] Move {move_uci} is {'legal' if is_legal else 'illegal'}")
        return jsonify({"isLegal": is_legal})
    except ValueError as e:
        print(f"[{timestamp}] Invalid move format: {e}")
        traceback.print_exc()
        return jsonify({"error": "Invalid move format"}), 400
    except Exception as e:
        print(f"[{timestamp}] Error validating move: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error validating move"}), 500


@app.route("/api/ai_move", methods=["POST"])
@cross_origin()
def ai_move():
    global current_board, ai_player, opponent_ai
    timestamp = time.time()
    print(f"[{timestamp}] AI making a move")
    try:
        if not ai_player and not opponent_ai:
            print(f"[{timestamp}] Error: AI not initialized")
            return jsonify({"error": "AI not initialized"}), 500

        if opponent_ai and current_board.turn == opponent_ai.side:
            move = opponent_ai.get_best_move(current_board)
        elif ai_player and current_board.turn == ai_player.side:
            move = ai_player.get_best_move(current_board)
        else:
            print(f"[{timestamp}] Error No AI to make a move")
            return jsonify({"error": "No AI to make move"}), 400

        if move:
            current_board.push(move)
            print(f"[{timestamp}] AI move made: {move}")

            if current_board.is_game_over():
                print(f"[{timestamp}] Game over detected")
                return jsonify(
                    {
                        "fen": board_to_fen(current_board),
                        "legalMoves": get_legal_moves(current_board),
                        "moves": get_moves_san(current_board),
                        "gameOver": True,
                        "winner": (
                            str(current_board.outcome().winner)
                            if current_board.outcome()
                            else None
                        ),
                    }
                )
            captured_pieces = {
                "white": [],
                "black": [],
            }
            temp_board = chess.Board()
            for move_in_stack in current_board.move_stack:
                if temp_board.is_capture(move_in_stack):
                    captured_piece = temp_board.piece_at(move_in_stack.to_square)
                    if captured_piece:
                        symbol = captured_piece.symbol()
                        if captured_piece.color == chess.WHITE:
                            captured_pieces["white"].append(symbol.upper())
                        else:
                            captured_pieces["black"].append(symbol.lower())
                temp_board.push(move_in_stack)

            return jsonify(
                {
                    "fen": board_to_fen(current_board),
                    "legalMoves": get_legal_moves(current_board),
                    "moves": get_moves_san(current_board),
                    "gameOver": False,
                    "capturedPieces": captured_pieces,
                }
            )
        else:
            print(f"[{timestamp}] No AI move found")
            return jsonify({"error": "No AI move found"}), 500
    except Exception as e:
        print(f"[{timestamp}] Error in AI move: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error in AI move"}), 500


@app.route("/api/save_game", methods=["POST"])
@cross_origin()
def save_game():
    global current_board
    timestamp = time.time()
    print(f"[{timestamp}] Saving game")
    try:
        data = request.get_json()
        fen = data.get("fen")
        if fen:
            board = chess.Board(fen)
            from chess_app.utils import SaveLoad

            SaveLoad.save_game(board, "saved_game.pgn")
            print(f"[{timestamp}] Game saved successfully")
            return jsonify({"success": True, "message": "Game Saved Successfully"})
        else:
            return (
                jsonify({"success": False, "message": "Failed to save: no fen found"}),
                400,
            )
    except Exception as e:
        print(f"[{timestamp}] Error saving game: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error saving game: {e}"}), 500


@app.route("/api/load_game", methods=["GET"])
@cross_origin()
def load_game():
    global current_board
    timestamp = time.time()
    print(f"[{timestamp}] Loading game")
    try:
        from chess_app.utils import SaveLoad

        board = SaveLoad.load_game("saved_game.pgn")
        current_board = board
        print(f"[{timestamp}] Game loaded successfully")
        return jsonify(
            {
                "success": True,
                "fen": board_to_fen(current_board),
                "moves": get_moves_san(current_board),
                "message": "Game Loaded Successfully",
            }
        )
    except Exception as e:
        print(f"[{timestamp}] Error loading game: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error loading game: {e}"}), 500


@app.route("/api/resign_game", methods=["POST"])
@cross_origin()
def resign_game():
    global current_board
    timestamp = time.time()
    print(f"[{timestamp}] Resigning game")
    try:
        # Logic can be implemented here. We can simply return a 200 message.
        current_board.clear()
        return jsonify({"success": True, "message": "Game Resigned."})
    except Exception as e:
        print(f"[{timestamp}] Error resigning game: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error resigning game: {e}"}), 500


@app.route("/api/offer_draw", methods=["POST"])
@cross_origin()
def offer_draw():
    timestamp = time.time()
    print(f"[{timestamp}] Offering draw")
    try:
        # Logic can be implemented here, We can simply return a 200 message.
        return jsonify({"success": True, "message": "Draw Offered."})
    except Exception as e:
        print(f"[{timestamp}] Error offering draw: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error offering draw: {e}"}), 500


if __name__ == "__main__":
    print("Starting Flask server")
    app.run(debug=True, port=6009, host="0.0.0.0")
