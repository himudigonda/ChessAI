# main.py

from chess_app.utils import SoundEffects
from chess_app.ui.main_window import MainWindow
from chess_app.utils import Timer, SaveLoad, AIPlayer
from chess_app.data import board_to_tensor, move_to_index
import sys
from chess_app.utils import Logger, GameSaver, EloRating
import chess
from threading import Thread
from chess_app.config import Config
# from tkinter_ui import MainWindow  # type: ignore # Remove if exists; ensure no old UI references
import tkinter as tk
from tkinter import messagebox
from chess_app.ui.utils import show_message
from chess_app.ui.styles import Styles


class ChessApp:
    def __init__(self):
        self.board = chess.Board()
        self.selected_square = None
        self.dragging_piece = None
        self.drag_start_coords = None
        self.last_move = None
        self.white_time = 300  # 5 minutes
        self.black_time = 300
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []
        self.sound_enabled = True
        self.model_loaded = False  # Flag to indicate if the model is loaded
        self.sound_effects = SoundEffects()
        # Initialize Logger
        self.logger_instance = Logger()
        self.logger = self.logger_instance.get_logger()

        # Initialize GameSaver
        self.game_saver = GameSaver()

        # Initialize Elo Rating
        self.elo_rating = EloRating(initial_elo=Config.INITIAL_ELO, k_factor=Config.K_FACTOR)

        # Initialize AIPlayer to None (load later in a thread)
        self.ai_player = None

        # Initialize Tkinter UI
        self.window = MainWindow(self)

    def run(self):
        """
        Runs the main application loop.
        """
        self.window.mainloop()

    def handle_move(self, move):
        """
        Handles the player's move and triggers the AI move if necessary.
        """
        try:
            # Validate if the move is legal
            if move not in self.board.legal_moves:
                self.update_status("Illegal move attempted.", color=Styles.CURRENT_THEME["status_error"])
                return

            # Push the move to the board
            self.board.push(move)
            self.last_move = (move.from_square, move.to_square)

            # Update the chessboard and UI
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()

            # Convert the move to SAN and update the move list
            move_san = self.board.san(move)
            self.window.side_panel.update_move_list(move_san)

            # Handle captures
            if self.board.is_capture(move):
                captured_piece = self.board.piece_at(move.to_square)
                if captured_piece:
                    symbol = captured_piece.symbol()
                    if captured_piece.color:
                        self.captured_pieces["black"].append(symbol.upper())
                    else:
                        self.captured_pieces["white"].append(symbol.lower())
                    self.window.side_panel.update_captured_pieces(self.captured_pieces["white"], self.captured_pieces["black"])

            # Play sound if enabled
            if self.sound_enabled:
                self.play_sound(move)

            # Handle game end or trigger the AI move
            if self.board.is_game_over():
                self.handle_game_over()
            elif self.ai_player and self.board.turn == self.ai_player.side:
                self.window.after(1000, self.ai_make_move)  # Delay AI move by 1 second

        except Exception as e:
            # Log and display the error
            self.update_status(f"Error handling move: {str(e)}", color=Styles.CURRENT_THEME["status_error"])
            self.logger.error(f"Error in handle_move: {str(e)}")

    def ai_make_move(self):
        """
        Handles the AI's move automatically.
        """
        if self.ai_player and self.model_loaded:
            move = self.ai_player.get_best_move(self.board)
            if move:
                self.handle_move(move)

    def start_game(self):
        """
        Starts the game and ensures AI moves first if it is White.
        """
        self.update_status("Game started.", color="green")
        if self.ai_player and self.ai_player.side == chess.WHITE:
            self.ai_make_move()

    def handle_game_over(self):
        """
        Handles the end of the game by updating the UI and logging the result.
        """
        outcome = self.board.outcome()
        if outcome.winner is None:
            result_text = "It's a draw!"
            self.update_status(result_text, color="blue")
            self.elo_rating.update(opponent_rating=1500, score=0.5)
        elif outcome.winner == self.ai_player.side:
            result_text = f"{'White' if self.ai_player.side == chess.WHITE else 'Black'} (AI) wins!"
            self.update_status(result_text, color="green")
            self.elo_rating.update(opponent_rating=1500, score=1.0)
        else:
            result_text = f"{'White' if outcome.winner == chess.WHITE else 'Black'} (Stockfish) wins!"
            self.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)

        # Save the game
        self.game_saver.save_game(self.board)

        # Log the outcome
        self.logger.info(f"Game over: {result_text}. ELO Rating: {self.elo_rating.rating:.0f}")

    def save_game(self):
        """
        Saves the current game to a PGN file.
        """
        SaveLoad.save_game(self.board, "saved_game.pgn")  # Modify as needed
        self.update_status("Game saved successfully.", color="green")

    def load_game(self):
        """
        Loads a game from a PGN file.
        """
        try:
            board = SaveLoad.load_game("saved_game.pgn")  # Modify as needed
            self.board = board
            self.window.chessboard.board = self.board
            self.window.chessboard.last_move = self.last_move
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()
            self.update_status("Game loaded successfully.", color="green")
        except Exception as e:
            self.update_status(f"Error loading game: {str(e)}", color="red")
            self.logger.error(f"Error loading game: {str(e)}")

    def resign(self):
        """
        Handles resignation by the player or AI.
        """
        if self.board.turn == chess.WHITE:
            # AI resigns
            result_text = "White (AI) resigns. Black (Stockfish) wins!"
            self.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)
        else:
            # Stockfish resigns
            result_text = "Black (Stockfish) resigns. White (AI) wins!"
            self.update_status(result_text, color="green")
            self.elo_rating.update(opponent_rating=1500, score=1.0)

        # Save the game
        self.game_saver.save_game(self.board)

        # Log the outcome
        self.logger.info(f"Game over: {result_text}. ELO Rating: {self.elo_rating.rating:.0f}")

    def offer_draw(self):
        """
        Offers a draw to the opponent.
        """
        # Placeholder for draw offer logic
        self.update_status("Draw offered to the opponent.", color="blue")
        # Implement opponent's response logic if applicable

    def undo_move(self):
        """
        Undoes the last move.
        """
        if len(self.board.move_stack) > 0:
            last_move = self.board.pop()
            self.redo_stack.append(last_move)
            if self.board.is_capture(last_move):
                captured_piece = last_move.drop
                if captured_piece:
                    symbol = captured_piece.symbol()
                    if captured_piece.color:
                        self.captured_pieces["black"].remove(symbol.upper())
                    else:
                        self.captured_pieces["white"].remove(symbol.lower())
            self.update_status("Move undone.", color="green")
            self.window.side_panel.undo_move()
            self.window.chessboard.draw_board()
            self.window.chessboard.draw_pieces()

    def redo_move(self):
        """
        Redoes the last undone move.
        """
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
        """
        Restarts the game by resetting the board and timers.
        """
        self.board.reset()
        self.last_move = None
        self.white_time = 300
        self.black_time = 300
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []
        self.window.side_panel.update_captured_pieces(self.captured_pieces["white"], self.captured_pieces["black"])
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
        """
        Sets the AI's difficulty level.

        :param level: Integer representing the difficulty level.
        """
        if self.ai_player:
            self.ai_player.set_difficulty(level)
            self.update_status(f"AI difficulty set to level {level}.", color="green")

    def toggle_sound(self, enabled):
        """
        Toggles sound effects.

        :param enabled: Boolean indicating if sound is enabled.
        """
        self.sound_enabled = enabled
        self.update_status(f"Sound Effects {'Enabled' if enabled else 'Disabled'}.", color="green")

    def show_hint(self):
        """
        Provides a hint for the best possible move.
        """
        if self.ai_player and self.model_loaded:
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
        """
        Analyzes the current position.
        """
        # Placeholder for position analysis
        messagebox.showinfo("Analyze Position", "Position analysis feature is under development.")
        self.update_status("Position analysis feature is under development.", color="blue")

    def analyze_game(self):
        """
        Analyzes the completed game.
        """
        # Placeholder for game analysis
        messagebox.showinfo("Analyze Game", "Game analysis feature is under development.")
        self.update_status("Game analysis feature is under development.", color="blue")

    def toggle_theme(self):
        """
        Toggles between light and dark themes.
        """
        Styles.toggle_theme()
        self.apply_theme()
        self.update_status("Theme toggled.", color="green")

    def apply_theme(self):
        """
        Applies the current theme to all UI components.
        """
        # Update background colors
        self.configure(bg=Styles.CURRENT_THEME["background"])
        self.window.chessboard.configure(bg=Styles.CURRENT_THEME["background"])
        self.window.control_panel.configure(bg=Styles.CURRENT_THEME["background"])
        self.window.side_panel.configure(bg=Styles.CURRENT_THEME["background"])
        self.window.status_bar.configure(bg=Styles.CURRENT_THEME["background"])

        # Update chessboard squares and pieces
        self.window.chessboard.draw_board()
        self.window.chessboard.draw_pieces()
        if self.window.chessboard.show_coordinates:
            self.window.chessboard.draw_coordinates()

        # Update control panel buttons
        for child in self.window.control_panel.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
            elif isinstance(child, ttk.Combobox):
                child.configure(background=Styles.CURRENT_THEME["background"], foreground=Styles.CURRENT_THEME["foreground"])

        # Update side panel labels
        self.window.side_panel.timer_label.configure(bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        self.window.side_panel.status_label.configure(bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        self.window.side_panel.captured_white_label.configure(bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        self.window.side_panel.captured_black_label.configure(bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        self.window.side_panel.move_list.configure(bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])

    def play_against_stockfish(self):
        """
        Sets up the AI to play against Stockfish.
        """
        # Implement AI vs Stockfish logic
        if not self.ai_player:
            self.update_status("AI model not loaded.", color="red")
            messagebox.showerror("Error", "AI model not loaded.")
            return

        # Initialize Stockfish as opponent
        self.opponent_engine = chess.engine.SimpleEngine.popen_uci(Config.ENGINE_PATH)
        self.opponent_side = chess.BLACK if self.ai_player.side == chess.WHITE else chess.WHITE
        self.update_status("Playing against Stockfish.", color="blue")
        self.play_game_thread = Thread(target=self.play_game, args=(self.opponent_engine, self.opponent_side), daemon=True)
        self.play_game_thread.start()

    def play_against_model(self):
        """
        Sets up the AI to play against the trained model.
        """
        # Implement AI vs Model logic
        if not self.ai_player:
            self.update_status("AI model not loaded.", color="red")
            messagebox.showerror("Error", "AI model not loaded.")
            return

        # For playing against the model, instantiate another AIPlayer with the same model
        self.opponent_ai = AIPlayer(model_path=self.ai_player.model_path, device=self.ai_player.device, side=chess.BLACK if self.ai_player.side == chess.WHITE else chess.WHITE)
        self.update_status("Playing against the model.", color="blue")
        self.play_game_thread = Thread(target=self.play_game_between_models, args=(self.opponent_ai,), daemon=True)
        self.play_game_thread.start()

    def watch_ai_vs_stockfish(self):
        """
        Watches the AI and Stockfish play against each other automatically.
        """
        # Implement AI vs Stockfish auto-play logic
        if not self.ai_player:
            self.update_status("AI model not loaded.", color="red")
            messagebox.showerror("Error", "AI model not loaded.")
            return

        # Initialize Stockfish as opponent
        self.opponent_engine = chess.engine.SimpleEngine.popen_uci(Config.ENGINE_PATH)
        self.update_status("Watching AI vs Stockfish.", color="blue")
        self.watch_game_thread = Thread(target=self.watch_game, args=(self.opponent_engine,), daemon=True)
        self.watch_game_thread.start()

    def play_game(self, opponent_engine, opponent_side):
        """
        Plays a game between AI and an opponent engine.

        :param opponent_engine: The opponent chess engine.
        :param opponent_side: The side the opponent is playing.
        """
        game_board = chess.Board()
        while not game_board.is_game_over():
            if game_board.turn == self.ai_player.side:
                move = self.ai_player.get_best_move(game_board)
            else:
                result = opponent_engine.play(game_board, chess.engine.Limit(depth=self.ai_player.difficulty_level))
                move = result.move
            game_board.push(move)
            self.update_ui_with_move(game_board, move)
            time.sleep(Config.MOVE_DELAY / 1000.0)  # Delay between moves

        # Handle game outcome
        self.handle_game_over_specific(game_board)

    def play_game_between_models(self, opponent_ai):
        """
        Plays a game between two AI models.

        :param opponent_ai: The opponent AIPlayer instance.
        """
        game_board = chess.Board()
        while not game_board.is_game_over():
            if game_board.turn == self.ai_player.side:
                move = self.ai_player.get_best_move(game_board)
            else:
                move = opponent_ai.get_best_move(game_board)
            game_board.push(move)
            self.update_ui_with_move(game_board, move)
            time.sleep(Config.MOVE_DELAY / 1000.0)  # Delay between moves

        # Handle game outcome
        self.handle_game_over_specific(game_board)

    def watch_game(self, opponent_engine):
        """
        Watches a game between AI and Stockfish without user intervention.

        :param opponent_engine: The opponent chess engine.
        """
        game_board = chess.Board()
        while not game_board.is_game_over():
            if game_board.turn == self.ai_player.side:
                move = self.ai_player.get_best_move(game_board)
            else:
                result = opponent_engine.play(game_board, chess.engine.Limit(depth=self.ai_player.difficulty_level))
                move = result.move
            game_board.push(move)
            self.update_ui_with_move(game_board, move)
            time.sleep(Config.MOVE_DELAY / 1000.0)  # Delay between moves

        # Handle game outcome
        self.handle_game_over_specific(game_board)

    def update_ui_with_move(self, board, move):
        """
        Updates the UI components with the latest move.

        :param board: The current chess.Board object.
        :param move: The latest chess.Move object.
        """
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
                self.window.side_panel.update_captured_pieces(self.captured_pieces["white"], self.captured_pieces["black"])

        if self.sound_enabled:
            self.play_sound(move)

    def handle_game_over_specific(self, board):
        """
        Handles the end of a specific game.

        :param board: The final chess.Board object.
        """
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
            result_text = f"{'White' if outcome.winner == chess.WHITE else 'Black'} (Stockfish) wins!"
            self.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)

        # Save the game
        self.game_saver.save_game(board)

        # Log the outcome
        self.logger.info(f"Game over: {result_text}. ELO Rating: {self.elo_rating.rating:.0f}")

    def toggle_coordinates(self, show):
        """
        Toggles the display of coordinate labels on the chessboard.

        :param show: Boolean indicating whether to show coordinates.
        """
        self.window.chessboard.toggle_coordinates(show)
        self.update_status(f"Coordinates {'shown' if show else 'hidden'}.", color="green")

    def update_status(self, message, color="green"):
        """
        Updates the status bar with a message.

        :param message: The message to display.
        :param color: The color of the message text.
        """
        self.window.status_bar.update_status(message, color)

    def play_sound(self, move):
        """
        Plays sound effects based on the move type.
        """
        if self.sound_enabled:
            if self.board.is_capture(move):
                self.sound_effects.play_capture()
            else:
                self.sound_effects.play_move()
    def play_against_stockfish(self):
        """
        Sets up the AI to play against Stockfish.
        """
        self.play_against_stockfish()

    def play_against_model(self):
        """
        Sets up the AI to play against the trained model.
        """
        self.play_against_model()

    def watch_ai_vs_stockfish(self):
        """
        Watches the AI and Stockfish play against each other automatically.
        """
        self.watch_ai_vs_stockfish()


if __name__ == "__main__":
    app = ChessApp()
    app.run()