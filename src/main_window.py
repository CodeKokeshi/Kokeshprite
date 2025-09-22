"""
Main Window for Kokeshprite Pixel Art Editor
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QMenuBar, QStatusBar, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from .canvas import Canvas
from .tools_panel import ToolsPanel
from .color_palette_panel import ColorPalettePanel

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Kokeshprite - Pixel Art Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create color palette panel (left side)
        self.color_palette = ColorPalettePanel()
        main_layout.addWidget(self.color_palette)
        
        # Create canvas (center)
        self.canvas = Canvas()
        main_layout.addWidget(self.canvas)
        
        # Create tools panel (right side)
        self.tools_panel = ToolsPanel()
        main_layout.addWidget(self.tools_panel)
        
        # Connect signals
        self.canvas.mouse_position_changed.connect(self.update_coordinates)
        self.tools_panel.tool_changed.connect(self.canvas.set_current_tool)
        self.color_palette.color_selected.connect(self.canvas.set_brush_color)
        self.canvas.color_picked.connect(self.color_palette.set_current_color)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        edit_menu.addAction(redo_action)
        
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