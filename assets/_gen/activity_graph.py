"""Render a self-hosted contribution activity graph SVG matching the README
design system (dark gradient panel, blue accent, light sweep).

Run to refresh:  python assets/_gen/activity_graph.py
Pulls the public contribution calendar (no auth) and writes assets/activity-graph.svg.
The SVG is a static snapshot — re-run to update the numbers.
"""
import json, urllib.request, datetime, os, calendar, math

USER = "Aditya20030420"
OUT = os.path.join(os.path.dirname(__file__), "..", "activity-graph.svg")
API = f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last"

# ---- data -----------------------------------------------------------------
with urllib.request.urlopen(API, timeout=30) as r:
    data = json.load(r)
days = data["contributions"]
total = data["total"]["lastYear"]

# group days into ISO-ish weeks of 7 (first day = first bucket start)
weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
wcounts = [sum(d["count"] for d in w) for w in weeks]
wstart = [datetime.date.fromisoformat(w[0]["date"]) for w in weeks]
n = len(weeks)
peak = max(wcounts) or 1

# ---- layout ---------------------------------------------------------------
W, H = 880, 200
L, R = 44, 852          # chart x range
TOP, BASE = 56, 168     # chart y range (BASE = zero line)
span = R - L
height = BASE - TOP

def px(i):   return L + (i / (n - 1)) * span if n > 1 else L
# sqrt scale: spiky contribution data reads flat on a linear axis
def py(v):   return BASE - (math.sqrt(v) / math.sqrt(peak)) * height

pts = [(px(i), py(v)) for i, v in enumerate(wcounts)]
line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
area = f"M{L:.1f},{BASE} " + "".join(f"L{x:.1f},{y:.1f} " for x, y in pts) + f"L{R:.1f},{BASE} Z"

# month labels where the month changes
months = []
prev = None
for i, d in enumerate(wstart):
    if d.month != prev:
        months.append((px(i), calendar.month_abbr[d.month]))
        prev = d.month

mlabels = "".join(
    f'<text class="ax" x="{x:.1f}" y="186" text-anchor="middle">{m}</text>'
    for x, m in months
)

# faint horizontal guide + peak tick
mid = py(peak / 2)
guides = (
    f'<line x1="{L}" y1="{BASE}" x2="{R}" y2="{BASE}" stroke="#233041" stroke-width="1"/>'
    f'<line x1="{L}" y1="{mid:.1f}" x2="{R}" y2="{mid:.1f}" stroke="#1b2531" stroke-width="1" stroke-dasharray="3 4"/>'
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" font-family="'Segoe UI',Helvetica,Arial,sans-serif"><defs><linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1620"/><stop offset="1" stop-color="#0b1017"/></linearGradient><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4F9EE8" stop-opacity="0.35"/><stop offset="1" stop-color="#4F9EE8" stop-opacity="0"/></linearGradient><linearGradient id="pscan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath><style>.tt{{font-size:14px;font-weight:700;fill:#e6edf3}}.mt{{font-size:12px;fill:#8b949e}}.ax{{font-size:9.5px;fill:#8b949e}}.sw{{animation:sw 9s ease-in-out infinite}}@keyframes sw{{0%{{transform:translateX(-360px)}}55%,100%{{transform:translateX(620px)}}}}</style></defs><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#pbg)" stroke="#233041"/><g clip-path="url(#pc)"><rect class="sw" x="0" y="0" width="160" height="{H}" fill="url(#pscan)"/><rect x="1" y="1" width="{W-2}" height="3" fill="#4F9EE8"/></g><text class="tt" x="24" y="30">Contribution Activity</text><text class="mt" x="856" y="30" text-anchor="end">{total} contributions in the last year</text>{guides}<path d="{area}" fill="url(#area)"/><polyline points="{line}" fill="none" stroke="#4F9EE8" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>{mlabels}</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {os.path.abspath(OUT)}  ({n} weeks, peak {peak}/wk, total {total})")
