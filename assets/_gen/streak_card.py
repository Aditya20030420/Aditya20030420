"""Render a self-hosted contribution-streak card matching the README design
system — a reliable, grade-free replacement for the herokuapp streak widget
(free dynos sleep / it has outages).

Run to refresh:  python assets/_gen/streak_card.py
Pulls the full public contribution calendar (no auth) and writes assets/streak-card.svg.
"""
import json, urllib.request, datetime, os, calendar

USER = "Aditya20030420"
OUT = os.path.join(os.path.dirname(__file__), "..", "streak-card.svg")

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "readme-gen"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# ?y=last is the only correctly-ordered window (ends today); the no-param
# endpoint's day array is mis-ordered, so use it only for the per-year totals.
days = get(f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last")["contributions"]
totals = get(f"https://github-contributions-api.jogruber.de/v4/{USER}")["total"]

dates = [datetime.date.fromisoformat(d["date"]) for d in days]
counts = [d["count"] for d in days]
total = sum(totals.values())          # all-time
first_year = min(totals)

def fmt(d): return f"{calendar.month_abbr[d.month]} {d.day}"
def rng(a, b): return fmt(a) if a == b else f"{fmt(a)} - {fmt(b)}"

# longest streak: max run of consecutive non-zero days
best = cur = 0
best_end = cur_start = None
for i, c in enumerate(counts):
    if c > 0:
        cur = cur + 1 if cur else 1
        if cur == 1:
            cur_start = dates[i]
        if cur > best:
            best, best_start, best_end = cur, cur_start, dates[i]
    else:
        cur = 0
longest_range = rng(best_start, best_end) if best else "—"

# current streak: walk back from the end; today may be empty without breaking it
i = len(counts) - 1
if i >= 0 and counts[i] == 0:
    i -= 1
cur = 0
cur_end = dates[i] if i >= 0 and counts[i] > 0 else None
while i >= 0 and counts[i] > 0:
    cur += 1
    cur_start = dates[i]
    i -= 1
current_range = rng(cur_start, cur_end) if cur else "—"

since = f"Since {first_year}"

W, H = 880, 150
cx = [176, 440, 704]   # column centers
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" font-family="'Segoe UI',Helvetica,Arial,sans-serif"><defs><linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1620"/><stop offset="1" stop-color="#0b1017"/></linearGradient><linearGradient id="pscan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath><style>.big{{font-size:34px;font-weight:700;fill:#e6edf3}}.lbl{{font-size:13px;font-weight:600;fill:#8b949e}}.lblc{{font-size:13px;font-weight:700;fill:#4F9EE8}}.dt{{font-size:11px;fill:#8b949e}}.ring{{font-size:30px;font-weight:700;fill:#e6edf3}}.sw{{animation:sw 9s ease-in-out infinite}}@keyframes sw{{0%{{transform:translateX(-360px)}}55%,100%{{transform:translateX(620px)}}}}</style></defs><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#pbg)" stroke="#233041"/><g clip-path="url(#pc)"><rect class="sw" x="0" y="0" width="160" height="{H}" fill="url(#pscan)"/><rect x="1" y="1" width="{W-2}" height="3" fill="#4F9EE8"/></g><line x1="293" y1="30" x2="293" y2="120" stroke="#233041"/><line x1="587" y1="30" x2="587" y2="120" stroke="#233041"/><text class="big" x="{cx[0]}" y="68" text-anchor="middle">{total}</text><text class="lbl" x="{cx[0]}" y="92" text-anchor="middle">Total Contributions</text><text class="dt" x="{cx[0]}" y="110" text-anchor="middle">{since}</text><circle cx="{cx[1]}" cy="62" r="33" fill="none" stroke="#4F9EE8" stroke-width="5"/><path d="M{cx[1]} 20 c5 6 2 9 -1 11 c-2 -1 -2 -3 -1 -5 c-4 2 -6 6 -3 10 a6 6 0 1 0 9 -3 c0 3 -2 4 -3 3 c2 -4 -1 -7 -1 -7 c0 4 -4 3 -3 -2 c-1 1 -3 0 -3 -2 l 0 0 z" fill="#4F9EE8"/><text class="ring" x="{cx[1]}" y="72" text-anchor="middle">{cur}</text><text class="lblc" x="{cx[1]}" y="112" text-anchor="middle">Current Streak</text><text class="dt" x="{cx[1]}" y="130" text-anchor="middle">{current_range}</text><text class="big" x="{cx[2]}" y="68" text-anchor="middle">{best}</text><text class="lbl" x="{cx[2]}" y="92" text-anchor="middle">Longest Streak</text><text class="dt" x="{cx[2]}" y="110" text-anchor="middle">{longest_range}</text></svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {os.path.abspath(OUT)}  (total {total}, current {cur}, longest {best})")
