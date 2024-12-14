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

    # UI Configurations
    LIGHT_THEME = {
        "background": "#F5F5F5",
        "foreground": "#000000",
        "button_bg": "#E0E0E0",
        "button_fg": "#000000",
        "highlight_color": "#0073e6",
        "chessboard_light": "#f0d9b5",
        "chessboard_dark": "#b58863",
        "status_success": "#00a651",
        "status_error": "#d9534f",
        "status_info": "#5bc0de",
    }

    DARK_THEME = {
        "background": "#2E2E2E",
        "foreground": "#FFFFFF",
        "button_bg": "#4D4D4D",
        "button_fg": "#FFFFFF",
        "highlight_color": "#1E90FF",
        "chessboard_light": "#CCCCCC",
        "chessboard_dark": "#333333",
        "status_success": "#28a745",
        "status_error": "#dc3545",
        "status_info": "#17a2b8",
    }

    CURRENT_THEME = LIGHT_THEME