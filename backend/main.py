# main.py

import os
import torch
from chess_app.utils import (
    SoundEffects,
    SaveLoad,
    AIPlayer,
    Logger,
    GameSaver,
    EloRating,
)
from chess_app.data import board_to_tensor, move_to_index
import sys
import chess
from threading import Thread
from chess_app.config import Config
import tkinter as tk
from tkinter import messagebox
from chess_app.ui.utils import show_message
from chess_app.ui.main_window import MainWindow
import time
import random


class ChessApp:
    def __init__(self):
        print("Initializing ChessApp")
        self.ai_player = None
        self.opponent_ai = None
        self.opponent_engine = None
        self.model_loaded = False
        self.white_time = 300
        self.black_time = 300
        self.board = chess.Board()
        self.captured_pieces = {"white": [], "black": []}
        self.drag_start_coords = None
        self.dragging_piece = None
        self.elo_rating = EloRating(
            initial_elo=Config.INITIAL_ELO, k_factor=Config.K_FACTOR
        )
        self.game_saver = GameSaver()
        self.last_move = None
        self.logger_instance = Logger()
        self.logger = self.logger_instance.get_logger()
        self.redo_stack = []
        self.selected_square = None
        self.sound_effects = SoundEffects()
        self.sound_enabled = True
        self.window = MainWindow(self)
        self.apply_theme()
        self.load_ai_model()

    def apply_theme(self):
        print("Applying theme")
        self.window.refresh_ui()

    def load_ai_model(self):
        print("Loading AI model")
        # Attempt to load AI model from MODEL_PATH
        if not Config.MODEL_PATH or not os.path.exists(Config.MODEL_PATH):
            print("No model path found or path does not exist")
            self.model_loaded = False
            self.ai_player = AIPlayer(
                model_path=Config.MODEL_PATH,
                device=("cuda" if torch.cuda.is_available() else "cpu"),
                side=chess.WHITE,
            )
            self.logger.info(
                "No trained model found, will fallback to Stockfish when needed."
            )
            self.update_status(
                "No trained model found. Using Stockfish fallback.", color="blue"
            )
        else:
            try:
                print("Model path found, attempting to load model")
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.ai_player = AIPlayer(
                    model_path=Config.MODEL_PATH, device=device, side=chess.WHITE
                )
                self.model_loaded = True
                self.update_status("AI model loaded successfully.", color="green")
            except Exception as e:
                print(f"Failed to load AI model: {e}")
                self.model_loaded = False
                self.ai_player = AIPlayer(
                    device=("cuda" if torch.cuda.is_available() else "cpu"),
                    side=chess.WHITE,
                )
                self.update_status(f"Failed to load AI model: {e}", color="red")
                self.logger.error(f"Failed to load AI model: {e}")

    def run(self):
        print("Running ChessApp")
        self.window.mainloop()

    def handle_move(self, move):
        print(f"Handling move: {move}")
        try:
            if not self.board.is_legal(move):
                print(f"Illegal move attempted: {move}")
                self.logger.warning(f"Attempted illegal move: {move}")
                self.update_status(f"Illegal move attempted: {move}.", color="red")
                return

            self.board.push(move)
            self.last_move = (move.from_square, move.to_square)
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()
            move_san = self.board.san(move)
            self.window.side_panel.update_move_list(move_san)

            if self.board.is_capture(move):
                captured_piece = self.board.piece_at(move.to_square)
                if captured_piece:
                    symbol = captured_piece.symbol()
                    if captured_piece.color == chess.WHITE:
                        self.captured_pieces["white"].append(symbol.upper())
                    else:
                        self.captured_pieces["black"].append(symbol.lower())
                    self.window.side_panel.update_captured_pieces(
                        self.captured_pieces["white"], self.captured_pieces["black"]
                    )

            if self.sound_enabled:
                self.play_sound(move)

            if self.board.is_game_over():
                print("Game over detected")
                self.handle_game_over()
            else:
                # If it's AI's turn (if playing against stockfish or model)
                if (
                    self.ai_player
                    and self.board.turn == self.ai_player.side
                    and self.opponent_engine is None
                    and self.opponent_ai is None
                ):
                    print("AI's turn to move")
                    # cAI is black, user is white, or vice versa if set
                    self.window.after(1000, self.ai_make_move)
                elif self.opponent_engine and self.board.turn == chess.BLACK:
                    print("Stockfish's turn to move")
                    self.window.after(1000, self.stockfish_move)
                elif self.opponent_ai and self.board.turn == self.opponent_ai.side:
                    print("Opponent AI's turn to move")
                    self.window.after(1000, self.model_vs_model_move)

        except Exception as e:
            print(f"Error handling move: {str(e)}")
            self.update_status(f"Error handling move: {str(e)}", color="red")
            self.logger.error(f"Error in handle_move: {str(e)}")

    def stockfish_move(self):
        print("Stockfish making a move")
        if self.opponent_engine and self.board.turn == chess.BLACK:
            result = self.opponent_engine.play(
                self.board, chess.engine.Limit(depth=Config.DEPTH)
            )
            if result.move:
                self.handle_move(result.move)

    def model_vs_model_move(self):
        print("Model vs Model move")
        # If playing AI vs AI
        if self.opponent_ai and self.board.turn == self.opponent_ai.side:
            move = self.opponent_ai.get_best_move(self.board)
            if move:
                self.handle_move(move)
        elif self.ai_player and self.board.turn == self.ai_player.side:
            move = self.ai_player.get_best_move(self.board)
            if move:
                self.handle_move(move)

    def ai_make_move(self):
        print("AI making a move")
        if self.ai_player and self.model_loaded:
            move = self.ai_player.get_best_move(self.board)
            if move:
                self.handle_move(move)

    def start_game(self):
        print("Starting game")
        self.update_status("Game started.", color="green")
        if (
            self.ai_player
            and self.ai_player.side == chess.WHITE
            and self.opponent_engine is None
            and self.opponent_ai is None
        ):
            # If AI is white and playing alone
            self.ai_make_move()

    def handle_game_over(self):
        print("Handling game over")
        outcome = self.board.outcome()
        if outcome.winner is None:
            result_text = "It's a draw!"
            self.update_status(result_text, color="blue")
        elif outcome.winner == chess.WHITE:
            result_text = "White wins!"
            self.update_status(result_text, color="green")
        else:
            result_text = "Black wins!"
            self.update_status(result_text, color="red")

        self.game_saver.save_game(self.board)
        self.logger.info(f"Game over: {result_text}")

    def save_game(self):
        print("Saving game")
        try:
            SaveLoad.save_game(self.board, "saved_game.pgn")
            self.update_status("Game saved successfully.", color="green")
        except Exception as e:
            print(f"Error saving game: {str(e)}")
            self.update_status(f"Error saving game: {str(e)}", color="red")
            self.logger.error(f"Error saving game: {str(e)}")

    def load_game(self):
        print("Loading game")
        try:
            board = SaveLoad.load_game("saved_game.pgn")
            self.board = board
            self.window.chessboard.board = self.board
            self.window.chessboard.last_move = self.last_move
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()
            self.update_status("Game loaded successfully.", color="green")
        except Exception as e:
            print(f"Error loading game: {str(e)}")
            self.update_status(f"Error loading game: {str(e)}", color="red")
            self.logger.error(f"Error loading game: {str(e)}")

    def resign(self):
        print("Resigning game")
        if self.board.turn == chess.WHITE:
            result_text = "White resigns. Black wins!"
            self.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)
        else:
            result_text = "Black resigns. White wins!"
            self.update_status(result_text, color="green")
            self.elo_rating.update(opponent_rating=1500, score=1.0)

        self.game_saver.save_game(self.board)
        self.logger.info(f"Game over: {result_text}. ELO: {self.elo_rating.rating:.0f}")

    def offer_draw(self):
        print("Offering draw")
        self.update_status("Draw offered to the opponent.", color="blue")

    def undo_move(self):
        print("Undoing move")
        if len(self.board.move_stack) > 0:
            last_move = self.board.pop()
            self.redo_stack.append(last_move)
            if self.board.is_capture(last_move):
                # captured piece restoration logic if needed
                pass
            self.update_status("Move undone.", color="green")
            self.window.side_panel.undo_move()
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()

    def redo_move(self):
        print("Redoing move")
        if self.redo_stack:
            move = self.redo_stack.pop()
            self.board.push(move)
            if self.board.is_capture(move):
                captured_piece = self.board.piece_at(move.to_square)
                if captured_piece:
                    symbol = captured_piece.symbol()
                    if captured_piece.color:
                        self.captured_pieces["black"].append(symbol.upper())
                    else:
                        self.captured_pieces["white"].append(symbol.lower())
            move_san = self.board.san(move)
            self.window.side_panel.update_move_list(move_san)
            self.update_status("Move redone.", color="green")
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()

    def restart_game(self):
        print("Restarting game")
        self.board.reset()
        self.last_move = None
        self.white_time = 300
        self.black_time = 300
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []
        self.window.side_panel.update_captured_pieces(
            self.captured_pieces["white"], self.captured_pieces["black"]
        )
        self.window.side_panel.move_list.config(state="normal")
        self.window.side_panel.move_list.delete("1.0", tk.END)
        self.window.side_panel.move_list.config(state="disabled")
        self.window.side_panel.update_timer("White: 05:00 - Black: 05:00")
        self.window.chessboard.board = self.board
        self.window.chessboard.last_move = self.last_move
        self.window.chessboard.draw_board()
        self.window.chessboard.draw_pieces()
        self.update_status("Game restarted.", color="green")

    def set_ai_difficulty(self, level):
        print(f"Setting AI difficulty to level {level}")
        if self.ai_player:
            self.ai_player.set_difficulty(level)
            self.update_status(f"AI difficulty set to level {level}.", color="green")

    def toggle_sound(self, enabled):
        print(f"Toggling sound to {'enabled' if enabled else 'disabled'}")
        self.sound_enabled = enabled
        self.update_status(
            f"Sound Effects {'Enabled' if enabled else 'Disabled'}.", color="green"
        )

    def show_hint(self):
        print("Showing hint")
        if self.ai_player and (self.model_loaded or self.ai_player.engine):
            move = self.ai_player.get_best_move(self.board)
            if move:
                move_san = self.board.san(move)
                messagebox.showinfo("Hint", f"Suggested Move: {move_san}")
                self.update_status(f"Hint: {move_san}", color="blue")
            else:
                messagebox.showwarning("Hint", "No hint available.")
                self.update_status("No hint available.", color="red")
        else:
            messagebox.showwarning("Hint", "AI model not loaded.")
            self.update_status("AI model not loaded.", color="red")

    def analyze_position(self):
        print("Analyzing position")
        messagebox.showinfo(
            "Analyze Position", "Position analysis feature is under development."
        )
        self.update_status(
            "Position analysis feature is under development.", color="blue"
        )

    def analyze_game(self):
        print("Analyzing game")
        messagebox.showinfo(
            "Analyze Game", "Game analysis feature is under development."
        )
        self.update_status("Game analysis feature is under development.", color="blue")

    def toggle_theme(self):
        print("Toggling theme")
        if Config.CURRENT_THEME == Config.LIGHT_THEME:
            Config.CURRENT_THEME = Config.DARK_THEME
        else:
            Config.CURRENT_THEME = Config.LIGHT_THEME
        self.apply_theme()
        self.update_status("Theme toggled.", color="green")

    def play_against_stockfish(self):
        print("Playing against Stockfish")
        try:
            self.opponent_engine = chess.engine.SimpleEngine.popen_uci(
                Config.ENGINE_PATH
            )
            self.update_status("Playing against Stockfish.", color="blue")
            self.window.control_panel.update_player_labels(
                "Player (White)", "Stockfish (Black)"
            )
            # White is user, Black is Stockfish
            # If it's White's turn (user), user moves. On user move completion, stockfish_move is called.
        except Exception as e:
            print(f"Failed to start Stockfish: {e}")
            self.update_status(f"Failed to start Stockfish: {e}", color="red")
            messagebox.showerror("Error", f"Failed to start Stockfish: {e}")

    def play_against_model(self):
        print("Playing against model")
        if not self.model_loaded or not self.ai_player:
            self.update_status("AI model not loaded.", color="red")
            messagebox.showerror("Error", "AI model not loaded.")
            return
        # White is user, Black is cAI
        self.opponent_ai = AIPlayer(
            model_path=Config.MODEL_PATH, device=self.ai_player.device, side=chess.BLACK
        )
        self.update_status("Playing against the model.", color="blue")
        self.window.control_panel.update_player_labels(
            "Player (White)", "Chess AI (Black)"
        )

    def watch_ai_vs_stockfish(self):
        print("Watching AI vs Stockfish")
        if not self.model_loaded or not self.ai_player:
            self.update_status("AI model not loaded.", color="red")
            messagebox.showerror("Error", "AI model not loaded.")
            return
        self.opponent_engine = chess.engine.SimpleEngine.popen_uci(Config.ENGINE_PATH)
        self.update_status("Watching AI vs Stockfish.", color="blue")
        self.window.control_panel.update_player_labels(
            "Chess AI (White)", "Stockfish (Black)"
        )
        self.watch_game_thread = Thread(
            target=self.watch_game, args=(self.opponent_engine,), daemon=True
        )
        self.watch_game_thread.start()

    def watch_game(self, opponent_engine):
        print("Watching game")
        game_board = chess.Board()
        while not game_board.is_game_over():
            if game_board.turn == self.ai_player.side:
                move = self.ai_player.get_best_move(game_board)
            else:
                result = opponent_engine.play(
                    game_board,
                    chess.engine.Limit(depth=self.ai_player.difficulty_level),
                )
                move = result.move
            game_board.push(move)
            self.update_ui_with_move(game_board, move)
            time.sleep(Config.MOVE_DELAY / 1000.0)
        self.handle_game_over_specific(game_board)

    def play_game_between_models(self, opponent_ai):
        print("Playing game between models")
        game_board = chess.Board()
        while not game_board.is_game_over():
            if game_board.turn == self.ai_player.side:
                move = self.ai_player.get_best_move(game_board)
            else:
                move = opponent_ai.get_best_move(game_board)
            game_board.push(move)
            self.update_ui_with_move(game_board, move)
            time.sleep(Config.MOVE_DELAY / 1000.0)
        self.handle_game_over_specific(game_board)

    def update_ui_with_move(self, board, move):
        print(f"Updating UI with move: {move}")
        self.board = board
        self.last_move = (move.from_square, move.to_square)
        self.window.chessboard.board = self.board
        self.window.chessboard.last_move = self.last_move
        self.window.chessboard.draw_board()
        self.window.chessboard.draw_pieces()
        move_san = self.board.san(move)
        self.window.side_panel.update_move_list(move_san)
        if self.board.is_capture(move):
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece:
                symbol = captured_piece.symbol()
                if captured_piece.color:
                    self.captured_pieces["black"].append(symbol.upper())
                else:
                    self.captured_pieces["white"].append(symbol.lower())
                self.window.side_panel.update_captured_pieces(
                    self.captured_pieces["white"], self.captured_pieces["black"]
                )
        if self.sound_enabled:
            self.play_sound(move)

    def handle_game_over_specific(self, board):
        print("Handling specific game over")
        outcome = board.outcome()
        if outcome.winner is None:
            result_text = "It's a draw!"
            self.update_status(result_text, color="blue")
            self.elo_rating.update(opponent_rating=1500, score=0.5)
        elif outcome.winner == self.ai_player.side:
            result_text = f"{'White' if self.ai_player.side == chess.WHITE else 'Black'} (AI) wins!"
            self.update_status(result_text, color="green")
            self.elo_rating.update(opponent_rating=1500, score=1.0)
        else:
            result_text = "Stockfish wins!"
            self.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)
        self.game_saver.save_game(board)
        self.logger.info(f"Game over: {result_text}. ELO: {self.elo_rating.rating:.0f}")

    def toggle_coordinates(self, show):
        self.window.chessboard.toggle_coordinates(show)
        self.update_status(
            f"Coordinates {'shown' if show else 'hidden'}.", color="green"
        )

    def update_status(self, message, color="green"):
        self.window.status_bar.update_status(message, color)

    def play_sound(self, move):
        if self.sound_enabled:
            if self.board.is_capture(move):
                self.sound_effects.play_capture()
            else:
                self.sound_effects.play_move()


if __name__ == "__main__":
    app = ChessApp()
    app.run()
