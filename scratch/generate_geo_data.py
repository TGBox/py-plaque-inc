"""Generiert src/py_plaque_inc/map/geo_data.py aus world_map.jpg mit allen 49 Territorien."""

import math
import pygame
from typing import List, Tuple, Dict, Optional

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

def dilate_mask(m: pygame.Mask, w: int, h: int, r: int = 2) -> pygame.Mask:
    res = pygame.Mask((w, h))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                res.draw(m, (dx, dy))
    return res

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

def find_pure_color_seed(surf: pygame.Surface, x: int, y: int, bg_col: Tuple[int, int, int], radius: int = 25) -> Optional[Tuple[int, int, Tuple[int, int, int]]]:
    candidates: Dict[Tuple[int, int, int], int] = {}
    w, h = surf.get_size()
    for dy in range(-radius, radius + 1, 2):
        for dx in range(-radius, radius + 1, 2):
            px, py = x + dx, y + dy
            if 0 <= px < w and 0 <= py < h:
                c = surf.get_at((px, py))[:3]
                dist_bg = sum(abs(c[i] - bg_col[i]) for i in range(3))
                dist_white = sum(abs(c[i] - 255) for i in range(3))
                if dist_bg > 85 and dist_white > 50:
                    q = (c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)
                    candidates[q] = candidates.get(q, 0) + 1

    if not candidates:
        return None

    best_col = max(candidates.items(), key=lambda item: item[1])[0]
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            px, py = x + dx, y + dy
            if 0 <= px < w and 0 <= py < h:
                c = surf.get_at((px, py))[:3]
                q = (c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)
                if q == best_col:
                    return px, py, c

    return None

def extract_territory_polygons(
    surf: pygame.Surface,
    seeds: List[Tuple[int, int]],
    bg_col: Tuple[int, int, int],
    bounds: pygame.Rect,
    eps: float = 2.0,
) -> List[List[Tuple[int, int]]]:
    w, h = surf.get_size()
    
    territory_mask = pygame.Mask((w, h))
    for sx, sy in seeds:
        res = find_pure_color_seed(surf, sx, sy, bg_col, radius=20)
        if res is None:
            continue
        px, py, target_c = res

        raw = pygame.mask.from_threshold(surf, target_c, (22, 22, 22))
        clipped = pygame.Mask((w, h))
        for by in range(max(0, bounds.top), min(h, bounds.bottom)):
            for bx in range(max(0, bounds.left), min(w, bounds.right)):
                if raw.get_at((bx, by)):
                    clipped.set_at((bx, by), 1)

        closed = dilate_mask(clipped, w, h, r=3)
        comps = closed.connected_components()

        for comp in comps:
            if comp.get_at((px, py)) or comp.get_at((sx, sy)):
                territory_mask.draw(comp, (0, 0))
                break

    dilated_territory = dilate_mask(territory_mask, w, h, r=2)
    final_comps = dilated_territory.connected_components()

    polygons: List[List[Tuple[int, int]]] = []
    for comp in final_comps:
        if comp.count() < 70:
            continue
        pts = comp.outline(every=2)
        if len(pts) >= 6:
            simple = rdp(pts, eps)
            # Korrekte Koordinatenumrechnung:
            # Bildinhalt liegt bei x=80..1445, y=100..869 (im 1531x980 Bild).
            # Spielkartenbereich: X=20..1260, Y=64..644 (1240x580 Pixel).
            _IOFF_X, _IOFF_Y = 80, 100
            _ISCALE_W, _ISCALE_H = 1365, 769   # 1445-80, 869-100
            _MAP_X, _MAP_Y = 20, 64
            _MAP_W, _MAP_H = 1240, 580
            game_pts: List[Tuple[int, int]] = []
            for x_img, y_img in simple:
                gx = int(round(_MAP_X + (x_img - _IOFF_X) * (_MAP_W / _ISCALE_W)))
                gy = int(round(_MAP_Y + (y_img - _IOFF_Y) * (_MAP_H / _ISCALE_H)))
                gx = max(20, min(1260, gx))
                gy = max(64, min(644, gy))
                game_pts.append((gx, gy))

            cleaned: List[Tuple[int, int]] = []
            for pt in game_pts:
                if not cleaned or pt != cleaned[-1]:
                    cleaned.append(pt)
            if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
                cleaned.pop()

            if len(cleaned) >= 4:
                polygons.append(cleaned)

    return polygons


TERRITORIES_DATA = [
    # 1. NORDAMERIKA
    {
        "id": "can", "name": "Kanada", "population": 39_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(320, 260), (360, 160), (420, 150), (460, 220), (470, 290)],
        "bounds": pygame.Rect(160, 80, 380, 290),
        "neighbors": ["usa", "gln"],
    },
    {
        "id": "usa", "name": "USA", "population": 335_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(300, 380), (380, 440), (180, 210)],
        "bounds": pygame.Rect(30, 120, 460, 370),
        "neighbors": ["can", "mex", "cub"],
    },
    {
        "id": "mex", "name": "Mexiko", "population": 128_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(300, 480), (265, 450)],
        "bounds": pygame.Rect(220, 420, 150, 120),
        "neighbors": ["usa", "cen", "cub"],
    },
    {
        "id": "cen", "name": "Zentralamerika", "population": 50_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(340, 520), (370, 535)],
        "bounds": pygame.Rect(320, 500, 80, 70),
        "neighbors": ["mex", "col", "cub"],
    },
    {
        "id": "cub", "name": "Karibik", "population": 44_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(375, 490), (415, 510), (440, 520)],
        "bounds": pygame.Rect(360, 475, 100, 60),
        "neighbors": ["usa", "mex", "cen", "col"],
    },
    {
        "id": "gln", "name": "Grönland", "population": 56_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(600, 200)],
        "bounds": pygame.Rect(500, 80, 160, 230),
        "neighbors": ["can"],
    },

    # 2. SÜDAMERIKA
    {
        "id": "col", "name": "Kolumbien", "population": 95_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(430, 565), (470, 550), (510, 560), (530, 560), (415, 595)],
        "bounds": pygame.Rect(390, 525, 170, 100),
        "neighbors": ["cen", "cub", "bra", "per"],
    },
    {
        "id": "bra", "name": "Brasilien", "population": 215_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(520, 640), (560, 620), (470, 600)],
        "bounds": pygame.Rect(430, 560, 180, 180),
        "neighbors": ["col", "per", "bol", "arg"],
    },
    {
        "id": "per", "name": "Peru", "population": 34_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(430, 640)],
        "bounds": pygame.Rect(405, 590, 65, 100),
        "neighbors": ["col", "bra", "bol", "chl"],
    },
    {
        "id": "bol", "name": "Bolivien", "population": 20_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": False,
        "seeds": [(465, 665), (495, 690)],
        "bounds": pygame.Rect(440, 640, 85, 90),
        "neighbors": ["per", "bra", "chl", "arg"],
    },
    {
        "id": "chl", "name": "Chile", "population": 19_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(445, 750), (455, 830)],
        "bounds": pygame.Rect(425, 680, 50, 190),
        "neighbors": ["per", "bol", "arg"],
    },
    {
        "id": "arg", "name": "Argentinien", "population": 50_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(475, 760), (460, 810), (505, 745), (495, 855)],
        "bounds": pygame.Rect(445, 695, 90, 180),
        "neighbors": ["chl", "bol", "bra"],
    },

    # 3. EUROPA
    {
        "id": "isl", "name": "Island", "population": 380_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(665, 305)],
        "bounds": pygame.Rect(645, 290, 45, 35),
        "neighbors": [],
    },
    {
        "id": "gbr", "name": "Großbritannien", "population": 73_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(715, 350), (700, 365), (705, 320)],
        "bounds": pygame.Rect(670, 290, 65, 90),
        "neighbors": ["fra"],
    },
    {
        "id": "fra", "name": "Frankreich", "population": 80_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(725, 375), (735, 350)],
        "bounds": pygame.Rect(700, 340, 60, 65),
        "neighbors": ["gbr", "esp", "deu", "ita"],
    },
    {
        "id": "esp", "name": "Spanien", "population": 58_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        # Seeds und Bounds kalibriert: Spanien liegt in Bild-Y 350-415 (Mittelmeer-Grenze).
        "seeds": [(700, 367), (715, 375), (695, 380), (672, 365)],
        "bounds": pygame.Rect(645, 348, 90, 68),
        "neighbors": ["fra", "nab"],
    },
    {
        "id": "deu", "name": "Deutschland", "population": 102_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(755, 345), (745, 375), (765, 375)],
        "bounds": pygame.Rect(735, 325, 55, 65),
        "neighbors": ["fra", "pol", "ita", "bal"],
    },
    {
        "id": "ita", "name": "Italien", "population": 59_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        # Stiefel der Apenninenhalbinsel: y=385-460, erste beiden Seeds lagen auf cream.
        "seeds": [(764, 406), (762, 420), (757, 435), (773, 445)],
        "bounds": pygame.Rect(735, 383, 55, 80),
        "neighbors": ["fra", "deu", "bal"],
    },
    {
        "id": "pol", "name": "Polen", "population": 58_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(795, 340), (780, 360), (790, 380)],
        "bounds": pygame.Rect(765, 325, 60, 70),
        "neighbors": ["deu", "bal", "ukr", "fin"],
    },
    {
        "id": "bal", "name": "Balkan", "population": 60_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(785, 405), (815, 385), (825, 410), (815, 435), (825, 450)],
        "bounds": pygame.Rect(775, 375, 70, 90),
        "neighbors": ["ita", "deu", "pol", "ukr", "tur"],
    },
    {
        "id": "sca", "name": "Skandinavien", "population": 27_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(790, 220), (775, 270), (765, 315), (748, 325)],
        "bounds": pygame.Rect(720, 195, 90, 140),
        "neighbors": ["fin", "rus", "deu"],
    },
    {
        "id": "fin", "name": "Finnland", "population": 12_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(815, 255), (815, 305), (815, 325)],
        "bounds": pygame.Rect(795, 205, 60, 130),
        "neighbors": ["sca", "pol", "rus", "ukr"],
    },
    {
        "id": "ukr", "name": "Ukraine", "population": 50_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(840, 350), (825, 335), (830, 375)],
        "bounds": pygame.Rect(805, 320, 75, 65),
        "neighbors": ["pol", "fin", "bal", "rus", "tur"],
    },

    # 4. RUSSLAND & ZENTRALASIEN
    {
        "id": "rus", "name": "Russland", "population": 144_000_000,
        "climate": "Climate.COLD", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [
            (880, 280), (840, 280), (910, 240), (980, 240), (1050, 240),
            (1150, 230), (1240, 230), (1310, 250), (1320, 290), (1275, 330)
        ],
        "bounds": pygame.Rect(820, 130, 540, 235),
        "neighbors": ["sca", "fin", "ukr", "kaz", "mon", "chn"],
    },
    {
        "id": "kaz", "name": "Zentralasien", "population": 75_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": False,
        "seeds": [(915, 335), (965, 335), (910, 380), (905, 400), (960, 380), (960, 400)],
        "bounds": pygame.Rect(870, 310, 130, 105),
        "neighbors": ["rus", "irn", "chn", "pak"],
    },
    {
        "id": "mon", "name": "Mongolei", "population": 3_500_000,
        "climate": "Climate.COLD", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": False,
        "seeds": [(1100, 345)],
        "bounds": pygame.Rect(1030, 325, 120, 50),
        "neighbors": ["rus", "chn"],
    },

    # 5. NAHER OSTEN
    {
        "id": "tur", "name": "Türkei", "population": 95_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(835, 395), (865, 395), (890, 385), (900, 395)],
        "bounds": pygame.Rect(815, 375, 100, 45),
        "neighbors": ["bal", "ukr", "mde", "irn"],
    },
    {
        "id": "mde", "name": "Naher Osten", "population": 70_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(855, 430), (865, 420), (885, 425)],
        "bounds": pygame.Rect(845, 410, 65, 45),
        "neighbors": ["tur", "sau", "irn", "egy"],
    },
    {
        "id": "sau", "name": "Saudi-Arabien", "population": 65_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(885, 465), (900, 490), (925, 515), (940, 500), (930, 475)],
        "bounds": pygame.Rect(865, 440, 100, 95),
        "neighbors": ["mde", "egy", "eaf"],
    },
    {
        "id": "irn", "name": "Iran", "population": 130_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(925, 425), (965, 415)],
        "bounds": pygame.Rect(895, 395, 95, 65),
        "neighbors": ["tur", "mde", "kaz", "pak"],
    },

    # 6. AFRIKA
    {
        "id": "nab", "name": "Nordafrika", "population": 90_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        # Nordafrika (Algerien/Marokko/Libyen) liegt in Bild-Y 420-510,
        # klar unterhalb des Mittelmeers (Cream-Lücke bei Y=385-420).
        "seeds": [(676, 435), (703, 437), (740, 432), (723, 466)],
        "bounds": pygame.Rect(635, 420, 150, 90),
        "neighbors": ["esp", "egy", "waf"],
    },
    {
        "id": "egy", "name": "Ägypten", "population": 118_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        # Ägypten: Nilder Deltabereich, klar südlich des Mittelmeers.
        "seeds": [(779, 477), (836, 480)],
        "bounds": pygame.Rect(745, 450, 110, 70),
        "neighbors": ["nab", "sud", "mde", "sau"],
    },
    {
        "id": "sud", "name": "Sudan", "population": 58_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(835, 505), (825, 550)],
        "bounds": pygame.Rect(800, 485, 65, 80),
        "neighbors": ["egy", "caf", "eaf", "waf"],
    },
    {
        "id": "waf", "name": "Westafrika", "population": 420_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(670, 490), (705, 500), (660, 520), (705, 545), (715, 530), (750, 540), (745, 495)],
        "bounds": pygame.Rect(640, 465, 130, 100),
        "neighbors": ["nab", "caf", "sud"],
    },
    {
        "id": "caf", "name": "Zentralafrika", "population": 160_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(775, 510), (765, 550), (790, 545), (745, 580), (760, 590), (785, 595), (800, 620)],
        "bounds": pygame.Rect(735, 485, 95, 160),
        "neighbors": ["waf", "sud", "eaf", "zaf"],
    },
    {
        "id": "eaf", "name": "Ostafrika", "population": 320_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(865, 525), (890, 525), (885, 545), (850, 585), (825, 580), (840, 625)],
        "bounds": pygame.Rect(815, 495, 100, 150),
        "neighbors": ["sud", "caf", "zaf", "sau"],
    },
    {
        "id": "zaf", "name": "Südafrika", "population": 140_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [
            (765, 645), (800, 655), (845, 665), (835, 705), (815, 680),
            (765, 705), (795, 700), (795, 755), (810, 740), (825, 745)
        ],
        "bounds": pygame.Rect(740, 625, 125, 160),
        "neighbors": ["caf", "eaf", "mdg"],
    },
    {
        "id": "mdg", "name": "Madagaskar", "population": 29_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(895, 685)],
        "bounds": pygame.Rect(875, 650, 50, 85),
        "neighbors": ["zaf", "eaf"],
    },

    # 7. SÜDASIEN
    {
        "id": "pak", "name": "Pakistan", "population": 240_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(980, 425)],
        "bounds": pygame.Rect(960, 400, 50, 65),
        "neighbors": ["irn", "kaz", "ind", "chn"],
    },
    {
        "id": "ind", "name": "Indien", "population": 1_600_000_000,
        "climate": "Climate.HOT", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1015, 455), (1030, 495), (1035, 540), (1075, 480), (1040, 575), (1050, 455), (1075, 455)],
        "bounds": pygame.Rect(990, 435, 100, 155),
        "neighbors": ["pak", "chn", "sea"],
    },

    # 8. OST- & SÜDOSTASIEN
    {
        "id": "chn", "name": "China", "population": 1_410_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1170, 450), (1160, 400), (1020, 390), (1030, 430), (1080, 430), (1215, 495), (1150, 525)],
        "bounds": pygame.Rect(990, 360, 240, 175),
        "neighbors": ["rus", "mon", "kaz", "pak", "ind", "sea", "kor"],
    },
    {
        "id": "kor", "name": "Korea", "population": 78_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1205, 400), (1210, 420)],
        "bounds": pygame.Rect(1185, 385, 40, 55),
        "neighbors": ["chn"],
    },
    {
        "id": "jpn", "name": "Japan", "population": 124_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1255, 400), (1270, 360), (1235, 425)],
        "bounds": pygame.Rect(1220, 345, 70, 110),
        "neighbors": [],
    },
    {
        "id": "sea", "name": "Südostasien", "population": 250_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1095, 490), (1115, 520), (1130, 500), (1140, 545), (1130, 585), (1190, 595)],
        "bounds": pygame.Rect(1075, 465, 135, 145),
        "neighbors": ["ind", "chn", "idn"],
    },
    {
        "id": "phl", "name": "Philippinen", "population": 115_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1215, 530), (1230, 575)],
        "bounds": pygame.Rect(1200, 515, 50, 80),
        "neighbors": [],
    },
    {
        "id": "idn", "name": "Indonesien", "population": 275_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.MEDIUM",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1135, 605), (1170, 635), (1185, 615), (1230, 620), (1250, 635)],
        "bounds": pygame.Rect(1110, 580, 160, 80),
        "neighbors": ["sea", "png", "aus"],
    },
    {
        "id": "png", "name": "Papua-Neuguinea", "population": 10_000_000,
        "climate": "Climate.HUMID", "wealth": "Wealth.POOR",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1300, 630)],
        "bounds": pygame.Rect(1260, 600, 80, 55),
        "neighbors": ["idn", "aus"],
    },

    # 9. OZEANIEN
    {
        "id": "aus", "name": "Australien", "population": 26_000_000,
        "climate": "Climate.ARID", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1230, 710), (1180, 720), (1280, 710), (1270, 790), (1275, 830)],
        "bounds": pygame.Rect(1140, 650, 180, 200),
        "neighbors": ["idn", "png", "nzl"],
    },
    {
        "id": "nzl", "name": "Neuseeland", "population": 5_000_000,
        "climate": "Climate.TEMPERATE", "wealth": "Wealth.RICH",
        "has_airport": True, "has_seaport": True,
        "seeds": [(1395, 810), (1365, 845)],
        "bounds": pygame.Rect(1340, 790, 80, 85),
        "neighbors": ["aus"],
    },
]


def generate_code():
    pygame.init()
    surf_src = pygame.image.load("world_map.jpg")
    bg_col = (255, 253, 241)

    # 1. Nachbarschaften bidirektional synchronisieren
    all_ids = {t["id"] for t in TERRITORIES_DATA}
    neighbors_map = {t["id"]: set(t["neighbors"]) for t in TERRITORIES_DATA}
    for cid, n_set in neighbors_map.items():
        for nid in list(n_set):
            assert nid in all_ids, f"Unbekannter Nachbar {nid} bei {cid}"
            neighbors_map[nid].add(cid)

    # 2. Polygone und Zentren extrahieren
    extracted_countries = []
    for t in TERRITORIES_DATA:
        cid = t["id"]
        name = t["name"]
        polys = extract_territory_polygons(surf_src, t["seeds"], bg_col, t["bounds"], eps=2.0)
        assert len(polys) >= 1, f"Kein Polygon extrahiert für {cid} ({name})"
        
        main_poly = max(polys, key=lambda p: len(p))
        capital = find_inside_point(main_poly)

        # Sortierte Nachbarn
        n_list = sorted(list(neighbors_map[cid]))

        extracted_countries.append({
            "id": cid,
            "name": name,
            "population": t["population"],
            "climate": t["climate"],
            "wealth": t["wealth"],
            "has_airport": t["has_airport"],
            "has_seaport": t["has_seaport"],
            "capital_pos": capital,
            "polygons": polys,
            "neighbors": n_list,
        })

    print(f"Erfolgreich extrahiert: {len(extracted_countries)} Länder")

    # 3. Code generieren
    lines = [
        '"""Geografische Vektordaten, Landesgrenzen und Routen für Py-Plaque-Inc.',
        'Automatisch generiert aus der Weltkartenvorlage world_map.jpg.',
        '"""',
        '',
        'from typing import List, Dict',
        'from py_plaque_inc.model.country import Country, Climate, Wealth',
        '',
        '',
        'def create_world_countries() -> Dict[str, Country]:',
        '    """',
        f'    Erstellt die Weltkarte mit {len(extracted_countries)} detaillierten Territorien,',
        '    die lückenlos anhand von world_map.jpg extrahiert wurden.',
        '    Die Koordinaten sind auf das Spielfenster (1280x720) ausgerichtet',
        '    (Kartenbereich X: 25..1255, Y: 68..635).',
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

    print("src/py_plaque_inc/map/geo_data.py erfolgreich geschrieben!")

if __name__ == "__main__":
    generate_code()
