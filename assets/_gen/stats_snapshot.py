"""Render a self-hosted "Snapshot" stats panel matching the README design
system — a positive, grade-free alternative to the github-readme-stats card.

Run to refresh:  python assets/_gen/stats_snapshot.py
Pulls live contribution + repo counts (no auth) and writes assets/stats-snapshot.svg.
"""
import json, urllib.request, os

USER = "Aditya20030420"
OUT = os.path.join(os.path.dirname(__file__), "..", "stats-snapshot.svg")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "readme-gen"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

contrib = fetch(f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last")["total"]["lastYear"]
repos = fetch(f"https://api.github.com/users/{USER}")["public_repos"]

# curated constants (rarely change)
FEATURED = 4      # projects showcased in Featured Projects
LANGS = 7         # distinct languages in the top-langs card

tiles = [
    (str(contrib), "Contributions · 1yr"),
    (str(repos),   "Public repos"),
    (str(FEATURED),"Featured projects"),
    (str(LANGS),   "Languages"),
]

W, H = 880, 112
cols = len(tiles)
colw = (W - 8) / cols
centers = [4 + colw * (i + 0.5) for i in range(cols)]

tile_svg = ""
for (num, label), cx in zip(tiles, centers):
    tile_svg += (
        f'<text class="num" x="{cx:.1f}" y="74" text-anchor="middle">{num}</text>'
        f'<text class="lbl" x="{cx:.1f}" y="92" text-anchor="middle">{label}</text>'
    )
dividers = "".join(
    f'<line x1="{4 + colw * i:.1f}" y1="48" x2="{4 + colw * i:.1f}" y2="96" stroke="#233041" stroke-width="1"/>'
    for i in range(1, cols)
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" font-family="'Segoe UI',Helvetica,Arial,sans-serif"><defs><linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1620"/><stop offset="1" stop-color="#0b1017"/></linearGradient><linearGradient id="pscan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath><style>.tt{{font-size:14px;font-weight:700;fill:#e6edf3}}.num{{font-size:24px;font-weight:700;fill:#4F9EE8}}.lbl{{font-size:10.5px;fill:#8b949e}}.sw{{animation:sw 9s ease-in-out infinite}}@keyframes sw{{0%{{transform:translateX(-360px)}}55%,100%{{transform:translateX(620px)}}}}</style></defs><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#pbg)" stroke="#233041"/><g clip-path="url(#pc)"><rect class="sw" x="0" y="0" width="160" height="{H}" fill="url(#pscan)"/><rect x="1" y="1" width="{W-2}" height="3" fill="#4F9EE8"/></g><text class="tt" x="24" y="30">Snapshot</text>{dividers}{tile_svg}</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {os.path.abspath(OUT)}  (contrib {contrib}, repos {repos})")
