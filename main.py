# main.py
import tkinter as tk
from chess_app.ui import ChessApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()