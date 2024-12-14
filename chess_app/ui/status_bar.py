# chess_app/ui/status_bar.py

import tkinter as tk
#from .styles import Styles


class StatusBar(tk.Frame):
    def __init__(self, parent, **kwargs):
        """
        Initializes the StatusBar.

        :param parent: The parent Tkinter widget.
        :param kwargs: Additional keyword arguments for Frame.
        """
        super().__init__(parent, bg="#F5F5F5", **kwargs) # Removed style reference
        self.label = tk.Label(self, text="Ready", anchor="w", bg="#F5F5F5", fg="#000000", font=("Helvetica", 12)) # Removed style reference
        self.label.pack(fill="both", expand=True)

    def update_status(self, message, color="green"):
        self.label.config(text=message)
        if color == "green":
            self.label.config(fg="#00a651")
        elif color == "red":
            self.label.config(fg="#d9534f")
        elif color == "blue":
            self.label.config(fg="#5bc0de")