"""Generate the animated hero SVG.

Background: a terminal that TYPES code line-by-line up to ~20 lines, holds,
clears, then types a DIFFERENT snippet — cycling through several distinct
snippets so the same code never shows twice in a row.
Foreground: name + underline, a cycling "Aspiring <role>" typewriter, and an
availability line (all static-visible so nothing vanishes if animation is off).

Run:  python assets/_gen/hero.py   ->  assets/hero.svg
Edit SNIPPETS / ROLES below and re-run to change the content.
"""
import os, re, html

OUT = os.path.join(os.path.dirname(__file__), "..", "hero.svg")

# ---- content ---------------------------------------------------------------
SNIPPETS = [
    # hybrid retrieval
    '''import torch
from rag import Retriever, Reranker, Index

class HybridRetriever:
    def __init__(self, alpha=0.7):
        self.alpha = alpha
        self.dense = Index("minilm")
        self.bm25 = Index("bm25")

    def search(self, query, k=8):
        dense = self.dense.query(query, k)
        sparse = self.bm25.query(query, k)
        return self.fuse(dense, sparse)

    def fuse(self, dense, sparse):
        scores = {}
        for doc, w in dense:
            scores[doc] = self.alpha * w
        return rank(scores, k=8)''',
    # training loop
    '''import torch
import torch.nn as nn

class RiskModel(nn.Module):
    def __init__(self, dim=128):
        super().__init__()
        self.lstm = nn.LSTM(dim, 64)
        self.head = nn.Linear(64, 1)

    def forward(self, x):
        h, _ = self.lstm(x)
        return self.head(h[-1])

model = RiskModel()
opt = torch.optim.Adam(model.parameters())
for epoch in range(100):
    for xb, yb in loader:
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()''',
    # document parsing
    '''import re
import pytesseract
from pdf import extract_pages

def parse(statement):
    text = ""
    for page in extract_pages(statement):
        text += pytesseract.ocr(page)
    return structure(text)

def structure(text):
    fields = {}
    for line in text.splitlines():
        m = re.match(r"(\\w+):\\s*(.+)", line)
        if m:
            fields[m[1]] = m[2]
    return fields

print(parse("hdfc.pdf"))''',
]
ROLES = ["AI / ML Engineer", "Data Analyst", "Data Scientist"]

# ---- code typing timeline --------------------------------------------------
PERCHAR = 0.016   # s per char typed
PERERASE = 0.006  # s per char deleted (faster than typing)
HOLD = 2.6        # s all lines visible before deleting
FS = 11           # code font-size
DY = 13.5         # line height
Y0 = 52           # first baseline
CPX = 6.45        # px per char at FS

KW = set("import from class def return for in if elif else while with as and or "
         "not None True False super print range lambda yield try except raise".split())

def color_line(s):
    """Light syntax highlight -> list of (text, cssclass)."""
    out, i = [], 0
    for m in re.finditer(r'(#.*$)|("[^"]*"|\'[^\']*\')|([A-Za-z_]\w*)|(\s+)|(.)', s):
        c, st, wd = m.group(1), m.group(2), m.group(3)
        if c is not None:
            out.append((c, "cm"))
        elif st is not None:
            out.append((st, "str"))
        elif wd is not None:
            out.append((wd, "kw" if wd in KW else "var"))
        else:
            out.append((m.group(0), "var"))
    # merge adjacent same-class for brevity
    merged = []
    for t, k in out:
        if merged and merged[-1][1] == k:
            merged[-1][0] += t
        else:
            merged.append([t, k])
    return merged

def tspans(s):
    return "".join(f'<tspan class="{k}">{html.escape(t)}</tspan>' for t, k in color_line(s))

# per-snippet window durations: type all lines, hold, then delete bottom-up
def tl(line): return max(0.15, len(line) * PERCHAR)
def el(line): return max(0.10, len(line) * PERERASE)
windows = [sum(tl(l) for l in snip.split("\n")) + HOLD + sum(el(l) for l in snip.split("\n"))
           for snip in SNIPPETS]
T = sum(windows) + 0.2   # small tail so no keyTime lands exactly on 1

defs, body = [], []
cum = 0.0
for s, snip in enumerate(SNIPPETS):
    lines = snip.split("\n")
    tls = [tl(l) for l in lines]
    els = [el(l) for l in lines]
    tt = sum(tls)
    tstart = [sum(tls[:i]) for i in range(len(lines))]
    order = list(reversed(range(len(lines))))          # delete bottom line first
    pos = {idx: p for p, idx in enumerate(order)}
    eoff = [sum(els[order[k]] for k in range(pos[i])) for i in range(len(lines))]
    for i, line in enumerate(lines):
        a = max((cum + tstart[i]) / T, 0.0006)
        b = (cum + tstart[i] + tls[i]) / T
        es = (cum + tt + HOLD + eoff[i]) / T           # this line's delete start
        ee = (cum + tt + HOLD + eoff[i] + els[i]) / T  # delete end
        if not line.strip():
            continue
        w = len(line) * CPX + 8
        y = Y0 + i * DY
        cid = f"cl{s}_{i}"
        defs.append(
            f'<clipPath id="{cid}"><rect x="40" y="{y-10:.0f}" width="0" height="15">'
            f'<animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0;0" '
            f'keyTimes="0;{a:.5f};{b:.5f};{es:.5f};{ee:.5f};1" dur="{T:.1f}s" '
            f'repeatCount="indefinite" calcMode="linear"/></rect></clipPath>')
        body.append(f'<g clip-path="url(#{cid})"><text x="40" y="{y}" class="code">{tspans(line)}</text></g>')
    cum += windows[s]

code_defs = "\n  ".join(defs)
code_body = "\n    ".join(body)

# ---- role cycle (fixed 'Aspiring' + typed role) ----------------------------
RT = 12.0
role_defs, role_body = [], []
rx = 564
for i, r in enumerate(ROLES):
    w = len(r) * 10.8 + 20
    car = rx + int(len(r) * 10.8)
    seg = 1.0 / len(ROLES)
    s0 = i * seg
    base = f'{w:.0f}' if i == 0 else "0"
    if i == 0:
        kt = f"0;{s0+0.08*seg:.4f};{s0+0.28*seg:.4f};{s0+0.333*seg:.4f};1"
        vals = f"0;{w:.0f};{w:.0f};0;0"
    else:
        kt = f"0;{s0:.4f};{s0+0.11*seg:.4f};{s0+0.55*seg:.4f};{s0+seg:.4f};1"
        vals = f"0;0;{w:.0f};{w:.0f};0;0"
    role_defs.append(
        f'<clipPath id="r{i}"><rect x="{rx}" y="218" width="{base}" height="26">'
        f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="{RT}s" '
        f'repeatCount="indefinite" calcMode="linear"/></rect></clipPath>')
    role_body.append(
        f'<g clip-path="url(#r{i})"><text x="{rx}" y="236" class="role">{html.escape(r)}</text>'
        f'<rect class="cur" x="{car}" y="221" width="9" height="19" fill="#58D6B0"/></g>')
role_defs = "\n  ".join(role_defs)
role_body = "\n  ".join(role_body)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 330" width="1200" height="330" role="img" aria-label="Aditya Ganjoo — Aspiring AI / ML Engineer · Data Analyst · Data Scientist · Open to Full-time &amp; Internships · 2026">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1620"/><stop offset="1" stop-color="#0b1017"/></linearGradient>
  <linearGradient id="ul" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A970D8"/><stop offset="1" stop-color="#4F9EE8"/></linearGradient>
  <radialGradient id="focus" cx="50%" cy="56%" r="60%"><stop offset="0" stop-color="#0b1017" stop-opacity="0.95"/><stop offset="52%" stop-color="#0b1017" stop-opacity="0.82"/><stop offset="100%" stop-color="#0b1017" stop-opacity="0"/></radialGradient>
  <clipPath id="round"><rect x="1" y="1" width="1198" height="328" rx="16"/></clipPath>
  {role_defs}
  {code_defs}
  <style>
    .code{{font-family:'JetBrains Mono','Fira Code',Consolas,monospace;font-size:{FS}px}}
    .kw{{fill:#A970D8}}.fn{{fill:#4F9EE8}}.str{{fill:#46A84E}}.var{{fill:#9fb0c3}}.cm{{fill:#5b6672}}
    .name{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:52px;font-weight:800;fill:#e6edf3}}
    .role{{font-family:'JetBrains Mono','Fira Code',Consolas,monospace;font-size:18px;font-weight:600;fill:#58D6B0}}
    .sub{{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:14px;fill:#8b949e}}
    .cur{{animation:bl 1s steps(1) infinite}}@keyframes bl{{0%,50%{{opacity:1}}50.01%,100%{{opacity:0}}}}
  </style>
</defs>

<g clip-path="url(#round)">
  <rect x="1" y="1" width="1198" height="328" fill="url(#bg)"/>
  <g opacity="0.7">
    {code_body}
  </g>
  <rect x="1" y="37" width="1198" height="292" fill="url(#focus)"/>
  <rect x="1" y="1" width="1198" height="36" fill="#11161f"/>
  <line x1="1" y1="37" x2="1199" y2="37" stroke="#233041"/>
  <circle cx="26" cy="19" r="5.5" fill="#ff5f56"/><circle cx="46" cy="19" r="5.5" fill="#ffbd2e"/><circle cx="66" cy="19" r="5.5" fill="#27c93f"/>
  <text x="90" y="23" class="code" font-size="13" fill="#8b949e">aditya-ganjoo.py</text>
  <text x="1176" y="23" class="code" font-size="13" fill="#6e7681" text-anchor="end">main</text>
  <text x="600" y="168" class="name" text-anchor="middle">Aditya Ganjoo</text>
  <rect x="446" y="182" width="308" height="4" rx="2" fill="url(#ul)"/>
  <text x="476" y="236" class="role">Aspiring</text>
  {role_body}
  <text x="600" y="266" class="sub" text-anchor="middle">Open to Full-time &amp; Internships · 2026</text>
</g>
<rect x="1" y="1" width="1198" height="328" rx="16" fill="none" stroke="#233041"/>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {os.path.abspath(OUT)}  ({len(SNIPPETS)} snippets, cycle {T:.1f}s)")
