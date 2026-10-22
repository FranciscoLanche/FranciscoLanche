#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
portrait_to_ascii.py — Convierte assets/retrato.jpg en arte ASCII estilo neofetch.

Uso:
    python3 tools/portrait_to_ascii.py [--cols N] [--contrast F] [--gamma F] [--crop F]

Salida: assets/ascii.txt (filas de texto plano).
El ramp hace que el fondo claro de la foto se vuelva espacio vacío
y el pelo oscuro se vuelva denso (@#%), igual que en los ASCII del neofetch.
"""

import argparse
import os
import sys
from PIL import Image, ImageOps, ImageEnhance

# Densidad: oscuro (@, denso) -> claro (espacio, vacío)
RAMP = "@%#*+=-~:. "

# Ratio glifo terminal: alto ≈ 2.0 × ancho (usamos 0.50 para cuadrar filas)
CELL_RATIO = 0.50


WEAK = " ~=:-."          # tonos "fuera de silueta" para la erosión de marco


def image_to_ascii(path, cols=56, contrast=1.35, gamma=1.0, crop=0.055, wipe=0,
                   erode=True):
    """Convierte la imagen a ASCII. Devuelve lista de filas.
    wipe: brillo >= wipe pasa a fondo vacío. 0 = sin wipe (fondo relleno tenue).
    erode: borra los tonos débiles que tocan el marco (fondo), conservando las
           figuras interiores (la cara queda rodeada de pelo denso)."""
    img = Image.open(path).convert("L")

    if crop > 0:
        w, h = img.size
        dx, dy = int(w * crop), int(h * crop)
        img = img.crop((dx, dy, w - dx, h - dy))

    w_img, h_img = img.size
    rows = max(8, round(cols * (h_img / w_img) * CELL_RATIO))

    img = img.resize((cols, rows), Image.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)

    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)

    if wipe:
        img = img.point(lambda v: 255 if v >= wipe else v)

    px = img.load()
    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            b = (px[x, y] / 255.0) ** gamma
            idx = int(b * (len(RAMP) - 1))
            line.append(RAMP[idx])
        if erode:
            L = "".join(line)
            i = 0
            while i < len(L) and (L[i] == " " or L[i] in WEAK):
                i += 1
            j = len(L)
            while j > 0 and (L[j-1] == " " or L[j-1] in WEAK):
                j -= 1
            line = list(" " * i + L[i:j] + " " * (len(L) - j)) if j >= i else [" "] * len(L)
        out.append("".join(line))
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(here)
    photo = os.path.join(repo, "assets", "retrato.jpg")
    out_file = os.path.join(repo, "assets", "ascii.txt")

    if not os.path.exists(photo):
        print(f"x No existe {photo}")
        sys.exit(1)

    ap = argparse.ArgumentParser()
    ap.add_argument("--cols", type=int, default=60)
    ap.add_argument("--contrast", type=float, default=1.45)
    ap.add_argument("--gamma", type=float, default=1.12)
    ap.add_argument("--crop", type=float, default=0.07, help="recorta fracción de cada borde (ej. 0.06)")
    ap.add_argument("--wipe", type=int, default=0, help="brillo >= wipe pasa a fondo vacío")
    ap.add_argument("--no-erode", action="store_true")
    a = ap.parse_args()

    rows = image_to_ascii(photo, a.cols, a.contrast, a.gamma, a.crop, a.wipe, not a.no_erode)

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))

    print(f"OK ASCII generado: {out_file}  ({a.cols} cols x {len(rows)} filas)")


if __name__ == "__main__":
    main()
