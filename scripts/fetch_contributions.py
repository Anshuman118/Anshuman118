#!/usr/bin/env python3
"""
Scrape GitHub's public contribution calendar without GraphQL or a PAT.

Usage:
    python scripts/fetch_contributions.py --username YOUR_GITHUB_USERNAME
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL_TEMPLATE = "https://github.com/users/{username}/contributions"
DEFAULT_OUTPUT = Path("data/contributions.json")
USER_AGENT = "animated-github-profile/1.0 (+https://github.com/)"


def parse_count(label: str) -> int:
    match = re.search(r"(\d[\d,]*)\s+contribution", label, re.I)
    return int(match.group(1).replace(",", "")) if match else 0


def level_from_classes(classes: list[str]) -> int:
    for cls in classes:
        m = re.fullmatch(r"ContributionCalendar-day--L(\d)", cls)
        if m:
            return max(0, min(5, int(m.group(1))))
    return 0


def fetch(username: str) -> list[dict]:
    url = URL_TEMPLATE.format(username=username)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code == 404:
        raise RuntimeError(f"GitHub user not found: {username}")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        # Fallback for minor markup changes: look for cells with data-date.
        cells = soup.select("[data-date]")
    if not cells:
        raise RuntimeError(
            "No contribution day cells were found. GitHub may have changed "
            "the public calendar HTML."
        )

    days = []
    for cell in cells:
        raw_date = cell.get("data-date")
        if not raw_date:
            continue
        label = cell.get("aria-label", "") or cell.get("data-level", "")
        count = parse_count(label)
        level = level_from_classes(cell.get("class", []))
        if level == 0 and count:
            level = 1 if count <= 2 else 2 if count <= 5 else 3 if count <= 9 else 4
        days.append({"date": raw_date, "count": count, "level": level})

    if not days:
        raise RuntimeError("Contribution calendar was parsed but contained no dated cells.")
    return sorted(days, key=lambda x: x["date"])


def longest_streak(days: list[dict]) -> int:
    best = current = 0
    prev = None
    for item in days:
        d = date.fromisoformat(item["date"])
        if item["count"] > 0:
            if prev is not None and d == prev + timedelta(days=1):
                current += 1
            else:
                current = 1
            best = max(best, current)
            prev = d
        else:
            current = 0
            prev = d
    return best


def current_streak(days: list[dict]) -> int:
    by_date = {date.fromisoformat(x["date"]): x["count"] for x in days}
    cursor = max(by_date)
    streak = 0
    while by_date.get(cursor, 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def build_payload(username: str, days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: (d["count"], d["date"]))
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "username": username,
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "days": days,
        "total_contributions": total,
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(days),
        "best_day": best,
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    username = args.username or __import__("os").environ.get("GITHUB_USERNAME")
    if not username or username == "YOUR_GITHUB_USERNAME":
        print("ERROR: supply --username YOUR_GITHUB_USERNAME", file=sys.stderr)
        return 2

    try:
        days = fetch(username)
        payload = build_payload(username, days)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(
            f"Saved {len(days)} days, {payload['total_contributions']:,} contributions "
            f"to {args.output}"
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
