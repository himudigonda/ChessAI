# chess_app/utils.py
import tkinter as tk
from tkinter import messagebox
import os

class Timer:
    @staticmethod
    def format_time(white_time, black_time):
        white_minutes, white_seconds = divmod(white_time, 60)
        black_minutes, black_seconds = divmod(black_time, 60)
        return f"Time: {white_minutes:02}:{white_seconds:02} - {black_minutes:02}:{black_seconds:02}"

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