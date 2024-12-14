import chess
from core.ai_logic import select_best_move, evaluate_board

class GameManager:
    def __init__(self):
        self.board = chess.Board()
        self.probabilities = [0.5]
        self.move_history = []
        self.ai_think_percentage = 0

    def make_ai_move(self):
        best_move = select_best_move(self.board, depth=3)
        self.board.push(best_move)
        self.move_history.append(best_move.uci())
        self.probabilities.append(evaluate_board(self.board) / 39.0)

    def reset(self):
        self.board.reset()
        self.probabilities = [0.5]
        self.move_history = []
