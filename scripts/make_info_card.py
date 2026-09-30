#!/usr/bin/env python3
"""Generate a configurable animated neofetch-style profile card SVG."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from xml.sax.saxutils import escape

PROFILE = {
    "username": "YOUR_GITHUB_USERNAME",
    "name": "Anshuman Verma",
    "location": "India",
    "role": "B.Tech Student & Developer",
    "now": "Building projects & learning DSA",
    "prev": "Web Development & WordPress",
    "stack": "Python  C++  JavaScript Git",
    "highlights": "GitHub Projects  Web Development"
    "status": "Available for collaboration",
}

BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
BORDER = "#30363d"
FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace"


def env_or_profile(key: str, value: str) -> str:
    return os.getenv(key.upper(), value)


def get_profile() -> dict[str, str]:
    p = {k: env_or_profile(k, v) for k, v in PROFILE.items()}
    # Environment variables use descriptive names.
    mapping = {
        "current_focus": "now",
        "previous_experience": "prev",
        "tech_stack": "stack",
    }
    for env_key, profile_key in mapping.items():
        if os.getenv(env_key.upper()):
            p[profile_key] = os.environ[env_key.upper()]
    return p


def svg_escape(value: str) -> str:
    return escape(str(value))


def build(profile: dict[str, str], static: bool) -> str:
    rows = [
        ("NAME", profile["name"]),
        ("ROLE", profile["role"]),
        ("NOW", profile["now"]),
        ("PREV", profile["prev"]),
        ("STACK", profile["stack"]),
        ("HIGHLIGHTS", profile["highlights"]),
        ("STATUS", profile["status"]),
    ]
    width, height = 860, 350
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Neofetch profile card">',
        f'<rect width="100%" height="100%" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>',
        f'<text x="26" y="34" fill="{ACCENT}" font-family="{FONT}" font-size="15" font-weight="700">'
        f'{svg_escape(profile["username"])}@github:~$ neofetch</text>',
        f'<text x="26" y="58" fill="{MUTED}" font-family="{FONT}" font-size="12">PROFILE // SYSTEM INFORMATION</text>',
    ]

    start_y = 94
    for i, (key, value) in enumerate(rows):
        y = start_y + i * 36
        delay = 0.25 + i * 0.12
        animation = ""
        if not static:
            animation = (
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur=".42s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="12 0" to="0 0" '
                f'begin="{delay:.2f}s" dur=".42s" fill="freeze"/>'
            )
        parts += [
            f'<g opacity="{"1" if static else "0"}">{animation}',
            f'<text x="28" y="{y}" fill="{ACCENT}" font-family="{FONT}" font-size="13" font-weight="700">'
            f'{svg_escape(key):<10}</text>',
            f'<text x="170" y="{y}" fill="{FG}" font-family="{FONT}" font-size="13">'
            f'{svg_escape(value)}</text>',
            '</g>'
        ]

    parts += [
        f'<line x1="26" y1="324" x2="834" y2="324" stroke="{BORDER}"/>',
        f'<text x="28" y="343" fill="{MUTED}" font-family="{FONT}" font-size="11">'
        f'edit PROFILE / regenerate to update</text>',
        '</svg>'
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("info-card.svg"))
    parser.add_argument(
        "--static", action="store_true",
        help="Generate a non-animated card. STATIC=1 also enables this."
    )
    args = parser.parse_args()
    static = args.static or os.getenv("STATIC") == "1"
    args.output.write_text(build(get_profile(), static), encoding="utf-8")
    print(f"Saved info card: {args.output} ({'static' if static else 'animated'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
