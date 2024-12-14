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
        self.legal_moves = []

        # Load piece images
        self.piece_images = {}
        self.load_piece_images()

    def load_piece_images(self):
        """
        Load chess piece images from the assets directory.
        """
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

        assets_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "assets")
        )

        for piece, filename in piece_filenames.items():
            image_path = os.path.join(assets_path, filename)
            print(f"Attempting to load piece image: {image_path}")  # Debug log
            if os.path.exists(image_path):
                self.piece_images[piece] = QPixmap(image_path)
                if self.piece_images[piece].isNull():
                    print(f"Error: Failed to load {image_path}, QPixmap is null!")
            else:
                print(f"Error: Missing asset file {image_path}")
                self.piece_images[piece] = None  # Placeholder

    def paintEvent(self, event):
        """
        Handle painting of the chessboard and pieces.
        """
        painter = QPainter(self)
        rect = self.rect()
        square_size = min(rect.width(), rect.height()) // 8
        
        # Draw squares
        colors = [QColor("#EEEED2"), QColor("#769656")]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                painter.fillRect(
                    col * square_size,
                    row * square_size,
                    square_size,
                    square_size,
                    color,
                )

        # Draw pieces
        for square, piece in self.board.piece_map().items():
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            x, y = col * square_size, row * square_size

            # Use piece symbol directly for the key
            piece_key = piece.symbol()  # E.g., "P" for White pawn, "k" for Black king
            piece_image = self.piece_images.get(piece_key)

            print(f"Drawing piece: {piece_key} at square ({row}, {col})")

            if piece_image:
                painter.drawPixmap(
                    QRect(x, y, square_size, square_size),
                    piece_image.scaled(
                        square_size,
                        square_size,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    ),
                )
            else:
                print(f"Error: No image loaded for piece {piece_key}")

    def highlight_square(self, painter, square, color, square_size):
        """
        Highlight a specific square.
        """
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(color)
        painter.drawRect(col * square_size, row * square_size, square_size, square_size)

    def mousePressEvent(self, event):
        if self.app.board.is_game_over():
            return

        rect = self.rect()
        square_size = rect.width() // 8
        col = event.x() // square_size
        row = 7 - event.y() // square_size
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
            self.legal_moves = [
                move for move in self.board.legal_moves if move.from_square == square
            ]
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.drag_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            rect = self.rect()
            square_size = rect.width() // 8
            col = event.x() // square_size
            row = 7 - event.y() // square_size
            to_square = chess.square(col, row)
            move = chess.Move(self.selected_square, to_square)

            if move in self.board.legal_moves:
                self.app.handle_move(move)

            self.dragging = False
            self.drag_piece = None
            self.selected_square = None
            self.legal_moves = []
            self.update()
