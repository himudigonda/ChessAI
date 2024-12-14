# main.py

import tkinter as tk
from chess_app.ui import ChessApp
from chess_app.config import Config

def main():
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()