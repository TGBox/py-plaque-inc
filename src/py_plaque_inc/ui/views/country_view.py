"""Detailansicht für das aktuell ausgewählte Land."""

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
)
from py_plaque_inc.model.country import Country
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button, ProgressBar
from py_plaque_inc.ui.hud import format_number


class CountryDetailView:
    """Zeigt vertiefte Informationen, Infektionszahlen und Infrastruktur eines Landes."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 220, 500, 440)
        
        self.btn_close = Button(
            pygame.Rect(self.panel_rect.right - 90, self.panel_rect.bottom - 46, 74, 32),
            "SCHLIESSEN",
            theme.font_tiny,
            bg_color=(35, 45, 60),
            hover_color=(50, 65, 85),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gibt True zurück, wenn die Detailansicht geschlossen werden soll."""
        if self.btn_close.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.panel_rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, country: Country) -> None:
        """Zeichnet das Infopanel zentriert über die Weltkarte."""
        # Abdunkelungs-Layer im Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Panel-Hintergrund
        UITheme.draw_panel(surface, self.panel_rect, bg_color=(16, 22, 32), border_color=(50, 70, 95), border_radius=8)

        # Kopfzeile mit Landesname
        UITheme.draw_text(
            surface,
            f"🌍 {country.name.upper()}",
            self.theme.font_title,
            color=(255, 255, 255),
            pos=(self.panel_rect.left + 24, self.panel_rect.top + 20),
        )

        sub_txt = f"Klima: {country.climate.value}  •  Wohlstand: {country.wealth.value}"
        UITheme.draw_text(
            surface,
            sub_txt,
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(self.panel_rect.left + 24, self.panel_rect.top + 55),
        )

        # Trennlinie
        pygame.draw.line(
            surface,
            (35, 48, 65),
            (self.panel_rect.left + 24, self.panel_rect.top + 80),
            (self.panel_rect.right - 24, self.panel_rect.top + 80),
            1,
        )

        # Bevölkerungs-Zahlen
        y = self.panel_rect.top + 95
        UITheme.draw_text(surface, "BEVÖLKERUNGSSTATUS:", self.theme.font_body_bold, color=COLOR_TEXT_PRIMARY, pos=(self.panel_rect.left + 24, y))
        y += 26

        # Fortschrittsbalken für Infektion und Tod
        bar_rect = pygame.Rect(self.panel_rect.left + 24, y, 452, 22)
        pygame.draw.rect(surface, (25, 35, 45), bar_rect, border_radius=4)
        
        # Gesund (Grün)
        h_width = int(bar_rect.width * (country.healthy / country.population if country.population > 0 else 0))
        if h_width > 0:
            pygame.draw.rect(surface, (40, 160, 80), (bar_rect.left, bar_rect.top, h_width, bar_rect.height), border_radius=4)

        # Infiziert (Rot)
        i_width = int(bar_rect.width * (country.infected / country.population if country.population > 0 else 0))
        if i_width > 0:
            pygame.draw.rect(surface, (220, 45, 45), (bar_rect.left + h_width, bar_rect.top, i_width, bar_rect.height))

        # Tot (Grau/Schwarz)
        d_width = int(bar_rect.width * (country.dead / country.population if country.population > 0 else 0))
        if d_width > 0:
            pygame.draw.rect(surface, (30, 25, 30), (bar_rect.right - d_width, bar_rect.top, d_width, bar_rect.height), border_radius=4)

        pygame.draw.rect(surface, COLOR_PANEL_BORDER, bar_rect, width=1, border_radius=4)
        y += 32

        # Detaillierte Zähler
        counts = [
            ("Gesamtbevölkerung:", format_number(country.population), (255, 255, 255)),
            ("Gesunde Bürger:", f"{format_number(country.healthy)} ({country.healthy / country.population * 100:.1f}%)", COLOR_SUCCESS),
            ("Infizierte:", f"{format_number(country.infected)} ({country.infection_ratio * 100:.1f}%)", COLOR_DANGER),
            ("Todesopfer:", f"{format_number(country.dead)} ({country.dead_ratio * 100:.1f}%)", (150, 160, 175)),
        ]

        for label, val_str, col in counts:
            UITheme.draw_text(surface, label, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
            UITheme.draw_text(surface, val_str, self.theme.font_body_bold, color=col, pos=(self.panel_rect.right - 24, y), align="right")
            y += 22

        # Trennlinie
        y += 6
        pygame.draw.line(surface, (35, 48, 65), (self.panel_rect.left + 24, y), (self.panel_rect.right - 24, y), 1)
        y += 12

        # Infrastruktur & Grenzen
        UITheme.draw_text(surface, "INFRASTRUKTUR & MAßNAHMEN:", self.theme.font_body_bold, color=COLOR_TEXT_PRIMARY, pos=(self.panel_rect.left + 24, y))
        y += 24

        def status_str(is_open: bool, exists: bool) -> tuple[str, tuple[int, int, int]]:
            if not exists:
                return "Nicht vorhanden", COLOR_TEXT_MUTED
            return ("OFFEN", COLOR_SUCCESS) if is_open else ("GESCHLOSSEN", COLOR_DANGER)

        border_status, border_col = ("OFFEN", COLOR_SUCCESS) if country.borders_open else ("GESCHLOSSEN", COLOR_DANGER)

        infra = [
            ("Internationaler Flughafen:", *status_str(country.airports_open, country.has_airport)),
            ("Übersee-Hafen:", *status_str(country.seaports_open, country.has_seaport)),
            ("Landgrenzen:", border_status, border_col),
            ("Forschungsbeitrag Heilmittel:", f"{country.cure_effort:.2f} Einheiten/Tag", (0, 190, 255)),
        ]

        for label, val_str, col in infra:
            UITheme.draw_text(surface, label, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
            UITheme.draw_text(surface, val_str, self.theme.font_body_bold, color=col, pos=(self.panel_rect.right - 24, y), align="right")
            y += 20

        # Schließen-Button
        self.btn_close.draw(surface)
