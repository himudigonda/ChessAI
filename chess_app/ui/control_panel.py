# chess_app/ui/control_panel.py

import tkinter as tk
from tkinter import ttk
from .styles import Styles


class ControlPanel(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        """
        Initializes the ControlPanel.

        :param parent: The parent Tkinter widget.
        :param app: The main ChessApp instance.
        :param kwargs: Additional keyword arguments for Frame.
        """
        super().__init__(parent, bg=Styles.CURRENT_THEME["background"], **kwargs)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        """
        Creates and places all the widgets in the control panel.
        """
        # Title
        title = tk.Label(self, text="Control Panel", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"], font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        # Game Control Buttons
        game_controls = tk.LabelFrame(self, text="Game Controls", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        game_controls.pack(fill="x", padx=10, pady=5)

        btn_start = tk.Button(game_controls, text="Start Game", command=self.app.start_game, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_start.pack(fill="x", padx=5, pady=2)

        btn_save = tk.Button(game_controls, text="Save Game", command=self.app.save_game, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_save.pack(fill="x", padx=5, pady=2)

        btn_load = tk.Button(game_controls, text="Load Game", command=self.app.load_game, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_load.pack(fill="x", padx=5, pady=2)

        btn_resign = tk.Button(game_controls, text="Resign", command=self.app.resign, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_resign.pack(fill="x", padx=5, pady=2)

        btn_offer_draw = tk.Button(game_controls, text="Offer Draw", command=self.app.offer_draw, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_offer_draw.pack(fill="x", padx=5, pady=2)

        btn_undo = tk.Button(game_controls, text="Undo Move", command=self.app.undo_move, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_undo.pack(fill="x", padx=5, pady=2)

        btn_redo = tk.Button(game_controls, text="Redo Move", command=self.app.redo_move, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_redo.pack(fill="x", padx=5, pady=2)

        btn_restart = tk.Button(game_controls, text="Restart Game", command=self.app.restart_game, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_restart.pack(fill="x", padx=5, pady=2)

        # AI Settings
        ai_settings = tk.LabelFrame(self, text="AI Settings", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        ai_settings.pack(fill="x", padx=10, pady=5)

        lbl_difficulty = tk.Label(ai_settings, text="AI Difficulty:", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        lbl_difficulty.pack(anchor="w", padx=5, pady=2)

        self.combo_difficulty = ttk.Combobox(ai_settings, values=["1", "2", "3", "4", "5"], state="readonly")
        self.combo_difficulty.current(1)  # Default difficulty level 2
        self.combo_difficulty.bind("<<ComboboxSelected>>", self.set_difficulty)
        self.combo_difficulty.pack(fill="x", padx=5, pady=2)

        # Sound Toggle
        self.var_sound = tk.BooleanVar(value=True)
        chk_sound = tk.Checkbutton(self, text="Sound Effects", variable=self.var_sound, command=self.toggle_sound, bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        chk_sound.pack(fill="x", padx=10, pady=5)

        # Hint Button
        btn_hint = tk.Button(self, text="Show Hint", command=self.app.show_hint, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_hint.pack(fill="x", padx=10, pady=2)

        # Analyze Buttons
        analyze_controls = tk.LabelFrame(self, text="Analysis", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        analyze_controls.pack(fill="x", padx=10, pady=5)

        btn_analyze_position = tk.Button(analyze_controls, text="Analyze Position", command=self.app.analyze_position, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_analyze_position.pack(fill="x", padx=5, pady=2)

        btn_analyze_game = tk.Button(analyze_controls, text="Analyze Game", command=self.app.analyze_game, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_analyze_game.pack(fill="x", padx=5, pady=2)

        # Auto Play Options
        auto_play = tk.LabelFrame(self, text="Auto Play", bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        auto_play.pack(fill="x", padx=10, pady=5)

        btn_play_stockfish = tk.Button(auto_play, text="Play Against Stockfish", command=self.app.play_against_stockfish, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_play_stockfish.pack(fill="x", padx=5, pady=2)

        btn_play_model = tk.Button(auto_play, text="Play Against Model", command=self.app.play_against_model, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_play_model.pack(fill="x", padx=5, pady=2)

        btn_watch_play = tk.Button(auto_play, text="Watch AI vs Stockfish", command=self.app.watch_ai_vs_stockfish, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_watch_play.pack(fill="x", padx=5, pady=2)

        # Toggle Theme
        btn_toggle_theme = tk.Button(self, text="Toggle Theme", command=self.app.toggle_theme, bg=Styles.CURRENT_THEME["button_bg"], fg=Styles.CURRENT_THEME["button_fg"])
        btn_toggle_theme.pack(fill="x", padx=10, pady=10)

        # Toggle Coordinates
        self.var_coordinates = tk.BooleanVar(value=False)
        chk_coordinates = tk.Checkbutton(self, text="Show Coordinates", variable=self.var_coordinates, command=self.toggle_coordinates, bg=Styles.CURRENT_THEME["background"], fg=Styles.CURRENT_THEME["foreground"])
        chk_coordinates.pack(fill="x", padx=10, pady=5)

    def set_difficulty(self, event):
        selected = self.combo_difficulty.get()
        self.app.set_ai_difficulty(int(selected))

    def toggle_sound(self):
        enabled = self.var_sound.get()
        self.app.toggle_sound(enabled)

    def toggle_coordinates(self):
        show = self.var_coordinates.get()
        self.app.toggle_coordinates(show)