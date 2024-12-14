# main.py
import torch
import tkinter as tk
from tkinter import ttk, messagebox
from chess_app.board import ChessBoard
from chess_app.data import board_to_tensor, move_to_index, index_to_move
from chess_app.ui.ui_side_panel import UISidePanel
from chess_app.utils import AIPlayer, GameAnalyzer, SaveLoad, SoundEffects, Timer, get_device, GameSaver, Logger, EloRating
import chess
import threading

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess AI")
        self.root.geometry("1200x800")  # Adequate window size
        self.root.configure(bg="#F5F5F7")

        # Initialize Logger
        self.logger_instance = Logger()
        self.logger = self.logger_instance.get_logger()

        # Initialize GameSaver
        self.game_saver = GameSaver()

        # Initialize Elo Rating
        self.elo_rating = EloRating(initial_elo=1800, k_factor=32)

        # Initialize game state
        self.board = chess.Board()
        self.selected_square = None
        self.dragging_piece = None
        self.drag_start_coords = None
        self.last_move = None
        self.white_time = 300  # 5 minutes
        self.black_time = 300
        self.white_increment = 5  # seconds
        self.black_increment = 5
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []

        # Initialize sound effects
        self.sound_effects = SoundEffects()
        self.sound_enabled = True

        # Initialize device
        self.device = get_device()

        # Initialize AIPlayer
        self.ai_player = AIPlayer(model_path="chess_model.pth", device=self.device, side=chess.WHITE)

        # Initialize training data
        self.training_data = []

        # Initialize UI components
        self.create_main_layout()
        self.create_chessboard()
        self.create_side_panel()
        self.create_status_bar()

        # Start the clock
        self.update_timer()
        self.update_clock()

        # Start AI vs Stockfish game
        self.start_ai_game()

    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid: chessboard on left, sidebar on right
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Chessboard Frame
        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

        # Sidebar Frame
        self.sidebar_frame = ttk.Frame(self.main_frame)
        self.sidebar_frame.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

    def create_chessboard(self):
        self.chess_board = ChessBoard(self.board_frame, self)
        self.chess_board.pack(fill=tk.BOTH, expand=True)

    def create_side_panel(self):
        self.ui_side_panel = UISidePanel(self, self.sidebar_frame)

    def create_status_bar(self):
        self.status_bar = ttk.Label(
            self.root,
            text="Welcome to Chess AI!",
            relief=tk.SUNKEN,
            anchor=tk.W,
            background="#F5F5F7",
            foreground="#333333",
            font=("Helvetica", 12)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status_bar(self, message):
        self.status_bar.config(text=message)
        self.logger.info(message)
        self.ui_side_panel.status_label.config(text=message)

    def update_timer(self):
        timer_text = Timer.format_time(self.white_time, self.black_time)
        self.ui_side_panel.timer_label.config(text=timer_text)

    def update_clock(self):
        if self.board.is_game_over():
            return

        if self.board.turn == chess.WHITE:
            if self.white_time > 0:
                self.white_time -= 1
            else:
                messagebox.showinfo("Time Up", "White's time is up. Black (Stockfish) wins!")
                self.update_status_bar("Black (Stockfish) wins on time.")
                self.board.push_san("resign")
                self.handle_game_over()
        else:
            if self.black_time > 0:
                self.black_time -= 1
            else:
                messagebox.showinfo("Time Up", "Black's time is up. White (AI) wins!")
                self.update_status_bar("White (AI) wins on time.")
                self.board.push_san("resign")
                self.handle_game_over()

        self.update_timer()
        self.root.after(1000, self.update_clock)

    def set_ai_difficulty(self, event):
        selected_depth = int(self.ui_side_panel.difficulty_var.get())
        if self.ai_player.engine:
            self.ai_player.engine.configure({"Skill Level": selected_depth})
            self.logger.info(f"AI difficulty set to depth {selected_depth}")
        self.update_status_bar(f"AI difficulty set to level {selected_depth}")

    def toggle_sound(self):
        self.sound_enabled = self.ui_side_panel.sound_toggle_var.get()
        self.update_status_bar(f"Sound Effects {'Enabled' if self.sound_enabled else 'Disabled'}")

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            last_move = self.board.pop()
            self.redo_stack.append(last_move)
            if self.board.is_capture(last_move):
                captured_piece = self.board.piece_at(last_move.to_square)
                if captured_piece:
                    color = "black" if captured_piece.color else "white"
                    self.captured_pieces[color].remove(captured_piece.symbol())
            self.update_captured_pieces()
            self.ui_side_panel.update_move_list_undo()
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()
            self.update_status_bar("Move undone.")

    def redo_move(self):
        if self.redo_stack:
            move = self.redo_stack.pop()
            self.board.push(move)
            if self.board.is_capture(move):
                captured_piece = self.board.piece_at(move.to_square)
                if captured_piece:
                    color = "black" if captured_piece.color else "white"
                    self.captured_pieces[color].append(captured_piece.symbol())
            self.update_captured_pieces()
            self.ui_side_panel.update_move_list_redo(move)
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()
            self.update_status_bar("Move redone.")

    def update_captured_pieces(self):
        white_captured = " ".join(self.captured_pieces["white"])
        black_captured = " ".join(self.captured_pieces["black"])
        self.ui_side_panel.captured_pieces_white.config(text=white_captured)
        self.ui_side_panel.captured_pieces_black.config(text=black_captured)

    def handle_move(self, move, promotion=None):
        if promotion:
            move.promotion = chess.Piece.from_symbol(promotion.upper()).piece_type
        if move in self.board.legal_moves:
            self.last_move = (move.from_square, move.to_square)

            # Play sound
            if self.sound_enabled:
                if self.board.is_capture(move):
                    self.sound_effects.play_capture()
                else:
                    self.sound_effects.play_move()

            # Handle captured pieces
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece:
                color = "black" if captured_piece.color else "white"
                self.captured_pieces[color].append(captured_piece.symbol())

            # Generate SAN for move list
            try:
                move_san = self.board.san(move)
            except ValueError:
                move_san = str(move)

            self.board.push(move)
            self.update_captured_pieces()
            self.ui_side_panel.update_move_list(move_san)

            # Apply increment
            if self.board.turn == chess.BLACK:
                self.white_time += self.white_increment
            else:
                self.black_time += self.black_increment

            self.update_timer()
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()

            self.update_status_bar("Move made successfully.")

            # Collect training data
            self.collect_training_data(move)

            if not self.board.is_game_over():
                # Fetch and display predictions (optional)
                predictions = self.get_probable_future_predictions()
                self.ui_side_panel.show_predictions(predictions)

                # AI's turn
                if self.board.turn == self.ai_player.side:
                    self.handle_ai_move()

    def collect_training_data(self, move):
        board_tensor = board_to_tensor(self.board).numpy()
        move_index = move_to_index(move)
        move_quality = "Average Step"  # Placeholder, can be improved
        self.training_data.append((board_tensor, move_index, 0.0, move_quality))  # Outcome to be set later

    def handle_ai_move(self):
        def ai_move_thread():
            move = self.ai_player.get_best_move(self.board)
            if move:
                self.root.after(0, self.execute_ai_move, move)

        threading.Thread(target=ai_move_thread).start()

    def execute_ai_move(self, ai_move):
        try:
            move_san = self.board.san(ai_move)
        except ValueError:
            move_san = str(ai_move)

        self.board.push(ai_move)
        self.last_move = (ai_move.from_square, ai_move.to_square)

        # Play sound
        if self.sound_enabled:
            if self.board.is_capture(ai_move):
                self.sound_effects.play_capture()
            else:
                self.sound_effects.play_move()

        # Handle captured pieces
        captured_piece = self.board.piece_at(ai_move.to_square)
        if captured_piece:
            color = "black" if captured_piece.color else "white"
            self.captured_pieces[color].append(captured_piece.symbol())

        self.update_captured_pieces()
        self.ui_side_panel.update_move_list(move_san)
        self.chess_board.draw_chessboard()
        self.chess_board.draw_pieces()
        self.update_status_bar("AI made its move.")

        # Collect training data
        self.collect_training_data(ai_move)

        if self.board.is_game_over():
            self.handle_game_over()

    def handle_game_over(self):
        outcome = self.board.outcome()
        if outcome:
            result = outcome.result()
            if result == "1-0":
                messagebox.showinfo("Game Over", "White (AI) wins!")
                self.update_status_bar("AI (White) wins!")
                self.elo_rating.update(opponent_rating=1500, score=1.0)
            elif result == "0-1":
                messagebox.showinfo("Game Over", "Black (Stockfish) wins!")
                self.update_status_bar("Stockfish (Black) wins!")
                self.elo_rating.update(opponent_rating=1500, score=0.0)
            else:
                messagebox.showinfo("Game Over", "It's a draw!")
                self.update_status_bar("Draw!")
                self.elo_rating.update(opponent_rating=1500, score=0.5)

        # Save the game
        self.game_saver.save_game(self.board)

        # Update training data outcomes
        outcome_val = 0.5  # Default for draw
        if outcome.winner is not None:
            outcome_val = 1.0 if outcome.winner == self.ai_player.side else 0.0

        for idx in range(len(self.training_data)):
            board_tensor, move_index, _, move_quality = self.training_data[idx]
            self.training_data[idx] = (board_tensor, move_index, outcome_val, move_quality)

    def save_game(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension=".pgn",
                                                 filetypes=[("PGN Files", "*.pgn")])
        if filename:
            SaveLoad.save_game(self.board, filename)
            messagebox.showinfo("Game Saved", "The game has been saved successfully.")
            self.update_status_bar("Game saved successfully.")

    def load_game(self):
        filename = tk.filedialog.askopenfilename(filetypes=[("PGN Files", "*.pgn")])
        if filename:
            try:
                self.board = SaveLoad.load_game(filename)
                self.last_move = None
                self.white_time = 300
                self.black_time = 300
                self.captured_pieces = {"white": [], "black": []}
                self.redo_stack = []
                self.update_captured_pieces()
                self.ui_side_panel.move_list.config(state=tk.NORMAL)
                self.ui_side_panel.move_list.delete(1.0, tk.END)
                self.ui_side_panel.move_list.config(state=tk.DISABLED)
                self.update_timer()
                self.chess_board.draw_chessboard()
                self.chess_board.draw_pieces()
                messagebox.showinfo("Game Loaded", "The game has been loaded successfully.")
                self.update_status_bar("Game loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load game: {e}")
                self.update_status_bar("Error: Failed to load game.")

    def resign(self):
        if self.board.turn == chess.WHITE:
            # It's White's turn, so White is resigning
            messagebox.showinfo("Game Over", "White (AI) resigns. Black (Stockfish) wins!")
            self.update_status_bar("White (AI) resigned. Black (Stockfish) wins!")
        else:
            # It's Black's turn, so Black is resigning
            messagebox.showinfo("Game Over", "Black (Stockfish) resigns. White (AI) wins!")
            self.update_status_bar("Black (Stockfish) resigned. White (AI) wins!")
        self.board.push_san("resign")
        self.handle_game_over()

    def offer_draw(self):
        response = messagebox.askyesno("Offer Draw", "Do you want to offer a draw?")
        if response:
            messagebox.showinfo("Draw Offered", "Draw offered to the opponent.")
            self.update_status_bar("Draw offered.")
            # Implement opponent's response logic if applicable

    def restart_game(self):
        self.board.reset()
        self.last_move = None
        self.white_time = 300
        self.black_time = 300
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []
        self.update_captured_pieces()
        self.ui_side_panel.move_list.config(state=tk.NORMAL)
        self.ui_side_panel.move_list.delete(1.0, tk.END)
        self.ui_side_panel.move_list.config(state=tk.DISABLED)
        self.update_timer()
        self.chess_board.draw_chessboard()
        self.chess_board.draw_pieces()
        self.update_status_bar("Game restarted.")
        self.training_data = []

    def analyze_position(self):
        self.update_status_bar("Analyzing position...")
        best_move = self.ai_player.get_best_move(self.board)
        if best_move:
            from_square = best_move.from_square
            to_square = best_move.to_square
            self.chess_board.highlight_square(from_square, "#00FF00")  # Green
            self.chess_board.highlight_square(to_square, "#00FF00")
            self.update_status_bar(f"Suggested Move: {self.board.san(best_move)}")
        else:
            self.update_status_bar("No suggestion available.")

    def show_hint(self):
        self.update_status_bar("Fetching hint...")
        best_move = self.ai_player.get_best_move(self.board)
        if best_move:
            from_square = best_move.from_square
            to_square = best_move.to_square
            self.chess_board.highlight_square(from_square, "#FFD700")  # Gold
            self.chess_board.highlight_square(to_square, "#FFD700")
            self.update_status_bar(f"Hint: {self.board.san(best_move)}")
        else:
            self.update_status_bar("No hint available.")

    def analyze_game(self):
        analyzer = GameAnalyzer(engine_path="/path/to/stockfish", depth=3)  # Update engine path
        analysis = analyzer.analyze_game(self.board)
        analyzer.close()

        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Game Analysis")
        analysis_window.geometry("500x600")

        scroll = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD, font=("Helvetica", 12))
        scroll.pack(expand=True, fill='both')

        for move, eval_score in analysis:
            try:
                move_san = self.board.san(move)
            except ValueError:
                move_san = str(move)
            eval_text = f"Move: {move_san}, Evaluation: {eval_score}"
            scroll.insert(tk.END, eval_text + "\n")

        scroll.config(state=tk.DISABLED)
        self.update_status_bar("Game analysis completed.")


    def get_probable_future_predictions(self, top_n=5):
        """
        Returns the top_n probable moves and their win probabilities.
        """
        model = self.ai_player.model
        device = self.ai_player.device
        if model is None:
            return []

        board_tensor = board_to_tensor(self.board).to(device)
        with torch.no_grad():
            policy, value = model(board_tensor.unsqueeze(0))  # Add batch dimension
        move_probs = torch.exp(policy).cpu().numpy()[0]
        top_move_indices = move_probs.argsort()[-top_n:][::-1]
        predictions = []

        for idx in top_move_indices:
            move = index_to_move(idx, self.board)
            if move in self.board.legal_moves:
                # Apply the move to a copy of the board
                temp_board = self.board.copy(stack=False)
                temp_board.push(move)
                # Get the value estimation from the model
                temp_board_tensor = board_to_tensor(temp_board).to(device)
                with torch.no_grad():
                    _, temp_value = model(temp_board_tensor.unsqueeze(0))
                win_prob = (temp_value.item() + 1) / 2  # Convert tanh output to [0,1]
                predictions.append((move, win_prob))

        return predictions

    def start_ai_game(self):
        threading.Thread(target=self.play_ai_vs_stockfish_game, daemon=True).start()

    def play_ai_vs_stockfish_game(self):
        self.board.reset()
        self.update_captured_pieces()
        self.ui_side_panel.move_list.config(state=tk.NORMAL)
        self.ui_side_panel.move_list.delete(1.0, tk.END)
        self.ui_side_panel.move_list.config(state=tk.DISABLED)
        self.white_time = 300
        self.black_time = 300
        self.update_timer()
        self.chess_board.draw_chessboard()
        self.chess_board.draw_pieces()
        self.update_status_bar("Starting AI vs Stockfish game.")

        self.training_data = []

        self.schedule_next_move()

    def schedule_next_move(self):
        if not self.board.is_game_over():
            if self.board.turn == self.ai_player.side:
                move = self.ai_player.get_best_move(self.board)
                self.handle_move(move)
            else:
                move = self.ai_player.get_best_move(self.board)
                self.handle_move(move)
            self.root.after(1000, self.schedule_next_move)  # Adjust delay as needed
        else:
            self.handle_game_over()
            outcome = self.board.outcome()
            outcome_val = 0.5
            if outcome.winner is not None:
                outcome_val = 1.0 if outcome.winner == self.ai_player.side else 0.0
            self.logger.info(f"Game finished with outcome: {outcome_val}. ELO: {self.elo_rating.rating:.0f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()