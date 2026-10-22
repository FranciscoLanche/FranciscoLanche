#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tune_ascii.py — genera 3 variantes de retrato ASCII y las renderiza juntas
para elegir la mejor a ojo. Solo para desarrollo."""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)

from portrait_to_ascii import image_to_ascii
import build_profile as bp

PHOTO = os.path.join(REPO, "assets", "retrato.jpg")

VARIANTS = {
    "e1": dict(cols=56, contrast=1.45, gamma=1.12, crop=0.055, wipe=0, erode=True),
    "e2": dict(cols=60, contrast=1.45, gamma=1.12, crop=0.07, wipe=0, erode=True),
    "e3": dict(cols=56, contrast=1.55, gamma=1.15, crop=0.07, wipe=0, erode=True),
}

def staticify(svg):
    svg = re.sub(r'style="animation-delay:[0-9.]+s"', "", svg)
    svg = re.sub(r'<animate[^>]*/>', "", svg)
    svg = re.sub(r'<clipPath[^>]*><rect x="([0-9.-]+)" y="([0-9.-]+)" width="0"',
                 r'<clipPath id="x"><rect x="\1" y="\2" width="1200"', svg)
    svg = re.sub(r'class="blk"', "", svg)
    svg = re.sub(r'class="dt"', "", svg)
    svg = re.sub(r'class="g"', "", svg)
    # QA local: evita glifos fancy del Nerd Font instalado en esta máquina
    svg = svg.replace("'JetBrains Mono','Cascadia Code','Fira Code',", "'DejaVu Sans Mono',")
    return svg

rows_all = {}
for name, p in VARIANTS.items():
    rows = image_to_ascii(PHOTO, **p)
    rows_all[name] = rows
    svg = staticify(bp.build_neofetch(ascii_rows=rows))
    path = f"/tmp/opencode/variant-{name}.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK {path}")

html = '<!doctype html><meta charset="utf-8"><style>body{background:#0d0e14;margin:0;padding:20px;display:flex;gap:18px}svg{display:block}</style>'
for n in VARIANTS:
    html += f'<img src="variant-{n}.svg" width="700">'
open("/tmp/opencode/check2.html", "w").write(html)
print("OK /tmp/opencode/check2.html")
