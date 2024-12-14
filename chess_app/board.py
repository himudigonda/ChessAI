# chess_app/board.py

import tkinter as tk
from chess import SQUARES, square_rank, square_file
from chess_app.utils import Timer, SoundEffects
import chess
import os


class ChessBoard(tk.Canvas):
    """
    ChessBoard is a Tkinter Canvas that displays the chessboard and pieces.
    It handles resizing and drawing of the board and pieces.
    """

    def __init__(self, parent, app, **kwargs):
        """
        Initializes the ChessBoard.

        :param parent: The parent Tkinter widget.
        :param app: The main ChessApp instance.
        :param kwargs: Additional keyword arguments for Tkinter Canvas.
        """
        super().__init__(parent, bg="#FFFFFF", highlightthickness=0, **kwargs)
        self.app = app
        self.board = app.board
        self.piece_images = {}
        self.load_piece_images()

        # Bind the resize event to redraw the board
        self.bind("<Configure>", self.on_canvas_resize)

        # Disable user interactions since AI vs Stockfish is automated
        # To enable user interactions, uncomment the following lines
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(current_dir, "..", "assets")

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
        """
        Handles the canvas resize event by redrawing the chessboard and pieces.

        :param event: The Tkinter event object.
        """
        self.draw_chessboard()
        self.draw_pieces()

    def draw_chessboard(self):
        """
        Draws the chessboard squares on the canvas.
        Highlights the last move if available.
        """
        self.delete("all")  # Clear the canvas before redrawing
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        self.square_size = min(canvas_width, canvas_height) // 8  # Size of each square

        # Define colors for the chessboard squares
        colors = ["#EEEED2", "#769656"]  # Light and dark squares

        # Draw the squares
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * self.square_size, row * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                self.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color, tags="square"
                )

        # Highlight the last move
        if self.app.last_move:
            from_square, to_square = self.app.last_move
            self.highlight_square(from_square, "#E6B800")  # Gold color
            self.highlight_square(to_square, "#E6B800")

    def draw_pieces(self):
        """
        Draws the chess pieces on the board based on the current board state.
        """
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
        """
        Highlights a specific square with the given color.

        :param square: The square to highlight.
        :param color: The color to use for highlighting.
        """
        row = 7 - square_rank(square)
        col = square_file(square)
        x1 = col * self.square_size
        y1 = row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        self.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags="highlight")

    def highlight_legal_moves(self):
        """
        Highlights all legal moves available for the selected piece.
        """
        self.delete("highlight")
        for move in self.app.legal_moves:
            to_square = move.to_square
            self.highlight_square(to_square, "#0073e6")  # Blue color
