"""
Symmetry system for mirroring brush strokes across rotatable lines
"""

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
import math

class SymmetryLine:
    """Represents a single symmetry line with position and rotation"""
    
    def __init__(self, center_x, center_y, angle=0):
        """
        Args:
            center_x: X position of the line's center point
            center_y: Y position of the line's center point
            angle: Rotation angle in degrees (0 = vertical, 90 = horizontal)
        """
        self.center_x = center_x
        self.center_y = center_y
        self.angle = angle  # Degrees
        self.enabled = True
        
    def get_mirrored_point(self, x, y):
        """
        Calculate the mirrored point across this symmetry line
        
        Args:
            x, y: Original point coordinates
            
        Returns:
            (mx, my): Mirrored point coordinates
        """
        # Convert angle to radians
        angle_rad = math.radians(self.angle)
        
        # Translate point to origin (relative to line center)
        dx = x - self.center_x
        dy = y - self.center_y
        
        # Calculate perpendicular distance to the line
        # Line direction vector (perpendicular to normal)
        line_dx = math.sin(angle_rad)
        line_dy = -math.cos(angle_rad)
        
        # Normal vector to the line
        normal_x = math.cos(angle_rad)
        normal_y = math.sin(angle_rad)
        
        # Distance from point to line (signed)
        distance = dx * normal_x + dy * normal_y
        
        # Mirror point by reflecting across the line
        mx = x - 2 * distance * normal_x
        my = y - 2 * distance * normal_y
        
        return (mx, my)
    
    def draw(self, painter, canvas_width, canvas_height, zoom=1.0):
        """
        Draw this symmetry line on the canvas
        
        Args:
            painter: QPainter to draw with
            canvas_width, canvas_height: Canvas dimensions
            zoom: Current zoom level
        """
        if not self.enabled:
            return
            
        # Convert angle to radians
        angle_rad = math.radians(self.angle)
        
        # Calculate line endpoints (extend across entire canvas)
        # Line direction vector
        dx = math.sin(angle_rad)
        dy = -math.cos(angle_rad)
        
        # Calculate line length to cover entire canvas
        diagonal = math.sqrt(canvas_width**2 + canvas_height**2)
        length = diagonal * 2
        
        # Start and end points
        start_x = self.center_x - dx * length / 2
        start_y = self.center_y - dy * length / 2
        end_x = self.center_x + dx * length / 2
        end_y = self.center_y + dy * length / 2
        
        # Draw the line
        pen = QPen(QColor(0, 150, 255, 180), 1.0 / zoom)  # Blue, semi-transparent
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))
        
        # Draw center point (larger and more visible)
        center_outer_size = 6 / zoom
        center_inner_size = 4 / zoom
        
        # Draw outer circle (white border)
        painter.setPen(QPen(QColor(255, 255, 255, 200), 2.0 / zoom))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(self.center_x, self.center_y), 
                          center_outer_size, center_outer_size)
        
        # Draw inner circle (blue filled)
        painter.setPen(QPen(QColor(0, 150, 255), 1.0 / zoom))
        painter.setBrush(QBrush(QColor(0, 150, 255, 200)))
        painter.drawEllipse(QPointF(self.center_x, self.center_y), 
                          center_inner_size, center_inner_size)


class SymmetryManager:
    """Manages multiple symmetry lines for mirrored drawing"""
    
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.lines = []
        self.max_lines = 8
        self.enabled = False
        
    def add_line(self, angle=0):
        """Add a new symmetry line at the canvas center with given angle"""
        if len(self.lines) < self.max_lines:
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2
            line = SymmetryLine(center_x, center_y, angle)
            self.lines.append(line)
            return line
        return None
    
    def remove_line(self, index):
        """Remove a symmetry line by index"""
        if 0 <= index < len(self.lines):
            self.lines.pop(index)
    
    def clear_lines(self):
        """Remove all symmetry lines"""
        self.lines.clear()
    
    def get_mirrored_points(self, x, y):
        """
        Get all mirrored points for a given input point
        
        For multiple lines, mirrors all accumulated points across each line
        to generate the full symmetry group (e.g., 4 points for cross, 8 for star)
        
        Args:
            x, y: Original point coordinates
            
        Returns:
            List of (x, y) tuples including original and all mirrored points
        """
        if not self.enabled or not self.lines:
            return [(x, y)]
        
        points = set([(x, y)])  # Use set to avoid duplicates
        
        # For each enabled line, mirror ALL current points across that line
        for line in self.lines:
            if line.enabled:
                new_points = set()
                for px, py in points:
                    # Keep the original point
                    new_points.add((px, py))
                    # Add its mirror
                    mx, my = line.get_mirrored_point(px, py)
                    new_points.add((mx, my))
                points = new_points
        
        return list(points)
    
    def draw_all(self, painter, zoom=1.0):
        """Draw all symmetry lines"""
        if not self.enabled:
            return
            
        for line in self.lines:
            line.draw(painter, self.canvas_width, self.canvas_height, zoom)
    
    def set_line_angle(self, index, angle):
        """Set the angle of a specific line"""
        if 0 <= index < len(self.lines):
            self.lines[index].angle = angle % 360
    
    def move_line(self, index, x, y):
        """Move a specific line's center point"""
        if 0 <= index < len(self.lines):
            self.lines[index].center_x = x
            self.lines[index].center_y = y
    
    def toggle_line(self, index):
        """Enable/disable a specific line"""
        if 0 <= index < len(self.lines):
            self.lines[index].enabled = not self.lines[index].enabled
    
    def add_preset_cross(self):
        """Add vertical + horizontal lines (cross pattern)"""
        self.clear_lines()
        self.add_line(0)    # Vertical
        self.add_line(90)   # Horizontal
    
    def add_preset_x(self):
        """Add diagonal lines (X pattern)"""
        self.clear_lines()
        self.add_line(45)   # Diagonal /
        self.add_line(135)  # Diagonal \
    
    def add_preset_star(self):
        """Add cross + X (8-way symmetry for mandalas/pizzas)"""
        self.clear_lines()
        self.add_line(0)     # Vertical
        self.add_line(45)    # Diagonal /
        self.add_line(90)    # Horizontal
        self.add_line(135)   # Diagonal \
