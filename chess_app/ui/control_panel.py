# chess_app/ui/control_panel.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QGridLayout,
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

        # Button Grid
        button_grid = QGridLayout()
        layout.addLayout(button_grid)

        buttons = [
            ("Show Hint", self.app.show_hint),
            ("Analyze Position", self.app.analyze_position),
            ("Analyze Game", self.app.analyze_game),
            ("Undo Move", self.app.undo_move),
            ("Redo Move", self.app.redo_move),
            ("Save Game", self.app.save_game),
            ("Load Game", self.app.load_game),
            ("Restart Game", self.app.restart_game),
            ("Resign", self.app.resign),
            ("Offer Draw", self.app.offer_draw),
        ]

        for i, (label, callback) in enumerate(buttons):
            button = QPushButton(label)
            button.clicked.connect(callback)
            button_grid.addWidget(button, i // 2, i % 2)

        # Toggle Theme
        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.clicked.connect(self.app.toggle_theme)
        layout.addWidget(self.theme_button)

        # Sound Toggle
        self.sound_checkbox = QCheckBox("Sound Effects")
        self.sound_checkbox.setChecked(True)
        self.sound_checkbox.stateChanged.connect(self.toggle_sound)
        layout.addWidget(self.sound_checkbox)

        layout.addStretch()

    def set_ai_difficulty(self):
        selected_depth = int(self.difficulty_combo.currentText())
        self.app.set_ai_difficulty(selected_depth)

    def toggle_sound(self):
        sound_enabled = self.sound_checkbox.isChecked()
        self.app.toggle_sound(sound_enabled)