"""
Canvas widget for pixel art drawing
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QScreen, QCursor, QPainterPath
import math
from .system_eyedropper import SystemEyedropper
from .history import HistoryManager

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
        self.brush_shape = "circle"  # "circle" or "square"
        self.pixel_perfect = False
        self.current_color = QColor(0, 0, 0)  # Black
        self.current_tool = "brush"  # Current selected tool
        self.drawing = False
        self.last_point = None
        # Pixel perfect tracking (pending corner suppression)
        self._pp_committed = []  # committed pixels this stroke (list of (x,y))
        self._pp_pending = None  # a single pending pixel (x,y) waiting to see if it becomes part of a diagonal or a straight line
        self._pp_last = None     # last committed or accepted position
        
        # System eyedropper
        self.system_eyedropper = SystemEyedropper()
        self.system_eyedropper.color_picked.connect(self.on_system_color_picked)
        
        # Enable mouse tracking for cursor preview
        self.setMouseTracking(True)
        
        # Enable key press events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize the canvas
        self.init_canvas()
        # History manager (after canvas init so pixmap exists)
        self.history = HistoryManager()
        self.history.push(self.pixmap)
        
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
        
        # Update cursor for initial tool
        self.update_cursor()
        
    def update_cursor(self):
        """Update the cursor based on current tool and settings"""
        if self.current_tool in ["brush", "eraser"]:
            # Create custom brush cursor for both brush and eraser
            cursor_pixmap = self.create_brush_cursor()
            if cursor_pixmap:
                cursor = QCursor(cursor_pixmap)
                self.setCursor(cursor)
            else:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        elif self.current_tool == "eyedropper":
            # Custom eyedropper cursor or default
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            # Default cursor for other tools
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            
    def create_brush_cursor(self):
        """Create a custom cursor showing brush size and shape"""
        # Get current zoom level
        current_scale = self.transform().m11()  # Get current scale factor
        
        # Calculate how big the brush will appear on screen
        # brush_size is in canvas pixels, we need screen pixels
        screen_brush_size = self.brush_size * current_scale
        
        # Ensure cursor is at least visible (minimum 4px) but allow it to be large for big brushes
        cursor_size = max(4, min(512, int(round(screen_brush_size))))
        
        # Create pixmap for cursor with some padding for border
        padding = 6  # Increased padding for better visibility
        pixmap = QPixmap(cursor_size + padding, cursor_size + padding)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Calculate center
        center_x = (cursor_size + padding) // 2
        center_y = (cursor_size + padding) // 2
        radius = cursor_size // 2
        
        # Draw the brush preview
        if self.brush_shape == "circle":
            # Draw circle border (white outline)
            border_pen = QPen(QColor(255, 255, 255), 2)
            painter.setPen(border_pen)
            painter.setBrush(QBrush())  # No fill for border
            painter.drawEllipse(center_x - radius, center_y - radius, cursor_size, cursor_size)
            
            # Draw inner circle with current color (semi-transparent)
            inner_color = QColor(self.current_color)
            inner_color.setAlpha(80)  # Semi-transparent
            inner_pen = QPen(QColor(0, 0, 0), 1)  # Black inner border
            inner_brush = QBrush(inner_color)
            painter.setPen(inner_pen)
            painter.setBrush(inner_brush)
            painter.drawEllipse(center_x - radius + 1, center_y - radius + 1, 
                              cursor_size - 2, cursor_size - 2)
        else:  # square
            # Draw square border (white outline)
            border_pen = QPen(QColor(255, 255, 255), 2)
            painter.setPen(border_pen)
            painter.setBrush(QBrush())  # No fill for border
            painter.drawRect(center_x - radius, center_y - radius, cursor_size, cursor_size)
            
            # Draw inner square with current color (semi-transparent)
            inner_color = QColor(self.current_color)
            inner_color.setAlpha(80)  # Semi-transparent
            inner_pen = QPen(QColor(0, 0, 0), 1)  # Black inner border
            inner_brush = QBrush(inner_color)
            painter.setPen(inner_pen)
            painter.setBrush(inner_brush)
            painter.drawRect(center_x - radius + 1, center_y - radius + 1, 
                           cursor_size - 2, cursor_size - 2)
        
        painter.end()
        return pixmap
        
    def mousePressEvent(self, event):
        """Handle mouse press events for drawing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert screen coordinates to scene coordinates
            scene_pos = self.mapToScene(event.position().toPoint())
            canvas_pos = self.pixmap_item.mapFromScene(scene_pos)
            
            x, y = int(canvas_pos.x()), int(canvas_pos.y())
            
            # Allow drawing even if mouse is outside canvas bounds (for large brushes)
            if self.current_tool != "eyedropper":
                # Normal drawing tools - start drawing regardless of position
                self.drawing = True
                self.last_point = (x, y)
                # Reset pixel-perfect state at stroke start
                self._pp_reset_state()
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
        
        # Update cursor position (for brush preview)
        if self.current_tool in ["brush", "eraser"]:
            self.update()  # Trigger repaint for cursor update
        
        # Continue drawing if left button is pressed
        if self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            # Allow drawing even when mouse is outside canvas bounds
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
            # Flush pending pixel (if any) then reset
            if self.pixel_perfect and self.brush_size == 1 and self._pp_pending is not None:
                self._pp_commit_pixel(*self._pp_pending)
            self._pp_reset_state()
            # Push snapshot after completed stroke
            self.history.push(self.pixmap)
            
    def draw_brush_stroke(self, x, y):
        """Draw with the brush tool using current size and shape"""
        if self.pixel_perfect and self.brush_size == 1:
            self._pp_handle_pixel(round(x), round(y))
            return

        painter = QPainter(self.pixmap)
        painter.setPen(QPen(self.current_color, 1))
        painter.setBrush(QBrush(self.current_color))

        if self.pixel_perfect:
            x = round(x)
            y = round(y)

        if self.brush_size == 1:
            if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                painter.drawPoint(int(x), int(y))
        else:
            radius = self.brush_size // 2
            brush_left = x - radius
            brush_top = y - radius
            brush_right = x + radius
            brush_bottom = y + radius
            if (brush_right >= 0 and brush_left < self.canvas_width and 
                brush_bottom >= 0 and brush_top < self.canvas_height):
                painter.setClipRect(0, 0, self.canvas_width, self.canvas_height)
                if self.brush_shape == "circle":
                    painter.drawEllipse(x - radius, y - radius, self.brush_size, self.brush_size)
                else:
                    painter.drawRect(x - radius, y - radius, self.brush_size, self.brush_size)
        painter.end()
        self.pixmap_item.setPixmap(self.pixmap)
        
    def draw_pixel(self, x, y):
        """Draw a single pixel at the given coordinates (legacy method)"""
        self.draw_brush_stroke(x, y)
        
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
            self.draw_brush_stroke(x, y)
        elif self.current_tool == "eraser":
            self.erase_brush_stroke(x, y)
        elif self.current_tool == "bucket":
            self.bucket_fill(x, y)
            
    def draw_line_with_tool(self, x1, y1, x2, y2):
        """Draw a line using the current tool"""
        if self.current_tool == "brush":
            self.draw_brush_line(x1, y1, x2, y2)
        elif self.current_tool == "eraser":
            self.erase_brush_line(x1, y1, x2, y2)
        # Bucket tool doesn't need line drawing
        
    def draw_brush_line(self, x1, y1, x2, y2):
        """Draw a line with the brush tool using current brush settings"""
        # Bresenham
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        x, y = x1, y1
        while True:
            self.draw_brush_stroke(x, y)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    # ---------------- Pixel Perfect (retroactive) ----------------
    def _pp_reset_state(self):
        self._pp_committed = []
        self._pp_pending = None
        self._pp_last = None

    def _pp_handle_pixel(self, x, y):
        # Bounds & duplicate filter
        if not (0 <= x < self.canvas_width and 0 <= y < self.canvas_height):
            return
        if self._pp_last == (x, y):
            return

        if self._pp_last is None:
            self._pp_commit_pixel(x, y)
            return

        lx, ly = self._pp_last
        dx = x - lx
        dy = y - ly
        # Only accept unit steps; if larger jump, flush pending and treat as new segment
        if abs(dx) > 1 or abs(dy) > 1:
            if self._pp_pending is not None:
                self._pp_commit_pixel(*self._pp_pending)
                self._pp_pending = None
            self._pp_commit_pixel(x, y)
            return

        is_diagonal = abs(dx) == 1 and abs(dy) == 1
        if is_diagonal:
            # On diagonal: commit diagonal pixel; drop any pending (turning L into \ or /)
            self._pp_commit_pixel(x, y)
            self._pp_pending = None
            return

        # Axis-aligned step (horizontal or vertical)
        # Buffer it; if next step becomes diagonal we'll discard it.
        # If there's already a pending different pixel, commit the previous pending first.
        if self._pp_pending is not None and self._pp_pending != (x, y):
            self._pp_commit_pixel(*self._pp_pending)
        self._pp_pending = (x, y)

    def _pp_commit_pixel(self, x, y):
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(self.current_color, 1))
        painter.drawPoint(int(x), int(y))
        painter.end()
        self._pp_committed.append((x, y))
        self._pp_last = (x, y)
        self.pixmap_item.setPixmap(self.pixmap)
                
    def erase_brush_stroke(self, x, y):
        """Erase with the brush tool using current size and shape"""
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(QColor(255, 255, 255), 1))  # White color
        painter.setBrush(QBrush(QColor(255, 255, 255)))  # White brush
        
        # Apply pixel perfect snapping if enabled
        if self.pixel_perfect:
            x = round(x)
            y = round(y)
        
        if self.brush_size == 1:
            # Single pixel - only erase if within bounds
            if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                painter.drawPoint(x, y)
        else:
            # Multi-pixel eraser - erase even if center is outside, but clip to canvas
            radius = self.brush_size // 2
            
            # Calculate brush bounds
            brush_left = x - radius
            brush_top = y - radius
            brush_right = x + radius
            brush_bottom = y + radius
            
            # Check if brush overlaps with canvas at all
            if (brush_right >= 0 and brush_left < self.canvas_width and 
                brush_bottom >= 0 and brush_top < self.canvas_height):
                
                # Set clipping to canvas bounds
                painter.setClipRect(0, 0, self.canvas_width, self.canvas_height)
                
                if self.brush_shape == "circle":
                    # Draw circle eraser
                    painter.drawEllipse(x - radius, y - radius, self.brush_size, self.brush_size)
                else:  # square
                    # Draw square eraser
                    painter.drawRect(x - radius, y - radius, self.brush_size, self.brush_size)
        
        painter.end()
        
        # Update the display
        self.pixmap_item.setPixmap(self.pixmap)
        
    def erase_brush_line(self, x1, y1, x2, y2):
        """Erase a line with the eraser tool using current brush settings"""
        # Use Bresenham-like algorithm to erase along the line
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            self.erase_brush_stroke(x, y)
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
                
    def erase_pixel(self, x, y):
        """Erase a single pixel (make it white) - legacy method"""
        self.erase_brush_stroke(x, y)
        
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
        # Only bucket fill if the click is within canvas bounds
        if not (0 <= x < self.canvas_width and 0 <= y < self.canvas_height):
            return
            
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
        # Record fill action
        self.history.push(self.pixmap)
        
    def on_system_color_picked(self, color):
        """Handle color picked from system eyedropper"""
        self.current_color = color
        self.color_picked.emit(color)
        print(f"System eyedropper picked color: {color.name()}")
        
    def update_brush_settings(self, settings):
        """Update brush settings from options panel"""
        self.brush_size = settings['size']
        self.brush_shape = settings['shape']
        self.pixel_perfect = settings['pixel_perfect']
        
        # Update cursor when settings change
        if self.current_tool in ["brush", "eraser"]:
            self.update_cursor()
        
        print(f"Brush settings updated: size={self.brush_size}, shape={self.brush_shape}, pixel_perfect={self.pixel_perfect}")
        
    def set_brush_color(self, color):
        """Set the current brush color"""
        self.current_color = color
        
        # Update cursor when color changes (for brush preview)
        if self.current_tool in ["brush", "eraser"]:
            self.update_cursor()
        
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
            
        # Update cursor for new tool
        self.update_cursor()
            
        print(f"Canvas tool changed to: {tool_name}")  # Debug
        
    def clear_canvas(self):
        """Clear the entire canvas"""
        self.pixmap.fill(Qt.GlobalColor.white)
        self.pixmap_item.setPixmap(self.pixmap)
        self.history.push(self.pixmap)

    # --------------- Dynamic Canvas Management ---------------
    def resize_canvas(self, width: int, height: int):
        """Resize canvas to new dimensions, clearing content."""
        width = max(1, min(2048, int(width)))
        height = max(1, min(2048, int(height)))
        self.canvas_width = width
        self.canvas_height = height
        self.pixmap = QPixmap(self.canvas_width, self.canvas_height)
        self.pixmap.fill(Qt.GlobalColor.white)
        self.pixmap_item.setPixmap(self.pixmap)
        self.centerOn(self.pixmap_item)
        if hasattr(self, 'history'):
            self.history.push(self.pixmap)

    def load_image(self, qimage):
        """Load a QImage into the canvas (auto-resize)."""
        if qimage.width() > 2048 or qimage.height() > 2048:
            return False
        self.canvas_width = qimage.width()
        self.canvas_height = qimage.height()
        self.pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(self.pixmap)
        self.centerOn(self.pixmap_item)
        if hasattr(self, 'history'):
            self.history.push(self.pixmap)
        return True

    # ---------------- Undo / Redo ----------------
    def undo(self):
        new_pix = self.history.undo()
        if new_pix is not None:
            self.pixmap = QPixmap(new_pix)
            self.pixmap_item.setPixmap(self.pixmap)
            self.update_cursor()

    def redo(self):
        new_pix = self.history.redo()
        if new_pix is not None:
            self.pixmap = QPixmap(new_pix)
            self.pixmap_item.setPixmap(self.pixmap)
            self.update_cursor()
        
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
        
        # Update cursor after zoom change (brush size appearance changes with zoom)
        if self.current_tool in ["brush", "eraser"]:
            self.update_cursor()
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        # Ctrl+E for system-wide eyedropper
        if event.key() == Qt.Key.Key_E and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.system_eyedropper.start_eyedropper()
        else:
            super().keyPressEvent(event)