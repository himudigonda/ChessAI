# chess_app/ui_board.py

import tkinter as tk
from PIL import Image, ImageTk
import chess
import chess.svg
from chess_app.data import board_to_tensor

class ChessBoard(tk.Canvas):
    def __init__(self, parent, app, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.board = app.board
        self.images = {}
        self.load_images()
        self.draw_chessboard()
        self.bind_events()

    def load_images(self):
        # Load images for pieces
        pieces = ['White_pawn', 'White_knight', 'White_bishop', 'White_rook', 'White_queen', 'White_king',
                  'Black_pawn', 'Black_knight', 'Black_bishop', 'Black_rook', 'Black_queen', 'Black_king']

        for piece in pieces:
            image = Image.open(f"assets/{piece}.png")
            image = image.resize((60, 60))
            self.images[piece] = ImageTk.PhotoImage(image)

    def draw_chessboard(self):
        self.delete("all")
        colors = ["#F0D9B5", "#B58863"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.create_rectangle(col*60, row*60, (col+1)*60, (row+1)*60, fill=color, outline=color)

    def draw_pieces(self):
        self.delete("pieces")
        for square, piece in self.board.piece_map().items():
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            x = col * 60 + 30
            y = row * 60 + 30
            piece_key = piece.symbol()
            if piece.color:
                piece_key = piece_key.upper()
            else:
                piece_key = piece_key.lower()
            piece_image = self.images.get(piece_key)
            if piece_image:
                self.create_image(x, y, image=piece_image, tags="pieces")

    def bind_events(self):
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)

    def on_click(self, event):
        col = event.x // 60
        row = event.y // 60
        square = chess.square(col, 7 - row)
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.app.selected_square = square
            self.dragging_piece = piece
            self.drag_start_coords = (event.x, event.y)

    def on_drag(self, event):
        if self.dragging_piece:
            # Implement drag visualization if desired
            pass

    def on_drop(self, event):
        if self.dragging_piece:
            col = event.x // 60
            row = event.y // 60
            to_square = chess.square(col, 7 - row)
            from_square = self.app.selected_square
            move = chess.Move(from_square, to_square)
            if move in self.board.legal_moves:
                self.app.handle_move(move)
            self.dragging_piece = None
            self.app.selected_square = None

    def highlight_square(self, square, color):
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        self.create_rectangle(col*60, row*60, (col+1)*60, (row+1)*60, outline=color, width=3, tags="highlight")

    def clear_highlights(self):
        self.delete("highlight")