# Generate ZipShield Pro launcher icons (all mipmap densities) with Pillow.
# Dark rounded-square background, neon cyan shield outline + lightning bolt.
# Run from the repo root:  python3 tools/generate_icon.py
from PIL import Image, ImageDraw
import os

DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

BG = (11, 15, 23, 255)      # #0B0F17
CYAN = (0, 243, 255, 255)   # #00F3FF


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # rounded square background
    r = int(size * 0.18)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=BG)
    # shield outline (top edge, sides curve down to a bottom point)
    cx = size / 2
    top = size * 0.16
    bottom = size * 0.86
    left = size * 0.22
    right = size * 0.78
    w = max(2, int(size * 0.045))
    pts = [
        (left, top + size * 0.06),
        (cx, top),
        (right, top + size * 0.06),
        (right, size * 0.52),
        (cx, bottom),
        (left, size * 0.52),
    ]
    d.line(pts + [pts[0]], fill=CYAN, width=w, joint="curve")
    # lightning bolt inside the shield
    bolt = [
        (cx + size * 0.06, size * 0.30),
        (cx - size * 0.07, size * 0.56),
        (cx + size * 0.01, size * 0.56),
        (cx - size * 0.06, size * 0.74),
        (cx + size * 0.08, size * 0.50),
        (cx + size * 0.00, size * 0.50),
    ]
    d.polygon(bolt, fill=CYAN)
    return img


for name, size in DENSITIES.items():
    outdir = os.path.join("res", name)
    os.makedirs(outdir, exist_ok=True)
    draw_icon(size).save(os.path.join(outdir, "ic_launcher.png"))
    print("wrote", name, "ic_launcher.png", size)
