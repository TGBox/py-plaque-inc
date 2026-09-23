"""Zentrale Konfiguration für Py-Plaque-Inc."""

from typing import Dict, Any

# Fenster & Darstellung
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Py-Plaque-Inc - Globale Pandemie-Simulation"

# Farbpalette (Plague Inc. Dark Sci-Fi Aesthetic)
COLOR_BG = (12, 16, 24)               # Tiefes Slate-Dunkelblau (Ozean)
COLOR_OCEAN_DEEP = (8, 12, 18)
COLOR_PANEL_BG = (18, 24, 36)          # Panel-Hintergrund
COLOR_PANEL_BORDER = (35, 48, 70)      # Dezenter Rahmen
COLOR_PANEL_HOVER = (26, 36, 54)

# Länderfarben
COLOR_COUNTRY_LAND = (38, 48, 58)      # Neutrales, gesundes Land
COLOR_COUNTRY_OUTLINE = (55, 70, 85)   # Landesgrenzen
COLOR_COUNTRY_HOVER = (70, 90, 110)    # Hover-Hervorhebung
COLOR_COUNTRY_SELECTED = (100, 130, 160)

# Infektion & Tod
COLOR_INFECTED_MIN = (210, 60, 60)     # Helles Rot bei Beginn der Infektion
COLOR_INFECTED_MAX = (150, 15, 15)     # Tiefes Blutrot bei 100% Infektion
COLOR_DEAD = (25, 20, 25)              # Aschgrau-Schwarz für entvölkerte Gebiete

# Akzent- und Statusfarben
COLOR_TEXT_PRIMARY = (240, 242, 245)
COLOR_TEXT_MUTED = (145, 155, 170)
COLOR_TEXT_DARK = (15, 20, 28)

COLOR_DNA = (255, 165, 0)              # Leuchtendes Orange für DNA-Punkte
COLOR_DNA_GLOW = (255, 190, 50)
COLOR_DNA_BUBBLE_RED = (230, 40, 40)   # Rote Infektions-Blase
COLOR_DNA_BUBBLE_ORANGE = (255, 150, 0)# Orange DNA-Bonus-Blase
COLOR_CURE_BUBBLE_BLUE = (0, 190, 255) # Blaue Heilmittel-Blase

COLOR_CURE = (0, 180, 230)             # Cyan/Blau für Heilmittelforschung
COLOR_CURE_BG = (15, 35, 50)
COLOR_SUCCESS = (46, 204, 113)         # Grün
COLOR_WARNING = (241, 196, 15)         # Gelb
COLOR_DANGER = (231, 76, 60)           # Rot

# Geschwindigkeitsstufen
SPEED_PAUSED = 0
SPEED_NORMAL = 1.0     # 1 Tag pro 1.0s (bei 60fps)
SPEED_FAST = 2.5       # 2.5 Tage pro 1.0s
SPEED_ULTRA = 5.0      # 5 Tage pro 1.0s

SPEED_MULTIPLIERS = {
    0: 0.0,
    1: 1.0,
    2: 2.5,
    3: 5.0,
}

# Schwierigkeitsgrade
DIFFICULTIES: Dict[str, Dict[str, Any]] = {
    "Leicht": {
        "id": "easy",
        "description": "Niemand wäscht sich die Hände. Ärzte forschen nur selten. Kranke werden herzlich umarmt.",
        "transmission_multiplier": 1.25,
        "cure_speed_multiplier": 0.65,
        "mutation_chance_multiplier": 1.3,
        "starting_dna": 15,
    },
    "Normal": {
        "id": "normal",
        "description": "67% der Bevölkerung waschen sich die Hände. Ärzte arbeiten 4 Tage die Woche. Kranke werden ignoriert.",
        "transmission_multiplier": 1.0,
        "cure_speed_multiplier": 1.0,
        "mutation_chance_multiplier": 1.0,
        "starting_dna": 10,
    },
    "Schwer": {
        "id": "brutal",
        "description": "Strikte Hygienevorschriften. Ärzte arbeiten rund um die Uhr. Kranke werden sofort isoliert.",
        "transmission_multiplier": 0.8,
        "cure_speed_multiplier": 1.35,
        "mutation_chance_multiplier": 0.8,
        "starting_dna": 5,
    },
}

# Kartengrenzen (Mercator-Projektionsbereich für Zeichnung)
MAP_X = 20
MAP_Y = 64
MAP_WIDTH = 1240
MAP_HEIGHT = 580
