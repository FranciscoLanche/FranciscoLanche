# -*- coding: utf-8 -*-
"""
Configuración central del perfil tipo terminal de Francisco Lanche.
Edita este archivo para cambiar textos, colores o tiempos de animación
y luego regenera los SVG con:  python3 tools/build_profile.py
"""

# -------------------------------------------------------------------------- #
#  PERSONA                                                                    #
# -------------------------------------------------------------------------- #

USER = "francisco"
HOST = "FranciscoLanche05"
GITHUB = "https://github.com/FranciscoLanche05"

# Ficha de neofetch (lado derecho del terminal hero)
# (etiqueta, valor)  — el largo máximo influye en el ancho del SVG.
NEOFETCH_INFO = [
    ("OS",         "GNU/Linux · Arch BTW"),
    ("Kernel",     "Full Stack · Game Dev"),
    ("Uptime",     "5 años compilando café"),
    ("Shell",      "zsh + git + obsesión"),
    ("Editor",     "Neovim (ex Vim, ex Nano)"),
    ("Languages",  "TypeScript · React · Next"),
    ("",           "Node · Python · C# · Java"),
    ("Stack",      "Unity · SQL · Docker"),
    ("Status",     "35+ repos · junior+"),
    ("Theme",      "Tokyo Night"),
]

CONTACT_ROWS = [
    ("github",    "github.com/FranciscoLanche05",  GITHUB, "github"),
    ("linkedin",  "in/franciscolanche",            "https://linkedin.com/in/franciscolanche", "linkedin"),
    ("instagram", "@franciscolanche",              "https://instagram.com/franciscolanche",   "instagram"),
    ("discord",   "francisco.lanche",              "https://discord.com",                     "discord"),
    ("email",     "franciscolanche@ejemplo.com",   "mailto:franciscolanche@ejemplo.com",      "gmail"),
]

# Badges clickeables under contact SVG: (texto, hex de fondo, logo, url)
CONTACT_BADGES = [
    ("$ cd github/",      "github",    GITHUB),
    ("$ ssh linkedin",    "linkedin",  "https://linkedin.com/in/franciscolanche"),
    ("$ curl instagram",  "instagram", "https://instagram.com/franciscolanche"),
    ("$ open discord",    "discord",   "https://discord.com"),
    ("$ mail -s hola",    "gmail",     "mailto:franciscolanche@ejemplo.com"),
]

SHIELD_COLORS = {
    "github":    "9ece6a", "linkedin":  "7aa2f7", "instagram": "bb9af7",
    "discord":   "7dcfff", "gmail":     "f7768e",
}

# -------------------------------------------------------------------------- #
#  PALETA TOKYO NIGHT                                                         #
# -------------------------------------------------------------------------- #

BG      = "#1a1b26"   # fondo terminal
BG_BAR  = "#16161e"   # barra de título
BORDER  = "#2f334d"
FG      = "#c0caf5"   # texto general
FAINT   = "#565f89"   # gris tenue (comentarios, divisor)
GREEN   = "#9ece6a"
BLUE    = "#7aa2f7"
RED     = "#f7768e"
YELLOW  = "#e0af68"
PURPLE  = "#bb9af7"
CYAN    = "#7dcfff"
WHITE   = "#ffffff"

MUTED_LABELS = True  # etiquetas en azul, valores en FG

# -------------------------------------------------------------------------- #
#  TIEMPOS DE ANIMACIÓN (estilo anime.js, horneados en el SVG)                #
# -------------------------------------------------------------------------- #

T = {
    "prompt_in":    0.20,   # primer prompt aparece
    "type_start":   0.45,   # empieza a teclear el comando
    "type_step":    0.055,  # ms por carácter
    "print_start":  1.05,   # el bloque neofetch empieza a imprimirse
    "step_row":     0.022,  # stagger por línea del bloque
    "step_info":    0.045,  # stagger por línea de info
    "cursor_at":    2.10,   # prompt final + cursor parpadeando
    "blink":        1.10,   # periodo del cursor
}
