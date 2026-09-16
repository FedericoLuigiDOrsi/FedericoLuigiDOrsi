#!/usr/bin/env python3
"""Self-hosted GitHub stats card. Generates assets/card-stats-{light,dark}.svg
from the public GitHub REST API — no third-party rendering service involved,
so it can't go down or rate-limit the profile README.

Regenerate: python3 scripts/cards.py
Re-run automatically by .github/workflows/cards.yml on a daily schedule.
"""
import json
import urllib.request
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = "FedericoLuigiDOrsi"
API = "https://api.github.com"
ASSETS = Path(__file__).resolve().parent.parent / "assets"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USERNAME, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def collect_stats():
    user = fetch(f"{API}/users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = fetch(f"{API}/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        page += 1

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    langs = Counter(r["language"] for r in repos if r.get("language"))
    top_langs = [name for name, _ in langs.most_common(5)]

    return {
        "public_repos": user.get("public_repos", len(repos)),
        "followers": user.get("followers", 0),
        "stars": total_stars,
        "forks": total_forks,
        "top_langs": top_langs,
    }


def render_svg(stats, dark: bool) -> str:
    bg = "#0d1117" if dark else "#ffffff"
    border = "#30363d" if dark else "#d0d7de"
    fg = "#c9d1d9" if dark else "#24292f"
    accent = "#58a6ff" if dark else "#2E9EF7"
    dim = "#8b949e" if dark else "#57606a"

    rows = [
        ("PUBLIC_REPOS", str(stats["public_repos"])),
        ("STARGAZERS", str(stats["stars"])),
        ("FOLLOWERS", str(stats["followers"])),
        ("FORKS", str(stats["forks"])),
        ("TOP_LANG", ", ".join(stats["top_langs"]) or "n/a"),
    ]

    width, height = 440, 32 + len(rows) * 28 + 16
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Fira Code, Consolas, monospace">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{bg}" stroke="{border}"/>',
        f'<text x="20" y="30" font-size="13" fill="{accent}" font-weight="600">stats.sh --user {USERNAME}</text>',
        f'<line x1="16" y1="42" x2="{width - 16}" y2="42" stroke="{border}"/>',
    ]
    y = 68
    for label, value in rows:
        lines.append(f'<text x="24" y="{y}" font-size="12.5" fill="{dim}">{escape(label)}</text>')
        lines.append(f'<text x="{width - 24}" y="{y}" font-size="12.5" fill="{fg}" text-anchor="end">{escape(value)}</text>')
        y += 28
    lines.append("</svg>")
    return "\n".join(lines)


def main():
    ASSETS.mkdir(exist_ok=True)
    stats = collect_stats()
    (ASSETS / "card-stats-dark.svg").write_text(render_svg(stats, dark=True))
    (ASSETS / "card-stats-light.svg").write_text(render_svg(stats, dark=False))
    print("wrote", stats)


if __name__ == "__main__":
    main()
