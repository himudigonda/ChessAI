# chess_app/ui/utils.py

import tkinter as tk
from tkinter import messagebox
from .styles import Styles


def show_message(title, message, icon="info"):
    """
    Displays a message box.

    :param title: Title of the message box.
    :param message: Message to display.
    :param icon: Icon type: "info", "warning", "error".
    """
    if icon == "info":
        messagebox.showinfo(title, message)
    elif icon == "warning":
        messagebox.showwarning(title, message)
    elif icon == "error":
        messagebox.showerror(title, message)