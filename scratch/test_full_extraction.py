"""Vollständige Extraktion aller 49 Territorien mit vollständigen Seeds für alle Länder."""

from typing import Optional
import math
import pygame
from typing import List, Tuple, Dict

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
        if comp.count() < 90:
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
    # --- NORDAMERIKA ---
    ("can", "Kanada", [
        (320, 260), (360, 160), (420, 150), (460, 220), (470, 290)
    ], pygame.Rect(160, 80, 380, 290)),

    ("usa", "USA", [
        (300, 380), (380, 440), (180, 210)
    ], pygame.Rect(30, 120, 460, 370)),

    ("mex", "Mexiko", [
        (300, 480), (265, 450)
    ], pygame.Rect(220, 420, 150, 120)),

    ("cen", "Zentralamerika", [
        (340, 520), (370, 535)
    ], pygame.Rect(320, 500, 80, 70)),

    ("cub", "Karibik", [
        (375, 490), (415, 510), (440, 520)
    ], pygame.Rect(360, 475, 100, 60)),

    ("gln", "Grönland", [
        (600, 200)
    ], pygame.Rect(500, 80, 160, 230)),

    # --- SÜDAMERIKA ---
    ("col", "Kolumbien", [
        (430, 565), (470, 550), (510, 560), (530, 560), (415, 595)
    ], pygame.Rect(390, 525, 170, 100)),

    ("bra", "Brasilien", [
        (520, 640), (560, 620), (470, 600)
    ], pygame.Rect(430, 560, 180, 180)),

    ("per", "Peru", [
        (430, 640)
    ], pygame.Rect(405, 590, 65, 100)),

    ("bol", "Bolivien", [
        (465, 665), (495, 690)
    ], pygame.Rect(440, 640, 85, 90)),

    ("chl", "Chile", [
        (445, 750), (455, 830)
    ], pygame.Rect(425, 680, 50, 190)),

    ("arg", "Argentinien", [
        (475, 760), (460, 810), (505, 745), (495, 855)
    ], pygame.Rect(445, 695, 90, 180)),

    # --- EUROPA ---
    ("isl", "Island", [
        (665, 305)
    ], pygame.Rect(645, 290, 45, 35)),

    ("gbr", "Großbritannien", [
        (715, 350), (700, 365), (705, 320)
    ], pygame.Rect(670, 290, 65, 90)),

    ("fra", "Frankreich", [
        (725, 375), (735, 350)
    ], pygame.Rect(700, 340, 60, 65)),

    ("esp", "Spanien", [
        (705, 420), (675, 420)
    ], pygame.Rect(660, 395, 75, 60)),

    ("deu", "Deutschland", [
        (755, 345), (745, 375), (765, 375)
    ], pygame.Rect(735, 325, 55, 65)),

    ("ita", "Italien", [
        (765, 405), (775, 440), (745, 425)
    ], pygame.Rect(735, 385, 55, 75)),

    ("pol", "Polen", [
        (795, 340), (780, 360), (790, 380)
    ], pygame.Rect(765, 325, 60, 70)),

    ("bal", "Balkan", [
        (785, 405), (815, 385), (825, 410), (815, 435), (825, 450)
    ], pygame.Rect(775, 375, 70, 90)),

    ("sca", "Skandinavien", [
        (790, 220), (775, 270), (765, 315), (748, 325)
    ], pygame.Rect(720, 195, 90, 140)),

    ("fin", "Finnland", [
        (815, 255), (815, 305), (815, 325)
    ], pygame.Rect(795, 205, 60, 130)),


    ("ukr", "Ukraine", [
        (840, 350), (825, 335), (830, 375)
    ], pygame.Rect(805, 320, 75, 65)),

    # --- RUSSLAND & NORDASIEN ---
    ("rus", "Russland", [
        (880, 280), (840, 280), (910, 240), (980, 240), (1050, 240),
        (1150, 230), (1240, 230), (1310, 250), (1320, 290), (1275, 330)
    ], pygame.Rect(820, 130, 540, 235)),

    ("kaz", "Zentralasien", [
        (915, 335), (965, 335), (910, 380), (905, 400), (960, 380), (960, 400)
    ], pygame.Rect(870, 310, 130, 105)),

    ("mon", "Mongolei", [
        (1100, 345)
    ], pygame.Rect(1030, 325, 120, 50)),

    # --- NAHER OSTEN ---
    ("tur", "Türkei", [
        (835, 395), (865, 395), (890, 385), (900, 395)
    ], pygame.Rect(815, 375, 100, 45)),

    ("mde", "Naher Osten", [
        (855, 430), (865, 420), (885, 425)
    ], pygame.Rect(845, 410, 65, 45)),

    ("sau", "Saudi-Arabien", [
        (885, 465), (900, 490), (925, 515), (940, 500), (930, 475)
    ], pygame.Rect(865, 440, 100, 95)),

    ("irn", "Iran", [
        (925, 425), (965, 415)
    ], pygame.Rect(895, 395, 95, 65)),

    # --- AFRIKA ---
    ("nab", "Nordafrika", [
        (675, 440), (710, 460), (755, 425)
    ], pygame.Rect(650, 410, 125, 75)),

    ("egy", "Ägypten", [
        (775, 460), (825, 460)
    ], pygame.Rect(745, 425, 105, 70)),

    ("sud", "Sudan", [
        (835, 505), (825, 550)
    ], pygame.Rect(800, 485, 65, 80)),

    ("waf", "Westafrika", [
        (670, 490), (705, 500), (660, 520), (705, 545), (715, 530), (750, 540), (745, 495)
    ], pygame.Rect(640, 465, 130, 100)),

    ("caf", "Zentralafrika", [
        (775, 510), (765, 550), (790, 545), (745, 580), (760, 590), (785, 595), (800, 620)
    ], pygame.Rect(735, 485, 95, 160)),

    ("eaf", "Ostafrika", [
        (865, 525), (890, 525), (885, 545), (850, 585), (825, 580), (840, 625)
    ], pygame.Rect(815, 495, 100, 150)),

    ("zaf", "Südafrika", [
        (765, 645), (800, 655), (845, 665), (835, 705), (815, 680),
        (765, 705), (795, 700), (795, 755), (810, 740), (825, 745)
    ], pygame.Rect(740, 625, 125, 160)),

    ("mdg", "Madagaskar", [
        (895, 685)
    ], pygame.Rect(875, 650, 50, 85)),

    # --- ASIEN ---
    ("pak", "Pakistan", [
        (980, 425)
    ], pygame.Rect(960, 400, 50, 65)),

    ("ind", "Indien", [
        (1015, 455), (1030, 495), (1035, 540), (1075, 480), (1040, 575), (1050, 455), (1075, 455)
    ], pygame.Rect(990, 435, 100, 155)),

    ("chn", "China", [
        (1170, 450), (1160, 400), (1020, 390), (1030, 430), (1080, 430), (1215, 495), (1150, 525)
    ], pygame.Rect(990, 360, 240, 175)),

    ("kor", "Korea", [
        (1205, 400), (1210, 420)
    ], pygame.Rect(1185, 385, 40, 55)),

    ("jpn", "Japan", [
        (1255, 400), (1270, 360), (1235, 425)
    ], pygame.Rect(1220, 345, 70, 110)),

    ("sea", "Südostasien", [
        (1095, 490), (1115, 520), (1130, 500), (1140, 545), (1130, 585), (1190, 595)
    ], pygame.Rect(1075, 465, 135, 145)),

    ("phl", "Philippinen", [
        (1215, 530), (1230, 575)
    ], pygame.Rect(1200, 515, 50, 80)),

    ("idn", "Indonesien", [
        (1135, 605), (1170, 635), (1185, 615), (1230, 620), (1250, 635)
    ], pygame.Rect(1110, 580, 160, 80)),

    ("png", "Papua-Neuguinea", [
        (1300, 630)
    ], pygame.Rect(1260, 600, 80, 55)),

    # --- OZEANIEN ---
    ("aus", "Australien", [
        (1230, 710), (1180, 720), (1280, 710), (1270, 790), (1275, 830)
    ], pygame.Rect(1140, 650, 180, 200)),

    ("nzl", "Neuseeland", [
        (1395, 810), (1365, 845)
    ], pygame.Rect(1340, 790, 80, 85)),
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
    total_polys = 0
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
            total_polys += len(polys)

            for p in polys:
                pygame.draw.polygon(preview_surf, (38, 52, 68), p)
                pygame.draw.lines(preview_surf, (65, 88, 115), True, p, 1)

            cx, cy = capital
            pygame.draw.circle(preview_surf, (255, 180, 50), (cx, cy), 3)
            lbl = font.render(name, True, (220, 230, 240))
            preview_surf.blit(lbl, (cx + 5, cy - 6))

    pygame.image.save(preview_surf, "scratch/preview_full.png")
    print(f"Fertig: {len(extracted_data)} / {len(TERRITORIES_DEF)} Territorien, {total_polys} Polygone. Gespeichert in scratch/preview_full.png")
