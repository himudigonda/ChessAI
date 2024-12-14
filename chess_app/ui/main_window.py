# chess_app/ui/main_window.py
import chess
from PyQt5.QtWidgets import (
        QMainWindow,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from .chessboard_widget import ChessBoardWidget
from .control_panel import ControlPanel
from .side_panel import SidePanel
from chess_app.utils import AIPlayer, Logger, GameSaver, EloRating
from PyQt5.QtCore import Qt, QTimer
import chess


class MainWindow(QMainWindow):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.setWindowTitle("Chess AI")
        self.setGeometry(100, 100, 1200, 800)  # Width x Height

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Chessboard Widget
        self.chessboard = ChessBoardWidget(self.app)
        main_layout.addWidget(self.chessboard, stretch=3)

        # Right Panel (Control + Side Panels)
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, stretch=1)

        # Control Panel
        self.control_panel = ControlPanel(self.app)
        right_panel.addWidget(self.control_panel)

        # Side Panel
        self.side_panel = SidePanel(self.app)
        right_panel.addWidget(self.side_panel)

        # Progress Bar for Model Loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Loading model...")
        right_panel.addWidget(self.progress_bar)

        # Timer Setup (Do not start yet)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_display)
        # Timer will be started once the model is loaded

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Welcome to Chess AI!")

    def start_game(self):
        """
        Starts the game by initiating the timer and hiding the progress bar.
        """
        self.progress_bar.hide()
        self.timer.start(1000)  # Update every second
        self.status.showMessage("Game started. Good luck!")

    def update_timer_display(self):
        white_minutes, white_seconds = divmod(self.app.white_time, 60)
        black_minutes, black_seconds = divmod(self.app.black_time, 60)
        timer_text = f"White: {white_minutes:02}:{white_seconds:02} - Black: {black_minutes:02}:{black_seconds:02}"
        self.side_panel.update_timer(timer_text)

    def update_status(self, message, color="green"):
        self.side_panel.update_status(message, color)
    def update_timer(self):
        if self.app.board.is_game_over():
            self.timer.stop()
            return

        if self.app.board.turn == chess.WHITE:
            if self.white_time > 0:
                self.white_time -= 1
            else:
                QMessageBox.information(
                    self, "Time Up", "White's time is up. Black (Stockfish) wins!"
                )
                self.app.handle_resignation(chess.WHITE)
                self.timer.stop()
        else:
            if self.black_time > 0:
                self.black_time -= 1
            else:
                QMessageBox.information(
                    self, "Time Up", "Black's time is up. White (AI) wins!"
                )
                self.app.handle_resignation(chess.BLACK)
                self.timer.stop()

        self.update_timer_display()

    def update_timer_display(self):
        white_minutes, white_seconds = divmod(self.white_time, 60)
        black_minutes, black_seconds = divmod(self.black_time, 60)
        timer_text = f"White: {white_minutes:02}:{white_seconds:02} - Black: {black_minutes:02}:{black_seconds:02}"
        self.side_panel.update_timer(timer_text)
