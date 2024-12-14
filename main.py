import chess
import chess.engine
import time
import tkinter as tk
from tkinter import Canvas, PhotoImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Evaluation Constants
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # King's value is handled separately.
}

PIECE_ICONS = {
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
    "k": "Black_king.png"
}

# Positional Evaluation Function
def evaluate_board(board):
    """Evaluate the current board position."""
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score

# Minimax Algorithm with Alpha-Beta Pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    """Perform the minimax algorithm with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)
    if maximizing_player:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Opponent Move Selection
def select_best_move(board, depth):
    """Select the best move for the AI."""
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, float('-inf'), float('inf'), not board.turn)
        board.pop()

        if board.turn == chess.WHITE:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move

    return best_move

# Chess UI Class
def create_probability_plot(probabilities, canvas):
    """Creates and embeds a probability graph in the UI."""
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(probabilities, color='blue')
    ax.set_title("Win Probability", fontsize=10)
    ax.set_xlabel("Moves", fontsize=8)
    ax.set_ylabel("White Win %", fontsize=8)
    ax.tick_params(axis='both', labelsize=8)
    fig.tight_layout()

    chart = FigureCanvasTkAgg(fig, master=canvas)
    chart_widget = chart.get_tk_widget()
    chart_widget.pack(side=tk.TOP, fill=tk.X, expand=False)

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BattleMind Chess Showdown")

        # Initialize board and variables
        self.board = chess.Board()
        self.depth = 3
        self.probabilities = [0.5]  # Start with equal probability for White
        self.piece_images = {}

        # Load piece images
        for key, value in PIECE_ICONS.items():
            self.piece_images[key] = PhotoImage(file=value)

        # Create UI components
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left section: Chessboard
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas = Canvas(self.board_frame, width=600, height=600, bg="brown")
        self.canvas.pack()
        self.update_board()

        # Right section: Graph and moves
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.graph_canvas = tk.Frame(self.right_frame, height=100)
        self.graph_canvas.pack(fill=tk.X, expand=False)
        create_probability_plot(self.probabilities, self.graph_canvas)

        self.moves_frame = tk.Frame(self.right_frame)
        self.moves_frame.pack(fill=tk.BOTH, expand=True)
        self.moves_listbox = tk.Listbox(self.moves_frame, font=("Courier", 14))
        self.moves_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Info and input
        self.info_label = tk.Label(root, text="Welcome to BattleMind Chess Showdown!", font=("Helvetica", 14))
        self.info_label.pack()

        self.move_entry = tk.Entry(root)
        self.move_entry.pack()

        self.move_button = tk.Button(root, text="Submit Move", command=self.handle_human_move)
        self.move_button.pack()

    def update_board(self):
        self.canvas.delete("all")
        square_size = 75
        for row in range(8):
            for col in range(8):
                x0, y0 = col * square_size, row * square_size
                x1, y1 = x0 + square_size, y0 + square_size
                color = "white" if (row + col) % 2 == 0 else "#D18B47"  # Brown and white board
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)

                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    self.canvas.create_image(x0 + square_size // 2, y0 + square_size // 2, image=self.piece_images[piece.symbol()])

    def update_probability_graph(self):
        for widget in self.graph_canvas.winfo_children():
            widget.destroy()
        create_probability_plot(self.probabilities, self.graph_canvas)

    def record_move(self, move):
        self.moves_listbox.insert(tk.END, move)

    def handle_human_move(self):
        move_text = self.move_entry.get()
        try:
            move = chess.Move.from_uci(move_text)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.probabilities.append(evaluate_board(self.board) / 39.0)  # Normalize score
                self.record_move(f"White: {move}")
                self.update_board()
                self.update_probability_graph()
                self.handle_ai_move()
            else:
                self.info_label.config(text="Illegal move! Try again.")
        except ValueError:
            self.info_label.config(text="Invalid move format. Use UCI (e.g., e2e4).")

    def handle_ai_move(self):
        self.info_label.config(text="AI is thinking...")
        start_time = time.time()
        ai_move = select_best_move(self.board, self.depth)
        end_time = time.time()
        self.board.push(ai_move)
        self.probabilities.append(evaluate_board(self.board) / 39.0)  # Normalize score
        self.record_move(f"Black: {ai_move}")
        self.update_board()
        self.update_probability_graph()
        self.info_label.config(text=f"AI moved: {ai_move}. Time: {end_time - start_time:.2f}s")

# Run the Chess App
def main():
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
