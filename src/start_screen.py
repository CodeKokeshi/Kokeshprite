from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt

class StartScreen(QWidget):
    """Intro/start screen with minimal options: New File, Open File."""
    new_file_requested = pyqtSignal()
    open_file_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setObjectName("StartScreen")
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Kokeshprite")
        title.setStyleSheet("font-size: 42px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Pixel Art Editor")
        subtitle.setStyleSheet("font-size: 16px; color: #bbbbbb;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        new_btn = QPushButton("New File")
        new_btn.setObjectName("NewFileButton")
        open_btn = QPushButton("Open File")
        open_btn.setObjectName("OpenFileButton")

        for btn in (new_btn, open_btn):
            btn.setMinimumWidth(220)
            btn.setMinimumHeight(48)
            btn.setStyleSheet(
                """
                QPushButton { background-color: #3d6ea8; color: white; font-size: 18px; font-weight: bold; border: 1px solid #2b4f78; border-radius: 6px; }
                QPushButton:hover { background-color: #4883c7; }
                QPushButton:pressed { background-color: #305780; }
                """
            )
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        new_btn.clicked.connect(self.new_file_requested.emit)
        open_btn.clicked.connect(self.open_file_requested.emit)

        self.setStyleSheet("background-color: #1e1e1e;")
