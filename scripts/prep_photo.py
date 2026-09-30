#!/usr/bin/env python3
"""
Prepare a portrait for ASCII conversion.

Usage:
    python scripts/prep_photo.py source-photo.jpg

The background is removed with rembg, local contrast is improved with
OpenCV CLAHE, the subject is composited on white, and the result is
converted to grayscale as <source-stem>-prepped.png.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

try:
    from rembg import remove
except ImportError as exc:
    raise SystemExit(
        "rembg is not installed. Activate your virtual environment and run "
        "`pip install -r scripts/requirements.txt`."
    ) from exc


def output_path_for(source: Path) -> Path:
    return source.with_name(f"{source.stem}-prepped.png")


def prepare(source: Path, output: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Source image does not exist: {source}")

    try:
        with Image.open(source) as img:
            rgba = img.convert("RGBA")
    except Exception as exc:
        raise ValueError(f"Could not open image '{source}': {exc}") from exc

    try:
        cutout = remove(rgba)
        if not isinstance(cutout, Image.Image):
            cutout = Image.open(cutout)
        cutout = cutout.convert("RGBA")
    except Exception as exc:
        raise RuntimeError(f"Background removal failed: {exc}") from exc

    # Composite on pure white so transparent pixels become bright background.
    white = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, cutout).convert("RGB")

    # OpenCV CLAHE improves local facial/edge contrast without globally
    # crushing highlights and shadows.
    bgr = cv2.cvtColor(np.asarray(composited), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    enhanced = cv2.cvtColor(
        cv2.merge((l_channel, a_channel, b_channel)), cv2.COLOR_LAB2BGR
    )
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)

    Image.fromarray(gray).save(output)
    print(f"Saved prepared portrait: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a portrait for ASCII art.")
    parser.add_argument("source", type=Path, help="Source photo (JPG/PNG/WebP/etc.)")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output PNG path. Defaults to <source-stem>-prepped.png."
    )
    args = parser.parse_args()

    output = args.output or output_path_for(args.source)
    try:
        prepare(args.source, output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
