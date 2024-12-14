# chess_app/config.py

import os


class Config:
    """
    Configuration class for the Chess AI project.
    Contains all the configurable parameters.
    """

    # Model and Training Configuration
    MODEL_PATH = "chess_model.pth"  # Path to save/load the trained model
    ENGINE_PATH = "/opt/homebrew/bin/stockfish"  # Path to the Stockfish engine executable
    SAVE_DIRECTORY = "saved_games"  # Directory to save game PGNs
    LOG_DIR = "logs"  # Directory to save log files
    PLOTLY_LOG_DIR = "tensorboard_logs"  # Directory for TensorBoard logs
    GAMES_PER_FILE = 100  # Number of games per PGN file
    FILES_PER_FOLDER = 10  # Number of PGN files per folder
    MAX_FOLDERS = 10  # Maximum number of folders to save games
    INITIAL_ELO = 1800  # Starting Elo rating
    K_FACTOR = 32  # Elo K-factor for rating updates
    MOVE_DELAY = 10  # Delay in milliseconds between moves in automated games
    BOARD_SIZE = 8  # Chessboard size (8x8)
    NUM_CHANNELS = 17  # Number of channels for the board tensor
    NUM_RESIDUAL_BLOCKS = 256  # Number of residual blocks in the model
    TENSORBOARD_COMMENT = "Chess AI Training"  # Comment for TensorBoard logs
    DEPTH = 3  # Search depth for Stockfish engine
    BATCH_SIZE = 64  # Batch size for training
    LEARNING_RATE = 3e-4  # Learning rate for the optimizer
    NUM_GAMES_EVAL = 10  # Number of games for evaluation
    NUM_ITERATIONS = 5  # Number of training iterations
    NUM_GAMES_PER_ITERATION = 100  # Number of games per iteration
    EPOCHS = 10  # Number of epochs for training
