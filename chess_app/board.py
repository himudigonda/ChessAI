# chess_app/board.py

import tkinter as tk
from chess import SQUARES, square_rank, square_file, Move
from chess_app.utils import Timer, SoundEffects
import chess
import os

class ChessBoard(tk.Canvas):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#FFFFFF", highlightthickness=0, **kwargs)
        self.app = app
        self.board = app.board
        self.piece_images = {}
        self.load_piece_images()

        # Bind events
        self.bind("<Configure>", self.on_canvas_resize)
        # Disable user interactions since AI vs Stockfish is automated
        # If you want to enable user interactions, uncomment the following lines
        # self.bind("<Button-1>", self.on_click)
        # self.bind("<B1-Motion>", self.on_drag)
        # self.bind("<ButtonRelease-1>", self.on_drop)

        self.dragging_piece = None
        self.drag_start_coords = None

    def load_piece_images(self):
        piece_filenames = {
            "P": "White_pawn.png",
            "N": "White_knight.png",
            "B": "White_bishop.png",
            "R": "White_rook.png",
            "Q": "White_queen.png",
            "K": "White_king.png",
            "p": "Black_pawn.png",
            "n": "Black_knight.png",
            "b": "Black_bishop.png",
            "r": "Black_rook.png",
            "q": "Black_queen.png",
            "k": "Black_king.png",
        }
        assets_path = "./assets"

        for piece, filename in piece_filenames.items():
            file_path = os.path.join(assets_path, filename)
            try:
                self.piece_images[piece] = tk.PhotoImage(file=file_path)
            except tk.TclError:
                print(f"Error: Missing file {file_path}")
                self.piece_images[piece] = None  # Placeholder for missing images

    def on_canvas_resize(self, event):
        self.draw_chessboard()
        self.draw_pieces()

    def draw_chessboard(self):
        self.delete("all")  # Clear everything before redrawing
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        self.square_size = min(canvas_width, canvas_height) // 8

        # Define colors based on theme
        if self.app.theme.current_theme == "light":
            colors = ["#EEEED2", "#769656"]
        else:
            colors = ["#303030", "#B58863"]

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * self.square_size, row * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                self.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color, tags="square"
                )

        if self.app.last_move:
            from_square, to_square = self.app.last_move
            self.highlight_square(from_square, "#E6B800")
            self.highlight_square(to_square, "#E6B800")

    def draw_pieces(self):
        # Ensure pieces are drawn after squares
        for square in SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = 7 - square_rank(square), square_file(square)
                x, y = (
                    col * self.square_size + self.square_size // 2,
                    row * self.square_size + self.square_size // 2,
                )
                image = self.piece_images.get(piece.symbol())
                if image:
                    self.create_image(
                        x, y, image=image, tags=f"piece_{square}", anchor=tk.CENTER
                    )
                else:
                    print(f"Warning: Image for piece {piece.symbol()} not found.")

    def highlight_square(self, square, color):
        row, col = 7 - square_rank(square), square_file(square)
        x1, y1 = col * self.square_size, row * self.square_size
        x2, y2 = x1 + self.square_size, y1 + self.square_size
        self.create_rectangle(
            x1, y1, x2, y2, outline=color, width=3, tags="highlight"
        )

    def highlight_legal_moves(self):
        self.delete("highlight")
        for move in self.app.legal_moves:
            to_square = move.to_square
            self.highlight_square(to_square, "#0073e6")