#!/usr/bin/env python3
"""
Generate Windows .ico files from Logo.png (PNG source).

Why:
- Windows EXE/Installer icons require .ico (not .png).
- We do not commit binary .ico into git; this script generates them during build.

Usage (from project root):
  python scripts/generate_windows_icons.py

Optional:
  python scripts/generate_windows_icons.py --input Logo.png --out build-config/TallyConnect.ico
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def _make_square_rgba(img):
    from PIL import Image

    img = img.convert("RGBA")
    w, h = img.size
    side = max(w, h)
    if w == h:
        return img
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2))
    return canvas


def generate_ico(input_png: Path, output_ico: Path, sizes: list[int]) -> None:
    from PIL import Image

    if not input_png.exists():
        raise FileNotFoundError(f"Input logo not found: {input_png}")

    output_ico.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(str(input_png))
    img = _make_square_rgba(img)

    # Pillow can generate all ICO sizes from a single source image.
    ico_sizes = [(s, s) for s in sizes]
    img.save(str(output_ico), format="ICO", sizes=ico_sizes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="Logo.png", help="Path to Logo.png (PNG)")
    parser.add_argument("--out", default=os.path.join("build-config", "TallyConnect.ico"), help="Output .ico path")
    parser.add_argument(
        "--sizes",
        default="16,24,32,48,64,128,256",
        help="Comma-separated icon sizes to include in ICO",
    )
    args = parser.parse_args()

    input_png = Path(args.input).resolve()
    output_ico = Path(args.out).resolve()
    sizes = [int(x.strip()) for x in str(args.sizes).split(",") if x.strip()]

    generate_ico(input_png=input_png, output_ico=output_ico, sizes=sizes)
    print(f"[OK] Generated ICO: {output_ico}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


