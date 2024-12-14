# chess_app/board.py

import tkinter as tk
from chess import SQUARES, square_rank, square_file
from chess_app.utils import Timer, SoundEffects
import chess
import os
from PIL import Image, ImageTk


class ChessBoard(tk.Canvas):
    """
    ChessBoard is a Tkinter Canvas that displays the chessboard and pieces.
    It handles resizing and drawing of the board and pieces.
    """

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#FFFFFF", highlightthickness=0, **kwargs)
        self.app = app
        self.board = app.board
        self.piece_images = {}
        self.square_size = 60  # Initialize with a default value
        self.load_piece_images()

        # Bind the resize event to redraw the board
        self.bind("<Configure>", self.on_canvas_resize)

        # If needed, user interactions can be enabled by binding mouse events
        self.dragging_piece = None
        self.drag_start_coords = None

    def load_piece_images(self):
        from PIL import Image, ImageTk

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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(current_dir, "..", "assets")

        # If called before square_size is known, just use a default size
        if self.square_size <= 0:
            self.square_size = 60

        for piece, filename in piece_filenames.items():
            file_path = os.path.join(assets_path, filename)
            try:
                image = Image.open(file_path).convert("RGBA")
                image = image.resize(
                    (self.square_size - 10, self.square_size - 10), Image.LANCZOS
                )
                background = Image.new("RGBA", image.size, (255, 255, 255, 0))
                combined = Image.alpha_composite(background, image)
                self.piece_images[piece] = ImageTk.PhotoImage(combined)
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")
                self.piece_images[piece] = None

    def on_canvas_resize(self, event):
        self.draw_chessboard()
        self.draw_pieces()

    def draw_chessboard(self):
        self.delete("all")  # Clear the canvas before redrawing
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        self.square_size = min(canvas_width, canvas_height) // 8

        # Reload images with new size
        self.load_piece_images()

        colors = ["#EEEED2", "#769656"]  # Light and dark squares

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * self.square_size, row * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                self.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color, tags="square"
                )

        # Highlight last move if available
        if self.app.last_move:
            from_square, to_square = self.app.last_move
            self.highlight_square(from_square, "#E6B800")  # Gold
            self.highlight_square(to_square, "#E6B800")

    def draw_pieces(self):
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
        row = 7 - square_rank(square)
        col = square_file(square)
        x1 = col * self.square_size
        y1 = row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        self.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags="highlight")
