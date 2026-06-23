"""Generates packaging/icon.ico from the Carbon Red palette. Run once: python packaging/make_icon.py"""
from pathlib import Path

from PIL import Image, ImageDraw

BG     = (10, 10, 11, 255)
ACCENT = (224, 48, 63, 255)

SIZES = [16, 24, 32, 48, 64, 128, 256]


def render(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG)
    draw = ImageDraw.Draw(img)
    pad = max(1, size // 6)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=max(1, size // 6),
        fill=ACCENT,
    )
    return img


def main():
    out_path = Path(__file__).parent / "icon.ico"
    images = [render(size) for size in SIZES]
    images[0].save(out_path, format="ICO", sizes=[(s, s) for s in SIZES])
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
