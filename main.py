import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import chess
import os
import time
from threading import Timer

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
        self.last_move = None

        self.white_time = 300  # 5 minutes for white
        self.black_time = 300  # 5 minutes for black
        self.active_timer = None
        self.is_white_turn = True

        self.create_main_layout()
        self.create_chessboard()
        self.create_side_panel()
        self.update_timer()

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
        self.board_canvas.delete("square")

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * self.square_size, row * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color, tags="square")

        if self.last_move:
            from_square, to_square = self.last_move
            self.highlight_square(from_square, "#e6b800")
            self.highlight_square(to_square, "#e6b800")

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
            self.highlight_square(to_square, "#0073e6")

    def highlight_square(self, square, color):
        row, col = 7 - chess.square_rank(square), chess.square_file(square)
        x1, y1 = col * self.square_size, row * self.square_size
        x2, y2 = x1 + self.square_size, y1 + self.square_size
        self.board_canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags="highlight")

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
                self.last_move = (self.selected_square, dropped_square)
                self.board.push(move)
                self.update_move_list(move)

                # Switch timers
                self.is_white_turn = not self.is_white_turn
                self.update_timer()

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

        # Timer display
        self.timer_label = ttk.Label(self.side_panel_frame, text="Time: 05:00 - 05:00", font=("Arial", 14))
        self.timer_label.pack(pady=5)

        # Move list
        self.move_list_label = ttk.Label(self.side_panel_frame, text="Moves:", font=("Arial", 14))
        self.move_list_label.pack(pady=5)

        self.move_list = tk.Text(self.side_panel_frame, height=20, width=30, state=tk.DISABLED, bg="#333", fg="white")
        self.move_list.pack(pady=5)

        # Buttons
        self.undo_button = ttk.Button(self.side_panel_frame, text="Undo Move", command=self.undo_move)
        self.undo_button.pack(pady=5)

        self.save_button = ttk.Button(self.side_panel_frame, text="Save Game", command=self.save_game)
        self.save_button.pack(pady=5)

        self.load_button = ttk.Button(self.side_panel_frame, text="Load Game", command=self.load_game)
        self.load_button.pack(pady=5)

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

    def undo_move(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()
            self.last_move = None
            self.is_white_turn = not self.is_white_turn
            self.update_timer()
            self.draw_chessboard()
            self.draw_pieces()

    def save_game(self):
        with open("saved_game.txt", "w") as f:
            f.write(self.board.fen())
        showinfo("Game Saved", "The game has been saved successfully.")

    def load_game(self):
        try:
            with open("saved_game.txt", "r") as f:
                fen = f.read().strip()
                self.board.set_fen(fen)
            self.last_move = None
            self.is_white_turn = self.board.turn
            self.update_timer()
            self.draw_chessboard()
            self.draw_pieces()
            showinfo("Game Loaded", "The game has been loaded successfully.")
        except FileNotFoundError:
            showinfo("Error", "No saved game found.")

    def resign(self):
        showinfo("Game Over", "You resigned!")

    def offer_draw(self):
        showinfo("Draw Offered", "You offered a draw!")

    def update_timer(self):
        if self.active_timer:
            self.root.after_cancel(self.active_timer)

        self.update_timer_display()
        if self.is_white_turn:
            self.active_timer = self.root.after(1000, self.decrement_white_timer)
        else:
            self.active_timer = self.root.after(1000, self.decrement_black_timer)

    def update_timer_display(self):
        white_minutes, white_seconds = divmod(self.white_time, 60)
        black_minutes, black_seconds = divmod(self.black_time, 60)
        self.timer_label.config(
            text=f"Time: {white_minutes:02}:{white_seconds:02} - {black_minutes:02}:{black_seconds:02}"
        )

    def decrement_white_timer(self):
        if self.white_time > 0:
            self.white_time -= 1
            self.update_timer()
        else:
            showinfo("Game Over", "Black wins on time!")

    def decrement_black_timer(self):
        if self.black_time > 0:
            self.black_time -= 1
            self.update_timer()
        else:
            showinfo("Game Over", "White wins on time!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
