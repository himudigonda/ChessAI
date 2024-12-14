# chess_app/ui/ui_controls.py

import tkinter as tk
from tkinter import ttk
from chess_app.config import Config

class UIControls(ttk.Frame):
    """
    UIControls is a Tkinter Frame that contains various control widgets such as AI difficulty settings,
    sound toggle, and action buttons like Show Hint, Analyze Position, etc.
    """
    def __init__(self, app, parent, *args, **kwargs):
        """
        Initializes the UIControls frame.

        :param app: The main ChessApp instance.
        :param parent: The parent Tkinter widget.
        :param args: Additional positional arguments for Tkinter Frame.
        :param kwargs: Additional keyword arguments for Tkinter Frame.
        """
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.create_controls()

    def create_controls(self):
        """
        Creates and packs all control widgets within the frame.
        """
        controls = self

        # AI Difficulty
        difficulty_label = ttk.Label(controls, text="AI Difficulty:")
        difficulty_label.pack(pady=5, anchor="w")

        self.difficulty_var = tk.StringVar(value="2")
        difficulty_options = ttk.Combobox(controls, textvariable=self.difficulty_var, state="readonly")
        difficulty_options['values'] = ("1", "2", "3", "4", "5")
        difficulty_options.pack(pady=5, fill=tk.X)
        difficulty_options.bind("<<ComboboxSelected>>", self.set_ai_difficulty)

        # Sound Toggle
        self.sound_toggle_var = tk.BooleanVar(value=True)
        self.sound_toggle = ttk.Checkbutton(
            controls,
            text="Sound Effects",
            variable=self.sound_toggle_var,
            command=self.app.toggle_sound
        )
        self.sound_toggle.pack(pady=5, anchor="w")

        # Hint Button
        self.hint_button = ttk.Button(controls, text="Show Hint", command=self.app.show_hint)
        self.hint_button.pack(pady=5, fill=tk.X)

        # Analyze Position Button
        self.analyze_button = ttk.Button(controls, text="Analyze Position", command=self.app.analyze_position)
        self.analyze_button.pack(pady=5, fill=tk.X)

        # Analyze Game Button
        self.analyze_game_button = ttk.Button(controls, text="Analyze Game", command=self.app.analyze_game)
        self.analyze_game_button.pack(pady=5, fill=tk.X)

        # Undo/Redo Buttons
        self.undo_button = ttk.Button(controls, text="Undo Move", command=self.app.undo_move)
        self.undo_button.pack(pady=5, fill=tk.X)

        self.redo_button = ttk.Button(controls, text="Redo Move", command=self.app.redo_move)
        self.redo_button.pack(pady=5, fill=tk.X)

        # Save/Load Buttons
        self.save_button = ttk.Button(controls, text="Save Game", command=self.app.save_game)
        self.save_button.pack(pady=5, fill=tk.X)

        self.load_button = ttk.Button(controls, text="Load Game", command=self.app.load_game)
        self.load_button.pack(pady=5, fill=tk.X)

        # Resign/Draw Buttons
        self.resign_button = ttk.Button(controls, text="Resign", command=self.app.resign)
        self.resign_button.pack(pady=5, fill=tk.X)

        self.draw_button = ttk.Button(controls, text="Offer Draw", command=self.app.offer_draw)
        self.draw_button.pack(pady=5, fill=tk.X)

        self.restart_button = ttk.Button(controls, text="Restart Game", command=self.app.restart_game)
        self.restart_button.pack(pady=5, fill=tk.X)

        # Theme Toggle
        self.theme_button = ttk.Button(controls, text="Toggle Theme", command=self.app.toggle_theme)
        self.theme_button.pack(pady=10, fill=tk.X)

    def set_ai_difficulty(self, event):
        """
        Sets the AI difficulty based on user selection.

        :param event: The Tkinter event object.
        """
        selected_depth = int(self.difficulty_var.get())
        if self.app.ai_player.engine:
            self.app.ai_player.engine.configure({"Skill Level": selected_depth})
            self.app.logger.info(f"AI difficulty set to depth {selected_depth}")
        self.app.update_status_bar(f"AI difficulty set to level {selected_depth}")

    def toggle_sound(self):
        """
        Toggles the sound effects on or off.
        """
        self.app.sound_enabled = self.sound_toggle_var.get()
        self.app.update_status_bar(f"Sound Effects {'Enabled' if self.sound_enabled else 'Disabled'}")