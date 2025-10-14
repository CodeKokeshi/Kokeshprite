# Building Kokeshprite to EXE

## Prerequisites
1. Python 3.13+ with virtual environment activated
2. PyInstaller and Pillow installed

## Icon Requirements

**For best quality, use a 256x256 or larger icon.png file!**

- Current `icon.png` is 32x32 (will be upscaled automatically)
- Windows displays icons at: 16×16, 32×32, 48×48, 64×64, 128×128, 256×256
- Small source icons will look pixelated when viewed as "Extra Large Icons" in Explorer

To replace the icon:
1. Replace `icon.png` with your high-resolution icon (256×256 recommended)
2. Run `python convert_icon.py` to regenerate `icon.ico`
3. Rebuild the executable

## Build Steps

### 1. Convert Icon (if icon.png changed)
```bash
python convert_icon.py
```
This converts `icon.png` to `icon.ico` with multiple Windows-standard sizes (16×16 to 256×256).

**Note:** The script will warn you if your icon.png is smaller than 256×256 and will upscale it, but quality will be better with a larger source image.

### 2. Build the Executable
```bash
python -m PyInstaller Kokeshprite.spec --clean
```

The `--clean` flag ensures a fresh build by removing temporary files.

### 3. Find Your EXE
The executable will be in:
```
dist/Kokeshprite.exe
```

## Build Output Structure

- **dist/Kokeshprite.exe** - The final single-file executable (this is what you distribute!)
- **build/** - Temporary build files (can be deleted)
- **Kokeshprite.spec** - Build configuration file

## Distribution

Just distribute `dist/Kokeshprite.exe` - it's a standalone executable with everything bundled inside!

Users can simply double-click `Kokeshprite.exe` to run your pixel art editor.

## Icon Features

✅ **Multi-resolution support**: The icon looks sharp at all Windows Explorer view sizes
✅ **Window icon**: Shows in the taskbar and window title bar when running
✅ **Executable icon**: Shows in Windows Explorer for the .exe file
✅ **Embedded**: Icon files are bundled inside the executable

The application automatically detects whether it's running as:
- **Development mode**: Uses `icon.png` from the project folder
- **Compiled .exe**: Uses `icon.ico` embedded in the executable

## Build Configuration

The `Kokeshprite.spec` file controls:
- **One-file mode**: Everything packed into single EXE
- **No console**: GUI-only, no command window
- **Icon**: Uses `icon.ico` for the executable file icon
- **Data files**: Embeds `icon.ico` and `icon.png` for runtime window icon
- **UPX compression**: Reduces file size
- **Hidden imports**: Ensures PyQt6 modules are included

## Troubleshooting

If the build fails:
1. Make sure virtual environment is activated
2. Ensure `icon.ico` exists (run `convert_icon.py`)
3. Delete `build/` and `dist/` folders and try again
4. Check that all imports in your code are available in the environment

## File Sizes

The EXE will be ~30-50MB due to:
- Python interpreter
- PyQt6 framework
- All dependencies bundled

This is normal for PyQt6 applications!
