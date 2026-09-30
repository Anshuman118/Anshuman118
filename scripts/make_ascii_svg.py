#!/usr/bin/env python3
"""Generate an animated, monochrome ASCII portrait SVG from a grayscale PNG."""

from __future__ import annotations

import argparse
import html
import math
import os
from pathlib import Path

from PIL import Image, ImageOps

RAMP = " .`:-=+*cs#%@"
DEFAULT_INPUT = Path("source-prepped.png")
DEFAULT_OUTPUT = Path("avi-ascii.svg")
COLS = 100
ROWS = 53
TEXT_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace"


def pixels_to_ascii(path: Path, cols: int, rows: int) -> list[str]:
    image = Image.open(path).convert("L")

    # Terminal glyphs are taller than they are wide, so compensate vertically.
    target_ratio = cols / (rows * 0.50)
    w, h = image.size
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_h = max(1, round(w / target_ratio))
        image = image.resize((w, new_h), Image.Resampling.LANCZOS)
    else:
        new_w = max(1, round(h * target_ratio))
        image = image.resize((new_w, h), Image.Resampling.LANCZOS)

    image = ImageOps.fit(image, (cols, rows), method=Image.Resampling.LANCZOS)
    result = []
    max_index = len(RAMP) - 1
    for y in range(rows):
        line = []
        for x in range(cols):
            brightness = image.getpixel((x, y))
            # White -> sparse, black -> dense.
            idx = round((255 - brightness) / 255 * max_index)
            line.append(RAMP[max(0, min(max_index, idx))])
        result.append("".join(line))
    return result


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def build_svg(lines: list[str], width: int = 1000, row_height: int = 18) -> str:
    height = 30 + len(lines) * row_height + 24
    font_size = 15
    total_duration = 0.35 + len(lines) * 0.055 + 0.55

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Animated ASCII portrait">',
        f'<rect width="100%" height="100%" rx="10" fill="{BG_COLOR}"/>',
        '<defs>',
        '<filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feGaussianBlur stdDeviation="1.4" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
        '</defs>',
        f'<g fill="{TEXT_COLOR}" font-family="{FONT}" font-size="{font_size}px" '
        'font-weight="500" xml:space="preserve" filter="url(#softGlow)">'
    ]

    for i, line in enumerate(lines):
        y = 22 + i * row_height
        delay = 0.25 + i * 0.055
        duration = 0.55
        clip_id = f"rowClip{i}"
        parts += [
            f'<clipPath id="{clip_id}"><rect x="8" y="{y-font_size}" width="0" height="{row_height+4}">'
            f'<animate attributeName="width" from="0" to="{width-16}" begin="{delay:.3f}s" '
            f'dur="{duration:.2f}s" fill="freeze"/></rect></clipPath>',
            f'<g clip-path="url(#{clip_id})">',
            f'<text x="8" y="{y}">{esc(line)}</text>',
            f'</g>',
            # Cursor follows the row reveal, then disappears.
            f'<rect x="8" y="{y-font_size+1}" width="7" height="{font_size+2}" fill="{TEXT_COLOR}" opacity="0">'
            f'<animate attributeName="x" from="8" to="{width-12}" begin="{delay:.3f}s" '
            f'dur="{duration:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.9;1" '
            f'begin="{delay:.3f}s" dur="{duration:.2f}s" fill="freeze"/></rect>'
        ]

    parts += [
        '</g>',
        f'<text x="12" y="{height-8}" fill="#8b949e" font-family="{FONT}" font-size="11px">'
        f'./avi-ascii.svg • {COLS}×{ROWS} • prints once</text>',
        '</svg>'
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
        raise SystemExit(
            f"Input not found: {args.input}. Run prep_photo.py first."
        )
    lines = pixels_to_ascii(args.input, args.cols, args.rows)
    args.output.write_text(build_svg(lines), encoding="utf-8")
    print(f"Saved ASCII SVG: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
