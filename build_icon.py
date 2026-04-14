"""Convert icon_source.png to a multi-size Windows .ico file."""
from pathlib import Path
from PIL import Image

src = Path(__file__).parent / "assets" / "icon_source.png"
dst = Path(__file__).parent / "assets" / "icon.ico"

img = Image.open(src).convert("RGBA")

# Crop to square (center crop)
w, h = img.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
img = img.crop((left, top, left + side, top + side))

# Resize to 256x256 first (the largest .ico supports well)
img = img.resize((256, 256), Image.LANCZOS)

# Save — Pillow auto-generates all standard sizes from the input
img.save(dst, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)])

print(f"Created {dst} ({dst.stat().st_size:,} bytes)")

# Verify
check = Image.open(dst)
print(f"Default opens at: {check.size}")
print(f"Embedded sizes: {check.info.get('sizes', 'n/a')}")
