# chess_app/ui_side_panel.py

import tkinter as tk
from tkinter import ttk, scrolledtext
from chess_app.config import Config
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class UISidePanel(ttk.Frame):
    def __init__(self, app, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.create_side_panel()

    def create_side_panel(self):
        side_panel = self

        # Buttons Frame
        buttons_frame = ttk.Frame(side_panel)
        buttons_frame.pack(fill=tk.X, pady=10)

        # The controls are handled in UIControls

        # Status Labels
        self.status_label = tk.Label(
            side_panel,
            text="White (AI) to move",
            font=("Helvetica", 16, "bold"),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.status_label.pack(pady=10)

        # Timer Display
        self.timer_label = tk.Label(
            side_panel,
            text="White: 05:00 - Black: 05:00",
            font=("Helvetica", 14),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.timer_label.pack(pady=10)

        # Captured Pieces
        captured_pieces_frame = tk.Frame(side_panel, bg="#FFFFFF")
        captured_pieces_frame.pack(pady=10, anchor="n")

        # White Captured Pieces
        white_captured_label = tk.Label(
            captured_pieces_frame, text="White Captured:", bg="#FFFFFF", font=("Helvetica", 12, "bold")
        )
        white_captured_label.grid(row=0, column=0, sticky="w")

        self.captured_pieces_white = tk.Label(
            captured_pieces_frame, text="", bg="#FFFFFF", font=("Helvetica", 12), wraplength=200, justify="left"
        )
        self.captured_pieces_white.grid(row=1, column=0, sticky="w")

        # Black Captured Pieces
        black_captured_label = tk.Label(
            captured_pieces_frame, text="Black Captured:", bg="#FFFFFF", font=("Helvetica", 12, "bold")
        )
        black_captured_label.grid(row=2, column=0, sticky="w")

        self.captured_pieces_black = tk.Label(
            captured_pieces_frame, text="", bg="#FFFFFF", font=("Helvetica", 12), wraplength=200, justify="left"
        )
        self.captured_pieces_black.grid(row=3, column=0, sticky="w")

        # Move List
        self.move_list_label = tk.Label(
            side_panel,
            text="Moves:",
            font=("Helvetica", 14, "bold"),
            bg="#FFFFFF",
            fg="#000000",
        )
        self.move_list_label.pack(pady=(20, 10))

        self.move_list = scrolledtext.ScrolledText(
            side_panel,
            height=20,
            width=25,
            state=tk.DISABLED,
            bg="#F0F0F0",
            fg="#333333",
            font=("Helvetica", 12),
            wrap=tk.WORD
        )
        self.move_list.pack(pady=10, fill=tk.BOTH, expand=True)

    def update_move_list(self, move_san):
        self.move_list.config(state=tk.NORMAL)
        move_number = self.app.board.fullmove_number
        if self.app.board.turn:
            # Black's move
            self.move_list.insert(tk.END, f"{move_number}. ... {move_san}\n")
        else:
            # White's move
            self.move_list.insert(tk.END, f"{move_number}. {move_san} ")
        self.move_list.config(state=tk.DISABLED)

    def update_move_list_undo(self):
        self.move_list.config(state=tk.NORMAL)
        content = self.move_list.get("1.0", tk.END).strip().split("\n")
        if content:
            last_line = content[-1]
            if last_line.startswith(f"{self.app.board.fullmove_number - 1}. ..."):
                # It's a Black move; remove the last line
                self.move_list.delete(f"{len(content)}.0 linestart", f"{len(content)}.end")
            else:
                # It's a White move; remove the last move after the move number
                # Find the last space and remove everything after it
                last_space = last_line.rfind(" ")
                if last_space != -1:
                    self.move_list.delete(f"{len(content)}.{last_space+1}c", f"{len(content)}.end")
        self.move_list.config(state=tk.DISABLED)

    def update_move_list_redo(self, move):
        self.move_list.config(state=tk.NORMAL)
        move_san = self.app.board.san(move)
        move_number = self.app.board.fullmove_number
        if self.app.board.turn:
            # After White's move, it's Black's turn
            self.move_list.insert(tk.END, f"{move_number}. ... {move_san}\n")
        else:
            # After Black's move, it's White's turn
            self.move_list.insert(tk.END, f"{move_number}. {move_san} ")
        self.move_list.config(state=tk.DISABLED)