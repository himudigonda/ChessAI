# chess_app/ui/ui_board.py

import tkinter as tk
from PIL import Image, ImageTk
import chess
from chess_app.data import board_to_tensor

class ChessBoard(tk.Canvas):
    """
    ChessBoard is a Tkinter Canvas that displays the chessboard and pieces.
    It handles user interactions for moving pieces via drag-and-drop.
    """

    def __init__(self, parent, app, *args, **kwargs):
        """
        Initializes the ChessBoard UI component.

        :param parent: The parent Tkinter widget.
        :param app: The main ChessApp instance.
        :param args: Additional positional arguments for Tkinter Canvas.
        :param kwargs: Additional keyword arguments for Tkinter Canvas.
        """
        super().__init__(parent, bg="#FFFFFF", highlightthickness=0, *args, **kwargs)
        self.app = app
        self.board = app.board
        self.images = {}
        self.load_images()
        self.bind("<Configure>", self.on_resize)
        self.bind_events()
        self.dragging_piece_id = None
        self.drag_image = None
        self.draw_chessboard()
        self.draw_pieces()

    def load_images(self):
        """
        Loads and resizes chess piece images from the assets folder.
        """
        # Load and resize images based on initial square size
        self.piece_size = 60  # Initial size; will adjust on resize
        pieces = ['White_pawn', 'White_knight', 'White_bishop', 'White_rook', 'White_queen', 'White_king',
                  'Black_pawn', 'Black_knight', 'Black_bishop', 'Black_rook', 'Black_queen', 'Black_king']

        for piece in pieces:
            try:
                image = Image.open(f"assets/{piece}.png")
                image = image.resize((int(self.piece_size), int(self.piece_size)), Image.ANTIALIAS)
                self.images[piece] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading image for {piece}: {e}")
                self.images[piece] = None  # Placeholder

    def on_resize(self, event):
        """
        Handles the resize event by redrawing the chessboard and pieces.

        :param event: The Tkinter event object.
        """
        self.delete("all")  # Clear the canvas
        self.width = event.width
        self.height = event.height
        self.square_size = min(self.width, self.height) / 8
        self.draw_chessboard()
        self.draw_pieces()

    def draw_chessboard(self):
        """
        Draws the chessboard squares on the canvas.
        Highlights the last move if available.
        """
        # Default light theme colors
        colors = ["#EEEED2", "#769656"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        if self.app.last_move:
            from_square, to_square = self.app.last_move
            self.highlight_square(from_square, "#E6B800")
            self.highlight_square(to_square, "#E6B800")

    def draw_pieces(self):
        """
        Draws the chess pieces on the chessboard based on the current board state.
        """
        for square, piece in self.board.piece_map().items():
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            x = (col + 0.5) * self.square_size
            y = (row + 0.5) * self.square_size
            piece_key = piece.symbol()
            piece_key = piece_key.upper() if piece.color else piece_key.lower()
            image = self.images.get(piece_key)
            if image:
                piece_id = self.create_image(
                    x, y, image=image, tags=("piece", f"piece_{square}"), anchor=tk.CENTER
                )

    def bind_events(self):
        """
        Binds mouse events for piece interactions (drag-and-drop).
        """
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)

    def on_click(self, event):
        """
        Handles the click event on a piece to start dragging.

        :param event: The Tkinter event object.
        """
        col = int(event.x // self.square_size)
        row = int(event.y // self.square_size)
        square = chess.square(col, 7 - row)
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.app.selected_square = square
            # Highlight the selected square
            self.highlight_square(square, "#ADD8E6")  # Light blue
            # Get the canvas item id for the piece
            piece_tag = f"piece_{square}"
            items = self.find_withtag(piece_tag)
            if items:
                self.dragging_piece_id = items[0]
                # Lift the piece to the top
                self.lift(self.dragging_piece_id)
                # Create a drag image
                self.drag_image = self.create_image(event.x, event.y, image=self.itemcget(self.dragging_piece_id, "image"), anchor=tk.CENTER)

    def on_drag(self, event):
        """
        Handles the drag motion by moving the drag image with the cursor.

        :param event: The Tkinter event object.
        """
        if self.dragging_piece_id and self.drag_image:
            # Move the drag image with the cursor
            self.coords(self.drag_image, event.x, event.y)

    def on_drop(self, event):
        """
        Handles the drop event by determining the target square and executing the move.

        :param event: The Tkinter event object.
        """
        if self.dragging_piece_id and self.drag_image:
            # Determine the square where the piece is dropped
            col = int(event.x // self.square_size)
            row = int(event.y // self.square_size)
            to_square = chess.square(col, 7 - row)
            from_square = self.app.selected_square
            move = chess.Move(from_square, to_square)
            if move in self.board.legal_moves:
                self.app.handle_move(move)
            # Remove the drag image
            self.delete(self.drag_image)
            self.drag_image = None
            self.dragging_piece_id = None
            self.app.selected_square = None
            # Remove highlight
            self.delete("highlight")

    def highlight_square(self, square, color):
        """
        Highlights a specific square with the given color.

        :param square: The square to highlight.
        :param color: Color code for highlighting.
        """
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        x1 = col * self.square_size
        y1 = row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        self.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags="highlight")

    def clear_highlights(self):
        """
        Clears all highlight overlays on the chessboard.
        """
        self.delete("highlight")