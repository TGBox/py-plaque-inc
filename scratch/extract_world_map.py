"""Extrahiert, vereinfacht und generiert detaillierte Vektor-Polygone aus world_map.jpg."""

import math
import pygame
from typing import List, Tuple, Dict, Any


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
    """Ramer-Douglas-Peucker Algorithmus zur Polygon-Glättung."""
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
    """Findet einen Punkt, der garantiert im Inneren des Polygons liegt."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    cx = int(sum(xs) / len(xs))
    cy = int(sum(ys) / len(ys))
    if point_in_polygon(cx, cy, polygon):
        return cx, cy

    # Raster-Suche um den Schwerpunkt
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
    """Findet den dominanten, echten Farbpixel des Landes ohne Textüberlagerung."""
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


def extract_country_polygons(
    surf: pygame.Surface,
    seeds: List[Tuple[int, int]],
    bg_col: Tuple[int, int, int],
    eps: float = 2.4,
) -> List[List[Tuple[int, int]]]:
    w, h = surf.get_size()
    polygons: List[List[Tuple[int, int]]] = []

    for sx, sy in seeds:
        px, py, target_c = find_pure_color_seed(surf, sx, sy, bg_col)
        dist_bg = sum(abs(target_c[i] - bg_col[i]) for i in range(3))
        if dist_bg <= 35:
            continue

        raw = pygame.mask.from_threshold(surf, target_c, (22, 22, 22))
        closed = dilate_mask(raw, w, h, r=3)
        comps = closed.connected_components()

        matched_comp = None
        for comp in comps:
            if comp.get_at((px, py)) or comp.get_at((sx, sy)):
                matched_comp = comp
                break

        if not matched_comp and comps:
            # Nächstliegende Komponente
            for comp in comps:
                r = comp.get_bounding_rects()[0]
                if r.inflate(20, 20).collidepoint(sx, sy):
                    matched_comp = comp
                    break

        if matched_comp:
            pts = matched_comp.outline(every=2)
            if len(pts) >= 6:
                simple = rdp(pts, eps)
                # Auf Spielfeld projizieren (30..1250, 75..630)
                game_pts: List[Tuple[int, int]] = []
                for x_img, y_img in simple:
                    gx = int(round(30 + (x_img - 70) * (1210 / 1376)))
                    gy = int(round(75 + (y_img - 100) * (540 / 772)))
                    gx = max(25, min(1255, gx))
                    gy = max(68, min(635, gy))
                    game_pts.append((gx, gy))

                # Duplikate entfernen
                cleaned_pts: List[Tuple[int, int]] = []
                for pt in game_pts:
                    if not cleaned_pts or pt != cleaned_pts[-1]:
                        cleaned_pts.append(pt)
                if len(cleaned_pts) >= 2 and cleaned_pts[0] == cleaned_pts[-1]:
                    cleaned_pts.pop()

                if len(cleaned_pts) >= 4:
                    polygons.append(cleaned_pts)

    return polygons


if __name__ == "__main__":
    pygame.init()
    surf = pygame.image.load("world_map.jpg")
    bg_col = (255, 253, 241)

    print("Extraktionstool geladen. Bild:", surf.get_size())
