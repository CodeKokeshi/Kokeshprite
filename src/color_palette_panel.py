"""
Color Palette Panel for Kokeshprite
Contains color swatches and palette management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QFrame, QScrollArea, QInputDialog,
                            QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
import random

class ColorSwatch(QPushButton):
    """Individual color swatch button"""
    
    def __init__(self, color=QColor(255, 255, 255)):
        super().__init__()
        self.color = color
        self.setFixedSize(30, 30)
        self.update_color()
        
    def update_color(self):
        """Update the swatch appearance"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 2px solid #ccc;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border-color: #007acc;
                border-width: 3px;
            }}
            QPushButton:pressed {{
                border-color: #005a9e;
                border-width: 3px;
            }}
        """)
        
    def set_color(self, color):
        """Set the color of this swatch"""
        self.color = color
        self.update_color()

class ColorPalettePanel(QScrollArea):
    """Color palette panel with expandable colors"""
    
    # Signal emitted when color is selected
    color_selected = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.colors = []
        self.swatches = []
        self.init_ui()
        self.create_default_palette()
        
    def init_ui(self):
        """Initialize the color palette UI"""
        # Set fixed width and scroll properties
        self.setFixedWidth(150)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Color palette title
        title = QLabel("Color Palette")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        title.setFont(font)
        self.main_layout.addWidget(title)
        
        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)
        
        # Current color display
        self.current_color_label = QLabel("Current Color:")
        self.main_layout.addWidget(self.current_color_label)
        
        # Current color swatch
        self.current_color_swatch = ColorSwatch(QColor(0, 0, 0))  # Black default
        self.main_layout.addWidget(self.current_color_swatch)
        
        # Add another separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line2)
        
        # Palette colors label
        palette_label = QLabel("Palette Colors:")
        self.main_layout.addWidget(palette_label)
        
        # Color grid container
        self.color_grid_widget = QWidget()
        self.color_grid = QGridLayout(self.color_grid_widget)
        self.color_grid.setSpacing(2)
        self.main_layout.addWidget(self.color_grid_widget)
        
        # Add colors button
        self.add_button = QPushButton("➕ Add Colors")
        self.add_button.setToolTip("Add more random colors to palette")
        self.add_button.clicked.connect(self.add_colors)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.main_layout.addWidget(self.add_button)
        
        # Add stretch to push everything to top
        self.main_layout.addStretch()
        
    def create_default_palette(self):
        """Create the default 16-color palette"""
        default_colors = [
            QColor(0, 0, 0),       # Black
            QColor(255, 255, 255), # White
            QColor(255, 0, 0),     # Red
            QColor(0, 255, 0),     # Green
            QColor(0, 0, 255),     # Blue
            QColor(255, 255, 0),   # Yellow
            QColor(255, 0, 255),   # Magenta
            QColor(0, 255, 255),   # Cyan
            QColor(128, 128, 128), # Gray
            QColor(128, 0, 0),     # Dark Red
            QColor(0, 128, 0),     # Dark Green
            QColor(0, 0, 128),     # Dark Blue
            QColor(128, 128, 0),   # Olive
            QColor(128, 0, 128),   # Purple
            QColor(0, 128, 128),   # Teal
            QColor(192, 192, 192)  # Light Gray
        ]
        
        for color in default_colors:
            self.add_color_to_palette(color)
            
    def add_color_to_palette(self, color):
        """Add a single color to the palette"""
        self.colors.append(color)
        
        # Create swatch
        swatch = ColorSwatch(color)
        swatch.clicked.connect(lambda checked, c=color: self.select_color(c))
        self.swatches.append(swatch)
        
        # Add to grid (4 columns)
        row = (len(self.swatches) - 1) // 4
        col = (len(self.swatches) - 1) % 4
        self.color_grid.addWidget(swatch, row, col)
        
    def add_colors(self):
        """Add more colors to the palette"""
        # Ask user how many colors to add
        count, ok = QInputDialog.getInt(
            self, 
            "Add Colors", 
            "How many colors you wanna expand to?",
            value=8,  # Default value
            min=1,    # Minimum
            max=100   # Maximum
        )
        
        if ok:
            # Generate random colors
            for _ in range(count):
                # Generate random RGB values
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                color = QColor(r, g, b)
                self.add_color_to_palette(color)
                
            print(f"Added {count} random colors to palette")
            
    def select_color(self, color):
        """Select a color from the palette"""
        self.current_color_swatch.set_color(color)
        self.color_selected.emit(color)
        print(f"Selected color: {color.name()}")
        
    def set_current_color(self, color):
        """Set the current color (from eyedropper, etc.)"""
        self.current_color_swatch.set_color(color)
        
    def get_current_color(self):
        """Get the currently selected color"""
        return self.current_color_swatch.color