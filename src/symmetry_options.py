"""
Symmetry options widget for controlling symmetry lines
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSpinBox, QGroupBox, QComboBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class SymmetryOptionsWidget(QWidget):
    """Widget for controlling symmetry settings"""
    
    # Signals
    symmetry_changed = pyqtSignal()  # Emitted when symmetry settings change
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.init_ui()
        
    def init_ui(self):
        """Initialize the symmetry options UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Enable/Disable toggle
        toggle_layout = QHBoxLayout()
        self.enable_btn = QPushButton("Enable Symmetry")
        self.enable_btn.setCheckable(True)
        self.enable_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: 2px solid #666;
                border-radius: 4px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
            QPushButton:hover {
                border-color: #007acc;
            }
        """)
        self.enable_btn.toggled.connect(self.on_enable_toggled)
        toggle_layout.addWidget(self.enable_btn)
        main_layout.addLayout(toggle_layout)
        
        # Preset buttons
        presets_group = QGroupBox("Presets")
        presets_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
        """)
        presets_layout = QVBoxLayout(presets_group)
        presets_layout.setSpacing(6)
        
        # Preset buttons grid
        preset_row1 = QHBoxLayout()
        preset_row1.setSpacing(6)
        
        self.preset_vertical_btn = QPushButton("Vertical |")
        self.preset_horizontal_btn = QPushButton("Horizontal —")
        self.preset_cross_btn = QPushButton("Cross +")
        
        preset_row1.addWidget(self.preset_vertical_btn)
        preset_row1.addWidget(self.preset_horizontal_btn)
        preset_row1.addWidget(self.preset_cross_btn)
        presets_layout.addLayout(preset_row1)
        
        preset_row2 = QHBoxLayout()
        preset_row2.setSpacing(6)
        
        self.preset_x_btn = QPushButton("Diagonal X")
        self.preset_star_btn = QPushButton("Star ✱")
        self.preset_clear_btn = QPushButton("Clear All")
        
        preset_row2.addWidget(self.preset_x_btn)
        preset_row2.addWidget(self.preset_star_btn)
        preset_row2.addWidget(self.preset_clear_btn)
        presets_layout.addLayout(preset_row2)
        
        # Style preset buttons
        preset_style = """
            QPushButton {
                background-color: #505050;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                padding: 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #606060;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #007acc;
            }
        """
        for btn in [self.preset_vertical_btn, self.preset_horizontal_btn, 
                   self.preset_cross_btn, self.preset_x_btn, 
                   self.preset_star_btn, self.preset_clear_btn]:
            btn.setStyleSheet(preset_style)
        
        # Connect preset buttons
        self.preset_vertical_btn.clicked.connect(lambda: self.apply_preset("vertical"))
        self.preset_horizontal_btn.clicked.connect(lambda: self.apply_preset("horizontal"))
        self.preset_cross_btn.clicked.connect(lambda: self.apply_preset("cross"))
        self.preset_x_btn.clicked.connect(lambda: self.apply_preset("x"))
        self.preset_star_btn.clicked.connect(lambda: self.apply_preset("star"))
        self.preset_clear_btn.clicked.connect(self.clear_lines)
        
        main_layout.addWidget(presets_group)
        
        # Manual control group
        manual_group = QGroupBox("Manual Control")
        manual_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
        """)
        manual_layout = QVBoxLayout(manual_group)
        manual_layout.setSpacing(8)
        
        # Add line button
        add_line_layout = QHBoxLayout()
        self.add_line_btn = QPushButton("Add Line")
        self.add_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a7a2a;
                border: 1px solid #3a9a3a;
                border-radius: 3px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9a3a;
            }
            QPushButton:disabled {
                background-color: #404040;
                border-color: #555;
                color: #888;
            }
        """)
        self.add_line_btn.clicked.connect(self.add_line)
        add_line_layout.addWidget(self.add_line_btn)
        
        # Line count label
        self.line_count_label = QLabel("Lines: 0/8")
        self.line_count_label.setStyleSheet("color: #aaa; font-size: 11px;")
        add_line_layout.addWidget(self.line_count_label)
        add_line_layout.addStretch()
        
        manual_layout.addLayout(add_line_layout)
        
        # Angle control for selected line
        angle_layout = QHBoxLayout()
        angle_label = QLabel("Angle:")
        angle_label.setStyleSheet("color: white;")
        angle_layout.addWidget(angle_label)
        
        self.angle_spinbox = QSpinBox()
        self.angle_spinbox.setRange(0, 359)
        self.angle_spinbox.setValue(0)
        self.angle_spinbox.setSuffix("°")
        self.angle_spinbox.setFixedWidth(80)
        self.angle_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #404040;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                padding: 4px;
            }
        """)
        self.angle_spinbox.valueChanged.connect(self.on_angle_changed)
        angle_layout.addWidget(self.angle_spinbox)
        
        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(0, 359)
        self.angle_slider.setValue(0)
        self.angle_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #666;
                height: 6px;
                background: #404040;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: 1px solid #005a9e;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
        """)
        self.angle_slider.valueChanged.connect(self.angle_spinbox.setValue)
        angle_layout.addWidget(self.angle_slider)
        
        manual_layout.addLayout(angle_layout)
        
        # Remove line button
        self.remove_line_btn = QPushButton("Remove Last Line")
        self.remove_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #7a2a2a;
                border: 1px solid #9a3a3a;
                border-radius: 3px;
                color: white;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #9a3a3a;
            }
            QPushButton:disabled {
                background-color: #404040;
                border-color: #555;
                color: #888;
            }
        """)
        self.remove_line_btn.clicked.connect(self.remove_last_line)
        manual_layout.addWidget(self.remove_line_btn)
        
        main_layout.addWidget(manual_group)
        
        # Info label
        info_label = QLabel("💡 Tip: Combine lines for complex patterns!")
        info_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        main_layout.addStretch()
        
        # Update UI state
        self.update_ui_state()
        
    def on_enable_toggled(self, checked):
        """Handle symmetry enable/disable"""
        self.canvas.symmetry.enabled = checked
        self.update_ui_state()
        self.canvas.viewport().update()
        self.symmetry_changed.emit()
        
    def apply_preset(self, preset_name):
        """Apply a symmetry preset"""
        if preset_name == "vertical":
            self.canvas.symmetry.clear_lines()
            self.canvas.symmetry.add_line(0)  # Vertical
        elif preset_name == "horizontal":
            self.canvas.symmetry.clear_lines()
            self.canvas.symmetry.add_line(90)  # Horizontal
        elif preset_name == "cross":
            self.canvas.symmetry.add_preset_cross()
        elif preset_name == "x":
            self.canvas.symmetry.add_preset_x()
        elif preset_name == "star":
            self.canvas.symmetry.add_preset_star()
        
        self.canvas.symmetry.enabled = True
        self.enable_btn.setChecked(True)
        self.update_ui_state()
        self.canvas.viewport().update()
        self.symmetry_changed.emit()
        
    def clear_lines(self):
        """Clear all symmetry lines"""
        self.canvas.symmetry.clear_lines()
        self.update_ui_state()
        self.canvas.viewport().update()
        self.symmetry_changed.emit()
        
    def add_line(self):
        """Add a new symmetry line"""
        angle = self.angle_spinbox.value()
        line = self.canvas.symmetry.add_line(angle)
        if line:
            self.update_ui_state()
            self.canvas.viewport().update()
            self.symmetry_changed.emit()
        
    def remove_last_line(self):
        """Remove the last symmetry line"""
        if self.canvas.symmetry.lines:
            self.canvas.symmetry.remove_line(len(self.canvas.symmetry.lines) - 1)
            self.update_ui_state()
            self.canvas.viewport().update()
            self.symmetry_changed.emit()
        
    def on_angle_changed(self, angle):
        """Handle angle change for the last line"""
        if self.canvas.symmetry.lines:
            # Update the last line's angle
            last_index = len(self.canvas.symmetry.lines) - 1
            self.canvas.symmetry.set_line_angle(last_index, angle)
            self.canvas.viewport().update()
            self.symmetry_changed.emit()
        
    def update_ui_state(self):
        """Update UI elements based on current state"""
        line_count = len(self.canvas.symmetry.lines)
        max_lines = self.canvas.symmetry.max_lines
        
        # Update line count label
        self.line_count_label.setText(f"Lines: {line_count}/{max_lines}")
        
        # Enable/disable buttons
        self.add_line_btn.setEnabled(line_count < max_lines)
        self.remove_line_btn.setEnabled(line_count > 0)
        
        # Update angle controls to show last line's angle
        if self.canvas.symmetry.lines:
            last_line = self.canvas.symmetry.lines[-1]
            self.angle_spinbox.blockSignals(True)
            self.angle_slider.blockSignals(True)
            self.angle_spinbox.setValue(int(last_line.angle))
            self.angle_slider.setValue(int(last_line.angle))
            self.angle_spinbox.blockSignals(False)
            self.angle_slider.blockSignals(False)
