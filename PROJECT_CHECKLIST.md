# Kokeshprite - Pixel Art Editor Feature Checklist

*Goal: Build core pixel art editor functionality*

## Legend
- `[ ]` - Not Started
- `[/]` - In Progress  
- `[X]` - Completed

---

## Setup & Foundation
- [X] Create virtual environment
- [X] Install core dependencies (PyQt6)
- [/] Set up basic project structure
- [/] Create main application window

---

## Main Interface

### Window Layout
- [/] Main application window
- [/] Menu bar (File, Edit, View, Tools, Animation, Help)
- [ ] Tool toolbar (vertical left side)
- [ ] Top options bar (tool-specific options)
- [/] Status bar (coordinates, zoom level, frame info)

### Panels & Dockable Windows
- [ ] Layer panel (with thumbnails, visibility, opacity)
- [ ] Color palette panel
- [ ] Timeline panel (for animation)
- [ ] Tool options panel
- [ ] Color picker panel
- [ ] Navigator/minimap panel

---

## Canvas System

### Core Canvas
- [/] Canvas rendering area
- [/] Pixel-perfect rendering
- [/] Zoom functionality (1x to 64x, fit to window)
- [ ] Pan/scroll with mouse drag
- [ ] Grid overlay (pixel grid, custom grid)
- [ ] Transparent checkerboard background
- [ ] Canvas centering

### Canvas Features
- [ ] Multiple document tabs
- [ ] Canvas rotation (90°, 180°, 270°)
- [ ] Canvas flipping (horizontal/vertical)
- [ ] Canvas resize
- [ ] Crop to content
- [ ] Image information display

---

## Drawing Tools

### Basic Tools (Toolbar)
- [/] Pencil tool (1px pixel drawing)
- [/] Brush tool (variable size)
- [ ] Eraser tool
- [ ] Line tool (straight lines)
- [ ] Rectangle tool (filled/outlined)
- [ ] Circle/Ellipse tool (filled/outlined)
- [ ] Paint bucket (flood fill)
- [ ] Eyedropper/Color picker
- [ ] Move tool
- [ ] Hand tool (pan canvas)
- [/] Zoom tool

### Selection Tools
- [ ] Rectangle selection
- [ ] Ellipse selection
- [ ] Lasso selection
- [ ] Magic wand selection
- [ ] Selection manipulation (move, copy, cut, paste)

### Tool Options (Context-sensitive)
- [ ] Brush size (1-100px)
- [ ] Brush opacity (0-100%)
- [ ] Tool preview cursor
- [ ] Pixel-perfect mode toggle
- [ ] Anti-aliasing toggle
- [ ] Symmetry options (horizontal/vertical/radial)

---

## Color System

### Color Management
- [ ] Current foreground/background color display
- [ ] Color picker dialog (RGB, HSV sliders)
- [ ] Color history (recent colors)
- [ ] Default palette (basic colors)
- [ ] Custom palette creation
- [ ] Palette import/export
- [ ] Eyedropper from anywhere on screen

### Color Features
- [ ] Color swatches
- [ ] Palette mode (indexed color)
- [ ] Color replacement tool
- [ ] Gradient generation

---

## Layer System

### Layer Management
- [ ] Layer creation/deletion
- [ ] Layer visibility toggle
- [ ] Layer opacity slider (0-100%)
- [ ] Layer blending modes (Normal, Multiply, Screen, Overlay)
- [ ] Layer reordering (drag & drop)
- [ ] Layer naming/renaming
- [ ] Layer thumbnails
- [ ] Background layer (locked by default)

### Layer Features
- [ ] Layer duplication
- [ ] Layer merging
- [ ] Layer grouping/folders
- [ ] Reference layers (non-editable overlay)

---

## Animation System

### Timeline
- [ ] Frame timeline at bottom
- [ ] Frame addition/deletion
- [ ] Frame duplication
- [ ] Frame reordering (drag & drop)
- [ ] Frame duration setting (in milliseconds)
- [ ] Current frame indicator
- [ ] Frame navigation (first, previous, next, last)

### Animation Controls
- [ ] Play/Pause/Stop buttons
- [ ] Loop options (once, loop, ping-pong)
- [ ] Playback speed control (FPS)
- [ ] Onion skinning (previous/next frames)
- [ ] Animation preview

### Animation Features
- [ ] Frame tags/labels
- [ ] Animation export (GIF)
- [ ] Sprite sheet export
- [ ] Frame-by-frame animation

---

## File Operations

### Basic File Handling
- [ ] New document (with size, color mode options)
- [ ] Open file dialog
- [ ] Save/Save As (native .ksprite format)
- [ ] Recent files menu
- [ ] Import image files (PNG, JPEG, BMP, GIF)
- [ ] Export image files (PNG, JPEG, BMP)

### Advanced File Features
- [ ] Auto-save functionality
- [ ] File recovery on crash
- [ ] Import/Export Aseprite files (.ase)
- [ ] Batch export options
- [ ] Template system

---

## Essential Features

### Undo/Redo System
- [ ] Unlimited undo/redo
- [ ] Undo history panel
- [ ] Memory-efficient undo storage

### Shortcuts & Hotkeys
- [ ] Tool shortcuts (B=Brush, P=Pencil, E=Eraser, etc.)
- [ ] File shortcuts (Ctrl+N, Ctrl+O, Ctrl+S, etc.)
- [ ] Canvas shortcuts (+ - for zoom, spacebar for pan)
- [ ] Custom shortcut assignment

### Pixel Art Specific
- [ ] Pixel-perfect drawing enforcement
- [ ] Nearest neighbor scaling
- [ ] Grid snapping
- [ ] Dithering patterns
- [ ] Outline generation

---

## Preferences & Settings
- [ ] Application preferences dialog
- [ ] Theme selection (dark/light)
- [ ] Grid settings (color, opacity)
- [ ] Default canvas size
- [ ] Auto-save interval
- [ ] Shortcut customization
- [ ] Performance settings

---

## Essential Filters & Effects
- [ ] Flip horizontal/vertical
- [ ] Rotate 90°/180°/270°
- [ ] Scale (2x, 3x, 4x with nearest neighbor)
- [ ] Color adjustments (brightness, contrast, hue)
- [ ] Color count reduction
- [ ] Outline effect

---

*Focus: Core functionality for creating pixel art and basic animations*
*Target: Functional pixel art editor with essential features*