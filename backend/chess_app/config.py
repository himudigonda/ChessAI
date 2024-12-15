# chess_app/config.py

import os


class Config:
    MODEL_PATH = "chess_model.pth"  # Path to save/load the trained model
    ENGINE_PATH = "/opt/homebrew/bin/stockfish"  # Make sure Stockfish is here
    SAVE_DIRECTORY = "saved_games"
    LOG_DIR = "logs"
    PLOTLY_LOG_DIR = "tensorboard_logs"
    GAMES_PER_FILE = 100
    FILES_PER_FOLDER = 10
    MAX_FOLDERS = 10
    INITIAL_ELO = 1800
    K_FACTOR = 32
    MOVE_DELAY = 10
    BOARD_SIZE = 8
    NUM_CHANNELS = 17
    NUM_RESIDUAL_BLOCKS = 256
    TENSORBOARD_COMMENT = "Chess AI Training"
    DEPTH = 3
    BATCH_SIZE = 64
    LEARNING_RATE = 3e-4
    NUM_GAMES_EVAL = 10
    NUM_ITERATIONS = 5
    NUM_GAMES_PER_ITERATION = 100
    EPOCHS = 10

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
