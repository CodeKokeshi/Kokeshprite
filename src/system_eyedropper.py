"""
System-wide Eyedropper Tool for Kokeshprite
Allows picking colors from anywhere on the screen with preview
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QColor, QCursor, QPainter, QPen, QFont, QScreen
import sys

class ColorPreviewWidget(QWidget):
    """Small preview window showing the color under cursor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(120, 80)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Color preview square
        self.color_square = QLabel()
        self.color_square.setFixedSize(60, 40)
        self.color_square.setStyleSheet("border: 2px solid black; background-color: white;")
        layout.addWidget(self.color_square, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Color info text
        self.color_text = QLabel("RGB: 255, 255, 255")
        self.color_text.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; padding: 2px; border-radius: 3px;")
        self.color_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(8)
        self.color_text.setFont(font)
        layout.addWidget(self.color_text)
        
        self.setLayout(layout)
        
    def update_color(self, color):
        """Update the preview with a new color"""
        self.color_square.setStyleSheet(f"border: 2px solid black; background-color: {color.name()};")
        self.color_text.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}")

class SystemEyedropper(QWidget):
    """System-wide eyedropper tool"""
    
    color_picked = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.preview_widget = ColorPreviewWidget()
        
        # Timer for updating color preview
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_color_preview)
        self.update_timer.setInterval(16)  # ~60fps for smooth preview
        
        # Store original cursor
        self.original_cursor = None
        
        # Track if we should be active
        self.should_be_active = False
        
    def start_eyedropper(self, auto_mode=False):
        """Start the system-wide eyedropper mode"""
        if self.is_active:
            return
            
        self.is_active = True
        self.should_be_active = True
        
        # Store original cursor and set crosshair cursor
        self.original_cursor = QApplication.overrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Install global event filter to capture mouse events
        QApplication.instance().installEventFilter(self)
        
        # Show preview widget
        self.preview_widget.show()
        
        # Start updating color preview
        self.update_timer.start()
        
        if not auto_mode:
            print("Eyedropper mode activated - click anywhere to pick color, press ESC to cancel")
            
    def set_enabled(self, enabled):
        """Enable or disable eyedropper mode (for tool switching)"""
        self.should_be_active = enabled
        if enabled:
            self.start_eyedropper(auto_mode=True)
        else:
            self.stop_eyedropper()
        
    def stop_eyedropper(self):
        """Stop the eyedropper mode"""
        if not self.is_active:
            return
            
        self.is_active = False
        
        # Stop timer
        self.update_timer.stop()
        
        # Hide preview
        self.preview_widget.hide()
        
        # Remove event filter
        QApplication.instance().removeEventFilter(self)
        
        # Restore original cursor
        if self.original_cursor:
            QApplication.setOverrideCursor(self.original_cursor)
        else:
            QApplication.restoreOverrideCursor()
            
        print("Eyedropper mode deactivated")
        
    def update_color_preview(self):
        """Update the color preview based on cursor position"""
        if not self.is_active:
            return
            
        # Get cursor position
        cursor_pos = QCursor.pos()
        
        # Check if cursor is over UI elements - temporarily disable if so
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
        if widget_under_cursor and self.should_check_ui_hover(widget_under_cursor):
            # Temporarily hide preview when over UI
            self.preview_widget.hide()
            return
        else:
            # Show preview when not over UI
            if not self.preview_widget.isVisible():
                self.preview_widget.show()
        
        # Position preview widget near cursor (offset to avoid blocking view)
        preview_pos = QPoint(cursor_pos.x() + 20, cursor_pos.y() - 100)
        
        # Keep preview on screen
        screen = QApplication.screenAt(cursor_pos)
        if screen:
            screen_rect = screen.geometry()
            if preview_pos.x() + self.preview_widget.width() > screen_rect.right():
                preview_pos.setX(cursor_pos.x() - self.preview_widget.width() - 20)
            if preview_pos.y() < screen_rect.top():
                preview_pos.setY(cursor_pos.y() + 20)
                
        self.preview_widget.move(preview_pos)
        
        # Get color at cursor position
        color = self.get_color_at_position(cursor_pos)
        if color:
            self.preview_widget.update_color(color)
            
    def should_check_ui_hover(self, widget):
        """Check if the widget under cursor is a UI element we should avoid"""
        # Check if it's part of our application UI
        if hasattr(widget, 'objectName'):
            # Skip UI elements like panels, buttons, etc.
            widget_class = widget.__class__.__name__
            if widget_class in ['ToolsPanel', 'ColorPalettePanel', 'QPushButton', 'QLabel', 'QScrollArea']:
                return True
        return False
            
    def get_color_at_position(self, pos):
        """Get the color at a specific screen position"""
        try:
            # Get the screen containing this position
            screen = QApplication.screenAt(pos)
            if not screen:
                screen = QApplication.primaryScreen()
                
            # Capture a 1x1 pixel at the cursor position
            pixmap = screen.grabWindow(0, pos.x(), pos.y(), 1, 1)
            
            if not pixmap.isNull():
                image = pixmap.toImage()
                if not image.isNull():
                    return image.pixelColor(0, 0)
        except Exception as e:
            print(f"Error getting color at position: {e}")
            
        return None
        
    def eventFilter(self, obj, event):
        """Filter events when eyedropper is active"""
        if not self.is_active:
            return False
            
        event_type = event.type()
        
        # Handle mouse click to pick color
        if event_type == event.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                cursor_pos = QCursor.pos()
                
                # Check if clicking on UI - if so, don't pick color, let UI handle it
                widget_under_cursor = QApplication.widgetAt(cursor_pos)
                if widget_under_cursor and self.should_check_ui_hover(widget_under_cursor):
                    return False  # Let the UI handle the click
                
                # Pick color from screen
                color = self.get_color_at_position(cursor_pos)
                if color:
                    self.color_picked.emit(color)
                    print(f"Picked color: {color.name()} at position {cursor_pos.x()}, {cursor_pos.y()}")
                return True
                
        # Handle ESC key to cancel and switch back to brush
        elif event_type == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                print("Eyedropper cancelled by user - switching to brush")
                # Signal that we want to switch to brush tool
                # This will be handled by the main application
                return True
                
        return False