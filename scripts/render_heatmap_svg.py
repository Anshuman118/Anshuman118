#!/usr/bin/env python3
"""Render contribution JSON as an animated, self-contained SVG heatmap."""

from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]
FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace"


def month_label(month: int) -> str:
    return ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month - 1]


def render(data: dict) -> str:
    days = {x["date"]: x for x in data.get("days", [])}
    if not days:
        raise ValueError("contributions.json contains no days.")

    dates = sorted(date.fromisoformat(d) for d in days)
    start = dates[0]
    # Align to Sunday, matching GitHub's visual calendar convention.
    start = start - __import__("datetime").timedelta(days=(start.weekday() + 1) % 7)
    end = dates[-1]
    end = end + __import__("datetime").timedelta(days=(6 - ((end.weekday() + 1) % 7)) % 7)

    weeks = math.ceil((end - start).days / 7) + 1
    cell = 11
    gap = 3
    left = 42
    top = 42
    grid_w = weeks * (cell + gap)
    width = left + grid_w + 24
    height = 145

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="GitHub contribution heatmap">',
        '<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d"/>',
        f'<text x="20" y="24" fill="#c9d1d9" font-family="{FONT}" font-size="13" font-weight="700">'
        f'{escape(data.get("username", "YOUR_GITHUB_USERNAME"))} / contributions</text>',
        f'<text x="{width-230}" y="24" fill="#8b949e" font-family="{FONT}" font-size="11">'
        f'{data.get("total_contributions", 0):,} contributions • last year</text>',
    ]

    for week in range(weeks):
        for dow in range(7):
            current = start + __import__("datetime").timedelta(days=week * 7 + dow)
            item = days.get(current.isoformat(), {"count": 0, "level": 0})
            level = max(0, min(5, int(item.get("level", 0))))
            x = left + week * (cell + gap)
            y = top + dow * (cell + gap)
            # Diagonal reveal: farther down/right means later.
            delay = 0.12 + (week + dow) * 0.018
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{PALETTE[level]}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" '
                f'dur=".32s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0 5" to="0 0" begin="{delay:.3f}s" dur=".32s" fill="freeze"/>'
                f'</rect>'
            )

    # Day labels.
    for label, dow in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        y = top + dow * (cell + gap) + 11
        parts.append(
            f'<text x="6" y="{y}" fill="#8b949e" font-family="{FONT}" font-size="9">{label}</text>'
        )

    # Month labels.
    seen = set()
    for week in range(weeks):
        current = start + __import__("datetime").timedelta(days=week * 7)
        key = (current.year, current.month)
        if key not in seen:
            seen.add(key)
            x = left + week * (cell + gap)
            parts.append(
                f'<text x="{x}" y="38" fill="#8b949e" font-family="{FONT}" font-size="9">'
                f'{month_label(current.month)}</text>'
            )

    legend_x = width - 195
    legend_y = height - 24
    parts.append(
        f'<text x="{legend_x-30}" y="{legend_y+11}" fill="#8b949e" '
        f'font-family="{FONT}" font-size="9">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        x = legend_x + i * 18
        parts.append(f'<rect x="{x}" y="{legend_y}" width="12" height="12" rx="3" fill="{color}"/>')
    parts.append(
        f'<text x="{legend_x+6*18+2}" y="{legend_y+11}" fill="#8b949e" '
        f'font-family="{FONT}" font-size="9">More</text>'
    )

    stats = (
        f'Streak {data.get("current_streak", 0)}d • '
        f'Longest {data.get("longest_streak", 0)}d • '
        f'Best {data.get("best_day", {}).get("count", 0)}'
    )
    parts.append(
        f'<text x="20" y="{height-12}" fill="#8b949e" font-family="{FONT}" font-size="10">'
        f'{escape(stats)}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/contributions.json"))
    parser.add_argument("--output", type=Path, default=Path("contrib-heatmap.svg"))
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.write_text(render(data), encoding="utf-8")
    print(f"Saved contribution heatmap: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
