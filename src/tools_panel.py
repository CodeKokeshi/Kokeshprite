"""
Tools panel for Kokeshprite
Contains drawing tools like brush, eraser, bucket fill, etc.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QButtonGroup, 
                            QScrollArea, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ToolsPanel(QScrollArea):
    """Tools panel with scrollable tool buttons"""
    
    # Signal emitted when tool is changed
    tool_changed = pyqtSignal(str)  # tool_name
    
    def __init__(self):
        super().__init__()
        self.current_tool = "brush"  # Default tool
        self.init_ui()
        
    def init_ui(self):
        """Initialize the tools panel UI"""
        # Set fixed width and scroll properties
        # Increased width so longest label (Eyedropper) not truncated
        self.setFixedWidth(160)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Tools title
        title = QLabel("Tools")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        title.setFont(font)
        layout.addWidget(title)
        
        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Create button group for exclusive selection
        self.tool_group = QButtonGroup()
        self.tool_group.setExclusive(True)
        
        # Create tool buttons
        self.create_tool_buttons(layout)
        
        # Add stretch to push tools to top
        layout.addStretch()
        
    def create_tool_buttons(self, layout):
        """Create all tool buttons"""
        tools = [
            ("brush", "🖌️ Brush", "Draw with brush"),
            ("eraser", "🧽 Eraser", "Erase pixels"),
            ("bucket", "🪣 Bucket", "Fill with color"),
            ("eyedropper", "💧 Eyedropper", "Pick color (canvas) or Ctrl+click (system-wide)")
        ]
        
        self.tool_buttons = {}
        
        for tool_id, text, tooltip in tools:
            button = QPushButton(text)
            button.setToolTip(tooltip)
            button.setCheckable(True)
            button.setFixedHeight(40)
            button.setMinimumWidth(90)
            
            # Style the button
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    border: 2px solid #666;
                    border-radius: 5px;
                    background-color: #404040;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    color: white;
                    border-color: #005a9e;
                }
                QPushButton:hover {
                    border-color: #007acc;
                }
            """)
            
            # Connect button click
            button.clicked.connect(lambda checked, tool=tool_id: self.select_tool(tool))
            
            # Add to button group and layout
            self.tool_group.addButton(button)
            layout.addWidget(button)
            
            # Store button reference
            self.tool_buttons[tool_id] = button
            
        # Set default tool (brush)
        self.tool_buttons["brush"].setChecked(True)
        
    def select_tool(self, tool_name):
        """Select a tool and emit signal"""
        if tool_name != self.current_tool:
            self.current_tool = tool_name
            self.tool_changed.emit(tool_name)
            print(f"Tool changed to: {tool_name}")  # Debug
            
    def get_current_tool(self):
        """Get the currently selected tool"""
        return self.current_tool