# tools/ — Pipeline del perfil estilo terminal

Todo el perfil se regenera con dos/tres comandos. Editar primero lo que quieras
en `config.py` (textos, paleta Tokyo Night, tiempos de animación) y, si cambias
la foto, regenera el ASCII.

## Archivos

| Archivo | Qué hace |
| --- | --- |
| `config.py` | Identidad, ficha neofetch, contactos, paleta, colores de niveles del calendario y tiempos `T` (estilo anime.js). Fuente única de verdad. |
| `fetch_data.py` | Baja datos reales de GitHub (repos, stars, followers, calendario de contribuciones con niveles, meses, racha máx) y cachea en `assets/stats.json`. Sin token; si la red falla conserva el cache anterior. |
| `portrait_to_ascii.py` | `assets/retrato.jpg` → `assets/ascii.txt` (ramp de densidad, wipe de fondo, erosión de marco). |
| `build_profile.py` | Lee `ascii.txt` + `stats.json` + `config.py` y genera los 3 SVG animados en `assets/`. |
| `tune_ascii.py` | Dev only: renderiza variantes A/B/C del retrato en `/tmp/opencode` para comparar. |
| `preview.html` | Playground con **anime.js real** (GitHub no ejecuta JS en README; aquí sí). |

## Uso

```bash
# 1) datos reales: stats + calendario de contribuciones → assets/stats.json
python3 tools/fetch_data.py

# 2) ASCII desde tu foto (largos avanzados: --cols, --contrast, --gamma, --crop, --wipe, --no-erode)
python3 tools/portrait_to_ascii.py

# 3) SVGs finales animados (neofetch-terminal, terminal-contact, terminal-divider)
python3 tools/build_profile.py

# Opcional: copias estáticas para inspección en /tmp/opencode
python3 tools/build_profile.py --static

# Opcional: comparar variantes del retrato
python3 tools/tune_ascii.py

# Opcional: preview anime.js (requiere servir el repo por http)
python3 -m http.server 8080          # en la raíz del repo
# → http://localhost:8080/tools/preview.html
```

> En producción esto corre solo: `.github/workflows/refresh.yml` ejecuta
> `fetch_data.py` + `build_profile.py` cada noche y commitea si cambió algo.

## Cómo funciona la animación en GitHub

- GitHub sirve los SVG del README como `<img>`: **no ejecuta scripts** y
  los SVG no pueden cargar recursos externos (por eso el snake se
  dibuja dentro del propio SVG y no se embebe el SVG generado por una action).
- La coreografía va horneada: CSS keyframes (stagger de líneas, blink del
  cursor, reveals) + SMIL `calcMode="discrete"` (typewriter glifo a glifo,
  clip que avanza por celda monoespaciada).
- **Panel `python3 snake.py`** (dentro del hero):
  - La cabeza (`animateMotion` + `mpath`) recorre una polilínea serpenteante
    por columnas sobre los centros de la rejilla 52×7.
  - El cuerpo se dibuja con el truco de `stroke-dasharray/dashoffset`:
    un guión de longitud fija (9 celdas) que se desliza de inicio a fin.
  - Cada cuadro con commits lleva una máscara que se enciende justo cuando
    la cabeza pasa por él: `values="0;0;1;1"` con el instante `E` codificado
    en `keyTimes` — el retardo sale de `E = k/(N-1) * periodo`.
  - Todo loopea con `repeatCount="indefinite"` y `dur=snake_period`, así que
    la serpiente se regenera y vuelve a comer cada vuelta, sin JavaScript.
- Los delays se calculan en `build_profile.py` a partir de `T`, así que
  cambiar el ritmo es cambiar `T` y regenerar.

## Cambiar foto / datos

- Foto: reemplaza `assets/retrato.jpg` y corre el paso 2 + 3.
- Datos en vivo: corre el paso 1 (o espera al workflow nocturno).
- Datos manuales (emails, handles, ficha): edita `config.py` y `README.md`
  (sección contactos) — y corre el paso 3.
