# chess_app/ui/chessboard_widget.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QRect
import chess
import os


class ChessBoardWidget(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.board = app_instance.board
        self.selected_square = None
        self.dragging = False
        self.drag_piece = None
        self.drag_position = None

        # Load piece images
        self.piece_images = {}
        self.load_piece_images()

    def load_piece_images(self):
        pieces = [
            "White_pawn",
            "White_knight",
            "White_bishop",
            "White_rook",
            "White_queen",
            "White_king",
            "Black_pawn",
            "Black_knight",
            "Black_bishop",
            "Black_rook",
            "Black_queen",
            "Black_king",
        ]
        assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
        for piece in pieces:
            image_path = os.path.join(assets_path, f"{piece}.png")
            if os.path.exists(image_path):
                print(">>", image_path)
                self.piece_images[piece] = QPixmap(image_path)
            else:
                print("<<", image_path)
                self.piece_images[piece] = None  # Placeholder or handle missing images
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        square_size = int(min(rect.width(), rect.height()) / 8)  # Convert to int

        # Draw squares
        colors = [QColor("#EEEED2"), QColor("#769656")]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                painter.fillRect(
                    int(col * square_size),
                    int(row * square_size),
                    square_size,
                    square_size,
                    color,
                )

        # Highlight last move
        if self.app.last_move:
            from_square, to_square = self.app.last_move
            self.highlight_square(painter, from_square, QColor("#E6B800"), square_size)
            self.highlight_square(painter, to_square, QColor("#E6B800"), square_size)

        # Draw pieces
        for square, piece in self.board.piece_map().items():
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            x = int(col * square_size)
            y = int(row * square_size)
            piece_key = piece.symbol()
            print(f"Drawing piece: {piece_key} at ({row}, {col})")

            if piece_key:
                piece_key = piece_key.lower() if piece.color == chess.BLACK else piece_key.upper()
                piece_name = {
                    "p": "pawn",
                    "r": "rook",
                    "n": "knight",
                    "b": "bishop",
                    "q": "queen",
                    "k": "king",
                }[piece_key.lower()]
                color = "White" if piece.color == chess.WHITE else "Black"
                image_key = f"{color}_{piece_name}"  # e.g., 'White_pawn', 'Black_king'
                print(f"Image key: {image_key}")
                if image_key in self.piece_images:
                    if self.piece_images[image_key]:
                        scaled_pixmap = self.piece_images[image_key].scaled(
                            square_size, square_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                        painter.drawPixmap(
                            QRect(x, y, square_size, square_size), scaled_pixmap
                        )
                    else:
                        print(f"Image for {image_key} is None")
                else:
                    print(f"Image key {image_key} not found in piece_images")

        # Draw dragging piece
        if self.dragging and self.drag_piece:
            piece_image = self.piece_images.get(self.drag_piece)
            if piece_image:
                scaled_pixmap = piece_image.scaled(
                    square_size, square_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                painter.drawPixmap(
                    int(self.drag_position.x() - square_size / 2),
                    int(self.drag_position.y() - square_size / 2),
                    square_size,
                    square_size,
                    scaled_pixmap,
                )

    def highlight_square(self, painter, square, color, square_size):
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(color)
        painter.drawRect(col * square_size, row * square_size, square_size, square_size)

    def mousePressEvent(self, event):
        if self.app.board.is_game_over():
            return

        rect = self.rect()
        square_size = min(rect.width(), rect.height()) / 8
        col = int(event.x() / square_size)
        row = 7 - int(event.y() / square_size)
        square = chess.square(col, row)
        piece = self.board.piece_at(square)

        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self.dragging = True
            self.drag_piece = (
                piece.symbol().lower()
                if piece.color == chess.BLACK
                else piece.symbol().upper()
            )
            self.drag_position = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.drag_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            rect = self.rect()
            square_size = min(rect.width(), rect.height()) / 8
            col = int(event.x() / square_size)
            row = 7 - int(event.y() / square_size)
            to_square = chess.square(col, row)
            move = chess.Move(self.selected_square, to_square)

            if move in self.app.board.legal_moves:
                self.app.handle_move(move)

            self.dragging = False
            self.drag_piece = None
            self.selected_square = None
            self.update()