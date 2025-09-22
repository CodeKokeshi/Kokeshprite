"""
Options panel for tool-specific settings
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QSlider, QSpinBox, QCheckBox, QButtonGroup,
                            QPushButton, QFrame, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class OptionsPanel(QWidget):
    """Top panel for tool-specific options"""
    
    # Signals for brush settings
    brush_settings_changed = pyqtSignal(dict)  # {size, shape, pixel_perfect}
    
    def __init__(self):
        super().__init__()
        self.current_tool = "brush"
        self.init_ui()
        
    def init_ui(self):
        """Initialize the options panel UI"""
        # Increase total height slightly to fit all controls while removing wasted top space
        self.setFixedHeight(88)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-bottom: 1px solid #555;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 2px; /* drastically reduced */
                padding-top: 4px; /* smaller padding */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
        """)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        # Reduce top margin to push content downward (actually reclaim area for controls)
        main_layout.setContentsMargins(10, 2, 10, 6)
        main_layout.setSpacing(14)
        
        # Create brush options
        self.create_brush_options(main_layout)
        
        # Add stretch to push everything to the left
        main_layout.addStretch()
        
        # Start with brush options visible
        self.set_current_tool("brush")
        
    def create_brush_options(self, main_layout):
        """Create brush-specific options (shared with eraser)"""
        # Brush/Eraser options group
        self.brush_group = QGroupBox("Brush Settings")
        brush_layout = QHBoxLayout(self.brush_group)
        brush_layout.setSpacing(14)
        brush_layout.setContentsMargins(10, 8, 10, 6)
        
        # Pixel Perfect toggle
        self.pixel_perfect_cb = QCheckBox("Pixel Perfect")
        self.pixel_perfect_cb.setStyleSheet("""
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #666;
                background-color: #404040;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #007acc;
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        self.pixel_perfect_cb.toggled.connect(self.emit_brush_settings)
        brush_layout.addWidget(self.pixel_perfect_cb)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        sep1.setStyleSheet("color: #555;")
        brush_layout.addWidget(sep1)
        
        # Brush size section
        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(3)
        
        # Size label and input
        size_input_layout = QHBoxLayout()
        size_input_layout.setSpacing(6)
        size_label = QLabel("Size:")
        size_input_layout.addWidget(size_label)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 64)
        self.size_spinbox.setValue(1)
        self.size_spinbox.setFixedWidth(64)
        self.size_spinbox.setFixedHeight(24)
        self.size_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #404040;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                padding: 4px;
                font-size: 12px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #555;
                border: none;
                width: 16px;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)
        self.size_spinbox.valueChanged.connect(self.on_size_changed)
        size_input_layout.addWidget(self.size_spinbox)
        size_layout.addLayout(size_input_layout)
        
        # Size slider
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 64)
        self.size_slider.setValue(1)
        self.size_slider.setFixedWidth(140)
        self.size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #666;
                height: 6px;
                background-color: #404040;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #007acc;
                border: 1px solid #005a9e;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        self.size_slider.valueChanged.connect(self.on_slider_changed)
        size_layout.addWidget(self.size_slider)
        
        brush_layout.addWidget(size_widget)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        sep2.setStyleSheet("color: #555;")
        brush_layout.addWidget(sep2)
        
        # Brush shape section
        shape_widget = QWidget()
        shape_layout = QVBoxLayout(shape_widget)
        shape_layout.setContentsMargins(0, 0, 0, 0)
        shape_layout.setSpacing(3)
        
        shape_label = QLabel("Shape:")
        shape_layout.addWidget(shape_label)
        
        shape_buttons_layout = QHBoxLayout()
        shape_buttons_layout.setSpacing(6)
        self.shape_group = QButtonGroup()
        
        # Circle button
        self.circle_btn = QPushButton("●")
        self.circle_btn.setCheckable(True)
        self.circle_btn.setChecked(True)
        self.circle_btn.setFixedSize(36, 28)
        self.circle_btn.setToolTip("Circle brush")
        
        # Square button  
        self.square_btn = QPushButton("■")
        self.square_btn.setCheckable(True)
        self.square_btn.setFixedSize(36, 28)
        self.square_btn.setToolTip("Square brush")
        
        # Style shape buttons
        shape_button_style = """
            QPushButton {
                background-color: #404040;
                border: 1px solid #666;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 2px;
            }
            QPushButton:checked {
                background-color: #007acc;
                border-color: #005a9e;
            }
            QPushButton:hover {
                border-color: #007acc;
            }
        """
        self.circle_btn.setStyleSheet(shape_button_style)
        self.square_btn.setStyleSheet(shape_button_style)
        
        self.shape_group.addButton(self.circle_btn, 0)  # Circle = 0
        self.shape_group.addButton(self.square_btn, 1)  # Square = 1
        self.shape_group.buttonToggled.connect(self.emit_brush_settings)
        
        shape_buttons_layout.addWidget(self.circle_btn)
        shape_buttons_layout.addWidget(self.square_btn)
        shape_layout.addLayout(shape_buttons_layout)
        
        brush_layout.addWidget(shape_widget)
        
        main_layout.addWidget(self.brush_group)
        
    def on_size_changed(self, value):
        """Handle size spinbox change"""
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(value)
        self.size_slider.blockSignals(False)
        self.emit_brush_settings()
        
    def on_slider_changed(self, value):
        """Handle size slider change"""
        self.size_spinbox.blockSignals(True)
        self.size_spinbox.setValue(value)
        self.size_spinbox.blockSignals(False)
        self.emit_brush_settings()
        
    def emit_brush_settings(self):
        """Emit current brush settings"""
        settings = {
            'size': self.size_spinbox.value(),
            'shape': 'circle' if self.circle_btn.isChecked() else 'square',
            'pixel_perfect': self.pixel_perfect_cb.isChecked()
        }
        self.brush_settings_changed.emit(settings)
        
    def set_current_tool(self, tool_name):
        """Show/hide appropriate options based on current tool"""
        self.current_tool = tool_name
        
        # Show brush options for both brush and eraser tools
        show_brush_options = tool_name in ["brush", "eraser"]
        self.brush_group.setVisible(show_brush_options)
        
        # Update group title based on tool
        if tool_name == "brush":
            self.brush_group.setTitle("Brush Settings")
        elif tool_name == "eraser":
            self.brush_group.setTitle("Eraser Settings")
        
        if show_brush_options:
            # Emit initial settings when brush/eraser is selected
            self.emit_brush_settings()