# chess_app/board.py

import chess
import os
from PIL import Image, ImageTk


class ChessBoard:
    """
    ChessBoard is a class that displays the chessboard and pieces.
    It handles the drawing and resizing of the board and pieces,
    but without any direct UI interaction, now handled by the React frontend.
    """

    def __init__(self, app=None):
        self.app = app
        self.piece_images = {}
        self.square_size = 60
        self.load_piece_images()

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
