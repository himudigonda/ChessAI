# chess_app/ui/side_panel.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QGroupBox,
)
from PyQt5.QtCore import Qt



class SidePanel(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Timer Display
        self.timer_label = QLabel("White: 05:00 - Black: 05:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.timer_label)

        # Status Label
        self.status_label = QLabel("Status: White (AI) to move")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: green;")
        layout.addWidget(self.status_label)

        # Captured Pieces
        captured_group = QGroupBox("Captured Pieces")
        captured_layout = QVBoxLayout()
        captured_group.setLayout(captured_layout)

        self.captured_white_label = QLabel("White:")
        captured_layout.addWidget(self.captured_white_label)

        self.captured_white_pieces = QLabel("")
        captured_layout.addWidget(self.captured_white_pieces)

        self.captured_black_label = QLabel("Black:")
        captured_layout.addWidget(self.captured_black_label)

        self.captured_black_pieces = QLabel("")
        captured_layout.addWidget(self.captured_black_pieces)

        layout.addWidget(captured_group)

        # Move List
        move_list_group = QGroupBox("Move List")
        move_list_layout = QVBoxLayout()
        move_list_group.setLayout(move_list_layout)

        self.move_list = QTextEdit()
        self.move_list.setReadOnly(True)
        move_list_layout.addWidget(self.move_list)

        layout.addWidget(move_list_group)
        layout.addStretch()

    def update_move_list(self, move_san):
        current_text = self.move_list.toPlainText().strip()
        if current_text:
            last_line = current_text.split("\n")[-1]
            if len(last_line.split()) == 2:
                self.move_list.append(f"{last_line.split()[0]} {last_line.split()[1]} {move_san}")
            else:
                move_number = current_text.count('\n') + 1
                self.move_list.append(f"{move_number}. {move_san}")
        else:
            self.move_list.append(f"1. {move_san}")
    
    def update_timer(self, timer_text):
        self.timer_label.setText(timer_text)

    def update_status(self, status_text, color="green"):
        self.status_label.setText(f"Status: {status_text}")
        self.status_label.setStyleSheet(f"font-size: 14px; color: {color};")

    def update_captured_pieces(self, white_pieces, black_pieces):
        self.captured_white_pieces.setText(" ".join(white_pieces))
        self.captured_black_pieces.setText(" ".join(black_pieces))


    def update_move_list_undo(self):
        current_text = self.move_list.toPlainText().strip().split("\n")
        if current_text:
            current_text.pop()
            self.move_list.setText("\n".join(current_text))

    def update_predictions(self, predictions):
        self.predictions_list.clear()
        for move, prob in predictions:
            item = QListWidgetItem(f"{move}: {prob * 100:.2f}% Win")
            self.predictions_list.addItem(item)
