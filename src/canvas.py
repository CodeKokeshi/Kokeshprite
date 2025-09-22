"""
Canvas widget for pixel art drawing
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QScreen
from .system_eyedropper import SystemEyedropper

class Canvas(QGraphicsView):
    """Main drawing canvas using QGraphicsView"""
    
    # Signals
    mouse_position_changed = pyqtSignal(int, int)  # x, y coordinates
    color_picked = pyqtSignal(QColor)  # Picked color from eyedropper
    
    def __init__(self, width=64, height=64):
        super().__init__()
        
        # Canvas properties
        self.canvas_width = width
        self.canvas_height = height
        self.zoom_factor = 8  # Start at 8x zoom for pixel art
        
        # Drawing properties
        self.brush_size = 1
        self.current_color = QColor(0, 0, 0)  # Black
        self.current_tool = "brush"  # Current selected tool
        self.drawing = False
        self.last_point = None
        
        # System eyedropper
        self.system_eyedropper = SystemEyedropper()
        self.system_eyedropper.color_picked.connect(self.on_system_color_picked)
        
        # Enable key press events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize the canvas
        self.init_canvas()
        
    def init_canvas(self):
        """Initialize the graphics scene and canvas"""
        # Create the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Create the pixmap for drawing
        self.pixmap = QPixmap(self.canvas_width, self.canvas_height)
        self.pixmap.fill(Qt.GlobalColor.white)  # White background
        
        # Add pixmap to scene
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.pixmap_item)
        
        # Set up the view
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # Pixel perfect
        
        # Set initial zoom
        self.scale(self.zoom_factor, self.zoom_factor)
        
        # Center the canvas
        self.centerOn(self.pixmap_item)
        
    def mousePressEvent(self, event):
        """Handle mouse press events for drawing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert screen coordinates to scene coordinates
            scene_pos = self.mapToScene(event.position().toPoint())
            canvas_pos = self.pixmap_item.mapFromScene(scene_pos)
            
            x, y = int(canvas_pos.x()), int(canvas_pos.y())
            
            # Check if click is within canvas bounds
            if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                if self.current_tool != "eyedropper":
                    # Normal drawing tools
                    self.drawing = True
                    self.last_point = (x, y)
                    self.use_current_tool(x, y)
                # Eyedropper is handled automatically by the system eyedropper
                
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drawing and cursor tracking"""
        # Convert screen coordinates to scene coordinates
        scene_pos = self.mapToScene(event.position().toPoint())
        canvas_pos = self.pixmap_item.mapFromScene(scene_pos)
        
        x, y = int(canvas_pos.x()), int(canvas_pos.y())
        
        # Emit mouse position for status bar
        self.mouse_position_changed.emit(x, y)
        
        # Continue drawing if left button is pressed
        if self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                # Use current tool from last point to current point
                if self.last_point and self.current_tool not in ["bucket", "eyedropper"]:
                    self.draw_line_with_tool(self.last_point[0], self.last_point[1], x, y)
                elif self.current_tool not in ["bucket", "eyedropper"]:
                    self.use_current_tool(x, y)
                self.last_point = (x, y)
                
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.last_point = None
            
    def draw_pixel(self, x, y):
        """Draw a single pixel at the given coordinates"""
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(self.current_color, 1))
        painter.drawPoint(x, y)
        painter.end()
        
        # Update the display
        self.pixmap_item.setPixmap(self.pixmap)
        
    def draw_line(self, x1, y1, x2, y2):
        """Draw a line between two points using Bresenham's algorithm"""
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(self.current_color, 1))
        
        # Simple line drawing - could be improved with Bresenham's algorithm
        painter.drawLine(x1, y1, x2, y2)
        painter.end()
        
        # Update the display
        self.pixmap_item.setPixmap(self.pixmap)
        
    def use_current_tool(self, x, y):
        """Use the currently selected tool at the given coordinates"""
        if self.current_tool == "brush":
            self.draw_pixel(x, y)
        elif self.current_tool == "eraser":
            self.erase_pixel(x, y)
        elif self.current_tool == "bucket":
            self.bucket_fill(x, y)
            
    def draw_line_with_tool(self, x1, y1, x2, y2):
        """Draw a line using the current tool"""
        if self.current_tool == "brush":
            self.draw_line(x1, y1, x2, y2)
        elif self.current_tool == "eraser":
            self.erase_line(x1, y1, x2, y2)
        # Bucket tool doesn't need line drawing
        
    def erase_pixel(self, x, y):
        """Erase a single pixel (make it white)"""
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(QColor(255, 255, 255), 1))  # White color
        painter.drawPoint(x, y)
        painter.end()
        
        # Update the display
        self.pixmap_item.setPixmap(self.pixmap)
        
    def erase_line(self, x1, y1, x2, y2):
        """Erase a line (make it white)"""
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(QColor(255, 255, 255), 1))  # White color
        painter.drawLine(x1, y1, x2, y2)
        painter.end()
        
        # Update the display
        self.pixmap_item.setPixmap(self.pixmap)
        
    def bucket_fill(self, x, y):
        """Fill an area with the current color (improved flood fill)"""
        # Get the image as QImage for pixel manipulation
        image = self.pixmap.toImage()
        target_color = image.pixelColor(x, y)
        fill_color = self.current_color
        
        # Don't fill if target and fill colors are the same
        if target_color == fill_color:
            return
        
        print(f"Bucket fill: target={target_color.name()}, fill={fill_color.name()}")  # Debug
            
        # Use a queue-based flood fill algorithm (more efficient)
        from collections import deque
        queue = deque([(x, y)])
        visited = set()
        
        while queue:
            px, py = queue.popleft()
            
            # Check bounds and if already visited
            if (px < 0 or px >= self.canvas_width or 
                py < 0 or py >= self.canvas_height or 
                (px, py) in visited):
                continue
                
            # Check if pixel color matches target
            current_pixel_color = image.pixelColor(px, py)
            if current_pixel_color != target_color:
                continue
                
            # Fill the pixel
            image.setPixelColor(px, py, fill_color)
            visited.add((px, py))
            
            # Add neighboring pixels to queue
            queue.extend([(px+1, py), (px-1, py), (px, py+1), (px, py-1)])
        
        print(f"Filled {len(visited)} pixels")  # Debug
        
        # Update the pixmap with the filled image
        self.pixmap = QPixmap.fromImage(image)
        self.pixmap_item.setPixmap(self.pixmap)
        
    def on_system_color_picked(self, color):
        """Handle color picked from system eyedropper"""
        self.current_color = color
        self.color_picked.emit(color)
        print(f"System eyedropper picked color: {color.name()}")
        
    def set_brush_color(self, color):
        """Set the current brush color"""
        self.current_color = color
        
    def set_brush_size(self, size):
        """Set the current brush size"""
        self.brush_size = size
        
    def set_current_tool(self, tool_name):
        """Set the current drawing tool"""
        # If switching away from eyedropper, disable it
        if self.current_tool == "eyedropper" and tool_name != "eyedropper":
            self.system_eyedropper.set_enabled(False)
            
        self.current_tool = tool_name
        
        # If switching to eyedropper, auto-activate it
        if tool_name == "eyedropper":
            self.system_eyedropper.set_enabled(True)
            
        print(f"Canvas tool changed to: {tool_name}")  # Debug
        
    def clear_canvas(self):
        """Clear the entire canvas"""
        self.pixmap.fill(Qt.GlobalColor.white)
        self.pixmap_item.setPixmap(self.pixmap)
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        # Zoom in/out with mouse wheel
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)
        
        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        # Ctrl+E for system-wide eyedropper
        if event.key() == Qt.Key.Key_E and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.system_eyedropper.start_eyedropper()
        else:
            super().keyPressEvent(event)