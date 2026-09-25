"""Generiert präzise, überlappungsfreie Landespolygone für src/py_plaque_inc/map/geo_data.py
anhand der Weltkartenvorlage world_map_dark.png (1240x580).
"""

import math
import os
from collections import deque
from typing import Dict, List, Tuple, Optional
import pygame

from py_plaque_inc.model.country import Climate, Wealth

def p_dist(p, p1, p2):
    x, y = p
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))

def rdp(points: List[Tuple[int, int]], epsilon: float) -> List[Tuple[int, int]]:
    if len(points) < 3:
        return points
    dmax = 0.0
    index = 0
    end = len(points) - 1
    for i in range(1, end):
        d = p_dist(points[i], points[0], points[end])
        if d > dmax:
            index = i
            dmax = d
    if dmax > epsilon:
        rec1 = rdp(points[: index + 1], epsilon)
        rec2 = rdp(points[index:], epsilon)
        return rec1[:-1] + rec2
    else:
        return [points[0], points[end]]

def point_in_polygon(x: int, y: int, polygon: List[Tuple[int, int]]) -> bool:
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def find_inside_point(polygon: List[Tuple[int, int]]) -> Tuple[int, int]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    cx = int(sum(xs) / len(xs))
    cy = int(sum(ys) / len(ys))
    if point_in_polygon(cx, cy, polygon):
        return cx, cy

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    step_x = max(1, (max_x - min_x) // 30)
    step_y = max(1, (max_y - min_y) // 30)

    best_p = (cx, cy)
    best_dist = 999999.0
    for y in range(min_y + 2, max_y - 2, step_y):
        for x in range(min_x + 2, max_x - 2, step_x):
            if point_in_polygon(x, y, polygon):
                d = math.hypot(x - cx, y - cy)
                if d < best_dist:
                    best_dist = d
                    best_p = (x, y)
    return best_p

# Metadaten aller 49 Territorien
TERRITORY_METADATA = [
    # 1. Nordamerika
    {
        "id": "can", "name": "Kanada", "population": 39_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(260, 140), (280, 160), (330, 180), (380, 160), (380, 100), (340, 100), (290, 90), (210, 110), (230, 120)],
        "neighbors": ["usa", "gln"],
    },
    {
        "id": "usa", "name": "USA", "population": 335_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(270, 240), (240, 230), (310, 250), (200, 260), (330, 230), (160, 130), (140, 140), (180, 125)],
        "neighbors": ["can", "mex", "cub"],
    },
    {
        "id": "mex", "name": "Mexiko", "population": 128_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(240, 280), (260, 290)],
        "neighbors": ["usa", "cen", "cub"],
    },
    {
        "id": "cen", "name": "Zentralamerika", "population": 50_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(275, 310), (290, 315)],
        "neighbors": ["mex", "col", "cub"],
    },
    {
        "id": "cub", "name": "Karibik", "population": 44_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(307, 287), (325, 292), (345, 302)],
        "neighbors": ["usa", "mex", "cen", "col"],
    },
    {
        "id": "gln", "name": "Grönland", "population": 56_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(480, 120), (510, 150), (450, 100)],
        "neighbors": ["can"],
    },

    # 2. Südamerika
    {
        "id": "col", "name": "Kolumbien", "population": 95_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(330, 335), (350, 330), (370, 330)],
        "neighbors": ["cen", "cub", "bra", "per"],
    },
    {
        "id": "bra", "name": "Brasilien", "population": 215_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(420, 370), (450, 380), (400, 400), (430, 420), (440, 360)],
        "neighbors": ["col", "per", "bol", "arg"],
    },
    {
        "id": "per", "name": "Peru", "population": 34_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(335, 375), (345, 395)],
        "neighbors": ["col", "bra", "bol", "chl"],
    },
    {
        "id": "bol", "name": "Bolivien", "population": 20_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": False,
        "seeds": [(375, 405), (395, 415)],
        "neighbors": ["per", "bra", "chl", "arg"],
    },
    {
        "id": "chl", "name": "Chile", "population": 19_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(363, 478), (360, 450), (365, 510)],
        "neighbors": ["per", "bol", "arg"],
    },
    {
        "id": "arg", "name": "Argentinien", "population": 50_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(380, 450), (385, 480), (390, 520), (410, 435)],
        "neighbors": ["chl", "bol", "bra"],
    },

    # 3. Europa
    {
        "id": "isl", "name": "Island", "population": 380_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(540, 175)],
        "neighbors": [],
    },
    {
        "id": "gbr", "name": "Großbritannien", "population": 73_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(570, 215), (580, 220), (560, 225)],
        "neighbors": ["fra"],
    },
    {
        "id": "fra", "name": "Frankreich", "population": 80_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(590, 245), (600, 245)],
        "neighbors": ["gbr", "esp", "deu", "ita"],
    },
    {
        "id": "esp", "name": "Spanien", "population": 58_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(560, 265), (575, 270), (550, 270)],
        "neighbors": ["fra", "nab"],
    },
    {
        "id": "deu", "name": "Deutschland", "population": 102_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(620, 235), (615, 240)],
        "neighbors": ["fra", "pol", "ita", "bal"],
    },
    {
        "id": "ita", "name": "Italien", "population": 59_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(625, 255), (630, 265), (620, 275)],
        "neighbors": ["fra", "deu", "bal"],
    },
    {
        "id": "pol", "name": "Polen", "population": 58_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(645, 225), (650, 235)],
        "neighbors": ["deu", "bal", "ukr", "fin"],
    },
    {
        "id": "bal", "name": "Balkan", "population": 60_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(650, 250), (660, 255), (660, 265)],
        "neighbors": ["ita", "deu", "pol", "ukr", "tur"],
    },
    {
        "id": "sca", "name": "Skandinavien", "population": 27_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(620, 170), (635, 180), (610, 215)],
        "neighbors": ["fin", "rus", "deu"],
    },
    {
        "id": "fin", "name": "Finnland", "population": 12_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(665, 160), (660, 195)],
        "neighbors": ["sca", "rus", "pol"],
    },
    {
        "id": "ukr", "name": "Ukraine", "population": 52_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(680, 230), (660, 220)],
        "neighbors": ["pol", "bal", "rus", "tur"],
    },

    # 4. Russland & Zentralasien
    {
        "id": "rus", "name": "Russland", "population": 144_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(700, 170), (750, 160), (800, 150), (850, 140), (900, 140), (950, 150), (1000, 170), (1050, 180), (1100, 160), (1130, 170), (750, 200), (820, 180)],
        "neighbors": ["sca", "fin", "ukr", "kaz", "mon", "chn"],
    },
    {
        "id": "kaz", "name": "Zentralasien", "population": 75_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": False,
        "seeds": [(750, 230), (780, 225), (760, 250), (790, 245)],
        "neighbors": ["rus", "irn", "chn", "pak"],
    },
    {
        "id": "mon", "name": "Mongolei", "population": 3_500_000,
        "climate": "Climate.COLD", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": False,
        "seeds": [(880, 220), (910, 220)],
        "neighbors": ["rus", "chn"],
    },

    # 5. Naher Osten
    {
        "id": "tur", "name": "Türkei", "population": 95_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(687, 253), (700, 250)],
        "neighbors": ["bal", "ukr", "mde", "irn"],
    },
    {
        "id": "mde", "name": "Naher Osten", "population": 70_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(710, 265), (720, 270)],
        "neighbors": ["tur", "irn", "sau", "egy"],
    },
    {
        "id": "sau", "name": "Saudi-Arabien", "population": 40_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(730, 290), (750, 305)],
        "neighbors": ["mde", "irn", "egy"],
    },
    {
        "id": "irn", "name": "Iran", "population": 88_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(755, 265), (775, 275)],
        "neighbors": ["tur", "mde", "sau", "kaz", "pak"],
    },

    # 6. Asien
    {
        "id": "chn", "name": "China", "population": 1_410_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(850, 260), (900, 270), (940, 280), (880, 300), (920, 310)],
        "neighbors": ["rus", "kaz", "mon", "ind", "pak", "sea", "kor"],
    },
    {
        "id": "ind", "name": "Indien", "population": 1_428_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(810, 310), (830, 320), (820, 340)],
        "neighbors": ["pak", "chn", "sea"],
    },
    {
        "id": "pak", "name": "Pakistan", "population": 280_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(790, 275), (800, 290)],
        "neighbors": ["irn", "kaz", "chn", "ind"],
    },
    {
        "id": "jpn", "name": "Japan", "population": 124_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1016, 258), (1030, 240)],
        "neighbors": [],
    },
    {
        "id": "kor", "name": "Korea", "population": 78_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(959, 259)],
        "neighbors": ["chn"],
    },
    {
        "id": "sea", "name": "Südostasien", "population": 380_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(890, 340), (910, 350), (930, 360)],
        "neighbors": ["ind", "chn", "idn"],
    },
    {
        "id": "idn", "name": "Indonesien", "population": 275_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(950, 400), (980, 410), (1030, 405), (1005, 385)],
        "neighbors": ["sea", "phl", "png", "aus"],
    },
    {
        "id": "phl", "name": "Philippinen", "population": 115_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(988, 357), (995, 375)],
        "neighbors": ["idn"],
    },

    # 7. Afrika
    {
        "id": "nab", "name": "Nordafrika", "population": 90_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(570, 290), (600, 295), (630, 295)],
        "neighbors": ["esp", "egy", "waf", "sud"],
    },
    {
        "id": "egy", "name": "Ägypten", "population": 118_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(670, 295), (680, 305)],
        "neighbors": ["nab", "sud", "mde", "sau"],
    },
    {
        "id": "waf", "name": "Westafrika", "population": 420_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(560, 330), (580, 340), (610, 340)],
        "neighbors": ["nab", "caf", "sud"],
    },
    {
        "id": "caf", "name": "Zentralafrika", "population": 180_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(640, 370), (650, 385)],
        "neighbors": ["waf", "sud", "eaf", "zaf"],
    },
    {
        "id": "eaf", "name": "Ostafrika", "population": 350_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(680, 340), (690, 360), (670, 370)],
        "neighbors": ["egy", "sud", "caf", "zaf"],
    },
    {
        "id": "zaf", "name": "Südafrika", "population": 68_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(635, 415), (645, 440), (660, 430)],
        "neighbors": ["caf", "eaf", "mdg"],
    },
    {
        "id": "mdg", "name": "Madagaskar", "population": 29_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(734, 403)],
        "neighbors": ["zaf"],
    },
    {
        "id": "sud", "name": "Sudan", "population": 75_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(650, 325), (670, 335)],
        "neighbors": ["nab", "egy", "waf", "caf", "eaf"],
    },

    # 8. Ozeanien
    {
        "id": "aus", "name": "Australien", "population": 26_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(990, 440), (1030, 450), (980, 480), (1050, 490), (1020, 520)],
        "neighbors": ["idn", "png", "nzl"],
    },
    {
        "id": "nzl", "name": "Neuseeland", "population": 5_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1099, 501), (1080, 515)],
        "neighbors": ["aus"],
    },
    {
        "id": "png", "name": "Neuguinea", "population": 9_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1058, 397)],
        "neighbors": ["idn", "aus"],
    },
]

def main():
    img = pygame.image.load("src/py_plaque_inc/assets/world_map_dark.png")
    w, h = img.get_size()
    print(f"Lade Karte: {w}x{h}")

    # 1. Landmaske erstellen
    land = [[False]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            c = img.get_at((x, y))
            if not (c[0] <= 20 and c[1] <= 26 and c[2] <= 38):
                land[y][x] = True

    def find_land_near(x, y, r=40):
        if 0 <= x < w and 0 <= y < h and land[y][x]:
            return x, y
        for d in range(1, r):
            for dx in range(-d, d + 1):
                for dy in (-d, d):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and land[ny][nx]:
                        return nx, ny
                for dy in range(-d + 1, d):
                    for nx in (x - d, x + d):
                        ny = y + dy
                        if 0 <= nx < w and 0 <= ny < h and land[ny][nx]:
                            return nx, ny
        return None

    # 2. Bereinigte Seeds mit Farbmustern
    seeds_dict: Dict[str, List[Tuple[int, int, Tuple[int, int, int]]]] = {}
    for meta in TERRITORY_METADATA:
        cid = meta["id"]
        valid_pts = []
        for p in meta["seeds"]:
            lp = find_land_near(*p)
            if lp:
                col = img.get_at(lp)[:3]
                if (lp[0], lp[1], col) not in valid_pts:
                    valid_pts.append((lp[0], lp[1], col))
        seeds_dict[cid] = valid_pts

    # 3. Farb-geführtes Dijkstra auf Landpixeln für exakte Grenzverläufe
    import heapq
    dist = [[999999.0]*w for _ in range(h)]
    owner = [[None]*w for _ in range(h)]
    heap = [] # (cost, x, y, cid, (r, g, b))

    for cid, pts in seeds_dict.items():
        for sx, sy, sc in pts:
            dist[sy][sx] = 0.0
            owner[sy][sx] = cid
            heapq.heappush(heap, (0.0, sx, sy, cid, sc))

    print("Starte farbgeführtes Dijkstra...")
    while heap:
        d, x, y, cid, sc = heapq.heappop(heap)
        if d > dist[y][x]:
            continue
        for dx, dy in ((-1,0), (1,0), (0,-1), (0,1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and land[ny][nx]:
                c = img.get_at((nx, ny))[:3]
                # Farbdistanz zur Ursprungsfarbe
                cdiff = abs(c[0] - sc[0]) + abs(c[1] - sc[1]) + abs(c[2] - sc[2])
                # Weiche Strafe für Farbabweichung, damit Grenzen exakt an Farbkanten einrasten
                step_cost = 1.0 + (cdiff / 16.0) ** 2
                nd = d + step_cost
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    owner[ny][nx] = cid
                    heapq.heappush(heap, (nd, nx, ny, cid, sc))

    print("Dijkstra abgeschlossen.")

    # 4. Verbleibende unassigned Inseln dem nächsten Territorium zuweisen
    unassigned = [(x, y) for y in range(h) for x in range(w) if land[y][x] and owner[y][x] is None]
    print(f"Unassigned Inselpixel: {len(unassigned)}")
    if unassigned:
        assigned_pts = [(x, y, owner[y][x]) for y in range(h) for x in range(w) if owner[y][x] is not None]
        for ux, uy in unassigned:
            # Finde nächsten Nachbarn in assigned_pts
            best_cid = None
            best_dist = 999999.0
            for ax, ay, acid in assigned_pts[::10]: # Abtastung für Performance
                d = (ux - ax)**2 + (uy - ay)**2
                if d < best_dist:
                    best_dist = d
                    best_cid = acid
            owner[uy][ux] = best_cid

    # 5. Polygone extrahieren
    MAP_OFFSET_X = 20
    MAP_OFFSET_Y = 64

    extracted_countries = []
    for meta in TERRITORY_METADATA:
        cid = meta["id"]
        # Erstelle Maske für dieses Territorium
        c_mask = pygame.Mask((w, h))
        for y in range(h):
            for x in range(w):
                if owner[y][x] == cid:
                    c_mask.set_at((x, y), 1)

        comps = c_mask.connected_components()
        polys = []
        for comp in comps:
            if comp.count() < 45: # Filter minimale Splitter
                continue
            outline = comp.outline(every=2)
            if len(outline) >= 6:
                simple = rdp(outline, epsilon=1.8)
                game_pts = [(MAP_OFFSET_X + px, MAP_OFFSET_Y + py) for px, py in simple]
                cleaned = []
                for pt in game_pts:
                    if not cleaned or pt != cleaned[-1]:
                        cleaned.append(pt)
                if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
                    cleaned.pop()
                if len(cleaned) >= 4:
                    polys.append(cleaned)

        if not polys:
            # Fallback: Rechteck um Seed
            sx, sy, _ = seeds_dict[cid][0]
            gx, gy = MAP_OFFSET_X + sx, MAP_OFFSET_Y + sy
            polys = [[(gx-10, gy-10), (gx+10, gy-10), (gx+10, gy+10), (gx-10, gy+10)]]

        # Größtes Polygon für Hauptstadt
        largest_poly = max(polys, key=lambda p: len(p))
        cap = find_inside_point(largest_poly)

        extracted_countries.append({
            "id": cid,
            "name": meta["name"],
            "population": meta["population"],
            "climate": meta["climate"],
            "wealth": meta["wealth"],
            "has_airport": meta["has_airport"],
            "has_seaport": meta["has_seaport"],
            "capital_pos": cap,
            "polygons": polys,
            "neighbors": sorted(meta["neighbors"]),
        })

    # Nachbarschaftssymmetrie sicherstellen
    neighbors_map = {c["id"]: set(c["neighbors"]) for c in extracted_countries}
    for cid, n_set in neighbors_map.items():
        for nid in list(n_set):
            neighbors_map[nid].add(cid)
    for c in extracted_countries:
        c["neighbors"] = sorted(list(neighbors_map[c["id"]]))

    # Code generieren
    lines = [
        '"""Geografische Vektordaten, Landesgrenzen und Routen für Py-Plaque-Inc.',
        'Automatisch generiert und kalibriert aus der Weltkartenvorlage world_map_dark.png.',
        '"""',
        '',
        'from typing import List, Dict',
        'from py_plaque_inc.model.country import Country, Climate, Wealth',
        '',
        '',
        'def create_world_countries() -> Dict[str, Country]:',
        '    """',
        f'    Erstellt die Weltkarte mit {len(extracted_countries)} detaillierten Territorien,',
        '    die lückenlos anhand von world_map_dark.png extrahiert wurden.',
        '    Die Koordinaten sind auf das Spielfenster (1280x720) ausgerichtet',
        '    (Kartenbereich X: 20..1260, Y: 64..644).',
        '    """',
        '    countries: List[Country] = [',
    ]

    for c in extracted_countries:
        lines.append('        Country(')
        lines.append(f'            id="{c["id"]}",')
        lines.append(f'            name="{c["name"]}",')
        lines.append(f'            population={c["population"]:,}'.replace(',', '_') + ',')
        lines.append(f'            climate={c["climate"]},')
        lines.append(f'            wealth={c["wealth"]},')
        lines.append(f'            has_airport={c["has_airport"]},')
        lines.append(f'            has_seaport={c["has_seaport"]},')
        lines.append(f'            capital_pos={c["capital_pos"]},')
        lines.append('            polygons=[')
        for poly in c["polygons"]:
            pts_str = ", ".join(f"({x}, {y})" for x, y in poly)
            lines.append(f'                [{pts_str}],')
        lines.append('            ],')
        neighbors_str = ", ".join(f'"{nid}"' for nid in c["neighbors"])
        lines.append(f'            neighbors=[{neighbors_str}],')
        lines.append('        ),')

    lines.append('    ]')
    lines.append('')
    lines.append('    return {c.id: c for c in countries}')
    lines.append('')

    code = "\n".join(lines)
    with open("src/py_plaque_inc/map/geo_data.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("src/py_plaque_inc/map/geo_data.py erfolgreich generiert!")

if __name__ == "__main__":
    main()
