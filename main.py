# main.py
from chess_app.utils import Timer, SaveLoad
from chess_app.data import board_to_tensor, move_to_index
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from chess_app.ui.main_window import MainWindow
from chess_app.utils import AIPlayer, Logger, GameSaver, EloRating
import chess

# main.py
from chess_app.utils import Timer, SaveLoad
from chess_app.data import board_to_tensor, move_to_index
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
from chess_app.ui.main_window import MainWindow
from chess_app.utils import AIPlayer, Logger, GameSaver, EloRating
import chess


class ModelLoaderThread(QThread):
    """
    A QThread to handle loading the AI model and other backend tasks.
    """

    model_loaded = pyqtSignal(AIPlayer)  # Signal emitted when model is loaded
    error = pyqtSignal(str)  # Signal emitted when there's an error

    def __init__(self):
        super().__init__()
        self.model_path = "chess_model.pth"  # Example: configurable path

    def run(self):
        try:
            # Simulate loading the AI model
            ai_player = AIPlayer(
                model_path=self.model_path, device=None, side=chess.WHITE
            )
            self.model_loaded.emit(ai_player)
        except Exception as e:
            self.error.emit(str(e))


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

        # Initialize Logger
        self.logger_instance = Logger()
        self.logger = self.logger_instance.get_logger()

        # Initialize GameSaver
        self.game_saver = GameSaver()

        # Initialize Elo Rating
        self.elo_rating = EloRating(initial_elo=1800, k_factor=32)

        # Initialize AIPlayer to None (load later in a thread)
        self.ai_player = None

        # Training data
        self.training_data = []

    def run(self):
        app = QApplication(sys.argv)

        # Create the MainWindow
        self.main_window = MainWindow(self)

        # Start a thread to load the AI model
        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.model_loaded.connect(self.on_model_loaded)
        self.model_loader_thread.error.connect(self.on_model_loading_error)
        self.model_loader_thread.start()

        # Show the UI immediately
        self.main_window.show()

        # Start the Qt application event loop
        sys.exit(app.exec_())

    def on_model_loaded(self, ai_player):
        self.ai_player = ai_player
        self.model_loaded = True
        self.main_window.progress_bar.hide()  # Stop and hide the progress bar
        self.main_window.update_status("Model loaded successfully.", color="green")

    def on_model_loading_error(self, error_message):
        """
        Callback when there is an error loading the AI model.
        """
        self.main_window.update_status(
            f"Error loading model: {error_message}", color="red"
        )
        QMessageBox.critical(
            self.main_window, "Error", f"Failed to load the model: {error_message}"
        )

    def handle_move(self, move):
        """
        Handles the player's move and triggers the AI move if necessary.
        """
        try:
            # Validate if the move is legal
            if move not in self.board.legal_moves:
                self.main_window.update_status("Illegal move attempted.", color="red")
                return

            # Push the move to the board
            self.board.push(move)
            
            # Update the chessboard and UI
            self.main_window.chessboard.update()

            # Convert the move to SAN and update the move list
            move_san = self.board.san(move)
            self.main_window.side_panel.update_move_list(move_san)

            # Handle game end or trigger the AI move
            if self.board.is_game_over():
                self.handle_game_over()
            elif self.board.turn == chess.BLACK and self.ai_player.side == chess.BLACK:
                self.ai_make_move()

        except Exception as e:
            # Log and display the error
            self.main_window.update_status(f"Error handling move: {str(e)}", color="red")
            self.logger.error(f"Error in handle_move: {str(e)}")


    def ai_make_move(self):
        """
        Handles the AI's move automatically.
        """
        move = self.ai_player.get_best_move(self.board)
        self.handle_move(move)

    def start_game(self):
        """
        Starts the game and ensures AI moves first if it is White.
        """
        self.main_window.update_status("Game started.")
        if self.ai_player.side == chess.WHITE:
            self.ai_make_move()

    def handle_game_over(self):
        outcome = self.board.outcome()
        if outcome.winner is None:
            result_text = "It's a draw!"
            self.main_window.side_panel.update_status(result_text, color="blue")
            self.elo_rating.update(opponent_rating=1500, score=0.5)
        elif outcome.winner == self.ai_player.side:
            result_text = "White (AI) wins!"
            self.main_window.side_panel.update_status(result_text, color="green")
            self.elo_rating.update(opponent_rating=1500, score=1.0)
        else:
            result_text = "Black (Stockfish) wins!"
            self.main_window.side_panel.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)

        # Save the game
        self.game_saver.save_game(self.board)

        # Log the outcome
        self.logger.info(
            f"Game over: {result_text}. ELO Rating: {self.elo_rating.rating:.0f}"
        )

    def collect_training_data(self, move):
        board_tensor = board_to_tensor(self.board).numpy()
        move_index = move_to_index(move)
        move_quality = "Average Step"  # Placeholder
        self.training_data.append(
            (board_tensor, move_index, 0.0, move_quality)
        )  # Outcome to be set later

    def save_game(self):
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window, "Save Game", "", "PGN Files (*.pgn)"
        )
        if filename:
            self.game_saver.save_game(self.board)
            QMessageBox.information(
                self.main_window, "Game Saved", "The game has been saved successfully."
            )
            self.main_window.side_panel.update_status(
                "Game saved successfully.", color="green"
            )

    def load_game(self):
        filename, _ = QFileDialog.getOpenFileName(
            self.main_window, "Load Game", "", "PGN Files (*.pgn)"
        )
        if filename:
            try:
                self.board = SaveLoad.load_game(filename)
                self.last_move = None
                self.white_time = 300
                self.black_time = 300
                self.captured_pieces = {"white": [], "black": []}
                self.redo_stack = []
                self.main_window.side_panel.update_captured_pieces(
                    self.captured_pieces["white"], self.captured_pieces["black"]
                )
                self.main_window.side_panel.move_list.setPlainText("")
                self.main_window.side_panel.update_timer("White: 05:00 - Black: 05:00")
                self.main_window.chessboard.board = self.board
                self.main_window.chessboard.update()
                QMessageBox.information(
                    self.main_window,
                    "Game Loaded",
                    "The game has been loaded successfully.",
                )
                self.main_window.side_panel.update_status(
                    "Game loaded successfully.", color="green"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", f"Failed to load game: {e}"
                )
                self.main_window.side_panel.update_status(
                    "Error: Failed to load game.", color="red"
                )

    def resign(self):
        if self.board.turn == chess.WHITE:
            # AI resigns
            QMessageBox.information(
                self.main_window,
                "Resign",
                "White (AI) resigns. Black (Stockfish) wins!",
            )
            self.app.handle_resignation(chess.WHITE)
        else:
            # Stockfish resigns
            QMessageBox.information(
                self.main_window,
                "Resign",
                "Black (Stockfish) resigns. White (AI) wins!",
            )
            self.app.handle_resignation(chess.BLACK)

    def offer_draw(self):
        response = QMessageBox.question(
            self.main_window,
            "Offer Draw",
            "Do you want to offer a draw?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if response == QMessageBox.Yes:
            QMessageBox.information(
                self.main_window, "Draw Offered", "Draw offered to the opponent."
            )
            self.main_window.side_panel.update_status("Draw offered.", color="blue")
            # Implement opponent's response logic if applicable

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            last_move = self.board.pop()
            self.redo_stack.append(last_move)
            if last_move.to_square is not None:
                captured_piece = self.board.piece_at(last_move.to_square)
                if captured_piece:
                    if captured_piece.color:
                        self.captured_pieces["black"].remove(captured_piece.symbol())
                    else:
                        self.captured_pieces["white"].remove(captured_piece.symbol())
            self.last_move = None
            self.main_window.side_panel.update_timer(
                Timer.format_time(self.white_time, self.black_time)
            )
            self.main_window.chessboard.draw_chessboard()
            self.main_window.chessboard.draw_pieces()
            self.main_window.side_panel.update_captured_pieces(
                self.captured_pieces["white"], self.captured_pieces["black"]
            )
            self.main_window.side_panel.update_move_list_undo()
            self.main_window.side_panel.update_status("Move undone.")

    def redo_move(self):
        if self.redo_stack:
            move = self.redo_stack.pop()
            self.board.push(move)
            if self.board.is_capture(move):
                captured_piece = self.board.piece_at(move.to_square)
                if captured_piece:
                    if captured_piece.color:
                        self.captured_pieces["black"].append(captured_piece.symbol())
                    else:
                        self.captured_pieces["white"].append(captured_piece.symbol())
            self.last_move = (move.from_square, move.to_square)
            self.main_window.side_panel.update_timer(
                Timer.format_time(self.white_time, self.black_time)
            )
            self.main_window.chessboard.draw_chessboard()
            self.main_window.chessboard.draw_pieces()
            self.main_window.side_panel.update_captured_pieces(
                self.captured_pieces["white"], self.captured_pieces["black"]
            )
            self.main_window.side_panel.update_move_list_redo(move)
            self.main_window.side_panel.update_status("Move redone.")

    def restart_game(self):
        self.board.reset()
        self.last_move = None
        self.white_time = 300
        self.black_time = 300
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []
        self.training_data = []
        self.main_window.side_panel.update_captured_pieces(
            self.captured_pieces["white"], self.captured_pieces["black"]
        )
        self.main_window.side_panel.move_list.setPlainText("")
        self.main_window.side_panel.update_timer("White: 05:00 - Black: 05:00")
        self.main_window.chessboard.board = self.board
        self.main_window.chessboard.update()
        self.main_window.side_panel.update_status("Game restarted.", color="green")

    def set_ai_difficulty(self, difficulty_level):
        self.ai_player.set_difficulty(difficulty_level)
        self.main_window.side_panel.update_status(
            f"AI difficulty set to level {difficulty_level}.", color="green"
        )

    def toggle_sound(self, enabled):
        self.sound_enabled = enabled
        self.main_window.side_panel.update_status(
            f"Sound Effects {'Enabled' if enabled else 'Disabled'}.", color="green"
        )

    def show_hint(self):
        best_move = self.ai_player.get_best_move(self.board)
        if best_move:
            move_san = self.board.san(best_move)
            QMessageBox.information(
                self.main_window, "Hint", f"Suggested Move: {move_san}"
            )
            self.main_window.side_panel.update_status(f"Hint: {move_san}", color="blue")
        else:
            QMessageBox.warning(self.main_window, "Hint", "No hint available.")
            self.main_window.side_panel.update_status("No hint available.", color="red")

    def analyze_position(self):
        # Placeholder for position analysis
        QMessageBox.information(
            self.main_window,
            "Analyze Position",
            "Position analysis feature is under development.",
        )
        self.main_window.side_panel.update_status(
            "Position analysis feature is under development.", color="blue"
        )

    def analyze_game(self):
        # Placeholder for game analysis
        QMessageBox.information(
            self.main_window,
            "Analyze Game",
            "Game analysis feature is under development.",
        )
        self.main_window.side_panel.update_status(
            "Game analysis feature is under development.", color="blue"
        )

    def toggle_theme(self):
        # Placeholder for theme toggling
        QMessageBox.information(
            self.main_window,
            "Toggle Theme",
            "Theme toggling feature is under development.",
        )
        self.main_window.side_panel.update_status(
            "Theme toggling feature is under development.", color="blue"
        )

    def handle_resignation(self, resigning_player):
        if resigning_player == chess.WHITE:
            result_text = "White (AI) resigns. Black (Stockfish) wins!"
            self.main_window.side_panel.update_status(result_text, color="red")
            self.elo_rating.update(opponent_rating=1500, score=0.0)
        else:
            result_text = "Black (Stockfish) resigns. White (AI) wins!"
            self.main_window.side_panel.update_status(result_text, color="green")
            self.elo_rating.update(opponent_rating=1500, score=1.0)

        # Save the game
        self.game_saver.save_game(self.board)

        # Log the outcome
        self.logger.info(
            f"Game over: {result_text}. ELO Rating: {self.elo_rating.rating:.0f}"
        )


if __name__ == "__main__":
    app_instance = ChessApp()
    app_instance.run()
