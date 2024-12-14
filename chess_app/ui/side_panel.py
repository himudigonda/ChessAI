# chess_app/ui/side_panel.py

import tkinter as tk
from chess_app.config import Config


class SidePanel(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Config.CURRENT_THEME["background"], **kwargs)
        self.app = app
        self.captured_white = []
        self.captured_black = []
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self,
            text="Game Info",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=10)

        self.timer_label = tk.Label(
            self,
            text="White: 05:00 - Black: 05:00",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
            font=("Helvetica", 14),
        )
        self.timer_label.pack(pady=5)

        self.status_label = tk.Label(
            self,
            text="Welcome to Chess AI!",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["status_info"],
            font=("Helvetica", 12),
        )
        self.status_label.pack(pady=5)

        captured_group = tk.LabelFrame(
            self,
            text="Captured Pieces",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
        )
        captured_group.pack(fill="x", padx=10, pady=5)

        lbl_white = tk.Label(
            captured_group,
            text="White:",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
        )
        lbl_white.pack(anchor="w", padx=5)
        self.captured_white_label = tk.Label(
            captured_group,
            text="",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
            font=("Helvetica", 12),
        )
        self.captured_white_label.pack(anchor="w", padx=20)

        lbl_black = tk.Label(
            captured_group,
            text="Black:",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
        )
        lbl_black.pack(anchor="w", padx=5)
        self.captured_black_label = tk.Label(
            captured_group,
            text="",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
            font=("Helvetica", 12),
        )
        self.captured_black_label.pack(anchor="w", padx=20)

        move_list_group = tk.LabelFrame(
            self,
            text="Move List",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
        )
        move_list_group.pack(fill="both", expand=True, padx=10, pady=5)

        self.move_list = tk.Text(
            move_list_group,
            height=15,
            state="disabled",
            bg=Config.CURRENT_THEME["background"],
            fg=Config.CURRENT_THEME["foreground"],
            font=("Helvetica", 12),
        )
        self.move_list.pack(fill="both", expand=True, padx=5, pady=5)

    def update_timer(self, timer_text):
        self.timer_label.config(text=timer_text)

    def update_status(self, message, color="green"):
        self.status_label.config(text=message)
        if color == "green":
            self.status_label.config(fg=Config.CURRENT_THEME["status_success"])
        elif color == "red":
            self.status_label.config(fg=Config.CURRENT_THEME["status_error"])
        elif color == "blue":
            self.status_label.config(fg=Config.CURRENT_THEME["status_info"])

    def update_move_list(self, move_san):
        self.move_list.config(state="normal")
        current_text = self.move_list.get("1.0", tk.END).strip()
        if current_text:
            last_move_num = current_text.count("\n") + 1
            self.move_list.insert(tk.END, f"{last_move_num}. {move_san}\n")
        else:
            self.move_list.insert(tk.END, f"1. {move_san}\n")
        self.move_list.config(state="disabled")
        self.move_list.see(tk.END)

    def update_captured_pieces(self, white_pieces, black_pieces):
        self.captured_white_label.config(text=" ".join(white_pieces))
        self.captured_black_label.config(text=" ".join(black_pieces))

    def undo_move(self):
        current_text = self.move_list.get("1.0", tk.END).strip().split("\n")
        if current_text:
            current_text.pop()
            self.move_list.config(state="normal")
            self.move_list.delete("1.0", tk.END)
            for line in current_text:
                self.move_list.insert(tk.END, f"{line}\n")
            self.move_list.config(state="disabled")
            self.move_list.see(tk.END)

    def redo_move(self, move_san):
        self.move_list.config(state="normal")
        current_text = self.move_list.get("1.0", tk.END).strip()
        if current_text:
            last_move_num = current_text.count("\n") + 1
            self.move_list.insert(tk.END, f"{last_move_num}. {move_san}\n")
        else:
            self.move_list.insert(tk.END, f"1. {move_san}\n")
        self.move_list.config(state="disabled")
        self.move_list.see(tk.END)
