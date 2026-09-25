"""Extrahiert alle 49 Territorien mit geografischen Bounding-Box-Einschränkungen."""

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

def find_pure_color_seed(surf: pygame.Surface, x: int, y: int, bg_col: Tuple[int, int, int], radius: int = 35) -> Tuple[int, int, Tuple[int, int, int]]:
    candidates: Dict[Tuple[int, int, int], int] = {}
    w, h = surf.get_size()
    for dy in range(-radius, radius + 1, 2):
        for dx in range(-radius, radius + 1, 2):
            px, py = x + dx, y + dy
            if 0 <= px < w and 0 <= py < h:
                c = surf.get_at((px, py))[:3]
                dist_bg = sum(abs(c[i] - bg_col[i]) for i in range(3))
                dist_white = sum(abs(c[i] - 255) for i in range(3))
                if dist_bg > 35 and dist_white > 45:
                    q = (c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)
                    candidates[q] = candidates.get(q, 0) + 1

    if candidates:
        best_col = max(candidates.items(), key=lambda item: item[1])[0]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                px, py = x + dx, y + dy
                if 0 <= px < w and 0 <= py < h:
                    c = surf.get_at((px, py))[:3]
                    q = (c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)
                    if q == best_col:
                        return px, py, c

    return x, y, surf.get_at((x, y))[:3]

def extract_territory_polygons(
    surf: pygame.Surface,
    seeds: List[Tuple[int, int]],
    bg_col: Tuple[int, int, int],
    bounds: pygame.Rect,
    eps: float = 2.4,
) -> List[List[Tuple[int, int]]]:
    w, h = surf.get_size()
    
    # 1. Maske nur innerhalb der Bounding-Box aufbauen
    territory_mask = pygame.Mask((w, h))
    for sx, sy in seeds:
        if not bounds.collidepoint(sx, sy):
            continue
        px, py, target_c = find_pure_color_seed(surf, sx, sy, bg_col)
        dist_bg = sum(abs(target_c[i] - bg_col[i]) for i in range(3))
        if dist_bg <= 35:
            continue

        raw = pygame.mask.from_threshold(surf, target_c, (22, 22, 22))
        # Maske strikt auf bounds beschränken
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
        if comp.count() < 120:
            continue
        pts = comp.outline(every=2)
        if len(pts) >= 6:
            simple = rdp(pts, eps)
            game_pts: List[Tuple[int, int]] = []
            for x_img, y_img in simple:
                gx = int(round(30 + (x_img - 70) * (1210 / 1376)))
                gy = int(round(75 + (y_img - 100) * (540 / 772)))
                gx = max(25, min(1255, gx))
                gy = max(68, min(635, gy))
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


TERRITORIES_DEF = [
    # Nordamerika
    ("can", "Kanada", [(320, 260), (410, 160), (350, 170)], pygame.Rect(180, 90, 420, 275)),
    ("usa", "USA", [(320, 390), (190, 220)], pygame.Rect(120, 150, 400, 320)),
    ("mex", "Mexiko", [(310, 490)], pygame.Rect(230, 440, 160, 110)),
    ("cen", "Zentralamerika", [(349, 524)], pygame.Rect(320, 490, 100, 80)),
    ("cub", "Karibik", [(415, 515)], pygame.Rect(390, 480, 90, 70)),
    ("gln", "Grönland", [(600, 200)], pygame.Rect(480, 80, 260, 260)),

    # Südamerika
    ("col", "Kolumbien", [(440, 570), (470, 560)], pygame.Rect(390, 530, 160, 90)),
    ("bra", "Brasilien", [(490, 620)], pygame.Rect(440, 560, 180, 200)),
    ("per", "Peru", [(415, 615)], pygame.Rect(380, 580, 90, 100)),
    ("bol", "Bolivien", [(470, 670), (490, 690)], pygame.Rect(430, 630, 90, 90)),
    ("chl", "Chile", [(455, 730)], pygame.Rect(430, 680, 50, 190)),
    ("arg", "Argentinien", [(480, 780), (510, 730)], pygame.Rect(450, 680, 100, 200)),

    # Europa
    ("isl", "Island", [(660, 240)], pygame.Rect(620, 200, 100, 80)),
    ("gbr", "Großbritannien", [(712, 350), (690, 360)], pygame.Rect(660, 310, 90, 100)),
    ("fra", "Frankreich", [(740, 388), (730, 360)], pygame.Rect(700, 350, 70, 70)),
    ("esp", "Spanien", [(710, 430), (690, 430)], pygame.Rect(660, 400, 85, 80)),
    ("deu", "Deutschland", [(788, 376)], pygame.Rect(750, 340, 70, 70)),
    ("ita", "Italien", [(785, 415), (790, 445), (760, 395)], pygame.Rect(750, 385, 70, 90)),
    ("ceu", "Zentraleuropa", [(795, 375), (810, 390)], pygame.Rect(775, 350, 70, 70)),
    ("pol", "Polen", [(834, 350)], pygame.Rect(800, 320, 70, 70)),
    ("sca", "Skandinavien", [(780, 280), (790, 310), (765, 335)], pygame.Rect(730, 210, 90, 140)),
    ("fin", "Finnland", [(840, 275), (825, 330)], pygame.Rect(805, 230, 70, 120)),
    ("ukr", "Ukraine", [(850, 345), (835, 330)], pygame.Rect(815, 315, 80, 80)),
    ("bal", "Balkan", [(825, 410), (840, 395), (820, 440)], pygame.Rect(795, 375, 80, 90)),

    # Russland & Zentralasien
    ("rus", "Russland", [(950, 250)], pygame.Rect(790, 130, 660, 250)),
    ("kaz", "Zentralasien", [(940, 370), (910, 400)], pygame.Rect(870, 320, 190, 100)),
    ("mon", "Mongolei", [(1100, 380)], pygame.Rect(1020, 340, 150, 90)),

    # Naher Osten
    ("tur", "Türkei", [(860, 395), (890, 390)], pygame.Rect(830, 365, 100, 70)),
    ("mde", "Naher Osten", [(885, 435), (865, 440)], pygame.Rect(850, 405, 70, 70)),
    ("sau", "Saudi-Arabien", [(900, 490), (910, 520)], pygame.Rect(850, 445, 110, 110)),
    ("irn", "Iran", [(940, 430)], pygame.Rect(900, 395, 80, 80)),

    # Afrika
    ("nab", "Nordafrika", [(695, 450), (740, 480)], pygame.Rect(660, 410, 120, 120)),
    ("egy", "Ägypten", [(810, 480), (770, 470)], pygame.Rect(760, 430, 110, 100)),
    ("waf", "Westafrika", [(700, 530), (720, 550), (725, 510)], pygame.Rect(650, 480, 110, 110)),
    ("caf", "Zentralafrika", [(760, 540), (770, 590), (745, 580)], pygame.Rect(730, 500, 100, 120)),
    ("eaf", "Ostafrika", [(810, 520), (840, 525), (860, 550)], pygame.Rect(790, 480, 110, 130)),
    ("saf", "Südafrika", [(820, 720), (780, 680), (810, 640)], pygame.Rect(740, 600, 140, 160)),
    ("mdg", "Madagaskar", [(920, 680)], pygame.Rect(880, 630, 70, 90)),

    # Asien
    ("pak", "Pakistan", [(980, 440), (960, 420)], pygame.Rect(940, 400, 70, 90)),
    ("ind", "Indien", [(1030, 520), (1070, 500)], pygame.Rect(970, 450, 110, 140)),
    ("chn", "China", [(1110, 440), (1210, 495)], pygame.Rect(1010, 370, 210, 150)),
    ("kor", "Korea", [(1190, 420)], pygame.Rect(1160, 395, 50, 60)),
    ("jpn", "Japan", [(1238, 398), (1260, 360)], pygame.Rect(1210, 350, 80, 130)),
    ("sea", "Südostasien", [(1120, 535), (1140, 590)], pygame.Rect(1070, 490, 100, 120)),
    ("phl", "Philippinen", [(1215, 545)], pygame.Rect(1190, 510, 60, 80)),
    ("idn", "Indonesien", [(1140, 625), (1175, 630), (1210, 620)], pygame.Rect(1100, 570, 170, 90)),
    ("png", "Papua-Neuguinea", [(1280, 625)], pygame.Rect(1250, 580, 90, 70)),

    # Ozeanien
    ("aus", "Australien", [(1230, 690), (1288, 815)], pygame.Rect(1150, 630, 190, 190)),
    ("nzl", "Neuseeland", [(1405, 805), (1365, 845)], pygame.Rect(1320, 770, 110, 110)),
]

if __name__ == "__main__":
    pygame.init()
    surf_src = pygame.image.load("world_map.jpg")
    bg_col = (255, 253, 241)

    preview_surf = pygame.Surface((1280, 720))
    preview_surf.fill((12, 16, 24))

    for x in range(30, 1260, 80):
        pygame.draw.line(preview_surf, (18, 26, 38), (x, 70), (x, 640), 1)
    for y in range(70, 640, 60):
        pygame.draw.line(preview_surf, (18, 26, 38), (30, y), (1260, y), 1)

    font = pygame.font.SysFont("Segoe UI, Arial", 10, bold=True)

    extracted_data = {}
    for cid, name, seeds, bounds in TERRITORIES_DEF:
        polys = extract_territory_polygons(surf_src, seeds, bg_col, bounds, eps=2.0)
        if polys:
            main_poly = max(polys, key=lambda p: len(p))
            capital = find_inside_point(main_poly)
            extracted_data[cid] = {
                "name": name,
                "polygons": polys,
                "capital": capital,
            }

            for p in polys:
                pygame.draw.polygon(preview_surf, (38, 52, 68), p)
                pygame.draw.lines(preview_surf, (65, 88, 115), True, p, 1)

            cx, cy = capital
            pygame.draw.circle(preview_surf, (255, 180, 50), (cx, cy), 3)
            lbl = font.render(name, True, (220, 230, 240))
            preview_surf.blit(lbl, (cx + 5, cy - 6))

    pygame.image.save(preview_surf, "scratch/preview_map.png")
    print(f"Bounded-Extraction fertig: {len(extracted_data)} / {len(TERRITORIES_DEF)} Länder. Gespeichert in scratch/preview_map.png")
