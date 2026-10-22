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
HOST = "FranciscoLanche"
GITHUB = "https://github.com/FranciscoLanche"

# Ficha de neofetch (lado derecho del terminal hero) — secciones separadas
NEOFETCH_INFO = [
    ("OS",         "GNU/Linux · Arch BTW"),
    ("Kernel",     "Full Stack · Game Dev"),
    ("Uptime",     "5 años compilando café"),
    ("Shell",      "zsh + git + obsesión"),
    ("Editor",     "Neovim (ex Vim, ex Nano)"),
    ("Languages",  "TypeScript · React · Next"),
    ("",           "Node · Python · C# · Java"),
    ("",           "Unity · MySQL · SQL Server"),
    ("Status",     "junior+ · autodidacta"),
    ("Theme",      "Tokyo Night"),
]

# (se usa como título de la ventana de contacto)
CONTACT_TITLE = f"{USER}@{HOST}: ~/contacto — zsh"

CONTACT_ROWS = [
    ("email",     "franciscolanche@ejemplo.com",  "mailto:franciscolanche@ejemplo.com", "gmail"),
    ("linkedin",  "in/franciscolanche",           "https://linkedin.com/in/franciscolanche", "linkedin"),
    ("instagram", "@franciscolanche",             "https://instagram.com/franciscolanche",   "instagram"),
    ("discord",   "francisco.lanche",             "https://discord.com",                     "discord"),
]

# Badges clickeables: (texto esc, logo, url)
CONTACT_BADGES = [
    ("$ github --clone",    "github",    GITHUB),
    ("$ ssh linkedin",      "linkedin",  "https://linkedin.com/in/franciscolanche"),
    ("$ curl instagram",    "instagram", "https://instagram.com/franciscolanche"),
    ("$ open discord",      "discord",   "https://discord.com"),
    ("$ mail -s hola",      "gmail",     "mailto:franciscolanche@ejemplo.com"),
]

SHIELD_COLORS = {
    "github":    "9ece6a", "linkedin":  "7aa2f7", "instagram": "bb9af7",
    "discord":   "7dcfff", "gmail":     "f7768e",
}

COMMAND_HERO = "neofetch --snake"     # comando tecleado en el hero

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

# Panel de contribuciones (niveles GitHub 0..4 → Tokyo Night)
LEVEL_COLORS = ["#202333", "#2b5140", "#3d7a5e", "#62b982", "#9ece6a"]
MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]

# -------------------------------------------------------------------------- #
#  TIEMPOS DE ANIMACIÓN (estilo anime.js, horneados en el SVG)                #
# -------------------------------------------------------------------------- #

T = {
    "prompt_in":    0.20,   # primer prompt aparece
    "type_start":   0.45,   # empieza a teclear el comando
    "type_step":    0.055,  # s por carácter
    "print_start":  1.05,   # el bloque neofetch empieza a imprimirse
    "step_row":     0.022,  # stagger por línea del bloque
    "step_info":    0.045,  # stagger por línea de info
    "type2_start":  2.00,   # teclea el comando del panel snake
    "snake_start":  2.90,   # la serpiente arranca a comer
    "snake_period": 12.0,   # segundos por vuelta de la serpiente
    "cursor_at":    16.0,   # prompt final + cursor (tras 1ª vuelta)
    "blink":        1.10,   # periodo del cursor
}
