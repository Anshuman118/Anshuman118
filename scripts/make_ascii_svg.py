#!/usr/bin/env python3
"""Generate a GitHub-compatible animated ASCII portrait SVG."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

RAMP = " .\`:-=+*cs#%@"
DEFAULT_INPUT = Path("source-prepped.png")
DEFAULT_OUTPUT = Path("avi-ascii.svg")
COLS, ROWS = 72, 53
FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace"


def pixels_to_ascii(path: Path, cols: int, rows: int) -> list[str]:
    image = Image.open(path).convert("L")
    image = ImageOps.autocontrast(image, cutoff=2)
    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageOps.fit(image, (cols, rows), method=Image.Resampling.LANCZOS)
    maximum = len(RAMP) - 1
    return [
        "".join(RAMP[round((255 - image.getpixel((x, y))) / 255 * maximum)]
                for x in range(cols))
        for y in range(rows)
    ]


def build_svg(lines: list[str]) -> str:
    width, height, font_size, row_height = 620, 470, 10, 8
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Animated ASCII portrait">',
        '<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="2"/>',
        f'<text x="18" y="24" fill="#58a6ff" font-family="{FONT}" font-size="11">profile@github:~$ whoami</text>',
        f'<g fill="#c9d1d9" font-family="{FONT}" font-size="{font_size}px" xml:space="preserve">',
    ]
    for index, line in enumerate(lines):
        y = 44 + index * row_height
        delay = 0.15 + index * 0.05
        parts.append(
            f'<text x="18" y="{y}" opacity="0">{html.escape(line, quote=False)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
            f'dur=".24s" fill="freeze"/></text>'
        )
    parts += [
        '</g>',
        f'<text x="18" y="{height - 14}" fill="#8b949e" font-family="{FONT}" font-size="10">portrait loaded • {COLS}×{ROWS}</text>',
        '</svg>',
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cols", type=int, default=COLS)
    parser.add_argument("--rows", type=int, default=ROWS)
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}. Run prep_photo.py first.")
    args.output.write_text(build_svg(pixels_to_ascii(args.input, args.cols, args.rows)), encoding="utf-8")
    print(f"Saved ASCII SVG: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
