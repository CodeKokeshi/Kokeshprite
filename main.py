#!/usr/bin/env python3
"""
Kokeshprite - Pixel Art Editor
Main application entry point
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow

def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Kokeshprite")
    app.setApplicationVersion("0.1.0")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()