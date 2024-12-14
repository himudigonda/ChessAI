# chess_app/ui/status_bar.py

import tkinter as tk
from .styles import Styles


class StatusBar(tk.Frame):
    def __init__(self, parent, **kwargs):
        """
        Initializes the StatusBar.

        :param parent: The parent Tkinter widget.
        :param kwargs: Additional keyword arguments for Frame.
        """
        super().__init__(parent, bg=Styles.CURRENT_THEME["background"], **kwargs)
        self.label = tk.Label(self, text="Ready", anchor="w", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"], font=("Helvetica", 12))
        self.label.pack(fill="both", expand=True)

    def update_status(self, message, color="green"):
        self.label.config(text=message)
        if color == "green":
            self.label.config(fg=Styles.CURRENT_THEME["status_success"])
        elif color == "red":
            self.label.config(fg=Styles.CURRENT_THEME["status_error"])
        elif color == "blue":
            self.label.config(fg=Styles.CURRENT_THEME["status_info"])