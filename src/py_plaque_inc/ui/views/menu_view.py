"""Hauptmenü: Pathogenauswahl, Schwierigkeitsgrad und Spielstart."""

from typing import Tuple, Optional
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_DNA,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    DIFFICULTIES,
)
from py_plaque_inc.model.pathogen import PathogenType, PATHOGEN_INFO
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button, TabButton


class MenuView:
    """Startbildschirm zur Konfiguration eines neuen Spiels."""

    def __init__(self, theme: UITheme):
        self.theme = theme

        # Ausgewählte Optionen
        self.pathogen_name: str = "Plaque-X"
        self.is_editing_name: bool = False
        self.selected_type: PathogenType = PathogenType.BACTERIA
        self.selected_diff: str = "Normal"

        # Buttons für Pathogentypen
        self.type_buttons = [
            TabButton(pygame.Rect(260, 240, 160, 44), "Bakterie", theme.font_header, "bacteria", is_active=True),
            TabButton(pygame.Rect(440, 240, 160, 44), "Virus", theme.font_header, "virus", is_active=False),
            TabButton(pygame.Rect(620, 240, 160, 44), "Pilz", theme.font_header, "fungus", is_active=False),
        ]

        # Buttons für Schwierigkeit
        self.diff_buttons = [
            TabButton(pygame.Rect(260, 440, 160, 38), "Leicht", theme.font_body_bold, "Leicht", is_active=False),
            TabButton(pygame.Rect(440, 440, 160, 38), "Normal", theme.font_body_bold, "Normal", is_active=True),
            TabButton(pygame.Rect(620, 440, 160, 38), "Schwer", theme.font_body_bold, "Schwer", is_active=False),
        ]

        # Buttons für Bildschirmmodus / Auflösung
        self.selected_res: str = "1280x720"
        self.on_change_resolution = None
        self.res_buttons = [
            TabButton(pygame.Rect(260, 638, 160, 30), "1280x720 (Fenster)", theme.font_tiny, "1280x720", is_active=True),
            TabButton(pygame.Rect(440, 638, 160, 30), "1920x1080 (Vollbild)", theme.font_tiny, "1920x1080", is_active=False),
            TabButton(pygame.Rect(620, 638, 160, 30), "2560x1080 (Ultrawide)", theme.font_tiny, "2560x1080", is_active=False),
        ]

        # Start-Button
        self.btn_start = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 140, 560, 280, 48),
            "SEUCHE FREISETZEN",
            theme.font_title,
            bg_color=(180, 35, 35),
            hover_color=(220, 50, 50),
            border_color=(255, 100, 100),
            border_radius=8,
        )

        self.name_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 140, 360, 42)

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, PathogenType, str, str]]:
        """
        Gibt (pathogen_name, pathogen_type, difficulty, resolution_mode) zurück,
        wenn das Spiel gestartet werden soll.
        """
        # Namens-Eingabefeld
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_editing_name = self.name_box_rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.is_editing_name:
            if event.key == pygame.K_RETURN:
                self.is_editing_name = False
            elif event.key == pygame.K_BACKSPACE:
                self.pathogen_name = self.pathogen_name[:-1]
            elif len(self.pathogen_name) < 18 and event.unicode.isprintable():
                self.pathogen_name += event.unicode

        # Pathogentyp-Auswahl
        for btn in self.type_buttons:
            tab = btn.handle_event(event)
            if tab:
                if tab == "bacteria":
                    self.selected_type = PathogenType.BACTERIA
                elif tab == "virus":
                    self.selected_type = PathogenType.VIRUS
                elif tab == "fungus":
                    self.selected_type = PathogenType.FUNGUS
                
                for b in self.type_buttons:
                    b.is_active = (b.tab_id == tab)

        # Schwierigkeit-Auswahl
        for btn in self.diff_buttons:
            diff = btn.handle_event(event)
            if diff:
                self.selected_diff = diff
                for b in self.diff_buttons:
                    b.is_active = (b.tab_id == diff)

        # Auflösung-Auswahl
        for btn in self.res_buttons:
            res = btn.handle_event(event)
            if res:
                self.selected_res = res
                for b in self.res_buttons:
                    b.is_active = (b.tab_id == res)
                if self.on_change_resolution:
                    self.on_change_resolution(res)

        # Start-Button
        if self.btn_start.handle_event(event):
            clean_name = self.pathogen_name.strip() or "Plaque-X"
            return clean_name, self.selected_type, self.selected_diff, self.selected_res

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet den Startbildschirm."""
        surface.fill(COLOR_BG)

        # Haupttitel mit Glow
        UITheme.draw_text(
            surface,
            "PY-PLAQUE-INC",
            self.theme.font_title,
            color=(230, 50, 50),
            pos=(SCREEN_WIDTH // 2, 40),
            align="center",
        )
        UITheme.draw_text(
            surface,
            "Globale Pandemie-Simulation • Erobere die Welt vor dem Heilmittel",
            self.theme.font_body,
            color=COLOR_TEXT_MUTED,
            pos=(SCREEN_WIDTH // 2, 75),
            align="center",
        )

        # 1. Namensfeld
        UITheme.draw_text(
            surface,
            "NAME DES ERREGERS (Klicke zum Bearbeiten):",
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(SCREEN_WIDTH // 2, 118),
            align="center",
        )
        box_border = (0, 180, 255) if self.is_editing_name else COLOR_PANEL_BORDER
        UITheme.draw_panel(surface, self.name_box_rect, bg_color=COLOR_PANEL_BG, border_color=box_border, border_radius=6)
        display_name = self.pathogen_name + ("|" if self.is_editing_name else "")
        UITheme.draw_text(
            surface,
            display_name,
            self.theme.font_header,
            color=(255, 255, 255),
            pos=self.name_box_rect.center,
            align="center",
        )

        # 2. Pathogentypen
        UITheme.draw_text(
            surface,
            "WÄHLE DEN PATHOGENTYP:",
            self.theme.font_body_bold,
            color=(255, 255, 255),
            pos=(SCREEN_WIDTH // 2, 215),
            align="center",
        )
        for btn in self.type_buttons:
            btn.draw(surface)

        # Typ-Beschreibungskarte
        type_info = PATHOGEN_INFO[self.selected_type]
        desc_rect = pygame.Rect(260, 295, 520, 85)
        UITheme.draw_panel(surface, desc_rect, bg_color=(20, 26, 38), border_color=(40, 55, 75), border_radius=6)
        UITheme.draw_text(surface, f"Eigenschaften: {type_info['name']}", self.theme.font_body_bold, color=COLOR_DNA, pos=(desc_rect.left + 14, desc_rect.top + 10))
        
        # Fließtext aufteilen
        words = type_info["description"].split(" ")
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 55:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        for i, l in enumerate(lines[:3]):
            UITheme.draw_text(surface, l, self.theme.font_small, color=COLOR_TEXT_PRIMARY, pos=(desc_rect.left + 14, desc_rect.top + 34 + i * 16))

        # 3. Schwierigkeitsgrad
        UITheme.draw_text(
            surface,
            "SCHWIERIGKEITSGRAD:",
            self.theme.font_body_bold,
            color=(255, 255, 255),
            pos=(SCREEN_WIDTH // 2, 415),
            align="center",
        )
        for btn in self.diff_buttons:
            btn.draw(surface)

        # Schwierigkeit-Beschreibung
        diff_info = DIFFICULTIES[self.selected_diff]
        diff_desc_rect = pygame.Rect(260, 488, 520, 52)
        UITheme.draw_panel(surface, diff_desc_rect, bg_color=(20, 26, 38), border_color=(40, 55, 75), border_radius=6)
        UITheme.draw_text(surface, diff_info["description"], self.theme.font_small, color=COLOR_TEXT_MUTED, pos=diff_desc_rect.center, align="center")

        # 4. Start Button
        self.btn_start.draw(surface)

        # 5. Bildschirmmodus & F11 Hinweis
        UITheme.draw_text(
            surface,
            "BILDSCHIRMMODUS (ODER F11 FÜR VOLLBILD):",
            self.theme.font_tiny,
            color=COLOR_TEXT_MUTED,
            pos=(SCREEN_WIDTH // 2, 622),
            align="center",
        )
        for btn in self.res_buttons:
            btn.draw(surface)
