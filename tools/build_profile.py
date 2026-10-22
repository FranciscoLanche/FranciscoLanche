#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_profile.py — Genera los SVG animados del perfil tipo terminal.

Lee assets/ascii.txt (retrato ASCII), assets/stats.json (contribuciones reales
cacheadas por fetch_data.py) y tools/config.py, y produce:

    assets/neofetch-terminal.svg   → hero: neofetch + ficha + snake de commits
    assets/terminal-contact.svg    → ventana "cat contacto.txt"
    assets/terminal-divider.svg    → divisor animado con punto viajero

    python3 tools/build_profile.py            # imágenes finales animadas
    python3 tools/build_profile.py --static   # copias estáticas en /tmp (debug)

Las animaciones van horneadas con CSS + SMIL (GitHub no ejecuta JS dentro de
<img>). El tipado usa clipPaths con SMIL; la serpiente loopea infinito porque
cada animación del panel usa  dur=snake_period + repeatCount="indefinite"  y
cada cuadro comido codifica su instante E dentro de keyTimes (sin depender de
eventos de otras animaciones: robusto en Chromium/Firefox/Safari).
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from config import (USER, HOST, NEOFETCH_INFO, CONTACT_ROWS,
                    COMMAND_HERO, LEVEL_COLORS, MONTHS_ES,
                    BG, BG_BAR, BORDER, FG, FAINT, GREEN, BLUE, RED, YELLOW,
                    PURPLE, CYAN, WHITE, T)

FONT_STACK = ("'JetBrains Mono','Cascadia Code','Fira Code',ui-monospace,"
              "SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace")

FS = 13.0        # font-size
CW = 7.8         # ancho de glifo (≈0.6em)
LH = 15.6        # alto de línea (celda terminal 2:1)
MARGIN = 28

# tonos del retrato ASCII (de denso a casi vacío) y sus clases
TONE = [("@%#*", "#d6dcff"),
        ("+=",   "#8b96cc"),
        ("-~",   "#565f89"),
        (":.",   "#3a4165")]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_stats():
    path = os.path.join(REPO, "assets", "stats.json")
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            pass
    return {"grid": [[0] * 52 for _ in range(7)], "months": [],
            "total": 0, "streak": 0, "repos": 0, "stars": 0, "followers": 0}


# -------------------------------------------------------------------------- #
#  CHROME / CSS                                                               #
# -------------------------------------------------------------------------- #

def css_block():
    return ("<style>"
            "text{font-family:" + FONT_STACK + ";font-size:13px}"
            ".g{animation:tin .22s ease-out both}"
            "@keyframes tin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
            ".blk{animation:bl 1.1s ease-in-out infinite;opacity:1}"
            "@keyframes bl{0%,45%{opacity:1}55%,100%{opacity:0}}"
            ".dt{animation:dv 5s ease-in-out infinite;opacity:0}"
            "@keyframes dv{0%{transform:translateX(-300px);opacity:0}12%{opacity:1}"
            "50%{transform:translateX(300px);opacity:1}64%{opacity:0}100%{opacity:0}}"
            ".pu{fill:" + GREEN + ";font-weight:bold}.pp{fill:" + BLUE + ";font-weight:bold}"
            ".pd{fill:" + FG + "}.cmd{fill:" + WHITE + ";font-weight:bold}"
            ".lbl{fill:" + BLUE + ";font-weight:bold}.val{fill:" + FG + "}"
            ".head{fill:" + PURPLE + ";font-weight:bold}.sep{fill:" + BORDER + "}"
            ".a0{fill:#d6dcff}.a1{fill:#8b96cc}.a2{fill:#565f89}.a3{fill:#3a4165}"
            ".key{fill:" + PURPLE + ";font-weight:bold}.url{fill:" + FG + "}"
            ".tip{fill:" + FAINT + ";font-size:11px}"
            "</style>")


def window_open(title, w, h):
    return (
        f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
        f'<path d="M0 36 h {w:.0f}" stroke="{BORDER}" stroke-width="1"/>'
        f'<rect x="0" y="0" width="{w:.0f}" height="36" rx="12" fill="{BG_BAR}"/>'
        f'<rect x="0" y="30" width="{w:.0f}" height="6" fill="{BG_BAR}"/>'
        f'<circle cx="24" cy="18" r="6" fill="{RED}"/>'
        f'<circle cx="46" cy="18" r="6" fill="{YELLOW}"/>'
        f'<circle cx="68" cy="18" r="6" fill="{GREEN}"/>'
        f'<text x="{w/2:.0f}" y="22" text-anchor="middle" fill="{FAINT}" font-size="12">{esc(title)}</text>'
    )


def prompt_tspans():
    p1 = f"{USER}@{HOST}"
    return (f'<tspan class="pu">{esc(p1)}</tspan>'
            f'<tspan class="pp"> ~ </tspan>'
            f'<tspan class="pd">$ </tspan>'), len(p1) + 5


def cmd_clip(cid, x, baseline, n_chars, t_start, step=None):
    """SMIL typewriter: clip que avanza un glifo por paso."""
    stp = step if step is not None else T["type_step"]
    steps = ";".join(f"{i*CW:.1f}" for i in range(1, n_chars + 1))
    dur = n_chars * stp
    return (f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{baseline-13:.1f}" width="0" height="18">'
            f'<animate attributeName="width" calcMode="discrete" begin="{t_start:.2f}s" '
            f'dur="{dur:.2f}s" values="0;{steps}" fill="freeze"/></rect></clipPath>')


def art_rows(x, y0, rows=None):
    """Bloque ASCII a 3 tonos con revelado en cascada. Devuelve (svg, n_rows)."""
    if rows is None:
        with open(os.path.join(REPO, "assets", "ascii.txt"), encoding="utf-8") as f:
            rows = [r.rstrip("\n") for r in f]

    parts = []
    for i, row in enumerate(rows):
        delay = T["print_start"] + i * T["step_row"]
        segs = []
        cur = ""
        tone = None
        for ch in row:
            tc = None
            for j, (chars, _c) in enumerate(TONE):
                if ch in chars:
                    tc = f"a{j}"
                    break
            if tone is None or tc != tone:
                if cur:
                    segs.append((tone, cur))
                tone, cur = tc, ch
            else:
                cur += ch
        if cur:
            segs.append((tone, cur))
        tsp = "".join(
            (f'<tspan class="{t}">{esc(s)}</tspan>' if t else esc(s))
            for t, s in segs
        )
        parts.append(f'<text xml:space="preserve" x="{x}" y="{y0 + i*LH:.1f}" '
                     f'class="g" style="animation-delay:{delay:.2f}s">{tsp}</text>')
    return "".join(parts), len(rows)


def idle_prompt(x_end, y, delay):
    return (f'<g class="g" style="animation-delay:{delay:.2f}s">'
            f'<rect class="blk" x="{x_end:.1f}" y="{y-13:.1f}" width="{CW:.1f}" height="{FS+3:.1f}" '
            f'fill="{WHITE}" opacity="0.9"/></g>')


# -------------------------------------------------------------------------- #
#  FICHA INFO (tech + contact + github)                                       #
# -------------------------------------------------------------------------- #

def info_rows(data):
    """Filas de la ficha: ('t' lbl val) texto, ('h' txt) encabezado, ('s' line) separador."""
    sep = "─" * 26
    rows = []
    for k, v in NEOFETCH_INFO:
        rows.append(("t", f"{k}:".ljust(11), v))
    rows.append(("s", sep, None))
    rows.append(("h", "<contact>", None))
    for k, v, *_ in CONTACT_ROWS:
        rows.append(("t", k.ljust(11), v))
    rows.append(("s", sep, None))
    rows.append(("h", "<github>", None))
    rows.append(("t", "repos".ljust(11), f"{data.get('repos', 0)} públicos"))
    rows.append(("t", "stars".ljust(11), str(data.get("stars", 0))))
    rows.append(("t", "followers".ljust(11), str(data.get("followers", 0))))
    rows.append(("t", "contribs".ljust(11), f"{data.get('total', 0)} / 365d"))
    rows.append(("t", "racha".ljust(11), f"{data.get('streak', 0)} días máx"))
    return rows


def info_svg(rows, x, y0):
    out = []
    for i, (kind, label, value) in enumerate(rows):
        delay = T["print_start"] + i * T["step_info"]
        y = f"{y0 + i * LH:.1f}"
        base = f'xml:space="preserve" x="{x}" y="{y}" class="g" style="animation-delay:{delay:.2f}s"'
        if kind == "s":
            out.append(f'<text {base}><tspan class="sep">{esc(label)}</tspan></text>')
        elif kind == "h":
            out.append(f'<text {base}><tspan class="head">{esc(label)}</tspan></text>')
        else:
            out.append(f'<text {base}><tspan class="lbl">{esc(label)}</tspan>'
                       f'<tspan class="val">{esc(value)}</tspan></text>')
    return "".join(out), len(rows)


# -------------------------------------------------------------------------- #
#  PANEL DE CONTRIBUCIONES + SERPIENTE                                        #
# -------------------------------------------------------------------------- #

def snake_panel(data, x0, y0):
    """Rejilla de commits 52×7 + serpiente que la devora en loop.

    Devuelve (svg, legend_y_rel) donde legend_y_rel es el offset de la línea
    de leyenda respecto a y0.
    """
    grid = data.get("grid") or [[0] * 52 for _ in range(7)]
    months = data.get("months") or []
    n_rows, n_cols = len(grid), len(grid[0])
    step = 12                      # paso entre centros (celda 9 + gap 3)
    cell = 9
    P = T["snake_period"]
    B = T["snake_start"]
    reveal = T["type2_start"] + 0.55

    # --- orden de la cabeza: serpenteo por columnas (↓ luego ↑, etc.) --------
    order = []
    for col in range(n_cols):
        rows_o = range(n_rows) if col % 2 == 0 else reversed(range(n_rows))
        for row in rows_o:
            order.append((row, col))
    N = len(order)
    total_len = (N - 1) * step
    seg_len = 9 * step             # cuerpo de 9 celdas

    k_of = {(row, col): k for k, (row, col) in enumerate(order)}

    def d_str(points):
        d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
        for px, py in points[1:]:
            d += f" L {px:.1f} {py:.1f}"
        return d

    pts = [(x0 + c * step + cell / 2, y0 + r * step + cell / 2) for r, c in order]
    path_d = d_str(pts)
    start_x, start_y = pts[0]

    # --- rejilla -------------------------------------------------------------
    grid_parts = []
    for month, col in months[:n_cols]:
        name = MONTHS_ES[month % 12]
        grid_parts.append(f'<text x="{x0 + col*step}" y="{y0 - 5}" class="tip">{esc(name)}</text>')
    for row, tag in ((0, "lun"), (2, "mié"), (4, "vie")):
        grid_parts.append(f'<text x="{x0 - 8}" y="{y0 + row*step + 8}" '
                          f'text-anchor="end" class="tip">{tag}</text>')

    for row in range(n_rows):
        for col in range(n_cols):
            lv = grid[row][col]
            grid_parts.append(
                f'<rect x="{x0 + col*step}" y="{y0 + row*step}" '
                f'width="{cell}" height="{cell}" rx="2" fill="{LEVEL_COLORS[lv]}"/>')

    # --- máscaras de "comido": se encienden cuando la cabeza pasa -------------
    # (loopean solas: dur=P con keyTimes codifica el instante E de cada cuadro)
    for (row, col), k in sorted(k_of.items(), key=lambda t: t[1]):
        if grid[row][col] <= 0:
            continue
        a = k / max(1, N - 1)
        b = min(1.0, a + 0.12 / P)
        grid_parts.append(
            f'<rect x="{x0 + col*step}" y="{y0 + row*step}" width="{cell}" height="{cell}" '
            f'rx="2" fill="{BG}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1" '
            f'keyTimes="0;{a:.4f};{b:.4f};1" dur="{P:.0f}s" begin="{B:.2f}s" '
            f'repeatCount="indefinite"/></rect>')

    # --- cuerpo y cabeza ------------------------------------------------------
    body = (
        f'<path id="snkpath" d="{path_d}" fill="none" stroke="{GREEN}" stroke-width="7" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'stroke-dasharray="{seg_len:.0f} {total_len:.0f}" stroke-dashoffset="0" '
        f'class="g" style="animation-delay:{B - 0.1:.2f}s">'
        f'<animate attributeName="stroke-dashoffset" values="{seg_len:.0f};{seg_len - total_len:.0f}" '
        f'dur="{P:.0f}s" begin="{B:.2f}s" repeatCount="indefinite"/></path>'
    )
    head = (
        f'<g class="g" style="animation-delay:{B - 0.1:.2f}s">'
        f'<circle cx="{start_x:.1f}" cy="{start_y:.1f}" r="5.2" fill="{YELLOW}" '
        f'stroke="{BG}" stroke-width="1.5">'
        f'<animateMotion dur="{P:.0f}s" begin="{B:.2f}s" repeatCount="indefinite" '
        f'rotate="0"><mpath xlink:href="#snkpath"/></animateMotion>'
        f'</circle></g>'
    )

    # --- leyenda --------------------------------------------------------------
    tot = data.get("total", 0)
    stk = data.get("streak", 0)
    legend_rel = n_rows * step + 26
    legend = (f'<text x="{x0}" y="{y0 + legend_rel:.1f}" class="tip">'
              f':: {tot} contribuciones / 365d  ·  mejor racha {stk} días  '
              f'·  vuelta cada {P:.0f}s</text>')

    panel = (f'<g class="g" style="animation-delay:{reveal:.2f}s">'
             + "".join(grid_parts) + legend + "</g>") + body + head

    return panel, legend_rel, n_cols * step


# -------------------------------------------------------------------------- #
#  HERO                                                                       #
# -------------------------------------------------------------------------- #

def build_neofetch():
    data = load_stats()

    with open(os.path.join(REPO, "assets", "ascii.txt"), encoding="utf-8") as f:
        art = [r.rstrip("\n") for r in f]
    cols = max(len(r) for r in art)
    art_roww = cols * CW
    y0 = 64
    info_x = MARGIN + art_roww + 26

    prompt, plen = prompt_tspans()
    cmd_x = MARGIN + plen * CW

    art_svg, n_art = art_rows(MARGIN, y0 + 2 * LH, art)
    art_bottom = y0 + 2 * LH + (n_art - 1) * LH

    rows = info_rows(data)
    info, _n_info = info_svg(rows, info_x, y0 + 2 * LH)

    # --- geometría del panel snake (bajo el neofetch) ------------------------
    s_y = art_bottom + 3 * LH          # segunda línea de prompt
    grid_y = s_y + 2 * LH              # etiquetas de meses van en y0-5
    grid_x = MARGIN + 34               # hueco para etiquetas lun/mié/vie
    panel, legend_rel, grid_w = snake_panel(data, grid_x, grid_y)
    legend_y = grid_y + legend_rel
    idle_y = legend_y + 2 * LH
    cursor_at = T["snake_start"] + T["snake_period"] + 0.2

    info_w = max(len(l) + len(v or "") for _k, l, v in rows) * CW
    w = max(info_x + info_w + MARGIN,
            grid_x + grid_w + MARGIN + 20,
            760)
    h = idle_y + 30

    cmd = COMMAND_HERO
    cmd2 = "python3 snake.py"

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" '
           f'role="img" aria-label="Terminal neofetch + snake de {esc(USER)}">',
           "<title>", esc(f"Terminal {USER} — neofetch + snake de commits"), "</title>",
           css_block(), window_open(f"{USER}@{HOST}: ~/github", w, h)]

    # prompt 1 + typing del comando
    svg.append(f'<g class="g" style="animation-delay:{T["prompt_in"]:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{y0}">{prompt}</text></g>')
    svg.append(cmd_clip("c1", cmd_x, y0, len(cmd), T["type_start"]))
    svg.append(f'<g clip-path="url(#c1)"><text xml:space="preserve" x="{cmd_x:.1f}" '
               f'y="{y0}" class="cmd">{esc(cmd)}</text></g>')

    svg.append(art_svg)
    svg.append(info)

    # prompt 2 + typing del comando del panel
    svg.append(f'<g class="g" style="animation-delay:{T["type2_start"] - 0.1:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{s_y:.1f}">{prompt}</text></g>')
    svg.append(cmd_clip("c2", cmd_x, s_y, len(cmd2), T["type2_start"]))
    svg.append(f'<g clip-path="url(#c2)"><text xml:space="preserve" x="{cmd_x:.1f}" '
               f'y="{s_y:.1f}" class="cmd">{esc(cmd2)}</text></g>')

    svg.append(panel)

    # prompt final + cursor
    svg.append(f'<g class="g" style="animation-delay:{cursor_at:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{idle_y:.1f}">{prompt}</text></g>')
    svg.append(idle_prompt(cmd_x, idle_y, cursor_at + 0.1))
    svg.append("</svg>")
    return "".join(svg)


# -------------------------------------------------------------------------- #
#  CONTACTO                                                                   #
# -------------------------------------------------------------------------- #

def build_contact():
    title = f"{USER}@{HOST}: ~/contacto — zsh"
    y0 = 64
    prompt, plen = prompt_tspans()
    cmd = "cat contacto.txt"
    cmd_x = MARGIN + plen * CW
    label_w = max(len(k) for k, *_ in CONTACT_ROWS)
    longest = max(label_w + 3 + len(v) for _k, v, *_ in CONTACT_ROWS)

    rows = []
    for i, (k, v, _url, _logo) in enumerate(CONTACT_ROWS):
        delay = T["print_start"] + i * T["step_info"]
        lab = k.ljust(label_w + 3)
        rows.append(
            f'<text xml:space="preserve" x="{MARGIN}" y="{y0 + 3*LH + i*LH:.1f}" class="g" '
            f'style="animation-delay:{delay:.2f}s"><tspan class="key">{esc(lab)}</tspan>'
            f'<tspan class="url">{esc(v)}</tspan></text>')

    idle_y = y0 + 3 * LH + (len(CONTACT_ROWS) + 1) * LH
    h = idle_y + 32
    w = int(max(MARGIN + (plen + len(cmd)) * CW + 40,
                MARGIN + longest * CW + MARGIN + 20, 560))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.0f}" '
           f'viewBox="0 0 {w} {h:.0f}" role="img" aria-label="Contacto de {esc(USER)}">',
           "<title>", esc(title), "</title>",
           css_block(), window_open(title, w, h)]
    svg.append(f'<g class="g" style="animation-delay:{T["prompt_in"]:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{y0}">{prompt}</text></g>')
    svg.append(cmd_clip("cc", cmd_x, y0, len(cmd), T["type_start"]))
    svg.append(f'<g clip-path="url(#cc)"><text xml:space="preserve" x="{cmd_x:.1f}" '
               f'y="{y0}" class="cmd">{esc(cmd)}</text></g>')
    svg.extend(rows)
    svg.append(f'<g class="g" style="animation-delay:{T["type2_start"] + 0.3:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{idle_y:.1f}">{prompt}</text></g>')
    svg.append(idle_prompt(cmd_x, idle_y, T["type2_start"] + 0.4))
    svg.append("</svg>")
    return "".join(svg)


# -------------------------------------------------------------------------- #
#  DIVISOR                                                                    #
# -------------------------------------------------------------------------- #

def build_divider():
    w, h = 860, 26
    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="Divisor">',
        css_block(),
        f'<line x1="0" y1="{h/2}" x2="{w/2-40}" y2="{h/2}" stroke="{BORDER}" stroke-width="2"/>',
        f'<line x1="{w/2+40}" y1="{h/2}" x2="{w}" y2="{h/2}" stroke="{BORDER}" stroke-width="2"/>',
        f'<text x="{w/2}" y="{h/2+4}" text-anchor="middle" fill="{CYAN}" font-size="12">◆</text>',
        f'<circle class="dt" cx="{w/2}" cy="{h/2}" r="4.5" fill="{GREEN}"/>',
        "</svg>"])


# -------------------------------------------------------------------------- #
#  STATIC + MAIN                                                              #
# -------------------------------------------------------------------------- #

def staticify(svg):
    svg = re.sub(r'style="animation-delay:[0-9.]+s"', "", svg)
    svg = re.sub(r'<animate[^>]*/>', "", svg)
    svg = re.sub(r'<animateMotion[^>]*>[\s\S]*?</animateMotion>', "", svg)
    svg = re.sub(r'<animate[^>]*>[\s\S]*?</animate>', "", svg)
    svg = re.sub(r'<clipPath[^>]*><rect x="([0-9.-]+)" y="([0-9.-]+)" width="0"',
                 r'<clipPath id="x"><rect x="\1" y="\2" width="1600"', svg)
    svg = re.sub(r'<rect id="([a-z0-9]+)" x="(0)" y="0" width="1" height="1" opacity="0"/>', "", svg)
    svg = re.sub(r'class="blk"', "", svg)
    svg = re.sub(r'class="dt"', "", svg)
    svg = re.sub(r'class="g"', "", svg)
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--static", action="store_true")
    a = ap.parse_args()
    out = os.path.join(REPO, "assets")

    built = build_neofetch(), build_contact(), build_divider()
    names = ["neofetch-terminal.svg", "terminal-contact.svg", "terminal-divider.svg"]

    for name, data in zip(names, built):
        if a.static:
            data = staticify(data)
            path = f"/tmp/opencode/{name.replace('.svg', '-static.svg')}"
        else:
            path = os.path.join(out, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"OK {path}  ({len(data)} bytes)")


if __name__ == "__main__":
    main()
