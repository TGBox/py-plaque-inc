"""Detailansicht für die gesamte Erde (globale Statistik, Infrastruktur und Pandemiestatus)."""

from typing import Optional
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_DNA,
    COLOR_CURE,
)
from py_plaque_inc.model.world import World
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button
from py_plaque_inc.ui.hud import format_number


class WorldDetailView:
    """Zeigt weltweite aggregierte Informationen, globale Infektionszahlen und Infrastruktur."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT // 2 - 240, 540, 480)

        self.btn_close = Button(
            pygame.Rect(self.panel_rect.right - 96, self.panel_rect.bottom - 46, 80, 32),
            "SCHLIESSEN",
            theme.font_tiny,
            bg_color=(35, 45, 60),
            hover_color=(50, 65, 85),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gibt True zurück, wenn die Welt-Detailansicht geschlossen werden soll."""
        if self.btn_close.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.panel_rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, world: World) -> None:
        """Zeichnet das globale Infopanel zentriert über die Weltkarte."""
        # 1. Abdunkelungs-Layer im Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # 2. Panel-Hintergrund
        UITheme.draw_panel(
            surface,
            self.panel_rect,
            bg_color=(16, 22, 32),
            border_color=(40, 140, 220),
            border_radius=8,
            border_width=2,
        )

        # 3. Kopfzeile mit Planet Erde
        UITheme.draw_text(
            surface,
            "🌍 PLANET ERDE (GESAMTE WELT)",
            self.theme.font_title,
            color=(255, 255, 255),
            pos=(self.panel_rect.left + 24, self.panel_rect.top + 18),
        )

        sub_txt = f"Erreger: {world.pathogen.name} ({world.pathogen.pathogen_type.value})  •  Schwierigkeit: {world.difficulty_name}  •  Tag {world.current_day}"
        UITheme.draw_text(
            surface,
            sub_txt,
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(self.panel_rect.left + 24, self.panel_rect.top + 50),
        )

        # Trennlinie
        pygame.draw.line(
            surface,
            (35, 48, 65),
            (self.panel_rect.left + 24, self.panel_rect.top + 74),
            (self.panel_rect.right - 24, self.panel_rect.top + 74),
            1,
        )

        # 4. Globale Bevölkerung
        y = self.panel_rect.top + 86
        UITheme.draw_text(
            surface,
            "GLOBALE BEVÖLKERUNG:",
            self.theme.font_body_bold,
            color=COLOR_TEXT_PRIMARY,
            pos=(self.panel_rect.left + 24, y),
        )
        y += 24

        # Fortschrittsbalken für Gesamtinfektion und Tod
        bar_rect = pygame.Rect(self.panel_rect.left + 24, y, 492, 22)
        pygame.draw.rect(surface, (25, 35, 45), bar_rect, border_radius=4)

        pop = world.total_population
        if pop > 0:
            # Gesund (Grün)
            h_width = int(bar_rect.width * (world.total_healthy / pop))
            if h_width > 0:
                pygame.draw.rect(
                    surface,
                    (40, 160, 80),
                    (bar_rect.left, bar_rect.top, h_width, bar_rect.height),
                    border_radius=4,
                )

            # Infiziert (Rot)
            i_width = int(bar_rect.width * (world.total_infected / pop))
            if i_width > 0:
                pygame.draw.rect(
                    surface,
                    (220, 45, 45),
                    (bar_rect.left + h_width, bar_rect.top, i_width, bar_rect.height),
                )

            # Tot (Grau/Schwarz)
            d_width = int(bar_rect.width * (world.total_dead / pop))
            if d_width > 0:
                pygame.draw.rect(
                    surface,
                    (30, 25, 30),
                    (bar_rect.right - d_width, bar_rect.top, d_width, bar_rect.height),
                    border_radius=4,
                )

        pygame.draw.rect(surface, COLOR_PANEL_BORDER, bar_rect, width=1, border_radius=4)
        y += 30

        # Detaillierte Zähler mit Prozentangaben
        healthy_pct = (world.total_healthy / pop * 100) if pop > 0 else 0.0
        infected_pct = (world.total_infected / pop * 100) if pop > 0 else 0.0
        dead_pct = (world.total_dead / pop * 100) if pop > 0 else 0.0

        counts = [
            ("Gesamtbevölkerung:", format_number(world.total_population), (255, 255, 255)),
            ("Gesunde Menschen:", f"{format_number(world.total_healthy)} ({healthy_pct:.1f}%)", COLOR_SUCCESS),
            ("Infizierte Menschen:", f"{format_number(world.total_infected)} ({infected_pct:.1f}%)", COLOR_DANGER),
            ("Todesopfer weltweit:", f"{format_number(world.total_dead)} ({dead_pct:.1f}%)", (150, 160, 175)),
        ]

        for label, val_str, col in counts:
            UITheme.draw_text(surface, label, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
            UITheme.draw_text(surface, val_str, self.theme.font_body_bold, color=col, pos=(self.panel_rect.right - 24, y), align="right")
            y += 20

        # Trennlinie
        y += 4
        pygame.draw.line(surface, (35, 48, 65), (self.panel_rect.left + 24, y), (self.panel_rect.right - 24, y), 1)
        y += 10

        # 5. Pandemie-Status & Weltweite Infrastruktur
        UITheme.draw_text(
            surface,
            "WELTWEITER STATUS & INFRASTRUKTUR:",
            self.theme.font_body_bold,
            color=COLOR_TEXT_PRIMARY,
            pos=(self.panel_rect.left + 24, y),
        )
        y += 22

        total_countries = len(world.countries)
        inf_countries = world.infected_countries_count
        dead_countries = sum(
            1 for c in world.countries.values()
            if c.population > 0 and c.dead >= c.population
        )
        unaffected_countries = sum(
            1 for c in world.countries.values()
            if not c.is_infected and c.dead == 0
        )

        airports_open = sum(1 for c in world.countries.values() if c.airports_open and c.has_airport)
        airports_total = sum(1 for c in world.countries.values() if c.has_airport)

        seaports_open = sum(1 for c in world.countries.values() if c.seaports_open and c.has_seaport)
        seaports_total = sum(1 for c in world.countries.values() if c.has_seaport)

        borders_open = sum(1 for c in world.countries.values() if c.borders_open)

        cure_status = f"{world.cure_progress:.1f}% ({'Aktiv' if world.cure_active else 'Noch nicht begonnen'})"

        infra = [
            ("Infizierte Länder:", f"{inf_countries} von {total_countries} ({inf_countries / total_countries * 100:.1f}%)", COLOR_DANGER if inf_countries > 0 else COLOR_SUCCESS),
            ("Zerstörte Länder (100% tot):", f"{dead_countries} von {total_countries}", (160, 160, 160)),
            ("Unberührte Länder:", f"{unaffected_countries} von {total_countries}", COLOR_SUCCESS if unaffected_countries > 0 else COLOR_TEXT_MUTED),
            ("Flughäfen weltweit geöffnet:", f"{airports_open} von {airports_total}", COLOR_SUCCESS if airports_open > 0 else COLOR_DANGER),
            ("Seehäfen weltweit geöffnet:", f"{seaports_open} von {seaports_total}", COLOR_SUCCESS if seaports_open > 0 else COLOR_DANGER),
            ("Offene Landgrenzen:", f"{borders_open} von {total_countries}", COLOR_SUCCESS if borders_open > 0 else COLOR_DANGER),
            ("Heilmittelforschung:", cure_status, COLOR_CURE),
        ]

        for label, val_str, col in infra:
            UITheme.draw_text(surface, label, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
            UITheme.draw_text(surface, val_str, self.theme.font_body_bold, color=col, pos=(self.panel_rect.right - 24, y), align="right")
            y += 18

        # Schließen-Button zeichnen
        self.btn_close.draw(surface)
