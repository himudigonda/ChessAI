import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def evaluate_board(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
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
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def select_best_move(board, depth):
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, float('-inf'), float('inf'), not board.turn)
        board.pop()

        if board.turn == chess.WHITE and eval > best_value:
            best_value = eval
            best_move = move
        elif board.turn == chess.BLACK and eval < best_value:
            best_value = eval
            best_move = move

    return best_move
