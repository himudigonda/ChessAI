import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import chess
import os

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess App")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")

        self.board = chess.Board()
        self.selected_square = None
        self.dragging_piece = None
        self.drag_start_coords = None
        self.legal_moves = []

        self.create_main_layout()
        self.create_chessboard()
        self.create_side_panel()

    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root, style="MainFrame.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.board_frame = ttk.Frame(self.main_frame, style="BoardFrame.TFrame")
        self.board_frame.grid(row=0, column=0, padx=20, pady=20)

        self.side_panel_frame = ttk.Frame(self.main_frame, style="SidePanelFrame.TFrame", width=300)
        self.side_panel_frame.grid(row=0, column=1, padx=20, pady=20, sticky="N")

    def create_chessboard(self):
        self.board_canvas = tk.Canvas(self.board_frame, width=640, height=640, bg="white", highlightthickness=0)
        self.board_canvas.pack()

        self.square_size = 80
        self.piece_images = {}
        self.load_piece_images()
        self.draw_chessboard()
        self.draw_pieces()

        self.board_canvas.bind("<Button-1>", self.on_click)
        self.board_canvas.bind("<B1-Motion>", self.on_drag)
        self.board_canvas.bind("<ButtonRelease-1>", self.on_drop)

    def load_piece_images(self):
        """Load piece images from the assets folder."""
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
            if os.path.exists(file_path):
                self.piece_images[piece] = tk.PhotoImage(file=file_path)
            else:
                print(f"Error: Missing file {file_path}")

    def draw_chessboard(self):
        colors = ["#f0d9b5", "#b58863"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * self.square_size, row * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def draw_pieces(self):
        self.board_canvas.delete("piece")
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = 7 - chess.square_rank(square), chess.square_file(square)
                x, y = col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2
                self.board_canvas.create_image(x, y, image=self.piece_images[piece.symbol()], tags=f"piece_{square}")

    def highlight_legal_moves(self):
        self.board_canvas.delete("highlight")
        for move in self.legal_moves:
            to_square = move.to_square
            row, col = 7 - chess.square_rank(to_square), chess.square_file(to_square)
            x1, y1 = col * self.square_size, row * self.square_size
            x2, y2 = x1 + self.square_size, y1 + self.square_size
            self.board_canvas.create_rectangle(x1, y1, x2, y2, outline="#0073e6", width=3, tags="highlight")

    def on_click(self, event):
        col = event.x // self.square_size
        row = event.y // self.square_size
        clicked_square = chess.square(col, 7 - row)

        piece = self.board.piece_at(clicked_square)
        if piece and piece.color == self.board.turn:
            self.selected_square = clicked_square
            self.legal_moves = [move for move in self.board.legal_moves if move.from_square == clicked_square]
            self.highlight_legal_moves()
            self.dragging_piece = self.piece_images[piece.symbol()]
            self.drag_start_coords = (event.x, event.y)
            # Highlight the source square
            self.board_canvas.itemconfig(f"piece_{clicked_square}", state="hidden")

    def on_drag(self, event):
        if self.dragging_piece:
            self.board_canvas.delete("drag")
            self.board_canvas.create_image(event.x, event.y, image=self.dragging_piece, tags="drag")

    def on_drop(self, event):
        if self.dragging_piece:
            col = event.x // self.square_size
            row = event.y // self.square_size
            dropped_square = chess.square(col, 7 - row)

            move = chess.Move(self.selected_square, dropped_square)
            if move in self.legal_moves:
                self.board.push(move)
                self.update_move_list(move)

            # Reset state
            self.selected_square = None
            self.dragging_piece = None
            self.drag_start_coords = None
            self.legal_moves = []

            self.board_canvas.delete("drag")
            self.board_canvas.delete("highlight")
            self.draw_chessboard()
            self.draw_pieces()

    def create_side_panel(self):
        # Game status label
        self.status_label = ttk.Label(self.side_panel_frame, text="White to move", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=10)

        # Move list
        self.move_list_label = ttk.Label(self.side_panel_frame, text="Moves:", font=("Arial", 14))
        self.move_list_label.pack(pady=5)

        self.move_list = tk.Text(self.side_panel_frame, height=25, width=30, state=tk.DISABLED, bg="#333", fg="white")
        self.move_list.pack(pady=5)

        # Buttons
        self.resign_button = ttk.Button(self.side_panel_frame, text="Resign", command=self.resign)
        self.resign_button.pack(pady=5)

        self.draw_button = ttk.Button(self.side_panel_frame, text="Offer Draw", command=self.offer_draw)
        self.draw_button.pack(pady=5)

    def update_move_list(self, move):
        self.move_list.config(state=tk.NORMAL)
        self.move_list.insert(tk.END, f"{move.uci()}\n")
        self.move_list.config(state=tk.DISABLED)

        turn = "White" if self.board.turn else "Black"
        self.status_label.config(text=f"{turn} to move")

    def resign(self):
        showinfo("Game Over", "You resigned!")

    def offer_draw(self):
        showinfo("Draw Offered", "You offered a draw!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
