# chess_app/ui/utils.py

import tkinter as tk
from tkinter import messagebox


def show_message(title, message, icon="info"):
    if icon == "info":
        messagebox.showinfo(title, message)
    elif icon == "warning":
        messagebox.showwarning(title, message)
    elif icon == "error":
        messagebox.showerror(title, message)
