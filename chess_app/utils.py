# chess_app/utils.py

import torch
import chess.engine
import chess.pgn
from chess_app.model import ChessNet, load_model, save_model
from chess_app.data import board_to_tensor, move_to_index, index_to_move
import random
import os
import threading
from tqdm import tqdm  # For progress bars
import json
import pygame
import time
import tkinter as tk
from tkinter import messagebox

def get_device():
    """
    Selects the best available device (CUDA or CPU).
    """
    if torch.cuda.is_available():
        print("Using CUDA device (NVIDIA GPU)")
        return torch.device("cuda")
    else:
        print("Using CPU device")
        return torch.device("cpu")


class AIPlayer:
    def __init__(self, model_path="chess_model.pth", device=None, side=chess.WHITE):
        self.device = device if device else get_device()
        self.model = ChessNet().to(self.device)
        self.model_path = model_path
        self.side = side
        if os.path.exists(model_path):
            load_model(self.model, model_path, self.device)
            print("Loaded trained model.")
        else:
            print("Trained model not found. Using Stockfish as fallback.")
            self.model = None
            self.engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")  # Update path if necessary

    def get_best_move(self, board):
        if self.model and board.turn == self.side:
            # Ensure the model is in evaluation mode
            self.model.eval()
            board_tensor = board_to_tensor(board).to(self.device)
            with torch.no_grad():
                policy, value = self.model(board_tensor.unsqueeze(0))  # Add batch dimension
            move_probs = torch.exp(policy).cpu().numpy()[0]
            top_move_indices = move_probs.argsort()[-10:][::-1]  # Top 10 moves
            for move_index in top_move_indices:
                move = index_to_move(move_index, board)
                if move in board.legal_moves:
                    return move
            # Fallback to random move if no top move is legal
            return random.choice(list(board.legal_moves))
        elif hasattr(self, 'engine') and self.engine:
            # Use Stockfish if AI model is not available or it's not AI's turn
            result = self.engine.play(board, chess.engine.Limit(time=0.1))
            return result.move
        else:
            # Fallback to random move
            return random.choice(list(board.legal_moves))

    def close(self):
        if hasattr(self, 'engine') and self.engine:
            self.engine.quit()


class GameAnalyzer:
    def __init__(self, engine_path, depth=3):
        self.engine_path = engine_path
        self.depth = depth
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
    
    def analyze_game(self, board):
        """
        Analyzes the game by iterating through all moves and collecting evaluations.
        Returns a list of tuples: (move, evaluation)
        """
        analysis = []
        temp_board = chess.Board()
        for move in board.move_stack:
            temp_board.push(move)
            try:
                info = self.engine.analyse(temp_board, chess.engine.Limit(depth=self.depth))
                score = info["score"].white()
                if score.is_mate():
                    eval_score = 100000 if score.mate() > 0 else -100000
                else:
                    eval_score = score.score(mate_score=100000)
                analysis.append((move, eval_score))
            except Exception as e:
                print(f"Error analyzing move {move}: {e}")
                analysis.append((move, 0))  # Neutral evaluation in case of error
        return analysis
    
    def close(self):
        self.engine.quit()


class SaveLoad:
    @staticmethod
    def save_game(board, filename):
        """
        Saves the current game to a PGN file.
        """
        game = chess.pgn.Game.from_board(board)
        with open(filename, 'w') as f:
            f.write(str(game))
    
    @staticmethod
    def load_game(filename):
        """
        Loads a game from a PGN file and returns a chess.Board object.
        """
        with open(filename, 'r') as f:
            game = chess.pgn.read_game(f)
        if game is None:
            raise ValueError("No game found in the PGN file.")
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
        return board


class SoundEffects:
    def __init__(self):
        pygame.mixer.init()
        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.mp3")
            self.capture_sound = pygame.mixer.Sound("assets/sounds/capture.mp3")
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


class Theme:
    def __init__(self, app):
        self.app = app
        self.current_theme = "light"
    
    def apply_light_theme(self):
        self.app.root.configure(bg="#F5F5F7")
        self.app.side_panel_frame.configure(bg="#FFFFFF")
        self.app.status_bar.configure(bg="#F5F5F7", fg="#333333")
        self.app.move_list.configure(bg="#F0F0F0", fg="#333333")
        self.app.chess_board.configure(bg="#FFFFFF")
        # Update other widgets' backgrounds and foregrounds as needed
    
    def apply_dark_theme(self):
        self.app.root.configure(bg="#2E2E2E")
        self.app.side_panel_frame.configure(bg="#3C3F41")
        self.app.status_bar.configure(bg="#2E2E2E", fg="#FFFFFF")
        self.app.move_list.configure(bg="#4D4D4D", fg="#FFFFFF")
        self.app.chess_board.configure(bg="#000000")
        # Update other widgets' backgrounds and foregrounds as needed
    
    def toggle_theme(self):
        if self.current_theme == "light":
            self.apply_dark_theme()
            self.current_theme = "dark"
        else:
            self.apply_light_theme()
            self.current_theme = "light"


class Timer:
    @staticmethod
    def format_time(white_time, black_time):
        white_minutes = white_time // 60
        white_seconds = white_time % 60
        black_minutes = black_time // 60
        black_seconds = black_time % 60
        return f"White: {white_minutes:02}:{white_seconds:02} - Black: {black_minutes:02}:{black_seconds:02}"