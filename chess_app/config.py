# chess_app/config.py

class Config:
    BOARD_SIZE = 8
    NUM_CHANNELS = 17  # 12 for pieces, 5 for additional features
    INPUT_SIZE = 805  # 768 (board) + 7 (auxiliary) + 30 (history)
    HIDDEN_SIZE = 1024
    NUM_RESIDUAL_BLOCKS = 64
    POLICY_OUTPUT_SIZE = 4672  # 64 squares * 73 possible moves
    VALUE_OUTPUT_SIZE = 1
    LEARNING_RATE = 1e-4
    BATCH_SIZE = 1024
    EPOCHS = 50
    NUM_GAMES = 1000
    ENGINE_PATH = "/opt/homebrew/bin/stockfish"  # Update this path as needed
    MOVE_DELAY = 1  # in milliseconds