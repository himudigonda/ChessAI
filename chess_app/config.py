# chess_app/config.py

import os

class Config:
    BOARD_SIZE = 8
    NUM_CHANNELS = 17  # 12 for pieces, 5 for additional features
    INPUT_SIZE = 805  # 768 (board) + 7 (auxiliary) + 30 (history)
    HIDDEN_SIZE = 1024
    NUM_RESIDUAL_BLOCKS = 128  # Increased residual blocks for more complexity
    POLICY_OUTPUT_SIZE = 4672  # 64 squares * 73 possible moves
    VALUE_OUTPUT_SIZE = 1
    LEARNING_RATE = 1e-4
    BATCH_SIZE = 1024
    EPOCHS = 50
    NUM_GAMES = 1000
    ENGINE_PATH = "/opt/homebrew/bin/stockfish"  # Update this path as needed
    MOVE_DELAY = 1000  # in milliseconds

    SAVE_DIRECTORY = "./saved_games"
    GAMES_PER_FILE = 10
    FILES_PER_FOLDER = 10
    MAX_FOLDERS = 10

    LOG_DIR = "./logs"
    TENSORBOARD_LOG_DIR = "./tensorboard_logs"

    MODEL_PATH = "chess_model.pth"

    # TensorBoard parameters
    TENSORBOARD_COMMENT = "Chess_AI_Training"

    # Additional configurations can be added as needed