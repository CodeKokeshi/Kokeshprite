"""
Color Palette Panel for Kokeshprite
Contains color swatches and palette management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QFrame, QScrollArea, QInputDialog,
                            QMessageBox, QColorDialog, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
import random

SWATCH_SIZE = 22  # Reduced from previous 30 for more compact UI

class ColorSwatch(QPushButton):
    """Individual color swatch button"""
    
    def __init__(self, color=QColor(255, 255, 255)):
        super().__init__()
        self.color = color
        self.setFixedSize(SWATCH_SIZE, SWATCH_SIZE)
        self.update_color()
        self.setToolTip("Click to select, double-click to edit")
        
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
    def mouseDoubleClickEvent(self, event):
        # Emit a custom signal via parent palette by using event bubbling if needed
        # We'll let the parent intercept by installing an event filter or simpler: call back
        parent = self.parent()
        while parent and not hasattr(parent, 'edit_swatch_color'):
            parent = parent.parent()
        if parent and hasattr(parent, 'edit_swatch_color'):
            parent.edit_swatch_color(self)
        super().mouseDoubleClickEvent(event)

class ColorPalettePanel(QScrollArea):
    """Color palette panel with expandable colors"""
    
    # Signal emitted when color is selected
    color_selected = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.colors = []
        self.swatches = []
        self.selected_swatch = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the color palette UI"""
        # Set fixed width and scroll properties
        # Width dynamic: 4 columns + margins; extra padding so vertical scrollbar never overlaps content
        # Previous: +36; increased slightly for better clearance
        self.setFixedWidth((SWATCH_SIZE * 4) + 48)
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
        self.color_grid.setSpacing(1)
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

        # Import .hex palette button
        self.import_button = QPushButton("📥 Import .hex")
        self.import_button.setToolTip("Import a .hex palette file (one hex per line)")
        self.import_button.clicked.connect(self.import_hex_palette)
        self.import_button.setStyleSheet("""
            QPushButton {
                background-color: #2d7dd2;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2569b1; }
            QPushButton:pressed { background-color: #1e578f; }
        """)
        self.main_layout.addWidget(self.import_button)
        
        # Add stretch to push everything to top
        self.main_layout.addStretch()
        
        # Initialize with 8 random colors
        self.create_initial_palette()
        
    def create_initial_palette(self):
        """Create initial palette with 8 random colors"""
        for _ in range(8):
            # Generate random RGB values
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = QColor(r, g, b)
            self.add_color_to_palette(color)
        
        # Select the first color by default
        if self.swatches:
            self.select_color(self.swatches[0].color)
        
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
        # Connect using swatch instance so edited color is picked up dynamically
        def handle_click(checked=False, s=swatch):
            self.select_color(s.color)
        swatch.clicked.connect(handle_click)
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
        # Find swatch matching color (first match) to set selected_swatch reference
        # If user clicked a swatch, click handler already supplies its current color; we map swatch by color attribute
        for sw in self.swatches:
            if sw.color == color:
                self.selected_swatch = sw
                break
        self.current_color_swatch.set_color(color)
        self.color_selected.emit(color)
        print(f"Selected color: {color.name()}")

    def edit_swatch_color(self, swatch):
        """Open a QColorDialog to edit a swatch's color and update palette list"""
        initial = swatch.color
        new_color = QColorDialog.getColor(initial, self, "Edit Color")
        if new_color.isValid():
            swatch.set_color(new_color)
            # Update internal colors list to keep in sync
            try:
                idx = self.swatches.index(swatch)
                self.colors[idx] = new_color
            except ValueError:
                pass
            # If edited swatch was current, update current display
            if self.selected_swatch is swatch:
                # Auto-update current color and emit so brush updates
                self.set_current_color(new_color)
                self.color_selected.emit(new_color)
            print(f"Edited swatch color -> {new_color.name()}")
        
    def set_current_color(self, color):
        """Set the current color (from eyedropper, etc.)"""
        self.current_color_swatch.set_color(color)
        
    def get_current_color(self):
        """Get the currently selected color"""
        return self.current_color_swatch.color

    # -------------- Palette Import (.hex) --------------
    def import_hex_palette(self):
        """Import a .hex file and replace entire palette.
        Format: each non-empty line contains a hex like #RRGGBB or RRGGBB.
        Lines starting with ';' or '#' (comment lines) are ignored unless it's a valid color token.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Import .hex Palette", "", "Hex Palette (*.hex);;All Files (*)")
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            QMessageBox.warning(self, "Import Failed", f"Could not read file:\n{e}")
            return

        parsed_colors = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            # Allow comments
            if line.startswith(';'):
                continue
            # Accept lines like #FFAABB or FFAABB
            if line.startswith('#'):
                token = line[1:]
            else:
                token = line
            if len(token) != 6 or any(c not in '0123456789aAbBcCdDeEfF' for c in token):
                # Not a valid color spec; skip silently (or we could warn)
                continue
            r = int(token[0:2], 16)
            g = int(token[2:4], 16)
            b = int(token[4:6], 16)
            parsed_colors.append(QColor(r, g, b))

        if not parsed_colors:
            QMessageBox.information(self, "No Colors", "No valid hex colors found in file.")
            return

        # Replace palette
        self._replace_palette(parsed_colors)
        print(f"Imported {len(parsed_colors)} colors from {file_path}")

    def _replace_palette(self, colors):
        # Clear existing structures
        self.colors.clear()
        # Remove swatch widgets from layout
        for sw in self.swatches:
            sw.setParent(None)
        self.swatches.clear()
        # Re-add all colors
        for c in colors:
            self.add_color_to_palette(c)
        # Reset selection to first color
        if self.swatches:
            first = self.swatches[0]
            self.select_color(first.color)

    def sort_palette_by_method(self, method_name):
        """Sort palette colors by the selected method."""
        if len(self.colors) < 2:
            return  # Nothing to sort
        
        if method_name == "HSV Similarity (Original)":
            self._sort_by_hsv_similarity()
        elif method_name == "Hue Only":
            self._sort_by_hue()
        elif method_name == "Saturation Only":
            self._sort_by_saturation()
        elif method_name == "Value/Brightness Only":
            self._sort_by_value()
        elif method_name == "Red Component":
            self._sort_by_red()
        elif method_name == "Green Component":
            self._sort_by_green()
        elif method_name == "Blue Component":
            self._sort_by_blue()
        elif method_name == "RGB Luminance":
            self._sort_by_luminance()
        elif method_name == "Color Temperature":
            self._sort_by_temperature()
        elif method_name == "Complementary Groups":
            self._sort_by_complementary()
        elif method_name == "Random Shuffle":
            self._sort_random()
        
        print(f"Sorted {len(self.colors)} colors by: {method_name}")
    
    def _sort_by_hsv_similarity(self):
        """Original HSV similarity sorting."""
        color_data = []
        for color in self.colors:
            h, s, v, _ = color.getHsv()
            h_norm = h / 359.0 if h >= 0 else 0
            s_norm = s / 255.0
            v_norm = v / 255.0
            
            if s < 30:  # Gray colors
                sort_key = (999, v_norm, s_norm)
            else:
                sort_key = (h_norm, s_norm, v_norm)
            
            color_data.append((sort_key, color))
        
        color_data.sort(key=lambda x: x[0])
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_hue(self):
        """Sort by hue component only."""
        color_data = []
        for color in self.colors:
            h, s, v, _ = color.getHsv()
            # Put grays (low saturation) at the end
            if s < 20:
                sort_key = 999  # End of spectrum
            else:
                sort_key = h if h >= 0 else 0
            color_data.append((sort_key, color))
        
        color_data.sort(key=lambda x: x[0])
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_saturation(self):
        """Sort by saturation component only."""
        color_data = []
        for color in self.colors:
            h, s, v, _ = color.getHsv()
            color_data.append((s, color))
        
        color_data.sort(key=lambda x: x[0], reverse=True)  # High sat first
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_value(self):
        """Sort by value/brightness component only."""
        color_data = []
        for color in self.colors:
            h, s, v, _ = color.getHsv()
            color_data.append((v, color))
        
        color_data.sort(key=lambda x: x[0], reverse=True)  # Bright first
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_red(self):
        """Sort by red component."""
        color_data = [(color.red(), color) for color in self.colors]
        color_data.sort(key=lambda x: x[0], reverse=True)
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_green(self):
        """Sort by green component."""
        color_data = [(color.green(), color) for color in self.colors]
        color_data.sort(key=lambda x: x[0], reverse=True)
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_blue(self):
        """Sort by blue component."""
        color_data = [(color.blue(), color) for color in self.colors]
        color_data.sort(key=lambda x: x[0], reverse=True)
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_luminance(self):
        """Sort by perceived luminance (weighted RGB)."""
        color_data = []
        for color in self.colors:
            # Standard luminance formula
            luminance = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
            color_data.append((luminance, color))
        
        color_data.sort(key=lambda x: x[0], reverse=True)  # Bright first
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_temperature(self):
        """Sort by color temperature (warm to cool)."""
        color_data = []
        for color in self.colors:
            r, g, b = color.red(), color.green(), color.blue()
            # Simple temperature heuristic: warm colors have more red/yellow
            temperature = (r + g * 0.5) - (b * 1.5)
            color_data.append((temperature, color))
        
        color_data.sort(key=lambda x: x[0], reverse=True)  # Warm first
        sorted_colors = [item[1] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_by_complementary(self):
        """Group colors by complementary pairs."""
        color_data = []
        for color in self.colors:
            h, s, v, _ = color.getHsv()
            if s < 20:  # Grays
                group_key = 999  # Put at end
            else:
                # Group by complementary zones (every 30 degrees)
                hue_zone = (h // 30) if h >= 0 else 0
                group_key = hue_zone
            
            color_data.append((group_key, h if h >= 0 else 0, s, color))
        
        color_data.sort(key=lambda x: (x[0], x[1]))  # Group, then hue within group
        sorted_colors = [item[3] for item in color_data]
        self._replace_palette(sorted_colors)
    
    def _sort_random(self):
        """Randomly shuffle the palette."""
        import random
        colors_copy = self.colors.copy()
        random.shuffle(colors_copy)
        self._replace_palette(colors_copy)