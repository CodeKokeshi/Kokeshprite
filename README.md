# Kokeshprite — Pixel Art Editor# Kokeshprite — Pixel Art Editor



**Version 0.1.0**A lightweight, feature-rich pixel art editor focused on pixel-perfect drawing, responsive UI, and professional-quality tools. Built with PyQt6 for a native desktop feel and designed for artists who want precise control over pixels, cursors, and symmetry.



A lightweight, feature-rich pixel art editor focused on pixel-perfect drawing, responsive UI, and professional-quality tools. Built with PyQt6 for a native desktop feel and designed for artists who want precise control over pixels, cursors, and symmetry.> This README describes the Kokeshprite project contained in this repository. It follows the structure you requested and highlights the project's capabilities, how to build the executable on Windows, and where to find important developer docs in the repo.



------



## ✨ Features## 🎯 Current Features



### 🎨 Core Canvas & Tools### � Core Canvas & Tools

- **Pixel-perfect canvas** with configurable zoom (default 8×)- Pixel-perfect canvas with configurable zoom (default 8×)

- **Drawing tools**: Brush, Eraser, Bucket Fill, Eyedropper- Tools: Brush, Eraser, Bucket (fill), Eyedropper

- **Brush options**: Size (1-50px), Shape (circle/square), Pixel-perfect toggle- Brush options: size, shape (circle / square), pixel-perfect toggle

- **High-quality eraser**: True transparency with alpha-channel preservation- Clean brush rendering and high-quality eraser that produces true transparency (alpha-preserving erase)

- **Undo/Redo history**: Snapshot-based history system- Undo/Redo history (snapshot-based history manager)



### 🧩 Advanced Symmetry System### 🧩 Symmetry System

- **Rotatable symmetry lines** at any angle (0°–359°) — not limited to H/V- Rotatable symmetry lines (any angle 0°–359°) — not just H/V

- **Stack up to 8 lines** for complex patterns (cross, X, star, custom)- Stack up to 8 symmetry lines for complex patterns (cross, X, star, custom)

- **Draggable centers**: Click and drag symmetry line origins anywhere on canvas- Draggable line centers (move the symmetry origin anywhere on the canvas)

- **Presets**: Vertical, Horizontal, Cross (+), Diagonal (X), Star (8-way)- Presets: Vertical, Horizontal, Cross (+), Diagonal (X), Star (8-way)

- **Tool integration**: Works seamlessly with brush and eraser- Works with brush and eraser (mirrors strokes and erasing across axes)

- **Visual feedback**: Cursor changes to open/closed hand when dragging

### 🖱 Cursor & Preview System

### 🖱 Cursor & Preview System- Aseprite-style brush cursor previews with pixel-accurate outlines

- **Aseprite-style brush cursor** with pixel-accurate outlines- Eraser preview shows inverted-edge outline for clarity

- **Eraser preview** with inverted-edge outline for clarity- Cursor scales correctly with zoom and reflects brush size/shape

- **Zoom-aware**: Cursor scales correctly with zoom level

- **Dynamic updates**: Reflects current brush size and shape in real-time### 🧾 Background & Grid

- Checkered background (user-configurable tile sizes) that scales correctly with zoom

### 🧾 Background & Grid- Grid overlay with configurable cell size and color

- **Checkered background**: User-configurable tile sizes, zoom-aware rendering

- **Grid overlay**: Configurable cell size and color### � UI & Panels

- **Settings dialogs**: Easy customization via View menu- Main window with dockable-like panels (Options, Tools, Color Palette)

- Start screen and new-file dialog for quick canvas creation

### 🎛 UI & Panels- Settings dialogs for grid & background customization

- **Main window** with integrated panels: Tools, Options, Color Palette

- **Start screen** for quick project setup### 🧠 Developer & Build Features

- **New File dialog** with preset canvas sizes- Robust image alpha handling (ARGB32) to avoid white→black erase bugs

- **Intuitive menus**: File, View, Edit with keyboard shortcuts- Icon conversion utility (`convert_icon.py`) to generate multi-resolution `.ico`

- `Kokeshprite.spec` and `BUILD_INSTRUCTIONS.md` for PyInstaller reproducible builds

---- `.gitignore` tuned to avoid committing build artifacts and caches



## 📁 Project Structure---



```## � Where to find important files

Kokeshprite/- `main.py` — Application entry point

├── main.py                  # Application entry point- `src/canvas.py` — Canvas, drawing, cursor logic, and tool implementations

├── convert_icon.py          # Icon conversion utility (PNG → ICO)- `src/symmetry.py` + `src/symmetry_options.py` — Symmetry engine and options UI

├── Kokeshprite.spec         # PyInstaller build configuration- `src/main_window.py` — MainWindow wiring, menus, and dialogs

├── requirements.txt         # Python dependencies- `convert_icon.py` — Convert `icon.png` → `icon.ico` multi-resolution icons

├── icon.png                 # Source icon (256×256 recommended)- `Kokeshprite.spec` — PyInstaller spec used to build the Windows EXE

│- `BUILD_INSTRUCTIONS.md` — Step-by-step build instructions (Windows)

├── src/- `SYMMETRY_GUIDE.md`, `DRAGGABLE_SYMMETRY.md`, `ICON_GUIDE.md` — Feature docs and guides

│   ├── canvas.py            # Canvas widget, drawing, tools, cursor logic

│   ├── symmetry.py          # Symmetry engine (lines, mirroring math)---

│   ├── symmetry_options.py  # Symmetry options panel UI

│   ├── main_window.py       # MainWindow, menus, dialogs## 🎯 Developer Quick Start (Windows)

│   ├── tools_panel.py       # Tools panel (brush/eraser/bucket/eyedropper)

│   ├── options_panel.py     # Brush options panel (size/shape/pixel-perfect)1. Create and activate a virtual environment inside the repo (recommended):

│   ├── color_palette_panel.py  # Color picker palette

│   ├── history.py           # Undo/redo history manager```powershell

│   ├── start_screen.py      # Start screen with new file buttonpython -m venv .venv

│   ├── new_file_dialog.py   # New canvas dialog.\\.venv\\Scripts\\Activate.ps1

│   └── system_eyedropper.py # System-wide eyedropper tool```

│

└── .venv/                   # Virtual environment (gitignored)2. Install developer dependencies (the project uses PyQt6 and Pillow for icon tooling):

```

```powershell

**Generated files** (gitignored):pip install -r requirements.txt

- `icon.ico` — Multi-resolution Windows icon (generated from `icon.png`)# If there is no requirements.txt, install the main deps used here:

- `build/` — PyInstaller temporary build filespip install pyqt6 pillow pyinstaller

- `dist/Kokeshprite.exe` — Final executable```



---3. (Optional) Create `icon.ico` from `icon.png`:



## 🚀 Quick Start```powershell

python convert_icon.py

### Prerequisites```

- Python 3.13+ (earlier versions may work but untested)

- Windows (primary target platform)4. Build a single-file Windows executable (one-file, windowed):



### Development Setup```powershell

.\\.venv\\Scripts\\python.exe -m PyInstaller Kokeshprite.spec --clean

1. **Clone the repository**```

```powershell

git clone https://github.com/CodeKokeshi/Kokeshprite.git5. The built EXE will be available in `dist/Kokeshprite.exe`.

cd Kokeshprite

```Notes:

- The spec file bundles `icon.ico` and `icon.png` so the running app can access the icon for the window/taskbar.

2. **Create and activate virtual environment**- If you change `icon.png`, re-run `python convert_icon.py` before building.

```powershell

python -m venv .venv---

.\.venv\Scripts\Activate.ps1

```## 🔒 Security & Data

- The project currently stores data locally (no cloud sync by default).

3. **Install dependencies**- API keys (if/when added) should be encrypted at rest. See the `BUILD_INSTRUCTIONS.md` and future `settings` implementation for best practices.

```powershell

pip install -r requirements.txt---

```

## 🛣 Roadmap & Next Steps

4. **Run the application**- Layers system (if not already implemented) and layer panel improvements

```powershell- Visual editor for symmetry lines (drag/rotate handles for each line)

python main.py- Save/Load presets for brushes, palettes, and symmetry setups

```- Installer creation/signing (MSI or similar) for Windows distribution

- Optional cloud sync with E2EE for cross-device workflows

---

---

## 🔨 Building Executable

## 🧰 Contribution Guide

### Icon Conversion (if icon.png changed)1. Fork the repository

2. Create a feature branch

**For best quality, use 256×256 or larger `icon.png`!** Small icons will be upscaled but look pixelated at large sizes.3. Implement changes and include tests where appropriate

4. Open a Pull Request describing the change and motivation

```powershell

python convert_icon.pyPlease follow the existing code style (PyQt6 idioms) and keep UIs consistent. If you add major features (new panels, file formats), add/update `BUILD_INSTRUCTIONS.md` and documentation under the repo root.

```

---

This generates `icon.ico` with multiple Windows-standard resolutions (16×16 to 256×256).

## License

### Build the EXESpecify your license here (MIT recommended if you want a permissive license). Add a `LICENSE` file at the repo root.



```powershell---

python -m PyInstaller Kokeshprite.spec --clean

```If you'd like, I can now:

- commit this `README.md` and push to the remote

**Output**: `dist/Kokeshprite.exe` (single-file executable, ~30-50MB)- create/update `requirements.txt` based on used modules

- scaffold a small `next-release-notes.md` listing the symmetry & eraser fixes

The `--clean` flag ensures a fresh build by removing temporary files.

Tell me which of the next steps you want me to take.
### Build Configuration

The `Kokeshprite.spec` file controls:
- **One-file mode**: Everything packed into single EXE
- **No console**: GUI-only, no command window
- **Icon embedding**: Uses `icon.ico` for executable icon
- **Data files**: Embeds `icon.ico` and `icon.png` for runtime window icon
- **UPX compression**: Reduces file size
- **Hidden imports**: Ensures PyQt6 modules are included

### Distribution

Simply distribute `dist/Kokeshprite.exe` — it's a standalone executable with everything bundled!

Users can double-click to run without installing Python or dependencies.

### Troubleshooting Builds

If build fails:
1. Ensure virtual environment is activated
2. Check `icon.ico` exists (run `convert_icon.py`)
3. Delete `build/` and `dist/` folders and retry
4. Verify all imports are available in environment

**Note**: 30-50MB EXE size is normal for PyQt6 applications (includes Python interpreter + Qt framework).

---

## 🛣 Roadmap

- [ ] **Layers system** with layer panel
- [ ] **Visual symmetry editor** with drag/rotate handles
- [ ] **Save/Load** brush, palette, and symmetry presets
- [ ] **File I/O** for saving/loading projects
- [ ] **Export** to PNG/GIF with transparency
- [ ] **Animation timeline** for sprite animations
- [ ] **Installer creation** (MSI or similar) for distribution
- [ ] **macOS and Linux support**

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please follow existing code style (PyQt6 idioms) and keep UI consistent.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔗 Links

- **Repository**: [github.com/CodeKokeshi/Kokeshprite](https://github.com/CodeKokeshi/Kokeshprite)
- **Issues**: [Report bugs or request features](https://github.com/CodeKokeshi/Kokeshprite/issues)

---

*Built with ❤️ using PyQt6*
