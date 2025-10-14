# Improving Your Application Icon

## Current Situation
Your current `icon.png` is **32×32 pixels**, which works but will look pixelated when viewed at larger sizes in Windows Explorer.

## Recommended Icon Specifications

### Ideal Size: **256×256 pixels or larger**

Windows uses these icon sizes:
- **16×16** - Small icons in lists
- **32×32** - Normal icons in Explorer
- **48×48** - Medium icons
- **64×64** - Large icons (tiles)
- **128×128** - Extra large icons
- **256×256** - Jumbo icons (Explorer thumbnails)

## How to Create a Better Icon

### Option 1: Scale Up Your Current Icon (Not Recommended)
If you want to keep the current design, you could scale it up in an image editor, but it will still look pixelated.

### Option 2: Redesign at 256×256 (Recommended)
Use any image editor to create a new icon:
- **GIMP** (Free): File → New → 256×256 pixels
- **Paint.NET** (Free): Image → Canvas Size → 256×256
- **Photoshop/Illustrator**: Create 256×256 artboard
- **Aseprite**: Perfect for pixel art icons! Create 256×256 canvas with 16× zoom

### Option 3: Use AI/Online Tools
- **Favicon.io**: Generate icon from text/emoji
- **Canva**: Free icon templates
- **Flaticon**: Download free icons (check license)

### Option 4: Pixel Art Icon (Authentic!)
Since this is a pixel art editor, create a pixel art icon:
1. Create a 16×16 pixel art design in Aseprite or your editor
2. Export at 16× scale (256×256 pixels) with nearest-neighbor scaling
3. Save as `icon.png`
4. Run `python convert_icon.py`
5. Rebuild the exe

This gives you crisp pixel art at all sizes!

## After Creating Your New Icon

1. Replace `icon.png` with your new 256×256 image
2. Run `python convert_icon.py`
3. Rebuild: `python -m PyInstaller Kokeshprite.spec --clean`
4. Your icon will now look sharp at all sizes! 🎨

## Testing Your Icon

After building:
1. **Explorer view**: Right-click in folder → View → Extra Large Icons
2. **Taskbar**: Run the app and check the taskbar icon
3. **Window title**: Check the icon in the window's title bar
4. **Alt+Tab**: Check the icon in the app switcher

All should look crisp and clear with a 256×256 source image!
