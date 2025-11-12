"""
Color Palette Panel for Kokesprite
Contains color swatches and palette management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QPushButton, QLabel, QFrame, QScrollArea, QInputDialog,
                            QMessageBox, QFileDialog, QSizePolicy, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QPixmap, QPainter, QIcon
import random
import math

from .color_picker_widget import ColorPickerWidget

SWATCH_SIZE = 22  # Reduced from previous 30 for more compact UI

class ColorSwatch(QPushButton):
    """Individual color swatch button"""

    _checkerboard_base = None
    _checker_dark = QColor(70, 70, 70)
    _checker_light = QColor(110, 110, 110)
    _checker_tile = 4
    
    def __init__(self, color=QColor(255, 255, 255, 255)):
        super().__init__()
        self.color = QColor(color)
        self._selected = False
        self.setFixedSize(SWATCH_SIZE, SWATCH_SIZE)
        self.setIconSize(QSize(SWATCH_SIZE, SWATCH_SIZE))
        self.update_color()
        
    def update_color(self):
        """Update the swatch appearance"""
        if ColorSwatch._checkerboard_base is None:
            ColorSwatch._checkerboard_base = self._create_checkerboard_pixmap()
        pixmap = QPixmap(ColorSwatch._checkerboard_base)
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), self.color)
        painter.end()
        self.setIcon(QIcon(pixmap))
        self._apply_stylesheet()
        hex_argb = self.color.name(QColor.NameFormat.HexArgb).upper()
        self.setToolTip(
            f"Click to select, double-click to edit\n{hex_argb} | RGBA({self.color.red()}, {self.color.green()}, {self.color.blue()}, {self.color.alpha()})"
        )
        
    def set_color(self, color):
        """Set the color of this swatch"""
        self.color = QColor(color)
        self.update_color()

    def set_selected(self, selected: bool):
        if self._selected != selected:
            self._selected = selected
            self._apply_stylesheet()

    def _apply_stylesheet(self):
        if self._selected:
            border_color = "#f1c232"
            border_width = 3
        else:
            border_color = "#b8b8b8"
            border_width = 2
        
        # Check if this swatch matches the current color for highlighting
        is_current_color = False
        try:
            # Find the palette panel
            parent_panel = self.parent()
            while parent_panel and not hasattr(parent_panel, 'current_color_swatch'):
                parent_panel = parent_panel.parent()
            
            if (parent_panel and hasattr(parent_panel, 'current_color_swatch') and 
                parent_panel.current_color_swatch and 
                self.color.rgba() == parent_panel.current_color_swatch.color.rgba()):
                is_current_color = True
        except:
            pass
        
        # If this matches current color, add highlighting border
        if is_current_color:
            # Use black border if swatch is white/light, otherwise white border
            if self.color.lightnessF() > 0.8:  # Light color - use black border
                highlight_color = "#000000"
            else:  # Dark color - use white border  
                highlight_color = "#ffffff"
            
            self.setStyleSheet(f"""
                QPushButton {{
                    border: {border_width}px solid {border_color};
                    border-radius: 4px;
                    background-color: transparent;
                    outline: 2px solid {highlight_color};
                    outline-offset: 1px;
                }}
                QPushButton:hover {{
                    border: 3px solid #3daee9;
                }}
                QPushButton:pressed {{
                    border: 3px solid #1e6ca1;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    border: {border_width}px solid {border_color};
                    border-radius: 4px;
                    background-color: transparent;
                }}
                QPushButton:hover {{
                    border: 3px solid #3daee9;
                }}
                QPushButton:pressed {{
                    border: 3px solid #1e6ca1;
                }}
            """)

    @classmethod
    def _create_checkerboard_pixmap(cls) -> QPixmap:
        size = SWATCH_SIZE
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        tile = cls._checker_tile
        for y in range(0, size, tile):
            for x in range(0, size, tile):
                color = cls._checker_light if ((x // tile + y // tile) % 2 == 0) else cls._checker_dark
                painter.fillRect(x, y, tile, tile, color)
        painter.end()
        return pixmap
    def mouseDoubleClickEvent(self, event):
        # Emit a custom signal via parent palette by using event bubbling if needed
        # We'll let the parent intercept by installing an event filter or simpler: call back
        parent = self.parent()
        while parent and not hasattr(parent, 'edit_swatch_color'):
            parent = parent.parent()
        if parent and hasattr(parent, 'edit_swatch_color'):
            parent.edit_swatch_color(self)
        super().mouseDoubleClickEvent(event)

class ColorPalettePanel(QWidget):
    """Color palette panel with expandable colors"""
    
    # Signal emitted when color is selected
    color_selected = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.colors = []
        self.swatches = []
        self.selected_swatch = None
        self.max_columns = 8
        
        # Aseprite-style transparent slot (always first, not part of colors list)
        self.transparent_swatch = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the color palette UI"""
        # RESPONSIVE: Use preferred width instead of fixed
        preferred_width = (SWATCH_SIZE * self.max_columns) + 40
        self.setMinimumWidth(preferred_width)
        self.setMaximumWidth(preferred_width + 60)  # Allow some growth
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout(self)
        # RESPONSIVE: Smaller margins when space is limited
        self.main_layout.setContentsMargins(8, 5, 8, 5)
        self.main_layout.setSpacing(6)  # Reduced spacing for better fit
        
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
        self.current_color_swatch = ColorSwatch(QColor(0, 0, 0, 255))  # Black default
        self.main_layout.addWidget(self.current_color_swatch)
        self._update_current_color_label(self.current_color_swatch.color)
        
        # Inline color picker
        self.color_picker = ColorPickerWidget()
        self.color_picker.colorChanged.connect(self._on_picker_color_changed)
        # Ensure color picker fits within panel width
        self.color_picker.setMaximumWidth((SWATCH_SIZE * self.max_columns) + 20)
        self.main_layout.addWidget(self.color_picker)

        # SEPARATE FLOOR: Hex input (BEFORE buttons!) - created here, not in color picker
        hex_layout = QHBoxLayout()
        hex_layout.addWidget(QLabel("Hex:"))
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#RRGGBBAA")
        from PyQt6.QtCore import QRegularExpression
        from PyQt6.QtGui import QRegularExpressionValidator
        validator = QRegularExpressionValidator(QRegularExpression(r"^#?[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$"))
        self.hex_input.setValidator(validator)
        self.hex_input.returnPressed.connect(self._on_hex_entered)
        hex_layout.addWidget(self.hex_input)
        self.main_layout.addLayout(hex_layout)

        # Add spacing between hex and buttons
        self.main_layout.addSpacing(8)

        # Picker controls (AFTER hex input!)
        picker_controls = QVBoxLayout()
        picker_controls.setSpacing(6)
        self.apply_picker_button = QPushButton("Apply to Selected")
        self.apply_picker_button.setToolTip("Apply the picker color to the selected swatch")
        self.apply_picker_button.clicked.connect(self.apply_color_to_selected_swatch)
        self.apply_picker_button.setEnabled(False)

        self.add_picker_button = QPushButton("Add Swatch")
        self.add_picker_button.setToolTip("Add the picker color as a new swatch")
        self.add_picker_button.clicked.connect(self.add_picker_color_to_palette)

        for btn in (self.apply_picker_button, self.add_picker_button):
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(30)  # Same height, but expanding width for uniformity
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: none;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    background-color: #666;
                    color: #bbb;
                }
                QPushButton:hover:!disabled {
                    background-color: #555;
                }
                QPushButton:pressed:!disabled {
                    background-color: #333;
                }
            """)

        picker_controls.addWidget(self.apply_picker_button)
        picker_controls.addWidget(self.add_picker_button)
        picker_controls.addStretch(1)
        self.main_layout.addLayout(picker_controls)
        
        # Add spacing to separate from palette section
        self.main_layout.addSpacing(15)

        # Add another separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line2)
        
        # Palette colors label
        palette_label = QLabel("Palette Colors:")
        self.main_layout.addWidget(palette_label)
        
        # Color grid container with dedicated scroll area
        self.swatch_scroll_area = QScrollArea()
        self.swatch_scroll_area.setWidgetResizable(True)
        self.swatch_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.swatch_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.swatch_scroll_area.setFrameShape(QFrame.Shape.Box)  # Add visible border
        self.swatch_scroll_area.setLineWidth(1)
        self.swatch_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #666;
                border-radius: 4px;
                background-color: #333;
            }
        """)
        # Calculate proper height: 4 rows of swatches + some padding (smaller, we have scrollbars)
        proper_height = (SWATCH_SIZE * 4) + 16  # 4 rows max visible + padding
        self.swatch_scroll_area.setFixedHeight(proper_height)
        self.swatch_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.swatch_scroll_area.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.color_grid_widget = QWidget()
        self.color_grid_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.color_grid = QGridLayout(self.color_grid_widget)
        self.color_grid.setContentsMargins(0, 0, 0, 0)
        self.color_grid.setHorizontalSpacing(0)
        self.color_grid.setVerticalSpacing(0)
        self.color_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.swatch_scroll_area.setWidget(self.color_grid_widget)

        self.main_layout.addWidget(self.swatch_scroll_area)
        
        # Create Aseprite-style transparent slot (always first)
        self._create_transparent_slot()
        
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
        self.colors.append(QColor(color))
        
        # Create swatch
        swatch = ColorSwatch(color)
        # Connect using swatch instance so edited color is picked up dynamically
        def handle_click(checked=False, s=swatch):
            self.select_color(s.color, s)
        swatch.clicked.connect(handle_click)
        swatch.set_selected(False)
        self.swatches.append(swatch)
        self._refresh_swatch_grid()
        
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
                color = QColor(r, g, b, 255)
                self.add_color_to_palette(color)
                
            print(f"Added {count} random colors to palette")

    def _refresh_swatch_grid(self):
        while self.color_grid.count():
            item = self.color_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(self.color_grid_widget)

        # Always place transparent slot at (0,0)
        if self.transparent_swatch:
            self.color_grid.addWidget(self.transparent_swatch, 0, 0)

        # Place regular swatches starting from position 1
        total = len(self.swatches)
        columns = self.max_columns
        
        for index, swatch in enumerate(self.swatches):
            # Calculate position offset by 1 (transparent slot is at 0)
            position = index + 1
            row = position // columns
            col = position % columns
            self.color_grid.addWidget(swatch, row, col)
        self.color_grid_widget.adjustSize()

    def _create_transparent_slot(self):
        """Create the Aseprite-style transparent slot (always first)"""
        transparent_color = QColor(0, 0, 0, 0)  # Fully transparent
        self.transparent_swatch = ColorSwatch(transparent_color)
        
        def handle_transparent_click(checked=False):
            self.select_color(transparent_color, self.transparent_swatch)
        
        self.transparent_swatch.clicked.connect(handle_transparent_click)
        self.transparent_swatch.set_selected(False)
        
        # Add transparent slot to grid
        self._refresh_swatch_grid()

    def add_picker_color_to_palette(self):
        """Add the current picker color as a new swatch"""
        color = self.color_picker.current_color()
        self.add_color_to_palette(color)
        self.select_color(color, self.swatches[-1])

    def apply_color_to_selected_swatch(self):
        """Apply picker color to the currently selected swatch"""
        if not self.selected_swatch:
            return

        updated_color = self.color_picker.current_color()
        self.selected_swatch.set_color(updated_color)
        try:
            idx = self.swatches.index(self.selected_swatch)
            self.colors[idx] = QColor(updated_color)
        except ValueError:
            pass

        self.set_current_color(updated_color, sync_picker=False)
        self.color_selected.emit(updated_color)
            
    def select_color(self, color, swatch: ColorSwatch | None = None):
        """Select a color from the palette"""
        # Handle transparent swatch specially
        if swatch is self.transparent_swatch:
            pass  # Use the provided transparent swatch
        elif swatch is not None and swatch not in self.swatches and swatch is not self.transparent_swatch:
            swatch = None

        if swatch is None:
            # Check transparent swatch first
            if self.transparent_swatch and self.transparent_swatch.color == color:
                swatch = self.transparent_swatch
            else:
                # Check regular swatches
                for candidate in self.swatches:
                    if candidate.color == color:
                        swatch = candidate
                        break

        if self.selected_swatch and self.selected_swatch is not swatch:
            self.selected_swatch.set_selected(False)

        self.selected_swatch = swatch

        if self.selected_swatch:
            self.selected_swatch.set_selected(True)

        if hasattr(self, 'apply_picker_button'):
            self.apply_picker_button.setEnabled(self.selected_swatch is not None)

        self.set_current_color(color)
        self.color_selected.emit(color)
        print(f"Selected color: {color.name(QColor.NameFormat.HexArgb)}")

    def edit_swatch_color(self, swatch):
        """Focus the inline picker for editing a swatch"""
        self.select_color(swatch.color, swatch)
        self.color_picker.set_color(swatch.color, emit_signal=False)
        # Focus hex input in palette panel (not color picker)
        if hasattr(self, 'hex_input'):
            self.hex_input.setFocus()
            self.hex_input.selectAll()
        
    def set_current_color(self, color, sync_picker: bool = True):
        """Set the current color (from eyedropper, picker, etc.)"""
        self.current_color_swatch.set_color(color)
        self._update_current_color_label(color)
        if (not self.selected_swatch) or (self.selected_swatch.color != color):
            match = next((sw for sw in self.swatches if sw.color == color), None)
            if match is not None:
                if self.selected_swatch and self.selected_swatch is not match:
                    self.selected_swatch.set_selected(False)
                self.selected_swatch = match
                self.selected_swatch.set_selected(True)
        if hasattr(self, 'apply_picker_button'):
            self.apply_picker_button.setEnabled(self.selected_swatch is not None)
        if sync_picker and hasattr(self, 'color_picker'):
            self.color_picker.set_color(color, emit_signal=False)
        
        # Refresh all swatch styles to update current color highlighting
        self._refresh_all_swatch_styles()

    def _refresh_all_swatch_styles(self):
        """Refresh styling for all swatches to update current color highlighting"""
        for swatch in self.swatches:
            swatch._apply_stylesheet()
        if self.transparent_swatch:
            self.transparent_swatch._apply_stylesheet()

    def _on_picker_color_changed(self, color: QColor):
        """Handle updates from the embedded color picker"""
        self.set_current_color(color, sync_picker=False)
        self.color_selected.emit(color)
        
    def _on_hex_entered(self):
        """Handle hex input changes"""
        text = self.hex_input.text().lstrip('#')
        if len(text) == 6:
            text += 'FF'
        color = QColor('#' + text)
        if color.isValid():
            self.color_picker.set_color(color, emit_signal=True)
        
    def get_current_color(self):
        """Get the currently selected color"""
        return self.current_color_swatch.color

    def _update_current_color_label(self, color: QColor):
        hex_value = color.name(QColor.NameFormat.HexArgb).upper()
        self.current_color_label.setText(f"Current Color: {hex_value}")

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
            if len(token) not in (6, 8) or any(c not in '0123456789aAbBcCdDeEfF' for c in token):
                # Not a valid color spec; skip silently (or we could warn)
                continue
            r = int(token[0:2], 16)
            g = int(token[2:4], 16)
            b = int(token[4:6], 16)
            a = 255
            if len(token) == 8:
                a = int(token[6:8], 16)
            parsed_colors.append(QColor(r, g, b, a))

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
        self.selected_swatch = None
        if hasattr(self, 'apply_picker_button'):
            self.apply_picker_button.setEnabled(False)
            self._refresh_swatch_grid()
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