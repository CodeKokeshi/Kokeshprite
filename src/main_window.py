"""
Main Window for Kokeshprite Pixel Art Editor
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QMenuBar, QStatusBar, QLabel, QStackedWidget, QFileDialog, QDialog, QFormLayout, QSpinBox, QPushButton, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QColor

from .canvas import Canvas
from .tools_panel import ToolsPanel
from .color_palette_panel import ColorPalettePanel
from .options_panel import OptionsPanel
from .start_screen import StartScreen
from .new_file_dialog import NewFileDialog

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_file_path: str | None = None
        self.document_modified: bool = False
        
        # Initialize background settings early
        self.background_tile_size = 2  # Default 2x2 tile size
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Kokeshprite - Pixel Art Editor")
        self.setGeometry(100, 100, 1200, 800)
        # Stacked root: start screen / editor
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Start screen
        self.start_screen = StartScreen()
        self.start_screen.new_file_requested.connect(self.show_new_file_dialog)
        self.start_screen.open_file_requested.connect(self.open_file_dialog)
        self.stacked.addWidget(self.start_screen)

        # Editor container widget
        self.editor_container = QWidget()
        editor_layout = QVBoxLayout(self.editor_container)
        editor_layout.setContentsMargins(0,0,0,0)
        editor_layout.setSpacing(0)

        self.options_panel = OptionsPanel()
        editor_layout.addWidget(self.options_panel)

        content_layout = QHBoxLayout()
        editor_layout.addLayout(content_layout)

        self.color_palette = ColorPalettePanel()
        content_layout.addWidget(self.color_palette)

        self.canvas = Canvas()
        content_layout.addWidget(self.canvas)

        self.tools_panel = ToolsPanel()
        content_layout.addWidget(self.tools_panel)

        self.stacked.addWidget(self.editor_container)
        self.stacked.setCurrentWidget(self.start_screen)

        # Connect signals (after canvas/tools created)
        self.canvas.mouse_position_changed.connect(self.update_coordinates)
        self.tools_panel.tool_changed.connect(self.canvas.set_current_tool)
        self.tools_panel.tool_changed.connect(self.options_panel.set_current_tool)
        self.color_palette.color_selected.connect(self.canvas.set_brush_color)
        self.canvas.color_picked.connect(self.color_palette.set_current_color)
        self.options_panel.brush_settings_changed.connect(self.canvas.update_brush_settings)
        self.canvas.modified.connect(self.on_canvas_modified)

        # Initialize canvas settings
        self.canvas.set_background_tile_size(self.background_tile_size)

        # Create menu bar & status bar
        self.create_menu_bar()
        self.create_status_bar()
        self.status_bar.setVisible(False)
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        self.new_action = QAction('New', self)
        self.new_action.setShortcut('Ctrl+N')
        self.new_action.triggered.connect(self.show_new_file_dialog)
        file_menu.addAction(self.new_action)
        
        self.open_action = QAction('Open', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(self.open_action)
        
        self.save_action = QAction('Save', self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction('Save As', self)
        self.save_as_action.setShortcuts([QKeySequence('Ctrl+Shift+S')])
        self.save_as_action.triggered.connect(self.save_file_as)
        self.save_as_action.setEnabled(False)
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')

        self.undo_action = QAction('Undo', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.triggered.connect(lambda: self.canvas.undo())
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction('Redo', self)
        self.redo_action.setShortcuts([QKeySequence('Ctrl+Y'), QKeySequence('Ctrl+Shift+Z')])
        self.redo_action.triggered.connect(lambda: self.canvas.redo())
        edit_menu.addAction(self.redo_action)

        # Add separator
        edit_menu.addSeparator()
        
        # Adjustments submenu
        adjustments_menu = edit_menu.addMenu('Adjustments')
        
        # Sort Color Palette submenu
        sort_palette_menu = adjustments_menu.addMenu('Sort Color Palette')
        
        # Sorting options
        sort_options = [
            ("HSV Similarity", "HSV Similarity (Original)"),
            ("By Hue", "Hue Only"),
            ("By Saturation", "Saturation Only"),
            ("By Brightness", "Value/Brightness Only"),
            ("By Red", "Red Component"),
            ("By Green", "Green Component"),
            ("By Blue", "Blue Component"),
            ("By Luminance", "RGB Luminance"),
            ("By Temperature", "Color Temperature"),
            ("Complementary Groups", "Complementary Groups"),
            ("Random Shuffle", "Random Shuffle")
        ]
        
        for menu_text, method_name in sort_options:
            action = QAction(menu_text, self)
            action.triggered.connect(lambda checked, method=method_name: self.sort_palette(method))
            sort_palette_menu.addAction(action)
        
        # Store adjustments menu for enabling/disabling
        self.adjustments_menu = adjustments_menu

        # View menu
        view_menu = menubar.addMenu('View')
        
        # Show submenu
        show_menu = view_menu.addMenu('Show')
        
        # Grid option with checkbox indicator
        self.grid_enabled = False  # Track grid state
        self.grid_width = 16  # Default grid cell width
        self.grid_height = 16  # Default grid cell height
        self.grid_color = QColor(0x1c, 0x34, 0xff)  # Default grid color #1c34ff
        
        self.grid_action = QAction('Grid', self)
        self.grid_action.triggered.connect(self.toggle_grid)
        self.update_grid_action_text()
        show_menu.addAction(self.grid_action)
        
        # Grid submenu
        grid_menu = view_menu.addMenu('Grid')
        
        # Grid Settings option
        grid_settings_action = QAction('Grid Settings...', self)
        grid_settings_action.triggered.connect(self.show_grid_settings)
        grid_menu.addAction(grid_settings_action)

        # Background submenu
        background_menu = view_menu.addMenu('Background')
        
        # Background Settings option
        background_settings_action = QAction('Background Settings...', self)
        background_settings_action.triggered.connect(self.show_background_settings)
        background_menu.addAction(background_settings_action)

        # Disable until a document is open
        self.set_edit_actions_enabled(False)

    def set_edit_actions_enabled(self, enabled: bool):
        self.undo_action.setEnabled(enabled)
        self.redo_action.setEnabled(enabled)
        self.adjustments_menu.setEnabled(enabled)
    
    def sort_palette(self, method_name):
        """Sort the color palette using the specified method."""
        if hasattr(self, 'color_palette'):
            self.color_palette.sort_palette_by_method(method_name)
    
    def toggle_grid(self):
        """Toggle the grid visibility state."""
        self.grid_enabled = not self.grid_enabled
        self.update_grid_action_text()
        # Refresh canvas to show/hide grid
        if hasattr(self, 'canvas'):
            self.canvas.set_grid_settings(self.grid_enabled, self.grid_width, self.grid_height, self.grid_color)
        print(f"Grid {'enabled' if self.grid_enabled else 'disabled'}")
    
    def update_grid_action_text(self):
        """Update the grid action text with checkbox indicator."""
        checkbox = "☑" if self.grid_enabled else "☐"
        self.grid_action.setText(f"Grid {checkbox}")
    
    def show_grid_settings(self):
        """Show the grid settings dialog."""
        # Get canvas dimensions properly
        canvas_width = self.canvas.canvas_width if hasattr(self, 'canvas') else 1024
        canvas_height = self.canvas.canvas_height if hasattr(self, 'canvas') else 1024
        
        dialog = GridSettingsDialog(self.grid_width, self.grid_height, 
                                   canvas_width, canvas_height, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.grid_width, self.grid_height = dialog.get_grid_size()
            # Update canvas with new grid settings
            if hasattr(self, 'canvas'):
                self.canvas.set_grid_settings(self.grid_enabled, self.grid_width, self.grid_height, self.grid_color)
            print(f"Grid settings updated: {self.grid_width}x{self.grid_height}")
    
    def show_background_settings(self):
        """Show the background settings dialog."""
        dialog = BackgroundSettingsDialog(self.background_tile_size, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.background_tile_size = dialog.get_tile_size()
            # Update canvas with new background settings
            if hasattr(self, 'canvas'):
                self.canvas.set_background_tile_size(self.background_tile_size)
            print(f"Background settings updated: {self.background_tile_size}x{self.background_tile_size} tile size")
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.statusBar()
        
        # Coordinates label
        self.coords_label = QLabel("X: 0, Y: 0")
        self.status_bar.addWidget(self.coords_label)
        
        # Zoom label
        self.zoom_label = QLabel("Zoom: 100%")
        self.status_bar.addPermanentWidget(self.zoom_label)
        
    def update_coordinates(self, x, y):
        """Update the coordinates display in the status bar"""
        self.coords_label.setText(f"X: {x}, Y: {y}")

    # -------------- Start Screen Actions --------------
    def show_new_file_dialog(self):
        # If an existing modified document is open, confirm before proceeding
        if not self.ensure_safe_to_discard():
            return
        dialog = NewFileDialog(self, default_width=64, default_height=64)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            w, h = dialog.get_dimensions()
            self.open_editor()
            self.canvas.resize_canvas(w, h)
            self.status_bar.setVisible(True)
            self.set_edit_actions_enabled(True)
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.current_file_path = None
            self.document_modified = True
            self.update_window_title()

    def open_file_dialog(self):
        # Confirm discard if there are unsaved changes
        if not self.ensure_safe_to_discard():
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.bmp *.gif *.jpg *.jpeg)")
        if not file_path:
            return
        from PyQt6.QtGui import QImage
        img = QImage(file_path)
        if img.isNull():
            QMessageBox.warning(self, "Open Failed", "Could not load image.")
            return
        if img.width() > 2048 or img.height() > 2048:
            QMessageBox.warning(self, "Too Large", "Image exceeds 2048x2048 limit.")
            return
        self.open_editor()
        self.canvas.load_image(img)
        self.status_bar.setVisible(True)
        self.set_edit_actions_enabled(True)
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)
        self.current_file_path = file_path
        self.document_modified = False
        self.update_window_title()

    def open_editor(self):
        self.stacked.setCurrentWidget(self.editor_container)

    # -------------- Modification Tracking --------------
    def on_canvas_modified(self):
        self.document_modified = True
        self.update_window_title()

    def update_window_title(self):
        base = "Kokeshprite - Pixel Art Editor"
        if self.current_file_path:
            import os
            name = os.path.basename(self.current_file_path)
        else:
            name = "Untitled"
        if self.document_modified:
            self.setWindowTitle(f"* {name} - {base}")
        else:
            self.setWindowTitle(f"{name} - {base}")

    # -------------- Save Logic --------------
    def save_file(self):
        if self.current_file_path is None:
            return self.save_file_as()
        self._write_pixmap(self.current_file_path)
        return True

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", self.current_file_path or "untitled.png", "PNG Image (*.png);;BMP Image (*.bmp);;JPEG Image (*.jpg *.jpeg)")
        if not file_path:
            return False
        if self._write_pixmap(file_path):
            self.current_file_path = file_path
            return True
        return False

    def _write_pixmap(self, path: str) -> bool:
        fmt = None
        lower = path.lower()
        if lower.endswith('.png'):
            fmt = 'PNG'
        elif lower.endswith('.bmp'):
            fmt = 'BMP'
        elif lower.endswith('.jpg') or lower.endswith('.jpeg'):
            fmt = 'JPEG'
        else:
            # Default to PNG
            path = path + '.png'
            fmt = 'PNG'
        if self.canvas.pixmap.save(path, fmt):
            self.document_modified = False
            self.update_window_title()
            return True
        QMessageBox.warning(self, "Save Failed", f"Could not save file to: {path}")
        return False

    # -------------- Unsaved Changes Handling --------------
    def ensure_safe_to_discard(self) -> bool:
        """Prompt the user to save/discard/cancel if there are unsaved changes.

        Returns True if it's safe to proceed (no changes, user saved, or user chose discard).
        Returns False if the action should be aborted (user canceled or save failed/canceled).
        """
        if not self.document_modified:
            return True
        # Build message box
        if self.current_file_path:
            import os
            name = os.path.basename(self.current_file_path)
        else:
            name = "Untitled"
        mbox = QMessageBox(self)
        mbox.setIcon(QMessageBox.Icon.Warning)
        mbox.setWindowTitle("Unsaved Changes")
        mbox.setText(f"You have unsaved changes to '{name}'.")
        mbox.setInformativeText("Do you want to save them before continuing?")
        save_btn = mbox.addButton(QMessageBox.StandardButton.Save)
        discard_btn = mbox.addButton(QMessageBox.StandardButton.Discard)
        cancel_btn = mbox.addButton(QMessageBox.StandardButton.Cancel)
        mbox.setDefaultButton(save_btn)
        mbox.exec()
        clicked = mbox.clickedButton()
        if clicked == save_btn:
            # Attempt to save; if user cancels Save As it returns False
            if self.save_file():
                return True
            return False  # Save failed or canceled
        elif clicked == discard_btn:
            return True
        else:  # Cancel
            return False

    def closeEvent(self, event):  # type: ignore[override]
        if self.ensure_safe_to_discard():
            event.accept()
        else:
            event.ignore()


class GridSettingsDialog(QDialog):
    """Dialog for configuring grid settings"""
    
    def __init__(self, current_width, current_height, canvas_width, canvas_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Settings")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        # Store canvas dimensions for validation
        self.max_width = canvas_width
        self.max_height = canvas_height
        
        # Create layout
        layout = QFormLayout(self)
        
        # Grid width input
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, self.max_width)
        self.width_spinbox.setValue(current_width)
        self.width_spinbox.setSuffix(" px")
        layout.addRow("Grid Width:", self.width_spinbox)
        
        # Grid height input
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, self.max_height)
        self.height_spinbox.setValue(current_height)
        self.height_spinbox.setSuffix(" px")
        layout.addRow("Grid Height:", self.height_spinbox)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_grid_size(self):
        """Return the selected grid width and height"""
        return self.width_spinbox.value(), self.height_spinbox.value()


class BackgroundSettingsDialog(QDialog):
    """Dialog for configuring checkered background settings"""
    
    def __init__(self, current_tile_size, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Background Settings")
        self.setModal(True)
        self.setFixedSize(350, 200)
        
        # Create layout
        layout = QFormLayout(self)
        
        # Add description
        description = QLabel("Configure the checkered background pattern:")
        description.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addRow(description)
        
        # Tile size input
        self.tile_size_spinbox = QSpinBox()
        self.tile_size_spinbox.setRange(1, 32)  # Reasonable range for tile sizes
        self.tile_size_spinbox.setValue(current_tile_size)
        self.tile_size_spinbox.setSuffix(" px")
        self.tile_size_spinbox.setToolTip("Size of each checkerboard tile in canvas pixels")
        layout.addRow("Tile Size:", self.tile_size_spinbox)
        
        # Add some preset buttons for common sizes
        presets_label = QLabel("Presets:")
        layout.addRow(presets_label)
        
        presets_widget = QWidget()
        presets_layout = QHBoxLayout(presets_widget)
        presets_layout.setContentsMargins(0, 0, 0, 0)
        
        preset_sizes = [1, 2, 4, 8, 16]
        for size in preset_sizes:
            btn = QPushButton(f"{size}x{size}")
            btn.setFixedWidth(50)
            btn.clicked.connect(lambda _, s=size: self.tile_size_spinbox.setValue(s))
            presets_layout.addWidget(btn)
        
        presets_layout.addStretch(1)
        layout.addRow(presets_widget)
        
        # Add explanation
        explanation = QLabel("Smaller values create a finer pattern.\nLarger values create bigger checkerboard squares.")
        explanation.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px;")
        layout.addRow(explanation)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_tile_size(self):
        """Return the selected tile size"""
        return self.tile_size_spinbox.value()