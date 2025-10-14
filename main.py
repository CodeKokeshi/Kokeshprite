#!/usr/bin/env python3
"""
Kokeshprite - Pixel Art Editor
Main application entry point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow

def get_icon_path():
    """Get the path to the icon file, works for both dev and compiled exe"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Try .ico first (Windows), fallback to .png
    icon_ico = os.path.join(base_path, 'icon.ico')
    icon_png = os.path.join(base_path, 'icon.png')
    
    if os.path.exists(icon_ico):
        return icon_ico
    elif os.path.exists(icon_png):
        return icon_png
    return None

def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Kokeshprite")
    app.setApplicationVersion("0.1.0")
    
    # Set application icon (shows in taskbar and window title)
    icon_path = get_icon_path()
    if icon_path:
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()