# chess_app/data.py

import random
import chess
import numpy as np
import torch

def board_to_tensor(board):
    """
    Converts a chess.Board object to a 17x8x8 tensor.
    12 channels for piece types, 4 for castling rights, and 1 for en passant.

    :param board: chess.Board object representing the current board state.
    :return: PyTorch tensor of shape (17, 8, 8).
    """
    piece_map = board.piece_map()
    tensor = np.zeros((17, 8, 8), dtype=np.float32)  # 17 channels

    piece_dict = {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
        'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
    }

    for square, piece in piece_map.items():
        piece_type = piece.symbol()
        if piece_type in piece_dict:
            plane = piece_dict[piece_type]
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            tensor[plane][row][col] = 1.0

    # Additional planes for castling rights and en passant
    tensor[12][0][0] = 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0
    tensor[13][0][7] = 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0
    tensor[14][7][0] = 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0
    tensor[15][7][7] = 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0

    if board.ep_square is not None:
        ep_row = 7 - chess.square_rank(board.ep_square)
        ep_col = chess.square_file(board.ep_square)
        tensor[16][ep_row][ep_col] = 1.0

    return torch.from_numpy(tensor).float()

def move_to_index(move):
    """
    Encodes a move into a unique index.
    Simplistic encoding: from_square * 73 + to_square

    :param move: chess.Move object to encode.
    :return: Integer index representing the move.
    """
    return move.from_square * 73 + move.to_square

def index_to_move(index, board):
    """
    Decodes an index back to a chess.Move object.
    This is a simplified version and may need adjustments for promotions.

    :param index: Integer index to decode.
    :param board: Current chess.Board object.
    :return: chess.Move object corresponding to the index.
    """
    from_square = index // 73
    to_square = index % 73
    possible_moves = [move for move in board.legal_moves if move.from_square == from_square]
    for move in possible_moves:
        if move.to_square == to_square:
            return move
    # Handle promotions if not found
    for move in board.legal_moves:
        if move.from_square == from_square and move.to_square == to_square:
            return move
    # If still not found, return a random legal move
    return random.choice(list(board.legal_moves))

class ChessDatasetTrain(torch.utils.data.Dataset):
    """
    PyTorch Dataset for training the ChessNet model.
    Each data point consists of a board tensor, move index, outcome, and move quality.
    """

    def __init__(self, data):
        """
        Initializes the dataset with training data.

        :param data: List of tuples (board_tensor, move_index, outcome, move_quality)
        """
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        board, move, outcome, move_quality = self.data[idx]
        # One-hot encode move_quality
        move_quality_mapping = {
            "Great Step": 4,
            "Good Step": 3,
            "Average Step": 2,
            "Bad Step": 1,
            "Blunder": 0
        }
        move_quality_encoded = move_quality_mapping.get(move_quality, 2)  # Default to "Average Step"
        return torch.tensor(board, dtype=torch.float32), torch.tensor(move, dtype=torch.long), torch.tensor(outcome, dtype=torch.float32), torch.tensor(move_quality_encoded, dtype=torch.long)