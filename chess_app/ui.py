# chess_app/ui.py
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from chess import Board
from chess_app.board import ChessBoard
from chess_app.utils import Timer, SaveLoad, Theme

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess App")
        self.root.geometry("1024x768")  # Smaller default window size
        self.root.configure(bg="#F5F5F7")

        self.board = Board()
        self.selected_square = None
        self.dragging_piece = None
        self.drag_start_coords = None
        self.legal_moves = []
        self.last_move = None

        self.white_time = 300  # 5 minutes for white
        self.black_time = 300  # 5 minutes for black
        self.is_white_turn = True
        self.captured_pieces = {"white": [], "black": []}

        self.create_main_layout()
        self.create_chessboard()
        self.create_side_panel()
        self.create_status_bar()
        self.update_timer()

    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.board_frame = tk.Frame(self.main_frame, bg="#D6D6D6", bd=0, highlightthickness=0)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

        self.side_panel_frame = tk.Frame(self.main_frame, bg="#FFFFFF", bd=0, highlightthickness=0)
        self.side_panel_frame.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_chessboard(self):
        self.chess_board = ChessBoard(self.board_frame, self)
        self.chess_board.pack(fill=tk.BOTH, expand=True)

    def create_side_panel(self):
        # Game status label
        self.status_label = tk.Label(
            self.side_panel_frame,
            text="White to move",
            font=("SF Pro Display", 18, "bold"),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.status_label.pack(pady=10)

        # Timer display
        self.timer_label = tk.Label(
            self.side_panel_frame,
            text="Time: 05:00 - 05:00",
            font=("SF Pro Display", 16),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.timer_label.pack(pady=10)

        # Captured pieces section
        captured_pieces_frame = tk.Frame(self.side_panel_frame, bg="#FFFFFF")
        captured_pieces_frame.pack(pady=10)

        self.captured_label_white = tk.Label(
            captured_pieces_frame, text="White Captured: ", bg="#FFFFFF", font=("SF Pro Display", 12)
        )
        self.captured_label_white.pack(anchor="w")

        self.captured_label_black = tk.Label(
            captured_pieces_frame, text="Black Captured: ", bg="#FFFFFF", font=("SF Pro Display", 12)
        )
        self.captured_label_black.pack(anchor="w")

        # Move list
        self.move_list_label = tk.Label(
            self.side_panel_frame,
            text="Moves:",
            font=("SF Pro Display", 16),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.move_list_label.pack(pady=10)

        self.move_list = tk.Text(
            self.side_panel_frame,
            height=15,
            width=25,
            state=tk.DISABLED,
            bg="#F0F0F0",
            fg="#333333",
            font=("SF Pro Display", 12),
        )
        self.move_list.pack(pady=10)

        # Buttons Section
        button_frame = tk.Frame(self.side_panel_frame, bg="#FFFFFF")
        button_frame.pack(pady=20)

        self.undo_button = ttk.Button(button_frame, text="Undo Move", command=self.undo_move)
        self.undo_button.pack(pady=5)

        self.save_button = ttk.Button(button_frame, text="Save Game", command=self.save_game)
        self.save_button.pack(pady=5)

        self.load_button = ttk.Button(button_frame, text="Load Game", command=self.load_game)
        self.load_button.pack(pady=5)

        self.resign_button = ttk.Button(button_frame, text="Resign", command=self.resign)
        self.resign_button.pack(pady=5)

        self.draw_button = ttk.Button(button_frame, text="Offer Draw", command=self.offer_draw)
        self.draw_button.pack(pady=5)

        self.restart_button = ttk.Button(button_frame, text="Restart Game", command=self.restart_game)
        self.restart_button.pack(pady=5)

        # Theme toggle button
        self.theme_button = ttk.Button(
            self.side_panel_frame, text="Toggle Theme", command=self.toggle_theme
        )
        self.theme_button.pack(pady=10)

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="Welcome to Chess App!",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#F5F5F7",
            fg="#333333",
            font=("SF Pro Display", 14),
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status_bar(self, message):
        self.status_bar.config(text=message)

    def highlight_square(self, square, color):
        self.chess_board.highlight_square(square, color)

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            last_move = self.board.pop()
            if last_move.to_square:
                captured_piece = self.board.piece_at(last_move.to_square)
                if captured_piece:
                    if captured_piece.color:
                        self.captured_pieces["black"].remove(captured_piece.symbol())
                    else:
                        self.captured_pieces["white"].remove(captured_piece.symbol())
            self.last_move = None
            self.is_white_turn = not self.is_white_turn
            self.update_timer()
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()
            self.update_captured_pieces()
            self.update_status_bar("Move undone.")

    def save_game(self):
        SaveLoad.save_game(self.board)
        showinfo("Game Saved", "The game has been saved successfully.")
        self.update_status_bar("Game saved successfully.")

    def load_game(self):
        try:
            fen = SaveLoad.load_game()
            self.board.set_fen(fen)
            self.last_move = None
            self.is_white_turn = self.board.turn
            self.update_timer()
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()
            self.update_captured_pieces()
            showinfo("Game Loaded", "The game has been loaded successfully.")
            self.update_status_bar("Game loaded successfully.")
        except FileNotFoundError:
            showinfo("Error", "No saved game found.")
            self.update_status_bar("Error: No saved game found.")

    def resign(self):
        showinfo("Game Over", "You resigned!")
        self.update_status_bar("You resigned.")

    def offer_draw(self):
        showinfo("Draw Offered", "You offered a draw!")
        self.update_status_bar("Draw offered.")

    def restart_game(self):
        self.board.reset()
        self.last_move = None
        self.is_white_turn = True
        self.white_time = 300
        self.black_time = 300
        self.move_list.config(state=tk.NORMAL)
        self.move_list.delete(1.0, tk.END)
        self.move_list.config(state=tk.DISABLED)
        self.captured_pieces = {"white": [], "black": []}
        self.update_captured_pieces()
        self.update_timer()
        self.chess_board.draw_chessboard()
        self.chess_board.draw_pieces()
        self.update_status_bar("Game restarted.")

    def update_captured_pieces(self):
        white_captured = " ".join(self.captured_pieces["white"])
        black_captured = " ".join(self.captured_pieces["black"])

        self.captured_label_white.config(text=f"White Captured: {white_captured}")
        self.captured_label_black.config(text=f"Black Captured: {black_captured}")

    def update_move_list(self, move):
        self.move_list.config(state=tk.NORMAL)

        if self.board.turn:
            # White's turn: Append black's move
            move_text = f"{self.board.fullmove_number}. {self.last_move[0]} {move.uci()}\n"
        else:
            # Black's turn: Append white's move
            move_text = f"{self.board.fullmove_number}. {move.uci()} "

        self.move_list.insert(tk.END, move_text)
        self.move_list.config(state=tk.DISABLED)

    def update_timer(self):
        self.timer_label.config(
            text=Timer.format_time(self.white_time, self.black_time)
        )

    def toggle_theme(self):
        Theme.toggle_theme(self)

    def handle_move(self, move):
        if move in self.legal_moves:
            self.last_move = (self.selected_square, move.to_square)
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece:
                if captured_piece.color:
                    self.captured_pieces["black"].append(captured_piece.symbol())
                else:
                    self.captured_pieces["white"].append(captured_piece.symbol())
            self.board.push(move)
            self.update_captured_pieces()
            self.update_move_list(move)

            # Switch timers
            self.is_white_turn = not self.is_white_turn
            self.update_timer()
            self.update_status_bar("Move made successfully.")

            # Redraw board
            self.chess_board.draw_chessboard()
            self.chess_board.draw_pieces()