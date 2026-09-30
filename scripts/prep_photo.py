#!/usr/bin/env python3
"""
Prepare a portrait for ASCII conversion.

Usage:
    python scripts/prep_photo.py source-photo.jpg

The background is removed with rembg, local contrast is improved with
OpenCV CLAHE, the subject is composited on white, and the result is
saved as source-prepped.png unless --output is supplied.
"""

from __future__ import annotations

import argparse
import io
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

DEFAULT_OUTPUT = Path("source-prepped.png")


def load_cutout(source: Image.Image) -> Image.Image:
    """Run rembg and normalize either supported output form to an RGBA image."""
    result = remove(source)
    if isinstance(result, Image.Image):
        return result.convert("RGBA")
    if isinstance(result, bytes):
        return Image.open(io.BytesIO(result)).convert("RGBA")
    raise TypeError(f"Background removal returned an unsupported value: {type(result)!r}")


def prepare(source: Path, output: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Source image does not exist: {source}")

    try:
        with Image.open(source) as image:
            rgba = image.convert("RGBA")
    except Exception as exc:
        raise ValueError(f"Could not open image '{source}': {exc}") from exc

    try:
        cutout = load_cutout(rgba)
    except Exception as exc:
        raise RuntimeError(f"Background removal failed: {exc}") from exc

    # Composite on pure white so transparent pixels become a sparse ASCII background.
    white = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, cutout).convert("RGB")

    # CLAHE improves local facial/edge contrast without crushing highlights.
    bgr = cv2.cvtColor(np.asarray(composited), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    lightness = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lightness)
    enhanced = cv2.cvtColor(
        cv2.merge((lightness, a_channel, b_channel)), cv2.COLOR_LAB2BGR
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)).save(output)
    print(f"Saved prepared portrait: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a portrait for ASCII art.")
    parser.add_argument("source", type=Path, help="Source photo (JPG/PNG/WebP/etc.)")
    parser.add_argument(
        "-o", "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Output PNG path (default: source-prepped.png)."
    )
    args = parser.parse_args()

    try:
        prepare(args.source, args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
