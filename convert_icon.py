"""Convert icon.png to icon.ico for Windows executable with proper multi-resolution support"""
from PIL import Image

# Load the PNG
img = Image.open('icon.png')
original_size = img.size
print(f"Original icon size: {original_size}")

# Standard Windows icon sizes
standard_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# If the original is smaller than 256x256, we'll upscale it first for better quality
if original_size[0] < 256 or original_size[1] < 256:
    print(f"⚠ Warning: Icon is small ({original_size}). Upscaling to 256x256 for better quality.")
    print("For best results, provide a 256x256 or larger icon.png")
    # Use LANCZOS for high-quality upscaling
    img_large = img.resize((256, 256), Image.Resampling.LANCZOS)
else:
    img_large = img

# Create different sizes by downscaling from the largest
images = []
for size in standard_sizes:
    if size[0] <= img_large.size[0]:
        resized = img_large.resize(size, Image.Resampling.LANCZOS)
        images.append(resized)
        print(f"  Generated {size[0]}x{size[1]}")

# Save as ICO with all sizes
img_large.save('icon.ico', format='ICO', sizes=[img.size for img in images], append_images=images[1:])

print(f"✓ icon.ico created successfully with {len(images)} sizes!")
print("  Sizes: " + ", ".join([f"{s[0]}x{s[1]}" for s in standard_sizes[:len(images)]]))
