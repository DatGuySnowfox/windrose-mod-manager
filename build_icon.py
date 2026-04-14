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

sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(dst, format="ICO", sizes=sizes)
print(f"Created {dst} ({dst.stat().st_size:,} bytes)")
