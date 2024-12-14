# chess_app/config.py

import os

class Config:
    # Model and Training Configuration
    MODEL_PATH = "chess_model.pth"
    ENGINE_PATH = "/path/to/stockfish"  # Update to your Stockfish path
    SAVE_DIRECTORY = "saved_games"
    LOG_DIR = "logs"
    PLOTLY_LOG_DIR = "tensorboard_logs"
    GAMES_PER_FILE = 100
    FILES_PER_FOLDER = 10
    MAX_FOLDERS = 10
    INITIAL_ELO = 1800
    K_FACTOR = 32  # Elo K-factor
    MOVE_DELAY = 10  # milliseconds
    BOARD_SIZE = 8
    NUM_CHANNELS = 17
    NUM_RESIDUAL_BLOCKS = 256
    TENSORBOARD_COMMENT = "Chess AI Training"
    DEPTH = 3
    BATCH_SIZE = 1024
    LEARNING_RATE = 3e-4
    NUM_GAMES_EVAL = 1  # Number of games for evaluation
    NUM_ITERATIONS = 1  # Number of training iterations
    NUM_GAMES_PER_ITERATION = 1  # Number of games per iteration
    EPOCHS = 1