# chess_app/ui/control_panel.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QMessageBox,
)


class ControlPanel(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # AI Difficulty
        difficulty_label = QLabel("AI Difficulty:")
        layout.addWidget(difficulty_label)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["1", "2", "3", "4", "5"])
        self.difficulty_combo.currentIndexChanged.connect(self.set_ai_difficulty)
        layout.addWidget(self.difficulty_combo)

        # Sound Toggle
        self.sound_checkbox = QCheckBox("Sound Effects")
        self.sound_checkbox.setChecked(True)
        self.sound_checkbox.stateChanged.connect(self.toggle_sound)
        layout.addWidget(self.sound_checkbox)

        # Action Buttons
        self.hint_button = QPushButton("Show Hint")
        self.hint_button.clicked.connect(self.app.show_hint)
        layout.addWidget(self.hint_button)

        self.analyze_position_button = QPushButton("Analyze Position")
        self.analyze_position_button.clicked.connect(self.app.analyze_position)
        layout.addWidget(self.analyze_position_button)

        self.analyze_game_button = QPushButton("Analyze Game")
        self.analyze_game_button.clicked.connect(self.app.analyze_game)
        layout.addWidget(self.analyze_game_button)

        self.undo_button = QPushButton("Undo Move")
        self.undo_button.clicked.connect(self.app.undo_move)
        layout.addWidget(self.undo_button)

        self.redo_button = QPushButton("Redo Move")
        self.redo_button.clicked.connect(self.app.redo_move)
        layout.addWidget(self.redo_button)

        self.save_button = QPushButton("Save Game")
        self.save_button.clicked.connect(self.app.save_game)
        layout.addWidget(self.save_button)

        self.load_button = QPushButton("Load Game")
        self.load_button.clicked.connect(self.app.load_game)
        layout.addWidget(self.load_button)

        self.resign_button = QPushButton("Resign")
        self.resign_button.clicked.connect(self.app.resign)
        layout.addWidget(self.resign_button)

        self.offer_draw_button = QPushButton("Offer Draw")
        self.offer_draw_button.clicked.connect(self.app.offer_draw)
        layout.addWidget(self.offer_draw_button)

        self.restart_button = QPushButton("Restart Game")
        self.restart_button.clicked.connect(self.app.restart_game)
        layout.addWidget(self.restart_button)

        # Toggle Theme
        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.clicked.connect(self.app.toggle_theme)
        layout.addWidget(self.theme_button)

        layout.addStretch()

    def set_ai_difficulty(self):
        selected_depth = int(self.difficulty_combo.currentText())
        self.app.set_ai_difficulty(selected_depth)

    def toggle_sound(self):
        sound_enabled = self.sound_checkbox.isChecked()
        self.app.toggle_sound(sound_enabled)
