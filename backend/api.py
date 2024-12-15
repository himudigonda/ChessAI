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
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Explicit CORS Configuration

# Global variable to hold game state
current_board = chess.Board()
ai_player = None
opponent_ai = None


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
    # Initialize AI players based on mode
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

            return jsonify(
                {
                    "fen": board_to_fen(current_board),
                    "legalMoves": get_legal_moves(current_board),
                    "moves": get_moves_san(current_board),
                    "gameOver": False,
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

            return jsonify(
                {
                    "fen": board_to_fen(current_board),
                    "legalMoves": get_legal_moves(current_board),
                    "moves": get_moves_san(current_board),
                    "gameOver": False,
                }
            )
        else:
            print(f"[{timestamp}] No AI move found")
            return jsonify({"error": "No AI move found"}), 500
    except Exception as e:
        print(f"[{timestamp}] Error in AI move: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error in AI move"}), 500


if __name__ == "__main__":
    print("Starting Flask server")
    app.run(debug=True, port=6009, host="0.0.0.0")
