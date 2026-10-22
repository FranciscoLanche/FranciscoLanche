#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_data.py — Descarga datos reales de GitHub y cachea en assets/stats.json.

Fuentes (públicas, sin token):
  - api.github.com/users/<user>                → repos y followers
  - api.github.com/search (stars)              → estrellas totales
  - github-contributions-api.jogruber.de/v4    → calendario de contribuciones
                                                 (369 días, niveles 0..4)

Si la red falla conserva el cache previo; si no existe cache usa datos demo.
Salida: assets/stats.json
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import date, timedelta

USER = "FranciscoLanche"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "assets", "stats.json")
UA = {"User-Agent": "Mozilla/5.0 (profile-builder)"}


def get(url, timeout=12):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_profile():
    d = get(f"https://api.github.com/users/{USER}")
    return {"repos": d.get("public_repos", 0), "followers": d.get("followers", 0)}


def fetch_stars():
    d = get(f"https://api.github.com/search/repositories?q=user:{USER}&per_page=100")
    total = sum((it.get("stargazers_count") or 0) for it in d.get("items", []))
    return total


def fetch_calendar():
    d = get(f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last")
    days = sorted(d["contributions"], key=lambda x: x["date"])

    # cuadrícula estilo GitHub: columnas = semanas, filas = lun..dom
    start = date.fromisoformat(days[0]["date"])
    # alinea la primera columna a lunes
    start = start - timedelta(days=start.weekday())

    end = date.fromisoformat(days[-1]["date"])
    n_weeks = ((end - start).days) // 7 + 1
    grid = [[0] * n_weeks for _ in range(7)]   # niveles
    counts = [[0] * n_weeks for _ in range(7)]

    by_date = {x["date"]: x for x in days}
    d0 = start
    while d0 <= end:
        col, row = (d0 - start).days // 7, d0.weekday()
        raw = by_date.get(d0.isoformat())
        if raw:
            grid[row][col] = int(raw.get("level", 0))
            counts[row][col] = int(raw.get("count", 0))
        d0 += timedelta(days=1)

    # meses por columna (para etiquetas del panel): [(mes 0-11, columna)]
    months = []
    prev = -1
    for col in range(n_weeks):
        dcol = start + timedelta(days=col * 7)
        if dcol.month != prev:
            months.append([dcol.month - 1, col])
            prev = dcol.month

    return grid, counts, months


def max_streak(counts):
    dias = []
    for week in range(len(counts[0])):
        for row in range(7):
            dias.append((row, week, counts[row][week]))
    dias.sort(key=lambda t: (t[1], t[0]))
    best = cur = 0
    for _, _, c in dias:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    return best


def main():
    cache = {}
    if os.path.exists(OUT):
        try:
            cache = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            cache = {}

    out = {
        "updated": date.today().isoformat(),
        "user": USER,
        "repos": cache.get("repos", 0),
        "followers": cache.get("followers", 0),
        "stars": cache.get("stars", 0),
        "total": cache.get("total", 0),
        "streak": cache.get("streak", 0),
        "grid": cache.get("grid"),
    }

    ok = True
    try:
        out.update(fetch_profile())
    except Exception as e:
        print(f"! perfil falló: {e}")
        ok = False
    try:
        out["stars"] = fetch_stars()
    except Exception as e:
        print(f"! estrellas falló: {e}")
        ok = False
    try:
        grid, counts, months = fetch_calendar()
        out["grid"] = grid
        out["months"] = months
        out["total"] = sum(map(sum, counts))
        out["streak"] = max_streak(counts)
    except Exception as e:
        print(f"! calendario falló: {e}")
        ok = False
    if out.get("grid") is None:
        # demo: rejilla vacía para que el builder compile igual
        out["grid"] = [[0] * 52 for _ in range(7)]
        out["months"] = []
        out["total"] = 0
        out["streak"] = 0

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK {OUT}  (repos={out['repos']} stars={out['stars']} "
          f"followers={out['followers']} contribs={out['total']} "
          f"racha={out['streak']} red_ok={ok})")


if __name__ == "__main__":
    main()
