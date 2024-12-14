# chess_app/ui/ui_side_panel.py

import tkinter as tk
from tkinter import ttk, scrolledtext

class UISidePanel(ttk.Frame):
    """
    UISidePanel is a Tkinter Frame that contains various UI elements such as captured pieces display,
    move list, timer, status label, and future move predictions.
    """
    def __init__(self, app, parent, *args, **kwargs):
        """
        Initializes the UISidePanel frame.

        :param app: The main ChessApp instance.
        :param parent: The parent Tkinter widget.
        :param args: Additional positional arguments for Tkinter Frame.
        :param kwargs: Additional keyword arguments for Tkinter Frame.
        """
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.configure()
        self.create_side_panel()

    def create_side_panel(self):
        """
        Creates and packs all UI elements within the side panel.
        """
        # AI Controls
        controls_label = tk.Label(self, text="Controls", font=("Helvetica", 14, "bold"), bg="#FFFFFF")
        controls_label.pack(pady=(10, 5))

        # AI Difficulty
        difficulty_frame = tk.Frame(self, bg="#FFFFFF")
        difficulty_frame.pack(pady=5, fill=tk.X, padx=5)

        difficulty_label = tk.Label(difficulty_frame, text="AI Difficulty:", bg="#FFFFFF")
        difficulty_label.pack(side=tk.LEFT)

        self.difficulty_var = tk.StringVar(value="2")
        difficulty_options = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var, state="readonly", width=5)
        difficulty_options['values'] = ("1", "2", "3", "4", "5")
        difficulty_options.pack(side=tk.LEFT, padx=5)
        difficulty_options.bind("<<ComboboxSelected>>", self.app.set_ai_difficulty)

        # Sound Toggle
        self.sound_toggle_var = tk.BooleanVar(value=True)
        self.sound_toggle = ttk.Checkbutton(
            self,
            text="Sound Effects",
            variable=self.sound_toggle_var,
            command=self.app.toggle_sound
        )
        self.sound_toggle.pack(pady=5, anchor="w", padx=5)

        # Hint Button
        self.hint_button = ttk.Button(self, text="Show Hint", command=self.app.show_hint)
        self.hint_button.pack(pady=5, fill=tk.X, padx=5)

        # Analyze Position Button
        self.analyze_button = ttk.Button(self, text="Analyze Position", command=self.app.analyze_position)
        self.analyze_button.pack(pady=5, fill=tk.X, padx=5)

        # Analyze Game Button
        self.analyze_game_button = ttk.Button(self, text="Analyze Game", command=self.app.analyze_game)
        self.analyze_game_button.pack(pady=5, fill=tk.X, padx=5)

        # Undo/Redo Buttons
        undo_redo_frame = tk.Frame(self, bg="#FFFFFF")
        undo_redo_frame.pack(pady=5, fill=tk.X, padx=5)

        self.undo_button = ttk.Button(undo_redo_frame, text="Undo Move", command=self.app.undo_move)
        self.undo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.redo_button = ttk.Button(undo_redo_frame, text="Redo Move", command=self.app.redo_move)
        self.redo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # Save/Load Buttons
        save_load_frame = tk.Frame(self, bg="#FFFFFF")
        save_load_frame.pack(pady=5, fill=tk.X, padx=5)

        self.save_button = ttk.Button(save_load_frame, text="Save Game", command=self.app.save_game)
        self.save_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.load_button = ttk.Button(save_load_frame, text="Load Game", command=self.app.load_game)
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # Resign/Draw Buttons
        resign_draw_frame = tk.Frame(self, bg="#FFFFFF")
        resign_draw_frame.pack(pady=5, fill=tk.X, padx=5)

        self.resign_button = ttk.Button(resign_draw_frame, text="Resign", command=self.app.resign)
        self.resign_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.draw_button = ttk.Button(resign_draw_frame, text="Offer Draw", command=self.app.offer_draw)
        self.draw_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # Restart Button
        self.restart_button = ttk.Button(self, text="Restart Game", command=self.app.restart_game)
        self.restart_button.pack(pady=5, fill=tk.X, padx=5)

        # Status Labels
        status_label = tk.Label(self, text="Status", font=("Helvetica", 14, "bold"), bg="#FFFFFF")
        status_label.pack(pady=(10, 5))

        self.status_label = tk.Label(
            self,
            text="White (AI) to move",
            font=("Helvetica", 12),
            bg="#FFFFFF",
            fg="#000000",
            anchor="w"
        )
        self.status_label.pack(pady=2, fill=tk.X, padx=5)

        # Timer Display
        self.timer_label = tk.Label(
            self,
            text="White: 05:00 - Black: 05:00",
            font=("Helvetica", 12),
            bg="#FFFFFF",
            fg="#000000",
            anchor="w"
        )
        self.timer_label.pack(pady=2, fill=tk.X, padx=5)

        # Captured Pieces
        captured_pieces_label = tk.Label(
            self,
            text="Captured Pieces",
            font=("Helvetica", 14, "bold"),
            bg="#FFFFFF"
        )
        captured_pieces_label.pack(pady=(10, 5))

        # White Captured Pieces
        white_captured_label = tk.Label(
            self,
            text="White:",
            font=("Helvetica", 12, "bold"),
            bg="#FFFFFF",
            anchor="w"
        )
        white_captured_label.pack(pady=(5, 0), padx=5, fill=tk.X)

        self.captured_pieces_white = tk.Label(
            self,
            text="",
            font=("Helvetica", 12),
            bg="#FFFFFF",
            anchor="w",
            justify="left",
            wraplength=200
        )
        self.captured_pieces_white.pack(pady=2, padx=5, fill=tk.X)

        # Black Captured Pieces
        black_captured_label = tk.Label(
            self,
            text="Black:",
            font=("Helvetica", 12, "bold"),
            bg="#FFFFFF",
            anchor="w"
        )
        black_captured_label.pack(pady=(5, 0), padx=5, fill=tk.X)

        self.captured_pieces_black = tk.Label(
            self,
            text="",
            font=("Helvetica", 12),
            bg="#FFFFFF",
            anchor="w",
            justify="left",
            wraplength=200
        )
        self.captured_pieces_black.pack(pady=2, padx=5, fill=tk.X)

        # Move List
        move_list_label = tk.Label(
            self,
            text="Move List",
            font=("Helvetica", 14, "bold"),
            bg="#FFFFFF"
        )
        move_list_label.pack(pady=(10, 5))

        self.move_list = scrolledtext.ScrolledText(
            self,
            height=20,
            width=25,
            state=tk.DISABLED,
            bg="#F0F0F0",
            fg="#333333",
            font=("Helvetica", 12),
            wrap=tk.WORD
        )
        self.move_list.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

    def update_predictions(self, predictions):
        """
        Updates the predictions section with the given list of probable moves and their win probabilities.

        :param predictions: List of tuples (move, probability)
        """
        # Remove existing prediction labels
        if hasattr(self, 'prediction_frame'):
            self.prediction_frame.destroy()

        # Create a new frame for predictions
        self.prediction_frame = tk.Frame(self, bg="#FFFFFF")
        self.prediction_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=5)

        predictions_label = tk.Label(
            self.prediction_frame,
            text="Future Predictions",
            font=("Helvetica", 14, "bold"),
            bg="#FFFFFF"
        )
        predictions_label.pack(pady=(0, 5))

        if not predictions:
            no_pred_label = tk.Label(
                self.prediction_frame,
                text="No predictions available.",
                font=("Helvetica", 12),
                bg="#FFFFFF",
                anchor="w"
            )
            no_pred_label.pack(pady=2, fill=tk.X)
            return

        for move, prob in predictions:
            move_san = self.app.board.san(move)
            prob_percent = f"{prob * 100:.2f}% Win"
            pred_label = tk.Label(
                self.prediction_frame,
                text=f"{move_san}: {prob_percent}",
                font=("Helvetica", 12),
                bg="#FFFFFF",
                anchor="w",
                justify="left",
                wraplength=200
            )
            pred_label.pack(pady=1, fill=tk.X)

    def show_predictions(self, predictions):
        """
        Displays the given predictions in the side panel.

        :param predictions: List of tuples (move, probability)
        """
        self.update_predictions(predictions)

    def update_move_list(self, move_san):
        """
        Updates the move list with the latest move in SAN notation.

        :param move_san: Move in SAN notation.
        """
        self.move_list.config(state=tk.NORMAL)
        move_number = self.app.board.fullmove_number
        if self.app.board.turn:
            # Black's move
            self.move_list.insert(tk.END, f"{move_number}. ... {move_san}\n")
        else:
            # White's move
            self.move_list.insert(tk.END, f"{move_number}. {move_san} ")
        self.move_list.config(state=tk.DISABLED)
        self.move_list.see(tk.END)  # Auto-scroll to latest move

    def update_move_list_undo(self):
        """
        Updates the move list when a move is undone.
        """
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
        """
        Updates the move list when a move is redone.

        :param move: The chess.Move object to redo.
        """
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