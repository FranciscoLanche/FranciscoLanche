# tools/ — Pipeline del perfil estilo terminal

Todo el perfil se regenera con dos comandos. Editar primero lo que quieras en
`config.py` (textos, paleta Tokyo Night, tiempos de animación) y, si cambias la
foto, regenera el ASCII.

## Archivos

| Archivo | Qué hace |
| --- | --- |
| `config.py` | Identidad, ficha neofetch, contactos, paleta y tiempos `T` (estilo anime.js). Fuente única de verdad. |
| `portrait_to_ascii.py` | `assets/retrato.jpg` → `assets/ascii.txt` (ramp densidad, wipe de fondo, erosión de marco). |
| `build_profile.py` | Lee `ascii.txt` + `config.py` y genera los 3 SVG animados en `assets/`. |
| `tune_ascii.py` | Dev only: renderiza variantes A/B/C del retrato en `/tmp/opencode` para comparar. |
| `preview.html` | Playground con **anime.js real** (GitHub no ejecuta JS en README; aquí sí). |

## Uso

```bash
# 1) ASCII desde tu foto (largos avanzados: --cols, --contrast, --gamma, --crop, --wipe, --no-erode)
python3 tools/portrait_to_ascii.py

# 2) SVGs finales animados (neofetch-terminal, terminal-contact, terminal-divider)
python3 tools/build_profile.py

# Opcional: copias estáticas para inspección en /tmp/opencode
python3 tools/build_profile.py --static

# Opcional: comparar variantes del retrato
python3 tools/tune_ascii.py

# Opcional: preview anime.js (requiere servir el repo por http)
python3 -m http.server 8080          # en la raíz del repo
# → http://localhost:8080/tools/preview.html
```

## Cómo funciona la animación en GitHub

- GitHub sirve los SVG del README como `<img>`: **no ejecuta scripts**.
- La coreografía va horneada: CSS keyframes (stagger de líneas, blink del
  cursor) + SMIL `calcMode="discrete"` (typewriter glifo a glifo, clip que
  avanza por celda monoespaciada).
- Los delays se calculan en `build_profile.py` a partir de `T`, así que
  cambiar el ritmo es cambiar `T` y regenerar.

## Cambiar foto / datos

- Foto: reemplaza `assets/retrato.jpg` y corre el paso 1 + 2.
- Datos (emails, handles, ficha): edita `config.py` y `README.md`
  (sección contactos) — y corridor el paso 2.
