"""
Canvas widget for pixel art drawing
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QScreen, QCursor, QPainterPath
import math
from .system_eyedropper import SystemEyedropper
from .history import HistoryManager
from functools import lru_cache

class Canvas(QGraphicsView):
    """Main drawing canvas using QGraphicsView"""
    
    # Signals
    mouse_position_changed = pyqtSignal(int, int)  # x, y coordinates
    color_picked = pyqtSignal(QColor)  # Picked color from eyedropper
    modified = pyqtSignal()  # Emitted after a change affecting pixel data
    
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

        # Grid properties
        self.grid_enabled = False
        self.grid_width = 16  # Grid cell width in pixels
        self.grid_height = 16  # Grid cell height in pixels
        self.grid_color = QColor(0x1c, 0x34, 0xff)  # Default grid color #1c34ff
        
        # Background properties
        self.background_tile_size = 2  # Default 2x2 tile size for checkerboard
        
        # Enable key press events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # Track last mouse position for dynamic cursor (eraser inverse preview)
        self._last_cursor_pos = (0, 0)
        # Panning state (needs to exist before init_canvas -> _update_scene_rect)
        self._panning = False
        self._pan_start = None  # screen position (QPointF)
        self._pan_scroll_origin = None  # (hval, vval)
        self._scene_padding = 1024  # pixels of empty margin around canvas for free panning

        # Initialize the canvas (uses _scene_padding)
        self.init_canvas()
        # History manager (after canvas init so pixmap exists)
        self.history = HistoryManager()
        self.history.push(self.pixmap)
        
        
    def init_canvas(self):
        """Initialize the graphics scene and canvas"""
        # Create the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Create the pixmap for drawing with proper alpha format
        self.pixmap = QPixmap(self.canvas_width, self.canvas_height)
        self.pixmap.fill(Qt.GlobalColor.transparent)
        
        # Ensure the pixmap has the correct format for alpha
        temp_image = self.pixmap.toImage()
        if temp_image.format() != temp_image.Format.Format_ARGB32:
            temp_image = temp_image.convertToFormat(temp_image.Format.Format_ARGB32)
            self.pixmap = QPixmap.fromImage(temp_image)
        
        # Add pixmap to scene
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.pixmap_item)
        # Provide padded scene rect so we can pan beyond visible canvas
        self._update_scene_rect()
        
        # Set up the view
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # Pixel perfect
        
        # Set initial zoom
        self.scale(self.zoom_factor, self.zoom_factor)
        
        # Center the canvas
        self.centerOn(self.pixmap_item)
        
        # Update cursor for initial tool
        self.update_cursor()
    
    def set_grid_settings(self, enabled, width, height, color):
        """Update grid settings and refresh display"""
        self.grid_enabled = enabled
        self.grid_width = width
        self.grid_height = height
        self.grid_color = color
        # Force redraw of the view to show/hide grid
        self.viewport().update()
        if hasattr(self, 'pixmap_item'):
            self.scene.update(self.pixmap_item.boundingRect())

    def set_background_tile_size(self, tile_size):
        """Update background tile size and refresh display"""
        self.background_tile_size = max(1, min(32, tile_size))  # Clamp to reasonable range
        # Force redraw of the view to update background
        self.viewport().update()
        if hasattr(self, 'pixmap_item'):
            self.scene.update(self.pixmap_item.boundingRect())

    def drawBackground(self, painter, rect):
        """Render transparency checkerboard behind the canvas"""
        painter.fillRect(rect, QColor(40, 40, 40))
        if not hasattr(self, 'pixmap_item'):
            return
        
        # Get canvas bounds
        canvas_rect = self.pixmap_item.boundingRect()
        target = rect.intersected(canvas_rect)
        if target.isEmpty():
            return
        
        # Draw checkerboard pattern that represents actual canvas pixels
        painter.save()
        painter.setClipRect(target)
        
        # Checkerboard colors
        light = QColor(110, 110, 110)
        dark = QColor(70, 70, 70)
        
        # Use configurable tile size for checkerboard pattern
        start_x = int(canvas_rect.left())
        start_y = int(canvas_rect.top())
        end_x = int(canvas_rect.right())
        end_y = int(canvas_rect.bottom())
        
        # Use configurable tile size instead of fixed 2x2
        tile_size = self.background_tile_size
        
        # Draw checkerboard pattern based on configurable tile size
        for y in range(start_y, end_y, tile_size):
            for x in range(start_x, end_x, tile_size):
                # Checkerboard pattern based on tile grid
                cell_x = x // tile_size
                cell_y = y // tile_size
                color = light if ((cell_x + cell_y) % 2 == 0) else dark
                
                # Draw tile block, but respect canvas boundaries
                block_width = min(tile_size, end_x - x)
                block_height = min(tile_size, end_y - y)
                painter.fillRect(x, y, block_width, block_height, color)
        
        painter.restore()
    
    def drawForeground(self, painter, rect):
        """Draw grid overlay on top of the canvas"""
        if not self.grid_enabled:
            return
        
        # Only draw grid within the canvas bounds
        canvas_rect = self.pixmap_item.boundingRect()
        
        # Set up grid pen
        grid_pen = QPen(self.grid_color)
        grid_pen.setWidth(0)  # Cosmetic pen (always 1 pixel regardless of zoom)
        painter.setPen(grid_pen)
        
        # Calculate grid lines
        start_x = int(canvas_rect.left())
        start_y = int(canvas_rect.top())
        end_x = int(canvas_rect.right())
        end_y = int(canvas_rect.bottom())
        
        # Draw vertical grid lines
        x = start_x
        while x <= end_x:
            if x >= start_x and x <= end_x:
                painter.drawLine(x, start_y, x, end_y)
            x += self.grid_width
        
        # Draw horizontal grid lines
        y = start_y
        while y <= end_y:
            if y >= start_y and y <= end_y:
                painter.drawLine(start_x, y, end_x, y)
            y += self.grid_height
        
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
        """Create clean cursor preview without rectangular containers:
        - Brush: Clean filled pixels showing exact color
        - Eraser: Individual pixel outlines showing exact erase area
        """
        current_scale = self.transform().m11()
        size = self.brush_size
        mask = self._brush_mask(size, self.brush_shape)
        if not mask:
            return None
        # Determine mask bounds
        min_dx = min(dx for dx, _ in mask)
        max_dx = max(dx for dx, _ in mask)
        min_dy = min(dy for _, dy in mask)
        max_dy = max(dy for _, dy in mask)
        mask_w = (max_dx - min_dx + 1)
        mask_h = (max_dy - min_dy + 1)

        # Pixel cell size on screen
        cell = max(1, int(round(current_scale)))
        # Minimal padding - just enough to not clip
        padding = 1
        pixmap = QPixmap(mask_w * cell + padding * 2, mask_h * cell + padding * 2)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        occupied = set(mask)

        if self.current_tool == 'eraser':
            # ERASER: Show only the OUTER edges of border pixels
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Get the underlying canvas colors for negation
            img = self.pixmap.toImage()
            cx, cy = self._last_cursor_pos
            
            # Draw only the outer edges of each border pixel
            for dx, dy in occupied:
                sx = (dx - min_dx) * cell + padding
                sy = (dy - min_dy) * cell + padding
                
                # Get the color behind this pixel for negation
                px = int(cx + dx)
                py = int(cy + dy)
                if 0 <= px < self.canvas_width and 0 <= py < self.canvas_height:
                    base_color = img.pixelColor(px, py)
                    neg_color = QColor(255 - base_color.red(), 255 - base_color.green(), 255 - base_color.blue(), 255)
                else:
                    neg_color = QColor(0, 0, 0, 255)
                
                painter.setPen(QPen(neg_color, 1))
                
                # Check each direction and only draw edges that face empty space
                # Top edge
                if (dx, dy - 1) not in occupied:
                    painter.drawLine(sx, sy, sx + cell - 1, sy)
                
                # Bottom edge  
                if (dx, dy + 1) not in occupied:
                    painter.drawLine(sx, sy + cell - 1, sx + cell - 1, sy + cell - 1)
                
                # Left edge
                if (dx - 1, dy) not in occupied:
                    painter.drawLine(sx, sy, sx, sy + cell - 1)
                
                # Right edge
                if (dx + 1, dy) not in occupied:
                    painter.drawLine(sx + cell - 1, sy, sx + cell - 1, sy + cell - 1)
                    
        else:
            # BRUSH: Clean filled pixels without any border
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Use current color at FULL opacity
            fill_color = QColor(self.current_color)
            fill_color.setAlpha(255)
            painter.setBrush(QBrush(fill_color))
            
            # Fill each pixel cleanly
            for dx, dy in occupied:
                sx = (dx - min_dx) * cell + padding
                sy = (dy - min_dy) * cell + padding
                painter.drawRect(sx, sy, cell, cell)

        # NO rectangular border around the entire shape!
        
        painter.end()
        return pixmap
        
    def mousePressEvent(self, event):
        """Handle mouse press events for drawing"""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Start panning (camera move)
            self._panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._pan_start = event.position()
            # Store initial scrollbar values
            self._pan_scroll_origin = (self.horizontalScrollBar().value(), self.verticalScrollBar().value())
            event.accept()
            return
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
        # Handle panning first (scrollbar-based like Aseprite)
        if self._panning and self._pan_start is not None and self._pan_scroll_origin is not None:
            delta = event.position() - self._pan_start
            h0, v0 = self._pan_scroll_origin
            self.horizontalScrollBar().setValue(int(h0 - delta.x()))
            self.verticalScrollBar().setValue(int(v0 - delta.y()))
            event.accept()
            # Dynamic expansion if nearing padded edge (optional minimal logic)
            view_center_scene = self.mapToScene(self.viewport().rect().center())
            r = self.scene.sceneRect()
            pad_extend_trigger = 128
            expanded = False
            if view_center_scene.x() < r.left() + pad_extend_trigger:
                r.setLeft(r.left() - self._scene_padding)
                expanded = True
            if view_center_scene.x() > r.right() - pad_extend_trigger:
                r.setRight(r.right() + self._scene_padding)
                expanded = True
            if view_center_scene.y() < r.top() + pad_extend_trigger:
                r.setTop(r.top() - self._scene_padding)
                expanded = True
            if view_center_scene.y() > r.bottom() - pad_extend_trigger:
                r.setBottom(r.bottom() + self._scene_padding)
                expanded = True
            if expanded:
                self.scene.setSceneRect(r)
        
        # Convert screen coordinates to scene coordinates
        scene_pos = self.mapToScene(event.position().toPoint())
        canvas_pos = self.pixmap_item.mapFromScene(scene_pos)
        
        x, y = int(canvas_pos.x()), int(canvas_pos.y())
        
        # Emit mouse position for status bar
        self.mouse_position_changed.emit(x, y)

        # Track last cursor position for dynamic eraser preview
        self._last_cursor_pos = (x, y)
        
        # Update cursor position (for brush preview)
        if self.current_tool in ["brush", "eraser"]:
            if self.current_tool == 'eraser':
                # Regenerate cursor each move for inverse colors
                self.update_cursor()
            self.update()  # Trigger repaint (if any overlay logic is later added)
        
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
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self._pan_start = None
            self._pan_scroll_origin = None
            self.update_cursor()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.last_point = None
            # Flush pending pixel (if any) then reset
            if self.pixel_perfect and self.brush_size == 1 and self._pp_pending is not None:
                self._pp_commit_pixel(*self._pp_pending)
            self._pp_reset_state()
            # Push snapshot after completed stroke
            self.history.push(self.pixmap)
            self.modified.emit()
            
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
            size = int(self.brush_size)
            # Generate mask offsets relative to center
            for dx, dy in self._brush_mask(size, self.brush_shape):
                px = int(x + dx)
                py = int(y + dy)
                if 0 <= px < self.canvas_width and 0 <= py < self.canvas_height:
                    painter.drawPoint(px, py)
        painter.end()
        self.pixmap_item.setPixmap(self.pixmap)

    @staticmethod
    @lru_cache(maxsize=256)
    def _brush_mask(size: int, shape: str):
        """Return list of (dx, dy) offsets for given size & shape.
        Circle uses discrete disk rasterization similar to common pixel editors (Aseprite style).
        Square is full size x size block.
        """
        if size <= 1:
            return [(0, 0)]
        offsets = []
        if shape == 'square':
            half = size // 2
            if size % 2:  # odd
                for dy in range(-half, half + 1):
                    for dx in range(-half, half + 1):
                        offsets.append((dx, dy))
            else:  # even, center between pixels
                # Even sizes cover a symmetric block with no single center pixel
                start = -half
                for dy in range(start, start + size):
                    for dx in range(start, start + size):
                        offsets.append((dx, dy))
            return offsets
        # Circle
        if size % 2:  # odd sizes: center at integer, radius = size//2
            r = size // 2
            r2 = r * r + 0.0001
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx*dx + dy*dy <= r2:
                        offsets.append((dx, dy))
        else:
            # even sizes: treat center at (0.5,0.5); iterate grid from -half .. half-1
            half = size // 2
            r = size / 2.0
            r2 = r * r + 0.0001
            for dy in range(-half, half):
                for dx in range(-half, half):
                    # Pixel center offset from (0,0) which is midpoint between four central pixels is (dx+0.5, dy+0.5)
                    cx = dx + 0.5
                    cy = dy + 0.5
                    if (cx*cx + cy*cy) <= r2:
                        offsets.append((dx, dy))
        return offsets
        
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
        """Erase with the brush tool using current size and shape - makes pixels fully transparent"""
        # Convert to image for direct pixel manipulation, ensuring alpha format
        image = self.pixmap.toImage()
        
        # Ensure the image format supports alpha channel
        if image.format() != image.Format.Format_ARGB32:
            image = image.convertToFormat(image.Format.Format_ARGB32)

        if self.pixel_perfect:
            x = round(x)
            y = round(y)

        # Fully transparent color (0 alpha) - explicitly transparent
        transparent_color = QColor(0, 0, 0, 0)  # RGBA: black with 0 alpha = fully transparent

        if self.brush_size == 1:
            if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                image.setPixelColor(int(x), int(y), transparent_color)
        else:
            size = int(self.brush_size)
            for dx, dy in self._brush_mask(size, self.brush_shape):
                px = int(x + dx)
                py = int(y + dy)
                if 0 <= px < self.canvas_width and 0 <= py < self.canvas_height:
                    image.setPixelColor(px, py, transparent_color)

        # Update pixmap from modified image, preserving alpha
        self.pixmap = QPixmap.fromImage(image)
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
        """Erase a line - makes pixels fully transparent"""
        # Convert to image for direct pixel manipulation
        image = self.pixmap.toImage()
        
        # Fully transparent color (0 alpha)
        transparent_color = QColor(0, 0, 0, 0)
        
        # Use Bresenham algorithm to draw transparent line
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                image.setPixelColor(x, y, transparent_color)
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        # Update pixmap from modified image
        self.pixmap = QPixmap.fromImage(image)
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
        
        print(
            f"Bucket fill: target={target_color.name(QColor.NameFormat.HexArgb)}, "
            f"fill={fill_color.name(QColor.NameFormat.HexArgb)}"
        )  # Debug
            
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
        self.modified.emit()
        
    def on_system_color_picked(self, color):
        """Handle color picked from system eyedropper"""
        self.current_color = color
        self.color_picked.emit(color)
        print(f"System eyedropper picked color: {color.name(QColor.NameFormat.HexArgb)}")
        
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
        self.pixmap.fill(Qt.GlobalColor.transparent)
        self.pixmap_item.setPixmap(self.pixmap)
        self.history.push(self.pixmap)
        self.modified.emit()
        self.viewport().update()

    # --------------- Dynamic Canvas Management ---------------
    def resize_canvas(self, width: int, height: int):
        """Resize canvas to new dimensions, clearing content."""
        width = max(1, min(2048, int(width)))
        height = max(1, min(2048, int(height)))
        self.canvas_width = width
        self.canvas_height = height
        self.pixmap = QPixmap(self.canvas_width, self.canvas_height)
        self.pixmap.fill(Qt.GlobalColor.transparent)
        self.pixmap_item.setPixmap(self.pixmap)
        self._update_scene_rect()
        self.centerOn(self.pixmap_item)
        if hasattr(self, 'history'):
            self.history.push(self.pixmap)
        self.modified.emit()
        self.viewport().update()

    def load_image(self, qimage):
        """Load a QImage into the canvas (auto-resize)."""
        if qimage.width() > 2048 or qimage.height() > 2048:
            return False
        self.canvas_width = qimage.width()
        self.canvas_height = qimage.height()
        self.pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(self.pixmap)
        self._update_scene_rect()
        self.centerOn(self.pixmap_item)
        if hasattr(self, 'history'):
            self.history.push(self.pixmap)
        self.modified.emit()
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

    # --------- Scene Rect Helper (padded workspace) ---------
    def _update_scene_rect(self):
        padding = self._scene_padding
        self.scene.setSceneRect(-padding, -padding, self.canvas_width + padding * 2, self.canvas_height + padding * 2)
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        # Ctrl+E for system-wide eyedropper
        if event.key() == Qt.Key.Key_E and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.system_eyedropper.start_eyedropper()
        else:
            super().keyPressEvent(event)