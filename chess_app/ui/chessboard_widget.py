# chess_app/ui/chessboard_widget.py

import tkinter as tk
from tkinter import Canvas
import chess
from PIL import Image, ImageTk
import os
from chess_app.config import Config


class ChessBoardWidget(Canvas):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Config.CURRENT_THEME["background"], **kwargs)
        self.app = app
        self.board = app.board
        self.square_size = 60
        self.images = {}
        self.load_piece_images()
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.dragging_piece = None
        self.drag_start = None
        self.drag_image = None
        self.highlight_squares = []
        self.show_coordinates = False

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
        assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        for piece, filename in piece_filenames.items():
            path = os.path.join(assets_path, filename)
            try:
                image = Image.open(path).convert("RGBA")
                image = image.resize(
                    (self.square_size - 10, self.square_size - 10), Image.LANCZOS
                )
                background = Image.new("RGBA", image.size, (255, 255, 255, 0))
                combined = Image.alpha_composite(background, image)
                self.images[piece] = ImageTk.PhotoImage(combined)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                self.images[piece] = None

    def on_resize(self, event):
        size = min(event.width, event.height)
        self.square_size = size // 8
        self.load_piece_images()
        self.draw_board()
        self.draw_pieces()
        if self.show_coordinates:
            self.draw_coordinates()

    def draw_board(self):
        self.delete("square")
        colors = [
            Config.CURRENT_THEME["chessboard_light"],
            Config.CURRENT_THEME["chessboard_dark"],
        ]
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = colors[(row + col) % 2]
                self.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color, tags="square"
                )

        for square in self.highlight_squares:
            self.highlight_square(square, Config.CURRENT_THEME["highlight_color"])

    def draw_pieces(self):
        self.delete("piece")
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row = 7 - chess.square_rank(square)
                col = chess.square_file(square)
                x = col * self.square_size
                y = row * self.square_size
                image = self.images.get(piece.symbol())
                if image:
                    self.create_image(
                        x + self.square_size // 2,
                        y + self.square_size // 2,
                        image=image,
                        tags="piece",
                    )

    def draw_coordinates(self):
        self.delete("coord")
        font = ("Helvetica", 10)
        for col in range(8):
            x = col * self.square_size + self.square_size / 2
            y = 8 * self.square_size
            self.create_text(
                x,
                y + 10,
                text=chr(ord("A") + col),
                tags="coord",
                font=font,
                fill=Config.CURRENT_THEME["foreground"],
            )
        for row in range(8):
            x = -10
            y = row * self.square_size + self.square_size / 2
            self.create_text(
                x,
                y,
                text=str(row + 1),
                tags="coord",
                font=font,
                fill=Config.CURRENT_THEME["foreground"],
            )

    def toggle_coordinates(self, show):
        self.show_coordinates = show
        if show:
            self.draw_coordinates()
        else:
            self.delete("coord")

    def highlight_square(self, square, color):
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        x1 = col * self.square_size
        y1 = row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        self.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags="highlight")

    def on_click(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        square = chess.square(col, row)
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self.drag_start = (event.x, event.y)
            self.highlight_squares = [
                move.to_square
                for move in self.board.legal_moves
                if move.from_square == square
            ]
            self.draw_board()
            self.draw_pieces()

    def on_drag(self, event):
        if hasattr(self, "selected_square") and self.selected_square is not None:
            if not self.dragging_piece:
                piece = self.board.piece_at(self.selected_square)
                if piece:
                    self.dragging_piece = piece.symbol()
                    self.drag_image = self.images.get(piece.symbol())
            if self.dragging_piece and self.drag_image:
                self.delete("drag")
                self.create_image(event.x, event.y, image=self.drag_image, tags="drag")

    def on_drop(self, event):
        if self.selected_square is not None:
            col = event.x // self.square_size
            row = 7 - (event.y // self.square_size)
            to_square = chess.square(col, row)
            move = chess.Move(self.selected_square, to_square)
            if self.board.is_legal(move):
                self.app.handle_move(move)
            else:
                self.app.update_status(f"Illegal move attempted: {move}.", color="red")

            self.selected_square = None
            self.highlight_squares = []
            self.draw_board()
            self.draw_pieces()
