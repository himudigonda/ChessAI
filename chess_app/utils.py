# chess_app/utils.py
import chess.engine
import chess.pgn
import pygame
import time
import os
from tkinter import messagebox


class AIPlayer:
    def __init__(self, engine_path="/opt/homebrew/bin/stockfish", depth=2):
        self.engine_path = engine_path
        self.depth = depth
        if not os.path.exists(engine_path):
            messagebox.showerror("Error", f"Stockfish engine not found at {engine_path}.")
            raise FileNotFoundError(f"Stockfish engine not found at {engine_path}.")
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def get_best_move(self, board):
        try:
            result = self.engine.play(board, chess.engine.Limit(depth=self.depth))
            return result.move
        except Exception as e:
            print(f"Error getting best move: {e}")
            return None

    def set_depth(self, depth):
        self.depth = depth

    def close(self):
        self.engine.quit()


class GameAnalyzer:
    def __init__(self, engine_path="/opt/homebrew/bin/stockfish"):
        self.engine_path = engine_path
        if not os.path.exists(engine_path):
            messagebox.showerror("Error", f"Stockfish engine not found at {engine_path}.")
            raise FileNotFoundError(f"Stockfish engine not found at {engine_path}.")
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def analyze_game(self, board):
        game = chess.pgn.Game.from_board(board)
        analysis = []
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
            try:
                result = self.engine.analyse(board, chess.engine.Limit(depth=15))
                evaluation = result["score"].relative.score(mate_score=10000)
                if evaluation is None:
                    evaluation = "MATE"
                analysis.append((move, evaluation))
            except Exception as e:
                print(f"Error during analysis: {e}")
                analysis.append((move, "Error"))
        return analysis

    def close(self):
        self.engine.quit()


class SaveLoad:
    @staticmethod
    def save_game(board, filename="saved_game.pgn"):
        game = chess.pgn.Game.from_board(board)
        with open(filename, "w") as f:
            f.write(str(game))

    @staticmethod
    def load_game(filename="saved_game.pgn"):
        with open(filename) as f:
            game = chess.pgn.read_game(f)
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
            return board


class SoundEffects:
    def __init__(self):
        pygame.mixer.init()
        assets_path = "./assets"
        self.move_sound = self.load_sound(f"{assets_path}/move.mp3")
        self.capture_sound = self.load_sound(f"{assets_path}/capture.mp3")

    def load_sound(self, filepath):
        if os.path.exists(filepath):
            return pygame.mixer.Sound(filepath)
        else:
            print(f"Sound file {filepath} not found.")
            return None

    def play_move(self):
        if self.move_sound:
            self.move_sound.play()

    def play_capture(self):
        if self.capture_sound:
            self.capture_sound.play()


class Timer:
    @staticmethod
    def format_time(white_time, black_time):
        white_minutes, white_seconds = divmod(white_time, 60)
        black_minutes, black_seconds = divmod(black_time, 60)
        return f"White: {white_minutes:02}:{white_seconds:02} - Black: {black_minutes:02}:{black_seconds:02}"


class Theme:
    def __init__(self, app):
        self.app = app
        self.current_theme = 'light'

    def toggle_theme(self):
        if self.current_theme == 'light':
            self.apply_dark_theme()
            self.current_theme = 'dark'
        else:
            self.apply_light_theme()
            self.current_theme = 'light'

    def apply_light_theme(self):
        self.app.root.configure(bg="#F5F5F7")
        self.app.side_panel_frame.configure(bg="#FFFFFF")
        self.app.status_bar.configure(bg="#F5F5F7", fg="#333333")
        self.app.timer_label.configure(bg="#FFFFFF", fg="#000000")
        self.app.status_label.configure(bg="#FFFFFF", fg="#000000")
        self.app.captured_label_white.configure(bg="#FFFFFF", fg="#000000")
        self.app.captured_label_black.configure(bg="#FFFFFF", fg="#000000")
        self.app.move_list.configure(bg="#F0F0F0", fg="#333333")
        # Update other widgets as needed

    def apply_dark_theme(self):
        self.app.root.configure(bg="#2E2E2E")
        self.app.side_panel_frame.configure(bg="#3C3C3C")
        self.app.status_bar.configure(bg="#2E2E2E", fg="#FFFFFF")
        self.app.timer_label.configure(bg="#3C3C3C", fg="#FFFFFF")
        self.app.status_label.configure(bg="#3C3C3C", fg="#FFFFFF")
        self.app.captured_label_white.configure(bg="#3C3C3C", fg="#FFFFFF")
        self.app.captured_label_black.configure(bg="#3C3C3C", fg="#FFFFFF")
        self.app.move_list.configure(bg="#4F4F4F", fg="#FFFFFF")
        # Update other widgets as needed