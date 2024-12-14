# chess_app/utils.py
from stockfish import Stockfish
import tkinter as tk
from tkinter import messagebox
import os
# chess_app/utils.py
import os
from playsound import playsound

class SoundEffects:
    @staticmethod
    def get_asset_path(filename):
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to project root and then into assets
        return os.path.join(os.path.dirname(current_dir), "assets", filename)

    @staticmethod
    def play_move():
        try:
            sound_path = SoundEffects.get_asset_path("move.mp3")
            playsound(sound_path, block=False)
        except Exception as e:
            print(f"Error playing move sound: {e}")
            
    @staticmethod
    def play_capture():
        try:
            sound_path = SoundEffects.get_asset_path("capture.mp3")
            playsound(sound_path, block=False)
        except Exception as e:
            print(f"Error playing capture sound: {e}")
class Timer:
    def __init__(self, initial_time=300, increment=2):
        self.white_time = initial_time
        self.black_time = initial_time
        self.increment = increment
        self.is_white_turn = True
    def format_time(white_time, black_time):
        white_minutes, white_seconds = divmod(white_time, 60)
        black_minutes, black_seconds = divmod(black_time, 60)
        return f"Time: {white_minutes:02}:{white_seconds:02} - {black_minutes:02}:{black_seconds:02}"

    def switch_turn(self):
        if self.is_white_turn:
            self.white_time += self.increment
        else:
            self.black_time += self.increment
        self.is_white_turn = not self.is_white_turn
    def set_timer_mode(self, mode):
        if mode == "bullet":
            self.timer = Timer(initial_time=60, increment=0)
        elif mode == "blitz":
            self.timer = Timer(initial_time=180, increment=2)
        elif mode == "rapid":
            self.timer = Timer(initial_time=600, increment=5)
        self.update_timer()
class SaveLoad:
    @staticmethod
    def save_game(board, filename="saved_game.txt"):
        with open(filename, "w") as f:
            f.write(board.fen())

    @staticmethod
    def load_game(filename="saved_game.txt"):
        if not os.path.exists(filename):
            raise FileNotFoundError("No saved game found.")
        with open(filename, "r") as f:
            fen = f.read().strip()
            return fen

class Theme:
    @staticmethod
    def toggle_theme(app):
        if app.root.cget("bg") == "#F5F5F7":
            app.root.configure(bg="#333333")
            app.side_panel_frame.configure(bg="#444444")
            app.board_frame.configure(bg="#444444")
            app.status_bar.configure(bg="#444444", fg="#FFFFFF")
            app.status_label.configure(bg="#444444", fg="#FFFFFF")
            app.timer_label.configure(bg="#444444", fg="#FFFFFF")
            app.captured_label_white.configure(bg="#444444", fg="#FFFFFF")
            app.captured_label_black.configure(bg="#444444", fg="#FFFFFF")
        else:
            app.root.configure(bg="#F5F5F7")
            app.side_panel_frame.configure(bg="#FFFFFF")
            app.board_frame.configure(bg="#D6D6D6")
            app.status_bar.configure(bg="#F5F5F7", fg="#333333")
            app.status_label.configure(bg="#FFFFFF", fg="#000000")
            app.timer_label.configure(bg="#FFFFFF", fg="#000000")
            app.captured_label_white.configure(bg="#FFFFFF", fg="#000000")
            app.captured_label_black.configure(bg="#FFFFFF", fg="#000000")

class AIPlayer:
    def __init__(self, stockfish_path="stockfish"):
        self.stockfish = Stockfish(stockfish_path)
        self.stockfish.set_skill_level(1)  # Default skill level

    def set_difficulty(self, skill_level):
        """Set the Stockfish difficulty level."""
        self.stockfish.set_skill_level(skill_level)

    def set_position(self, fen):
        """Set the position on the board using FEN."""
        self.stockfish.set_fen_position(fen)

    def get_best_move(self):
        """Get the best move calculated by Stockfish."""
        return self.stockfish.get_best_move()