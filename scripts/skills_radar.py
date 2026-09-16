#!/usr/bin/env python3
"""Self-rated skills radar chart, in the same terminal aesthetic as the
banner. Self-hosted — hand-drawn SVG polygon math, no charting library and
no third-party rendering service. Edit SKILLS below and re-run to update.

Regenerate: python3 scripts/skills_radar.py
Re-run automatically by .github/workflows/cards.yml on a daily schedule.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# (axis label, 0-10 self rating)
SKILLS = [
    ("Automation (n8n)", 9),
    ("AI Agents", 9),
    ("Backend / Python", 8),
    ("Product & Systems", 8),
    ("Business Ops", 7),
    ("Frontend", 6),
]

WIDTH = 680
HEIGHT = 460
CENTER_X = WIDTH / 2
CENTER_Y = 34 + (HEIGHT - 34 - 40) / 2
RADIUS = 130
RINGS = 4


def render(dark: bool) -> str:
    bg = "#0d1117" if dark else "#ffffff"
    panel = "#161b22" if dark else "#f6f8fa"
    border = "#30363d" if dark else "#d0d7de"
    fg = "#c9d1d9" if dark else "#24292f"
    dim = "#8b949e" if dark else "#57606a"
    accent = "#58a6ff" if dark else "#2E9EF7"
    fill = "rgba(88,166,255,0.28)" if dark else "rgba(46,158,247,0.22)"

    n = len(SKILLS)
    angle_step = 2 * math.pi / n
    start = -math.pi / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Fira Code, Consolas, monospace">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{bg}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="{border}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="34" rx="12" fill="{panel}"/>',
        f'<rect x="0.5" y="22" width="{WIDTH - 1}" height="13" fill="{panel}"/>',
        f'<line x1="0.5" y1="34.5" x2="{WIDTH - 0.5}" y2="34.5" stroke="{border}"/>',
        '<circle cx="20" cy="17" r="5" fill="#ff5f56"/>',
        '<circle cx="38" cy="17" r="5" fill="#ffbd2e"/>',
        '<circle cx="56" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH / 2}" y="21" font-size="12" fill="{dim}" text-anchor="middle">skills.sh --radar --self-rated</text>',
    ]

    # rings
    for ring in range(1, RINGS + 1):
        r = RADIUS * ring / RINGS
        pts = " ".join(f"{CENTER_X + r * math.cos(start + i * angle_step):.1f},{CENTER_Y + r * math.sin(start + i * angle_step):.1f}" for i in range(n))
        parts.append(f'<polygon points="{pts}" fill="none" stroke="{border}" stroke-width="1"/>')

    # spokes + labels
    for i, (label, _) in enumerate(SKILLS):
        a = start + i * angle_step
        x2, y2 = CENTER_X + RADIUS * math.cos(a), CENTER_Y + RADIUS * math.sin(a)
        parts.append(f'<line x1="{CENTER_X}" y1="{CENTER_Y}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{border}" stroke-width="1"/>')
        lx, ly = CENTER_X + (RADIUS + 34) * math.cos(a), CENTER_Y + (RADIUS + 34) * math.sin(a)
        anchor = "middle"
        if lx < CENTER_X - 10:
            anchor = "end"
        elif lx > CENTER_X + 10:
            anchor = "start"
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="11" fill="{dim}" text-anchor="{anchor}">{escape(label)}</text>')

    # data polygon
    pts = []
    for i, (_, value) in enumerate(SKILLS):
        a = start + i * angle_step
        r = RADIUS * (value / 10)
        pts.append(f"{CENTER_X + r * math.cos(a):.1f},{CENTER_Y + r * math.sin(a):.1f}")
    parts.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{accent}" stroke-width="2"/>')
    for i, (_, value) in enumerate(SKILLS):
        a = start + i * angle_step
        r = RADIUS * (value / 10)
        cx, cy = CENTER_X + r * math.cos(a), CENTER_Y + r * math.sin(a)
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{accent}"/>')

    parts.append(f'<text x="{WIDTH / 2}" y="{HEIGHT - 14}" font-size="10.5" fill="{dim}" text-anchor="middle">self-rated · out of 10 · updated by hand, not by vanity</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "radar-dark.svg").write_text(render(dark=True))
    (ASSETS / "radar-light.svg").write_text(render(dark=False))
    print("wrote radar-dark.svg and radar-light.svg")


if __name__ == "__main__":
    main()
