# chess_app/ui.py

import random
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import chess
import chess.pgn
from chess_app.board import ChessBoard
from chess_app.utils import AIPlayer, GameAnalyzer, SaveLoad, SoundEffects, Theme, Timer
import time
# Import matplotlib modules
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess AI")
        self.root.geometry("1400x800")  # Increased width for side panel
        self.root.configure(bg="#F5F5F7")

        self.board = chess.Board()
        self.selected_square = None
        self.dragging_piece = None
        self.drag_start_coords = None
        self.legal_moves = []
        self.last_move = None
        self.pending_promotion = None
        self.evaluation_history = []
        self.move_numbers = []

        self.white_time = 300  # 5 minutes for white
        self.black_time = 300  # 5 minutes for black
        self.white_increment = 5  # seconds per move
        self.black_increment = 5
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []

        self.sound_effects = SoundEffects()
        self.sound_enabled = True

        self.ai_player = AIPlayer(engine_path="/opt/homebrew/bin/stockfish")

        self.theme = Theme(self)

        # Create UI elements first
        self.create_main_layout()
        self.create_chessboard()
        self.create_side_panel()
        self.create_move_analysis_panel()  # New method for the graph
        self.create_status_bar()
        self.update_timer()

        # Apply theme after UI elements are created
        self.theme.apply_light_theme()

        self.update_clock()

    def create_move_analysis_panel(self):
        """
        Creates a panel with a matplotlib graph to display Stockfish's evaluations over moves.
        """
        # Frame for the graph
        analysis_frame = tk.Frame(self.side_panel_frame, bg="#FFFFFF")
        analysis_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Label for the graph
        graph_label = tk.Label(
            analysis_frame,
            text="Win Probability Graph",
            font=("Helvetica", 14, "bold"),
            bg="#FFFFFF",
            fg="#000000",
        )
        graph_label.pack(pady=(0, 5))

        # Create a matplotlib Figure
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Stockfish Evaluation Over Moves")
        self.ax.set_xlabel("Move Number")
        self.ax.set_ylabel("Evaluation (Centipawns)")

        # Create a FigureCanvasTkAgg widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=analysis_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_evaluation_graph(self):
        """
        Updates the matplotlib graph with the latest evaluation data.
        """
        self.ax.cla()  # Clear the previous plot
        self.ax.set_title("Stockfish Evaluation Over Moves")
        self.ax.set_xlabel("Move Number")
        self.ax.set_ylabel("Evaluation (Centipawns)")

        # Plot the evaluation history
        self.ax.plot(self.move_numbers, self.evaluation_history, marker='o', linestyle='-')

        # Add a horizontal line at 0 (equal position)
        self.ax.axhline(0, color='gray', linestyle='--')

        self.canvas.draw()

    def handle_move(self, move, promotion=None):
        # ... [existing handle_move code]

        # After handling the move, fetch and store the evaluation
        self.fetch_and_store_evaluation()

        # Update the graph
        self.update_evaluation_graph()

    def execute_ai_move(self, ai_move):
        # ... [existing execute_ai_move code]

        # After handling the AI move, fetch and store the evaluation
        self.fetch_and_store_evaluation()

        # Update the graph
        self.update_evaluation_graph()

    def fetch_and_store_evaluation(self):
        """
        Fetches the current evaluation from Stockfish and stores it for graphing.
        """
        # Assuming AIPlayer has a method to get the current evaluation
        # You may need to adjust this based on your AIPlayer implementation
        try:
            # Get the evaluation in centipawns
            evaluation = self.ai_player.get_evaluation(self.board)
            self.evaluation_history.append(evaluation)
            self.move_numbers.append(len(self.move_numbers) + 1)
        except Exception as e:
            print(f"Error fetching evaluation: {e}")
            # Handle cases where evaluation might not be available

    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid to have two columns: board and side panel
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Board Frame
        self.board_frame = tk.Frame(self.main_frame, bg="#D6D6D6", bd=0, highlightthickness=0)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

        # Side Panel Frame
        self.side_panel_frame = tk.Frame(self.main_frame, bg="#FFFFFF", bd=0, highlightthickness=0)
        self.side_panel_frame.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

    def create_chessboard(self):
        self.chess_board = ChessBoard(self.board_frame, self)
        self.chess_board.pack(fill=tk.BOTH, expand=True)

    def create_side_panel(self):
        side_panel = self.side_panel_frame

        # Buttons Frame
        buttons_frame = ttk.Frame(side_panel)
        buttons_frame.pack(fill=tk.X, pady=10)

        # AI Difficulty
        difficulty_label = ttk.Label(buttons_frame, text="AI Difficulty:")
        difficulty_label.pack(pady=5, anchor="w")

        self.difficulty_var = tk.StringVar(value="2")
        difficulty_options = ttk.Combobox(buttons_frame, textvariable=self.difficulty_var, state="readonly")
        difficulty_options['values'] = ("1", "2", "3", "4", "5")
        difficulty_options.pack(pady=5, fill=tk.X)
        difficulty_options.bind("<<ComboboxSelected>>", self.set_ai_difficulty)

        # Sound Toggle
        self.sound_toggle_var = tk.BooleanVar(value=True)
        self.sound_toggle = ttk.Checkbutton(
            buttons_frame,
            text="Sound Effects",
            variable=self.sound_toggle_var,
            command=self.toggle_sound
        )
        self.sound_toggle.pack(pady=5, anchor="w")

        # Hint Button
        self.hint_button = ttk.Button(buttons_frame, text="Show Hint", command=self.show_hint)
        self.hint_button.pack(pady=5, fill=tk.X)

        # Analyze Position Button
        self.analyze_button = ttk.Button(buttons_frame, text="Analyze Position", command=self.analyze_position)
        self.analyze_button.pack(pady=5, fill=tk.X)

        # Analyze Game Button
        self.analyze_game_button = ttk.Button(buttons_frame, text="Analyze Game", command=self.analyze_game)
        self.analyze_game_button.pack(pady=5, fill=tk.X)

        # Undo/Redo Buttons
        self.undo_button = ttk.Button(buttons_frame, text="Undo Move", command=self.undo_move)
        self.undo_button.pack(pady=5, fill=tk.X)

        self.redo_button = ttk.Button(buttons_frame, text="Redo Move", command=self.redo_move)
        self.redo_button.pack(pady=5, fill=tk.X)

        # Save/Load Buttons
        self.save_button = ttk.Button(buttons_frame, text="Save Game", command=self.save_game)
        self.save_button.pack(pady=5, fill=tk.X)

        self.load_button = ttk.Button(buttons_frame, text="Load Game", command=self.load_game)
        self.load_button.pack(pady=5, fill=tk.X)

        # Resign/Draw Buttons
        self.resign_button = ttk.Button(buttons_frame, text="Resign", command=self.resign)
        self.resign_button.pack(pady=5, fill=tk.X)

        self.draw_button = ttk.Button(buttons_frame, text="Offer Draw", command=self.offer_draw)
        self.draw_button.pack(pady=5, fill=tk.X)

        self.restart_button = ttk.Button(buttons_frame, text="Restart Game", command=self.restart_game)
        self.restart_button.pack(pady=5, fill=tk.X)

        # Theme Toggle
        self.theme_button = ttk.Button(buttons_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(pady=10, fill=tk.X)

        # Status Labels
        self.status_label = tk.Label(
            side_panel,
            text="White to move",
            font=("Helvetica", 16, "bold"),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.status_label.pack(pady=10)

        # Timer Display
        self.timer_label = tk.Label(
            side_panel,
            text="White: 05:00 - Black: 05:00",
            font=("Helvetica", 14),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.timer_label.pack(pady=10)

        # Captured Pieces
        captured_pieces_frame = tk.Frame(side_panel, bg="#FFFFFF")
        captured_pieces_frame.pack(pady=10, anchor="n")

        # White Captured Pieces
        white_captured_label = tk.Label(
            captured_pieces_frame, text="White Captured:", bg="#FFFFFF", font=("Helvetica", 12, "bold")
        )
        white_captured_label.grid(row=0, column=0, sticky="w")

        self.captured_pieces_white = tk.Label(
            captured_pieces_frame, text="", bg="#FFFFFF", font=("Helvetica", 12), wraplength=200, justify="left"
        )
        self.captured_pieces_white.grid(row=1, column=0, sticky="w")

        # Black Captured Pieces
        black_captured_label = tk.Label(
            captured_pieces_frame, text="Black Captured:", bg="#FFFFFF", font=("Helvetica", 12, "bold")
        )
        black_captured_label.grid(row=2, column=0, sticky="w")

        self.captured_pieces_black = tk.Label(
            captured_pieces_frame, text="", bg="#FFFFFF", font=("Helvetica", 12), wraplength=200, justify="left"
        )
        self.captured_pieces_black.grid(row=3, column=0, sticky="w")

        # Move List
        self.move_list_label = tk.Label(
            side_panel,
            text="Moves:",
            font=("Helvetica", 14, "bold"),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.move_list_label.pack(pady=(20, 10))

        self.move_list = scrolledtext.ScrolledText(
            side_panel,
            height=20,
            width=25,
            state=tk.DISABLED,
            bg="#F0F0F0",
            fg="#333333",
            font=("Helvetica", 12),
            wrap=tk.WORD
        )
        self.move_list.pack(pady=10, fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="Welcome to Chess AI!",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#F5F5F7",
            fg="#333333",
            font=("Helvetica", 12),
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status_bar(self, message):
        self.status_bar.config(text=message)

    def update_timer(self):
        self.timer_label.config(
            text=Timer.format_time(self.white_time, self.black_time)
        )

    def update_clock(self):
        if self.board.is_game_over():
            return

        # Use self.board.turn to determine whose turn it is
        if self.board.turn == chess.WHITE:
            # It's White's turn; decrement White's time
            if self.white_time > 0:
                self.white_time -= 1
            else:
                messagebox.showinfo("Time Up", "White's time is up. Black wins!")
                self.update_status_bar("Black wins on time.")
                self.board.push_san("resign")
                self.handle_game_over()
        else:
            # It's Black's turn; decrement Black's time
            if self.black_time > 0:
                self.black_time -= 1
            else:
                messagebox.showinfo("Time Up", "Black's time is up. White wins!")
                self.update_status_bar("White wins on time.")
                self.board.push_san("resign")
                self.handle_game_over()

        self.update_timer()
        self.root.after(1000, self.update_clock)

    def set_ai_difficulty(self, event):
        selected_depth = int(self.difficulty_var.get())
        self.ai_player.set_depth(selected_depth)
        self.update_status_bar(f"AI difficulty set to level {selected_depth}")

    def toggle_sound(self):
        self.sound_enabled = self.sound_toggle_var.get()
        self.update_status_bar(f"Sound Effects {'Enabled' if self.sound_enabled else 'Disabled'}")

    def toggle_theme(self):
        self.theme.toggle_theme()
        self.update_status_bar("Theme toggled.")

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            last_move = self.board.pop()
            self.redo_stack.append(last_move)
            if last_move.to_square:
                captured_piece = self.board.piece_at(last_move.to_square)
                if captured_piece:
                    if captured_piece.color:
                        self.captured_pieces["black"].remove(captured_piece.symbol())
                    else:
                        self.captured_pieces["white"].remove(captured_piece.symbol())
            self.last_move = None
            self.update_timer()
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()
            self.update_captured_pieces()
            self.update_move_list_undo()
            self.update_status_bar("Move undone.")

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
            self.update_timer()
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()
            self.update_captured_pieces()
            self.update_move_list_redo(move)
            self.update_status_bar("Move redone.")

    def update_captured_pieces(self):
        white_captured = " ".join(self.captured_pieces["white"])
        black_captured = " ".join(self.captured_pieces["black"])

        # Update the labels instead of config on separate labels
        self.captured_pieces_white.config(text=white_captured)
        self.captured_pieces_black.config(text=black_captured)

    def update_move_list(self, move_san):
        self.move_list.config(state=tk.NORMAL)
        move_number = self.board.fullmove_number
        if self.board.turn:
            # Black's move
            self.move_list.insert(tk.END, f"{move_number}. ... {move_san}\n")
        else:
            # White's move
            self.move_list.insert(tk.END, f"{move_number}. {move_san} ")
        self.move_list.config(state=tk.DISABLED)

    def update_move_list_undo(self):
        self.move_list.config(state=tk.NORMAL)
        content = self.move_list.get("1.0", tk.END).strip().split("\n")
        if content:
            last_line = content[-1]
            if last_line.startswith(f"{self.board.fullmove_number - 1}. ..."):
                # It's a Black move; remove the last line
                self.move_list.delete(f"{len(content)}.0 linestart", f"{len(content)}.end")
            else:
                # It's a White move; remove the last move after the move number
                # Find the last space and remove everything after it
                last_space = last_line.rfind(" ")
                if last_space != -1:
                    self.move_list.delete(f"{len(content)}.{last_space+1}c", f"{len(content)}.end")
        self.move_list.config(state=tk.DISABLED)

    def update_move_list_redo(self, move):
        self.move_list.config(state=tk.NORMAL)
        move_san = self.board.san(move)
        move_number = self.board.fullmove_number
        if self.board.turn:
            # After White's move, it's Black's turn
            self.move_list.insert(tk.END, f"{move_number}. ... {move_san}\n")
        else:
            # After Black's move, it's White's turn
            self.move_list.insert(tk.END, f"{move_number}. {move_san} ")
        self.move_list.config(state=tk.DISABLED)

    def handle_move(self, move, promotion=None):
        if promotion:
            move.promotion = chess.Piece.from_symbol(promotion.upper()).piece_type
        if move in self.legal_moves:
            self.last_move = (move.from_square, move.to_square)

            # Play appropriate sound
            if self.sound_enabled:
                if self.board.is_capture(move):
                    self.sound_effects.play_capture()
                else:
                    self.sound_effects.play_move()

            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece:
                if captured_piece.color:
                    self.captured_pieces["black"].append(captured_piece.symbol())
                else:
                    self.captured_pieces["white"].append(captured_piece.symbol())

            # Generate SAN before pushing the move
            try:
                move_san = self.board.san(move)
            except ValueError:
                move_san = str(move)

            self.board.push(move)
            self.update_captured_pieces()
            self.update_move_list(move_san)  # Pass SAN instead of move

            # Apply increment based on the move that was just pushed
            if self.board.turn == chess.BLACK:
                # White just moved
                self.white_time += self.white_increment
            else:
                # Black just moved
                self.black_time += self.black_increment

            # No need for self.is_white_turn; use board.turn
            self.update_timer()

            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()

            self.update_status_bar("Move made successfully.")

            if not self.board.is_game_over():
                self.handle_ai_move()

    def handle_ai_move(self):
        def ai_move_thread():
            ai_move = self.ai_player.get_best_move(self.board)
            if ai_move:
                # Introduce a delay before making the move
                time.sleep(1.5)  # 1.5 seconds delay

                # Schedule the move to be pushed on the main thread
                self.root.after(0, self.execute_ai_move, ai_move)

        threading.Thread(target=ai_move_thread).start()

    def execute_ai_move(self, ai_move):
        # Generate SAN before pushing
        try:
            move_san = self.board.san(ai_move)
        except ValueError:
            move_san = str(ai_move)

        self.board.push(ai_move)
        self.last_move = (ai_move.from_square, ai_move.to_square)

        # Play capture or move sound
        if self.sound_enabled:
            if self.board.is_capture(ai_move):
                self.sound_effects.play_capture()
            else:
                self.sound_effects.play_move()

        captured_piece = self.board.piece_at(ai_move.to_square)
        if captured_piece:
            if captured_piece.color:
                self.captured_pieces["black"].append(captured_piece.symbol())
            else:
                self.captured_pieces["white"].append(captured_piece.symbol())

        self.update_captured_pieces()
        self.update_move_list(move_san)  # Pass SAN instead of move

        # Apply increment based on the move that was just pushed
        if self.board.turn == chess.WHITE:
            # Black just moved
            self.black_time += self.black_increment
        else:
            # White just moved
            self.white_time += self.white_increment

        self.update_timer()
        self.chess_board.draw_chessboard()
        self.chess_board.draw_pieces()
        self.update_status_bar("AI made its move.")

        if self.board.is_game_over():
            self.handle_game_over()

    def handle_game_over(self):
        outcome = self.board.outcome()
        if outcome:
            result = outcome.result()
            if result == "1-0":
                messagebox.showinfo("Game Over", "White wins!")
                self.update_status_bar("White wins!")
            elif result == "0-1":
                messagebox.showinfo("Game Over", "Black wins!")
                self.update_status_bar("Black wins!")
            else:
                messagebox.showinfo("Game Over", "It's a draw!")
                self.update_status_bar("Draw!")

    def save_game(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pgn",
                                                filetypes=[("PGN Files", "*.pgn")])
        if filename:
            SaveLoad.save_game(self.board, filename)
            messagebox.showinfo("Game Saved", "The game has been saved successfully.")
            self.update_status_bar("Game saved successfully.")

    def load_game(self):
        filename = filedialog.askopenfilename(filetypes=[("PGN Files", "*.pgn")])
        if filename:
            try:
                self.board = SaveLoad.load_game(filename)
                self.last_move = None
                self.white_time = 300
                self.black_time = 300
                self.captured_pieces = {"white": [], "black": []}
                self.redo_stack = []
                self.update_captured_pieces()
                self.move_list.config(state=tk.NORMAL)
                self.move_list.delete(1.0, tk.END)
                self.move_list.config(state=tk.DISABLED)
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
            messagebox.showinfo("Game Over", "White resigns. Black wins!")
            self.update_status_bar("White resigned. Black wins!")
        else:
            # It's Black's turn, so Black is resigning
            messagebox.showinfo("Game Over", "Black resigns. White wins!")
            self.update_status_bar("Black resigned. White wins!")
        self.board.push_san("resign")
        self.handle_game_over()

    def offer_draw(self):
        response = messagebox.askyesno("Offer Draw", "Do you want to offer a draw?")
        if response:
            messagebox.showinfo("Draw Offered", "Draw offered to the opponent.")
            self.update_status_bar("Draw offered.")
            # Here, you can implement logic to handle opponent's response

    def restart_game(self):
        self.board.reset()
        self.last_move = None
        self.white_time = 300
        self.black_time = 300
        self.captured_pieces = {"white": [], "black": []}
        self.redo_stack = []
        self.update_captured_pieces()
        self.move_list.config(state=tk.NORMAL)
        self.move_list.delete(1.0, tk.END)
        self.move_list.config(state=tk.DISABLED)
        self.update_timer()
        self.chess_board.draw_chessboard()
        self.chess_board.draw_pieces()
        self.update_status_bar("Game restarted.")

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
        analyzer = GameAnalyzer(engine_path=self.ai_player.engine_path)
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

    def update_move_list(self, move_san):
        self.move_list.config(state=tk.NORMAL)
        move_number = self.board.fullmove_number
        if self.board.turn:
            # Black's move
            self.move_list.insert(tk.END, f"{move_number}. ... {move_san}\n")
        else:
            # White's move
            self.move_list.insert(tk.END, f"{move_number}. {move_san} ")
        self.move_list.config(state=tk.DISABLED)

    def handle_promotion(self, promotion_piece):
        if self.pending_promotion:
            move, promotion = self.pending_promotion
            self.handle_move(move, promotion)
            self.pending_promotion = None

    def update_status_bar(self, message):
        self.status_bar.config(text=message)