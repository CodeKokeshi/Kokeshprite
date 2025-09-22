from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QSpinBox, QPushButton, QDialogButtonBox, QWidget, QGridLayout
from PyQt6.QtCore import Qt

MAX_DIMENSION = 2048
PRESETS = [32, 64, 128, 256, 512]

class DimensionSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(1, MAX_DIMENSION)
        self.setAccelerated(True)
        self.setSingleStep(1)
        # Use fixed width for visual stability
        self.setMinimumWidth(90)
        # Connect textChanged for immediate clamp
        self.lineEdit().textChanged.connect(self._enforce_text)

    def _enforce_text(self, text: str):
        if not text or not text.isdigit():
            return
        val = int(text)
        if val > MAX_DIMENSION:
            self.blockSignals(True)
            self.setValue(MAX_DIMENSION)
            self.blockSignals(False)

class NewFileDialog(QDialog):
    def __init__(self, parent=None, default_width=64, default_height=64):
        super().__init__(parent)
        self.setWindowTitle("New File")
        self.setModal(True)
        self.width_value = default_width
        self.height_value = default_height
        self._build_ui(default_width, default_height)

    def _build_ui(self, default_width, default_height):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        self.width_spin = DimensionSpinBox(); self.width_spin.setValue(default_width)
        self.height_spin = DimensionSpinBox(); self.height_spin.setValue(default_height)

        form.addRow("Width", self.width_spin)
        form.addRow("Height", self.height_spin)

        # Presets row
        presets_container = QWidget()
        presets_layout = QHBoxLayout(presets_container)
        presets_layout.setContentsMargins(0,0,0,0)
        presets_layout.setSpacing(6)
        presets_layout.addWidget(QLabel("Presets:"))
        for p in PRESETS:
            btn = QPushButton(str(p))
            btn.setFixedWidth(48)
            btn.clicked.connect(lambda _, v=p: self._apply_preset(v))
            presets_layout.addWidget(btn)
        presets_layout.addStretch(1)
        layout.addWidget(presets_container)

        # Max hint
        max_hint = QLabel(f"Maximum size: {MAX_DIMENSION} x {MAX_DIMENSION}")
        max_hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(max_hint)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _apply_preset(self, value):
        self.width_spin.setValue(value)
        self.height_spin.setValue(value)

    def _accept(self):
        w = self.width_spin.value()
        h = self.height_spin.value()
        if w < 1:
            w = 1
        if h < 1:
            h = 1
        if w > MAX_DIMENSION:
            w = MAX_DIMENSION
        if h > MAX_DIMENSION:
            h = MAX_DIMENSION
        self.width_value = w
        self.height_value = h
        self.accept()

    def get_dimensions(self):
        return self.width_value, self.height_value
