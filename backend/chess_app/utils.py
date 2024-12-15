# chess_app/utils.py

from chess_app.config import Config
from chess_app.data import board_to_tensor, move_to_index, index_to_move
from chess_app.model import ChessNet, load_model, save_model
from sklearn.linear_model import LinearRegression
from tkinter import messagebox
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import chess.engine
import chess.pgn
import json
import logging
import numpy as np
import os
import pygame
import random
import threading
import time
import torch
import torch.nn as nn
import torch.optim as optim


def get_device():
    if torch.cuda.is_available():
        print("Using CUDA device (NVIDIA GPU)")
        return torch.device("cuda")
    else:
        print("Using CPU device")
        return torch.device("cpu")


class AIPlayer:
    def __init__(
        self,
        model_path="chess_model.pth",
        device=None,
        side=chess.WHITE,
        engine_path=Config.ENGINE_PATH,
    ):
        self.device = device if device else get_device()
        self.model = ChessNet().to(self.device)
        self.model_path = model_path
        self.side = side
        self.engine_path = engine_path

        if model_path and os.path.exists(model_path):
            load_model(self.model, model_path, self.device)
            print("Loaded trained model.")
            self.engine = None
        else:
            print("Trained model not found. Using Stockfish as fallback.")
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

        self.difficulty_level = 2

    def set_difficulty(self, level):
        self.difficulty_level = level
        if self.engine:
            self.engine.configure({"Skill Level": level})

    def get_best_move(self, board):
        if self.model and (not self.engine) and board.turn == self.side:
            self.model.eval()
            board_tensor = board_to_tensor(board).to(self.device)
            with torch.no_grad():
                policy, _, _ = self.model(board_tensor.unsqueeze(0))
            move_probs = torch.exp(policy).cpu().numpy()[0]
            top_move_indices = move_probs.argsort()[-10:][::-1]
            for move_index in top_move_indices:
                move = index_to_move(move_index, board)
                if move in board.legal_moves:
                    return move
            return random.choice(list(board.legal_moves))
        elif self.engine and board.turn == self.side:
            # Opponent is Stockfish
            result = self.engine.play(
                board, chess.engine.Limit(depth=self.difficulty_level)
            )
            return result.move
        elif self.engine and board.turn != self.side:
            # Opponent is Stockfish
            result = self.engine.play(
                board, chess.engine.Limit(depth=self.difficulty_level)
            )
            return result.move
        else:
            # Fallback if something goes wrong
            return random.choice(list(board.legal_moves))

    def close(self):
        if self.engine:
            self.engine.quit()


class GameAnalyzer:
    def __init__(self, engine_path, depth=3):
        self.engine_path = engine_path
        self.depth = depth
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

    def analyze_game(self, board):
        analysis = []
        temp_board = chess.Board()
        for move in board.move_stack:
            temp_board.push(move)
            try:
                info = self.engine.analyse(
                    temp_board, chess.engine.Limit(depth=self.depth)
                )
                score = info["score"].white()
                if score.is_mate():
                    eval_score = 100000 if score.mate() > 0 else -100000
                else:
                    eval_score = score.score(mate_score=100000)
                analysis.append((move, eval_score))
            except Exception as e:
                print(f"Error analyzing move {move}: {e}")
                analysis.append((move, 0))
        return analysis

    def close(self):
        self.engine.quit()


class SaveLoad:
    @staticmethod
    def save_game(board, filename):
        game = chess.pgn.Game.from_board(board)
        with open(filename, "w") as f:
            exporter = chess.pgn.FileExporter(f)
            game.accept(exporter)

    @staticmethod
    def load_game(filename):
        with open(filename, "r") as f:
            game = chess.pgn.read_game(f)
        if game is None:
            raise ValueError("No game found in the PGN file.")
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
        return board


class GameSaver:
    def __init__(self):
        self.save_dir = Config.SAVE_DIRECTORY
        self.games_per_file = Config.GAMES_PER_FILE
        self.files_per_folder = Config.FILES_PER_FOLDER
        self.max_folders = Config.MAX_FOLDERS
        self.current_folder = 1
        self.current_file = 1
        self.games_in_current_file = 0
        self.initialize_directories()

    def initialize_directories(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        for folder_num in range(1, self.max_folders + 1):
            folder_path = os.path.join(self.save_dir, f"batch_{folder_num}")
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        for folder_num in range(1, self.max_folders + 1):
            folder_path = os.path.join(self.save_dir, f"batch_{folder_num}")
            for file_num in range(1, self.files_per_folder + 1):
                file_path = os.path.join(folder_path, f"games_{file_num}.pgn")
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        games = []
                        while True:
                            game = chess.pgn.read_game(f)
                            if game is None:
                                break
                            games.append(game)
                        if len(games) < self.games_per_file:
                            self.current_folder = folder_num
                            self.current_file = file_num
                            self.games_in_current_file = len(games)
                            return
                else:
                    self.current_folder = folder_num
                    self.current_file = file_num
                    self.games_in_current_file = 0
                    return

        self.current_folder = 1
        self.current_file = 1
        self.games_in_current_file = 0

    def save_game(self, board):
        folder_path = os.path.join(self.save_dir, f"batch_{self.current_folder}")
        file_path = os.path.join(folder_path, f"games_{self.current_file}.pgn")

        with open(file_path, "a") as f:
            game = chess.pgn.Game.from_board(board)
            exporter = chess.pgn.FileExporter(f)
            game.accept(exporter)

        self.games_in_current_file += 1
        if self.games_in_current_file >= self.games_per_file:
            self.games_in_current_file = 0
            self.current_file += 1
            if self.current_file > self.files_per_folder:
                self.current_file = 1
                self.current_folder += 1
                if self.current_folder > self.max_folders:
                    self.current_folder = 1


class Logger:
    def __init__(self):
        self.logger = logging.getLogger("ChessAI")
        self.logger.setLevel(logging.DEBUG)
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(os.path.join(Config.LOG_DIR, "chess_ai.log"))
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        f_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def get_logger(self):
        return self.logger


class PlotlyDashApp(threading.Thread):
    def __init__(self, logger, config=Config):
        super().__init__()
        self.logger = logger
        self.config = config
        self.app = None
        self.figure = None
        self.x_data = []
        self.y_data = []
        self.elo_data = []
        self.daemon = True

    def run(self):
        import dash
        from dash import html, dcc
        import plotly.graph_objs as go

        self.app = dash.Dash(__name__)
        self.app.layout = html.Div(
            [
                html.H1("Chess AI Training Progress"),
                dcc.Graph(id="live-update-graph"),
                dcc.Interval(id="interval-component", interval=5 * 1000, n_intervals=0),
            ]
        )

        @self.app.callback(
            dash.dependencies.Output("live-update-graph", "figure"),
            [dash.dependencies.Input("interval-component", "n_intervals")],
        )
        def update_graph_live(n):
            log_file = os.path.join(self.config.LOG_DIR, "chess_ai_training.json")
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    data = json.load(f)
                self.x_data = [entry["epoch"] for entry in data]
                self.y_data = [entry["loss"] for entry in data]
                self.elo_data = [entry["elo"] for entry in data]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=self.x_data, y=self.y_data, mode="lines+markers", name="Loss"
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=self.x_data,
                    y=self.elo_data,
                    mode="lines+markers",
                    name="Elo Rating",
                    yaxis="y2",
                )
            )
            fig.update_layout(
                title="Training Progress",
                xaxis_title="Epoch",
                yaxis_title="Loss",
                yaxis2=dict(title="Elo Rating", overlaying="y", side="right"),
            )
            return fig

        self.app.run_server()


class TensorBoardLogger:
    def __init__(self):
        self.writer = SummaryWriter(
            log_dir=Config.PLOTLY_LOG_DIR, comment=Config.TENSORBOARD_COMMENT
        )

    def log_metrics(self, metrics, epoch):
        for key, value in metrics.items():
            self.writer.add_scalar(key, value, epoch)

    def close(self):
        self.writer.close()


class EloRating:
    def __init__(self, initial_elo=Config.INITIAL_ELO, k_factor=Config.K_FACTOR):
        self.rating = initial_elo
        self.k = k_factor

    def update(self, opponent_rating, score):
        expected_score = 1 / (1 + 10 ** ((opponent_rating - self.rating) / 400))
        self.rating += self.k * (score - expected_score)
        return self.rating


class SoundEffects:
    def __init__(self):
        pygame.mixer.init()
        assets_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
        move_sound_path = os.path.join(assets_path, "move.mp3")
        capture_sound_path = os.path.join(assets_path, "capture.mp3")
        try:
            self.move_sound = (
                pygame.mixer.Sound(move_sound_path)
                if os.path.exists(move_sound_path)
                else None
            )
            self.capture_sound = (
                pygame.mixer.Sound(capture_sound_path)
                if os.path.exists(capture_sound_path)
                else None
            )
        except pygame.error as e:
            print(f"Error loading sound files: {e}")
            self.move_sound = None
            self.capture_sound = None

    def play_move(self):
        if self.move_sound:
            self.move_sound.play()

    def play_capture(self):
        if self.capture_sound:
            self.capture_sound.play()


class Timer:
    @staticmethod
    def format_time(white_time, black_time):
        white_minutes = white_time // 60
        white_seconds = white_time % 60
        black_minutes = black_time // 60
        black_seconds = black_time % 60
        return f"White: {white_minutes:02}:{white_seconds:02} - Black: {black_minutes:02}:{black_seconds:02}"
