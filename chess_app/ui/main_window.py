# chess_app/ui/main_window.py

import tkinter as tk
from .chessboard_widget import ChessBoardWidget
from .control_panel import ControlPanel
from .side_panel import SidePanel
from .status_bar import StatusBar


class MainWindow(tk.Tk):
    def __init__(self, app):
        """
        Initializes the MainWindow.

        :param app: The main ChessApp instance.
        """
        super().__init__()
        self.app = app
        self.title("Chess AI")
        self.geometry("1200x800")
        self.configure(bg="#F5F5F5")  # Removed style reference

        # Create main frames
        self.create_widgets()

    def create_widgets(self):
        """
        Creates and places all main widgets in the window.
        """
        # Chessboard
        self.chessboard = ChessBoardWidget(self, self.app, width=600, height=600)
        self.chessboard.pack(side="left", padx=10, pady=10)

        # Right Panel containing Control and Side Panels
        right_panel = tk.Frame(self, bg="#F5F5F5") # Removed Style Reference
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Control Panel
        self.control_panel = ControlPanel(right_panel, self.app)
        self.control_panel.pack(fill="x", pady=5)

        # Side Panel
        self.side_panel = SidePanel(right_panel, self.app)
        self.side_panel.pack(fill="both", expand=True, pady=5)

        # Status Bar
        self.status_bar = StatusBar(self)
        self.status_bar.pack(side="bottom", fill="x")

        # Link status bar to app
        self.app.status_bar = self.status_bar
    
    def refresh_ui(self):
        """
        Refreshes the UI elements, e.g., after theme change.
        """
        self.configure(bg="#F5F5F5")
        self.chessboard.configure(bg="#F5F5F5")
        self.control_panel.configure(bg="#F5F5F5")
        self.side_panel.configure(bg="#F5F5F5")
        self.status_bar.configure(bg="#F5F5F5")

        # Update chessboard squares and pieces
        self.chessboard.draw_board()
        self.chessboard.draw_pieces()

        # Update control panel buttons
        for child in self.control_panel.winfo_children():
             if isinstance(child, tk.Button):
                child.configure(bg="#E0E0E0", fg="#000000") # Removed Style Reference

        # Update side panel labels
        self.side_panel.timer_label.configure(bg="#F5F5F5", fg="#000000") # Removed Style Reference
        self.side_panel.status_label.configure(bg="#F5F5F5", fg="#000000") # Removed Style Reference
        self.side_panel.captured_white_label.configure(bg="#F5F5F5", fg="#000000") # Removed Style Reference
        self.side_panel.captured_black_label.configure(bg="#F5F5F5", fg="#000000") # Removed Style Reference
        self.side_panel.move_list.configure(bg="#F5F5F5", fg="#000000") # Removed Style Reference