#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_profile.py — Genera los SVG animados del perfil tipo terminal.

Leemos assets/ascii.txt (retrato ASCII) + tools/config.py y producimos:
    assets/neofetch-terminal.svg   → hero: terminal neofetch con tu retrato
    assets/terminal-contact.svg    → ventana "cat contacto.txt"
    assets/terminal-divider.svg    → divisor animado con punto viajero

    python3 tools/build_profile.py            # imágenes finales animadas
    python3 tools/build_profile.py --static   # copias estáticas en /tmp (debug)

Las animaciones van horneadas con CSS + SMIL (sin JS, GitHub no ejecuta
JavaScript dentro de <img>) siguiendo los tiempos estilo anime.js de config.T.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from config import (USER, HOST, GITHUB, NEOFETCH_INFO, CONTACT_ROWS,
                    BG, BG_BAR, BORDER, FG, FAINT, GREEN, BLUE, RED, YELLOW,
                    PURPLE, CYAN, WHITE, T)

FONT_STACK = ("'JetBrains Mono','Cascadia Code','Fira Code',ui-monospace,"
              "SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace")

FS = 13.0        # font-size
CW = 7.8          # ancho glifo (≈ 0.6em)
LH = 15.6         # alto línea (relación celda terminal 2:1 con CW)
MARGIN = 28

# tones del ASCII (de denso a casi vacío)
TONE = [("@%#*",  "#d6dcff"),   # masa principal (pelo denso)
        ("+=",   "#8b96cc"),    # volumen medio
        ("-~",   "#565f89"),    # silueta tenue
        (":.",   "#3a4165")]    # casi apagado


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def css_block():
    return (
        "<style>"
        "text{font-family:" + FONT_STACK + ";font-size:13px}"
        ".g{animation:tin .22s ease-out both}"
        "@keyframes tin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
        ".blk{animation:bl 1.1s ease-in-out infinite;opacity:1}"
        "@keyframes bl{0%,45%{opacity:1}55%,100%{opacity:0}}"
        ".dt{animation:dv 5s ease-in-out infinite;opacity:0}"
        "@keyframes dv{0%{transform:translateX(-300px);opacity:0}12%{opacity:1}"
        "50%{transform:translateX(300px);opacity:1}64%{opacity:0}100%{opacity:0}}"
        ".pu{fill:%GREEN%;font-weight:bold}.pp{fill:%BLUE%;font-weight:bold}"
        ".pd{fill:%FG%}.cmd{fill:%WHITE%;font-weight:bold}"
        ".lbl{fill:%BLUE%;font-weight:bold}.val{fill:%FG%}"
        ".a0{fill:#d6dcff}.a1{fill:#8b96cc}.a2{fill:#565f89}.a3{fill:#3a4165}"
        ".key{fill:%PURPLE%}.url{fill:%FG%}"
        "</style>"
    ).replace("%GREEN%", GREEN).replace("%BLUE%", BLUE).replace("%FG%", FG) \
     .replace("%WHITE%", WHITE).replace("%PURPLE%", PURPLE)


def window_open(title, w, h):
    bar = (
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
        f'<path d="M0 36 h {w}" stroke="{BORDER}" stroke-width="1"/>'
        f'<rect x="0" y="0" width="{w}" height="36" rx="12" fill="{BG_BAR}"/>'
        f'<rect x="0" y="30" width="{w}" height="6" fill="{BG_BAR}"/>'
        f'<circle cx="24" cy="18" r="6" fill="{RED}"/>'
        f'<circle cx="46" cy="18" r="6" fill="{YELLOW}"/>'
        f'<circle cx="68" cy="18" r="6" fill="{GREEN}"/>'
        f'<text x="{w/2:.0f}" y="22" text-anchor="middle" fill="{FAINT}" font-size="12">{esc(title)}</text>'
    )
    return bar


def prompt_tspans():
    p1 = f"{USER}@{HOST}"
    return (f'<tspan class="pu">{esc(p1)}</tspan>'
            f'<tspan class="pp"> ~ </tspan>'
            f'<tspan class="pd">$ </tspan>'), len(p1) + 5   # " ~ $" → espacios + $ + espacio


def cmd_clip(cid, x, baseline, n_chars, t_start):
    """SMIL typewriter: clip que avanza un glifo por paso."""
    steps = ";".join(f"{i*CW:.1f}" for i in range(1, n_chars + 1))
    dur = n_chars * T["type_step"]
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{baseline-13:.1f}" width="0" height="18">'
            f'<animate attributeName="width" calcMode="discrete" begin="{t_start:.2f}s" '
            f'dur="{dur:.2f}s" values="0;{steps}" fill="freeze"/></rect></clipPath>')


def art_rows(x, y0, rows=None):
    """Construye el bloque ASCII a 3 tonos. Devuelve (svg, alto)."""
    if rows is None:
        with open(os.path.join(REPO, "assets", "ascii.txt"), encoding="utf-8") as f:
            rows = [r.rstrip("\n") for r in f]
    for r in rows:
        r = "".join(c if c in "@%#*+=-~:." else " " for c in r)

    parts = []
    n = len(rows)
    for i, row in enumerate(rows):
        delay = f'{T["print_start"] + i * T["step_row"]:.2f}'
        # tokeniza por tramos de tono (los espacios se mantienen text íntegro)
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
                     f'class="g" style="animation-delay:{delay}s">{tsp}</text>')
    return "".join(parts), n


def idle_prompt(x_end, y, delay):
    return (f'<g class="g" style="animation-delay:{delay:.2f}s">'
            f'<rect class="blk" x="{x_end:.1f}" y="{y-13:.1f}" width="{CW}" height="{FS+3:.1f}" '
            f'fill="{WHITE}" opacity="0.9"/></g>')


def build_neofetch(ascii_rows=None):
    if ascii_rows is not None:
        art = ["".join(c if c in "@%#*+=-~:." else " " for c in r) for r in ascii_rows]
    else:
        with open(os.path.join(REPO, "assets", "ascii.txt"), encoding="utf-8") as f:
            art = [r.rstrip("\n") for r in f]
    cols = max(len(r) for r in art)

    title = f"{USER}@{HOST}: ~/github — neofetch"
    art_w = cols * CW
    info_x = MARGIN + art_w + 26
    y0 = 64                              # baseline del prompt
    rows_svg, n_rows = art_rows(MARGIN, y0 + 2 * LH, art)
    art_bottom = y0 + 2 * LH + (n_rows - 1) * LH

    prompt, plen = prompt_tspans()
    cmd = "neofetch"
    cmd_x = MARGIN + plen * CW

    # info
    info = []
    for i, (k, v) in enumerate(NEOFETCH_INFO):
        delay = T["print_start"] + 0.05 + i * T["step_info"]
        if k:
            lab = f"{k}:".ljust(11)
        else:
            lab = " " * 11
        info.append(
            f'<text xml:space="preserve" x="{info_x}" y="{y0 + 2*LH + i*LH:.1f}" class="g" '
            f'style="animation-delay:{delay:.2f}s"><tspan class="lbl">{esc(lab)}</tspan>'
            f'<tspan class="val">{esc(v)}</tspan></text>')

    idle_y = art_bottom + 3 * LH
    h = idle_y + 30
    w = MARGIN + art_w + 26 + max(12 + len(v) for _k, v in NEOFETCH_INFO) * CW + MARGIN

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
           f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Terminal neofetch de {USER}">',
           "<title>", esc(f"Terminal {USER} — neofetch"), "</title>",
           css_block(), window_open(title, w, h)]
    # prompt inicial
    svg.append(f'<g class="g" style="animation-delay:{T["prompt_in"]:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{y0}">{prompt}</text></g>')
    # comando tecleado (SMIL)
    svg.append(cmd_clip("c1", cmd_x, y0, len(cmd), T["type_start"]))
    svg.append(f'<g clip-path="url(#c1)"><text xml:space="preserve" x="{cmd_x}" y="{y0}" class="cmd">'
               f'{esc(cmd)}</text></g>')
    svg.append(rows_svg)
    svg.extend(info)
    # prompt final + cursor
    idle_x = MARGIN + plen * CW
    svg.append(f'<g class="g" style="animation-delay:{T["cursor_at"]:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{idle_y}">{prompt}</text></g>')
    svg.append(idle_prompt(idle_x, idle_y, T["cursor_at"] + 0.1))
    svg.append("</svg>")
    return "".join(svg)


def build_contact():
    title = f"{USER}@{HOST}: ~/contacto — zsh"
    y0 = 64
    prompt, plen = prompt_tspans()
    cmd = "cat contacto.txt"
    cmd_x = MARGIN + plen * CW
    label_w = max(len(k) for k, *_ in CONTACT_ROWS)
    longest = max(len(label_w * " ") + 3 + len(v) for _k, v, *_ in CONTACT_ROWS)

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
    w = max(MARGIN + (plen + len(cmd)) * CW + 40,   # ancho del comando
            MARGIN + longest * CW + MARGIN + 20)
    w = int(max(w, 560))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.0f}" '
           f'viewBox="0 0 {w} {h:.0f}" role="img" aria-label="Contacto de {USER}">',
           "<title>", esc("contacto.txt"), "</title>",
           css_block(), window_open(title, w, h)]
    svg.append(f'<g class="g" style="animation-delay:{T["prompt_in"]:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{y0}">{prompt}</text></g>')
    svg.append(cmd_clip("cc", cmd_x, y0, len(cmd), T["type_start"]))
    svg.append(f'<g clip-path="url(#cc)"><text xml:space="preserve" x="{cmd_x}" y="{y0}" class="cmd">'
               f'{esc(cmd)}</text></g>')
    svg.extend(rows)
    svg.append(f'<g class="g" style="animation-delay:{T["cursor_at"]:.2f}s">'
               f'<text xml:space="preserve" x="{MARGIN}" y="{idle_y}">{prompt}</text></g>')
    svg.append(idle_prompt(cmd_x, idle_y, T["cursor_at"] + 0.1))
    svg.append("</svg>")
    return "".join(svg)


def build_divider():
    w, h = 860, 26
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Divisor">',
           css_block(),
           f'<line x1="0" y1="{h/2}" x2="{w/2-40}" y2="{h/2}" stroke="{BORDER}" stroke-width="2"/>',
           f'<line x1="{w/2+40}" y1="{h/2}" x2="{w}" y2="{h/2}" stroke="{BORDER}" stroke-width="2"/>',
           f'<text x="{w/2}" y="{h/2+4}" text-anchor="middle" fill="{CYAN}" font-size="12">◆</text>',
           f'<circle class="dt" cx="{w/2}" cy="{h/2}" r="4.5" fill="{GREEN}"/>',
           "</svg>"]
    return "".join(svg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--static", action="store_true")
    a = ap.parse_args()
    out = os.path.join(REPO, "assets")

    build = build_neofetch(), build_contact(), build_divider()
    names = ["neofetch-terminal.svg", "terminal-contact.svg", "terminal-divider.svg"]

    for name, data in zip(names, build):
        if a.static:
            # copia estática: sin delays ni SMIL (para inspección visual)
            import re
            data = re.sub(r'style="animation-delay:[0-9.]+s"', "", data)
            data = re.sub(r'<animate[^>]*/>', "", data)
            data = re.sub(r'<clipPath[^>]*><rect x="([0-9.-]+)" y="([0-9.-]+)" width="0"',
                          r'<clipPath id="x"><rect x="\1" y="\2" width="1200"', data)
            data = re.sub(r'class="blk"', "", data)
            data = re.sub(r'class="dt"', "", data)
            data = re.sub(r'class="g"', "", data)
            path = f"/tmp/opencode/{name.replace('.svg', '-static.svg')}"
        else:
            path = os.path.join(out, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"OK {path}  ({len(data)} bytes)")


if __name__ == "__main__":
    main()
