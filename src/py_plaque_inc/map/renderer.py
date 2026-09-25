"""Weltkarten-Renderer mit Polygon-Darstellung, Infektions-Shading und Routen."""

import math
import os
from typing import Dict, List, Optional, Tuple
import pygame

from py_plaque_inc.config import (
    COLOR_BG,
    COLOR_OCEAN_DEEP,
    COLOR_COUNTRY_LAND,
    COLOR_COUNTRY_OUTLINE,
    COLOR_COUNTRY_HOVER,
    COLOR_COUNTRY_SELECTED,
    COLOR_INFECTED_MIN,
    COLOR_DEAD,
    COLOR_CURE,
)
from py_plaque_inc.model.country import Country
from py_plaque_inc.model.transport import TransportManager, TransportType


def point_in_polygon(x: int, y: int, polygon: List[Tuple[int, int]]) -> bool:
    """Ray-Casting Algorithmus zur Bestimmung, ob ein Punkt im Polygon liegt."""
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


def blend_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """Mischt zwei Farben linear mit Faktor t (0.0 bis 1.0)."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


class MapRenderer:
    """Zeichnet die Vektor-Weltkarte, Infektionsstufen und Verkehrsrouten."""

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.hovered_country_id: Optional[str] = None
        self.selected_country_id: Optional[str] = None
        self.pulse_timer: float = 0.0

        # Weltkarten-Hintergrundbild laden (falls vorhanden)
        self.map_surface: Optional[pygame.Surface] = None
        self._overlay_surface: Optional[pygame.Surface] = None
        try:
            asset_path = os.path.join(os.path.dirname(__file__), "..", "assets", "world_map_dark.png")
            if os.path.exists(asset_path):
                raw = pygame.image.load(asset_path)
                self.map_surface = pygame.transform.smoothscale(raw, (self.rect.width, self.rect.height))
                self._overlay_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        except Exception:
            self.map_surface = None
            self._overlay_surface = None

        # Cache für die nach Fläche sortierte Treffreihenfolge.
        # Kleinere Länder werden zuerst getestet und gewinnen bei Überlappung.
        self._hit_order_cache: Optional[List[str]] = None
        self._hit_order_key: int = -1
        self._hit_order_key: int = -1

    def _build_hit_order(self, countries: Dict[str, Country]) -> List[str]:
        """Sortiert Länder-IDs aufsteigend nach Polygongesamtfläche (Shoelace).
        Kleinere / spezifischere Regionen werden zuerst geprüft und gewinnen
        bei Überschneidungen mit ausgebluteten Groß-Polygonen (z. B. Russland).
        """
        def total_area(c: Country) -> float:
            area = 0.0
            for poly in c.polygons:
                n = len(poly)
                a = 0.0
                for i in range(n):
                    j = (i + 1) % n
                    a += poly[i][0] * poly[j][1]
                    a -= poly[j][0] * poly[i][1]
                area += abs(a) * 0.5
            return area

        return sorted(countries.keys(), key=lambda cid: total_area(countries[cid]))

    def handle_mouse_motion(self, pos: Tuple[int, int], countries: Dict[str, Country]) -> Optional[str]:
        """Prüft, über welchem Land sich der Mauszeiger befindet.
        Kleinere Länder haben Vorrang bei Überschneidungen mit größeren Polygonen.
        """
        mx, my = pos
        if not self.rect.collidepoint(mx, my):
            self.hovered_country_id = None
            return None

        # Sortierte Treffreihenfolge einmalig berechnen und cachen.
        dict_key = id(countries)
        if self._hit_order_cache is None or self._hit_order_key != dict_key:
            self._hit_order_cache = self._build_hit_order(countries)
            self._hit_order_key = dict_key

        for c_id in self._hit_order_cache:
            country = countries[c_id]
            for poly in country.polygons:
                if point_in_polygon(mx, my, poly):
                    self.hovered_country_id = c_id
                    return c_id

        self.hovered_country_id = None
        return None

    def get_country_at_pos(self, pos: Tuple[int, int], countries: Dict[str, Country]) -> Optional[Country]:
        """Gibt das Land an der Klickposition zurück."""
        c_id = self.handle_mouse_motion(pos, countries)
        if c_id and c_id in countries:
            return countries[c_id]
        return None

    def update(self, dt: float) -> None:
        self.pulse_timer += dt * 3.0

    def draw(
        self,
        surface: pygame.Surface,
        countries: Dict[str, Country],
        transport_mgr: TransportManager,
        font: pygame.font.Font,
    ) -> None:
        """Rendert die gesamte Weltkarte inklusive aller Schichten."""
        # 1. Ozean- / Karten-Hintergrund
        if self.map_surface:
            surface.blit(self.map_surface, self.rect.topleft)
            self._draw_grid_lines(surface)
        else:
            pygame.draw.rect(surface, COLOR_OCEAN_DEEP, self.rect)
            self._draw_grid_lines(surface)
            # Im Fallback-Modus ohne Kartenbild alle Länder als Basis zeichnen
            for c_id, country in countries.items():
                for poly in country.polygons:
                    if len(poly) >= 3:
                        pygame.draw.polygon(surface, COLOR_COUNTRY_LAND, poly)
                        pygame.draw.polygon(surface, COLOR_COUNTRY_OUTLINE, poly, 1)

        # Falls die gesamte Welt ausgewählt ist: Ozean-Rahmen & Badge
        if self.selected_country_id == "world":
            pygame.draw.rect(surface, (40, 140, 220), self.rect, width=2)
            badge_surf = font.render("AUSWAHL: PLANET ERDE (GESAMTE WELT)", True, (200, 230, 255))
            badge_rect = badge_surf.get_rect(topleft=(self.rect.left + 16, self.rect.top + 12))
            bg_rect = badge_rect.inflate(14, 8)
            pygame.draw.rect(surface, (14, 22, 34, 230), bg_rect, border_radius=4)
            pygame.draw.rect(surface, (40, 140, 220), bg_rect, width=1, border_radius=4)
            surface.blit(badge_surf, badge_rect)

        # 2. Länder-Overlays (Infektion, Tod, Hover, Selektion)
        if self._overlay_surface:
            self._overlay_surface.fill((0, 0, 0, 0))
            rx, ry = self.rect.left, self.rect.top
            for c_id, country in countries.items():
                is_hovered = (c_id == self.hovered_country_id)
                is_selected = (c_id == self.selected_country_id)
                self._draw_country_overlay(country, is_hovered, is_selected, rx, ry)
            surface.blit(self._overlay_surface, self.rect.topleft)
        else:
            for c_id, country in countries.items():
                is_hovered = (c_id == self.hovered_country_id)
                is_selected = (c_id == self.selected_country_id)
                self._draw_country_legacy(surface, country, is_hovered, is_selected)

        # 3. Hauptstädte / Zentroid-Punkte
        for c_id, country in countries.items():
            cx, cy = country.capital_pos
            inf_ratio = country.infection_ratio
            dead_ratio = country.dead_ratio
            cap_color = (180, 200, 220)
            if inf_ratio > 0:
                cap_color = (255, 100, 100)
            if dead_ratio > 0.5:
                cap_color = (90, 80, 85)
            pygame.draw.circle(surface, cap_color, (cx, cy), 2)

        # 4. Flug- und Schiffsrouten
        self._draw_transports(surface, transport_mgr)

        # 5. Länder-Namen dezent einblenden (bei Hover oder Infektion)
        if self.hovered_country_id and self.hovered_country_id in countries:
            h_country = countries[self.hovered_country_id]
            cx, cy = h_country.capital_pos
            # Tooltip-Badge
            name_text = f"{h_country.name} ({h_country.infection_ratio * 100:.1f}%)"
            txt_surf = font.render(name_text, True, (255, 255, 255))
            badge_rect = txt_surf.get_rect(center=(cx, cy - 14))
            bg_rect = badge_rect.inflate(12, 6)
            pygame.draw.rect(surface, (15, 20, 30, 220), bg_rect, border_radius=4)
            pygame.draw.rect(surface, (80, 110, 140), bg_rect, width=1, border_radius=4)
            surface.blit(txt_surf, badge_rect)

    def _draw_grid_lines(self, surface: pygame.Surface) -> None:
        """Zeichnet ein elegantes Längen- und Breitengrad-Netz."""
        grid_color = (18, 26, 38)
        # Horizontale Linien (Breitengrade)
        for y in range(self.rect.top + 50, self.rect.bottom, 70):
            pygame.draw.line(surface, grid_color, (self.rect.left, y), (self.rect.right, y), 1)
        # Vertikale Linien (Längengrade)
        for x in range(self.rect.left + 80, self.rect.right, 100):
            pygame.draw.line(surface, grid_color, (x, self.rect.top), (x, self.rect.bottom), 1)

    def _draw_country_overlay(
        self,
        country: Country,
        is_hovered: bool,
        is_selected: bool,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Rendert transparente Infektions-, Todes-, Hover- und Selektionsschichten auf dem Overlay."""
        inf_ratio = country.infection_ratio
        dead_ratio = country.dead_ratio
        has_pulse = country.infected_pulse > 0

        # Nichts zu zeichnen wenn kein Status aktiv
        if not (inf_ratio > 0 or dead_ratio > 0 or is_hovered or is_selected or has_pulse):
            return

        for poly in country.polygons:
            if len(poly) < 3:
                continue
            # Koordinaten relativ zum Overlay-Surface (rect.topleft)
            rel_poly = [(px - offset_x, py - offset_y) for px, py in poly]

            # 1. Infektions-Rot-Tönung
            if inf_ratio > 0:
                alpha_inf = int(170 * min(1.0, inf_ratio * 1.25))
                pygame.draw.polygon(self._overlay_surface, (225, 28, 28, alpha_inf), rel_poly)

            # 2. Toter Asche-Filter
            if dead_ratio > 0:
                alpha_dead = int(210 * min(1.0, dead_ratio * 1.2))
                pygame.draw.polygon(self._overlay_surface, (15, 18, 24, alpha_dead), rel_poly)

            # 3. Hover-Hervorhebung
            if is_hovered:
                pygame.draw.polygon(self._overlay_surface, (100, 180, 255, 65), rel_poly)
                pygame.draw.polygon(self._overlay_surface, (160, 215, 255, 240), rel_poly, 2)

            # 4. Selektions-Rahmen
            if is_selected:
                pygame.draw.polygon(self._overlay_surface, (0, 220, 255, 80), rel_poly)
                pygame.draw.polygon(self._overlay_surface, (0, 240, 255, 255), rel_poly, 2)

            # 5. Pulsieren bei Neuinfektion
            if has_pulse and not is_selected:
                pulse_alpha = int((math.sin(self.pulse_timer * 4.0) * 0.5 + 0.5) * 220)
                pygame.draw.polygon(self._overlay_surface, (255, 60, 60, pulse_alpha), rel_poly, 2)

    def _draw_country_legacy(
        self,
        surface: pygame.Surface,
        country: Country,
        is_hovered: bool,
        is_selected: bool,
    ) -> None:
        """Fallback-Zeichnung ohne Bildressource."""
        inf_ratio = country.infection_ratio
        dead_ratio = country.dead_ratio

        base_color = COLOR_COUNTRY_LAND
        if inf_ratio > 0:
            base_color = blend_color(COLOR_COUNTRY_LAND, COLOR_INFECTED_MIN, min(1.0, inf_ratio * 1.3))
        if dead_ratio > 0:
            base_color = blend_color(base_color, COLOR_DEAD, min(1.0, dead_ratio * 1.2))
        if is_hovered:
            base_color = blend_color(base_color, COLOR_COUNTRY_HOVER, 0.45)

        outline_color = COLOR_COUNTRY_OUTLINE
        outline_width = 1
        if is_selected:
            outline_color = COLOR_COUNTRY_SELECTED
            outline_width = 2
        elif is_hovered:
            outline_color = (160, 190, 220)
            outline_width = 2
        elif country.infected_pulse > 0:
            pulse_alpha = math.sin(self.pulse_timer * 4.0) * 0.5 + 0.5
            outline_color = blend_color(COLOR_COUNTRY_OUTLINE, (255, 60, 60), pulse_alpha)
            outline_width = 2

        for poly in country.polygons:
            if len(poly) >= 3:
                pygame.draw.polygon(surface, base_color, poly)
                pygame.draw.polygon(surface, outline_color, poly, outline_width)

        # Hauptstadt / Zentroid als kleiner Punkt
        cx, cy = country.capital_pos
        cap_color = (180, 200, 220)
        if inf_ratio > 0:
            cap_color = (255, 100, 100)
        if dead_ratio > 0.5:
            cap_color = (90, 80, 85)
        pygame.draw.circle(surface, cap_color, (cx, cy), 2)

    def _draw_transports(self, surface: pygame.Surface, transport_mgr: TransportManager) -> None:
        """Zeichnet Flugzeuge, Schiffe und deren Flugpfade."""
        for route in transport_mgr.active_transports:
            # Pfad dezent andeuten
            x0, y0 = route.start_pos
            x1, y1 = route.current_pos
            x2, y2 = route.end_pos
            
            # Farbe je nach Status
            if route.transport_type == TransportType.CURE_PLANE:
                veh_color = COLOR_CURE
                line_color = (0, 120, 180, 80)
            elif route.is_infected:
                veh_color = (255, 60, 60)
                line_color = (180, 30, 30, 80)
            else:
                veh_color = (200, 220, 240)
                line_color = (70, 90, 120, 60)

            # Fahrzeug zeichnen
            if route.transport_type in (TransportType.AIRPLANE, TransportType.CURE_PLANE):
                # Dreieckiges Flugzeug-Symbol
                rad = math.radians(route.angle_degrees)
                size = 6
                # Nase
                p_nose = (x1 + math.cos(rad) * size, y1 + math.sin(rad) * size)
                # Flügel
                p_left = (x1 + math.cos(rad + 2.5) * (size * 0.8), y1 + math.sin(rad + 2.5) * (size * 0.8))
                p_right = (x1 + math.cos(rad - 2.5) * (size * 0.8), y1 + math.sin(rad - 2.5) * (size * 0.8))
                pygame.draw.polygon(surface, veh_color, [p_nose, p_left, p_right])
            else:
                # Schiffs-Symbol (kleines Quadrat / Raute)
                pygame.draw.circle(surface, veh_color, (x1, y1), 3)
