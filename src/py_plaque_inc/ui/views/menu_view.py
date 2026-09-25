"""Hauptmenü: Dynamisches, responsives Dashboard für Widescreen, Vollbild und Ultrawide."""

from typing import Tuple, Optional, List
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_DNA,
    COLOR_DNA_GLOW,
    COLOR_CURE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    DIFFICULTIES,
)
from py_plaque_inc.model.pathogen import PathogenType, PATHOGEN_INFO
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button, TabButton


class MenuView:
    """Startbildschirm mit responsiver Anordnung für alle Fenster- und Bildschirmauflösungen."""

    def __init__(self, theme: UITheme):
        self.theme = theme

        # Fenstermaße
        self.width: int = SCREEN_WIDTH
        self.height: int = SCREEN_HEIGHT

        # Ausgewählte Optionen
        self.pathogen_name: str = "Plaque-X"
        self.is_editing_name: bool = False
        self.selected_type: PathogenType = PathogenType.BACTERIA
        self.selected_diff: str = "Normal"
        self.selected_res: str = "1280x720"
        self.on_change_resolution = None

        # Komponenten instanziieren
        dummy_rect = pygame.Rect(0, 0, 10, 10)
        self.type_buttons: List[TabButton] = [
            TabButton(dummy_rect, "Bakterie", theme.font_header, "bacteria", is_active=True),
            TabButton(dummy_rect, "Virus", theme.font_header, "virus", is_active=False),
            TabButton(dummy_rect, "Pilz", theme.font_header, "fungus", is_active=False),
        ]

        self.diff_buttons: List[TabButton] = [
            TabButton(dummy_rect, "Leicht", theme.font_body_bold, "Leicht", is_active=False),
            TabButton(dummy_rect, "Normal", theme.font_body_bold, "Normal", is_active=True),
            TabButton(dummy_rect, "Schwer", theme.font_body_bold, "Schwer", is_active=False),
        ]

        self.res_buttons: List[TabButton] = [
            TabButton(dummy_rect, "1280x720 (Fenster)", theme.font_tiny, "1280x720", is_active=True),
            TabButton(dummy_rect, "1920x1080 (Vollbild)", theme.font_tiny, "1920x1080", is_active=False),
            TabButton(dummy_rect, "2560x1080 (Ultrawide)", theme.font_tiny, "2560x1080", is_active=False),
        ]

        self.btn_start = Button(
            dummy_rect,
            "SEUCHE FREISETZEN",
            theme.font_header,
            bg_color=(180, 32, 32),
            hover_color=(225, 45, 45),
            border_color=(255, 100, 100),
            border_radius=8,
        )
        self.btn_quit = Button(
            dummy_rect,
            "BEENDEN",
            theme.font_header,
            bg_color=(35, 42, 55),
            hover_color=(75, 30, 38),
            border_color=(180, 55, 65),
            border_radius=8,
        )

        # Panel- und Layout-Rechtecke initial berechnen
        self.name_box_rect = dummy_rect
        self.panel_left_rect = dummy_rect
        self.panel_right_rect = dummy_rect
        self.pathogen_card_rect = dummy_rect
        self.diff_card_rect = dummy_rect
        self.hint_card_rect = dummy_rect
        self.res_header_y = 0

        self.update_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

    def update_layout(self, width: int, height: int) -> None:
        """Passt das Menü-Layout dynamisch an verfügbare Fenstergröße, Vollbild und Widescreen an."""
        self.width = width
        self.height = height

        is_spacious = (height >= 800)

        # Horizontale Aufteilung: 2 ausgewogene Hauptspalten (Links: Pathogen, Rechts: Spiel- & Grafikeinstellungen)
        if width >= 2200:
            # Ultrawide (z.B. 2560x1080, 3440x1440)
            content_width = min(int(width * 0.82), 1960)
            col_gap = 48
        elif width >= 1500:
            # 16:9 Full HD / Widescreen (z.B. 1920x1080)
            content_width = min(int(width * 0.86), 1520)
            col_gap = 36
        else:
            # Standard Fenster (z.B. 1280x720)
            content_width = min(width - 60, 1160)
            col_gap = 24

        col_w = (content_width - col_gap) // 2
        col1_x = (width - content_width) // 2
        col2_x = col1_x + col_w + col_gap

        # 1. Kopfbereich: Titel & Namenseingabe
        title_y = 36 if is_spacious else 22
        subtitle_y = title_y + (36 if is_spacious else 28)
        name_label_y = subtitle_y + (32 if is_spacious else 24)

        name_box_w = 440 if is_spacious else 360
        name_box_h = 42 if is_spacious else 36
        name_box_y = name_label_y + (22 if is_spacious else 18)
        self.name_box_rect = pygame.Rect(width // 2 - name_box_w // 2, name_box_y, name_box_w, name_box_h)

        # 2. Hauptspalten Vertikalmaße
        panel_top = name_box_y + name_box_h + (24 if is_spacious else 16)
        footer_h = 75 if is_spacious else 62
        panel_bottom = height - footer_h - (16 if is_spacious else 10)
        panel_h = max(260, panel_bottom - panel_top)

        self.panel_left_rect = pygame.Rect(col1_x, panel_top, col_w, panel_h)
        self.panel_right_rect = pygame.Rect(col2_x, panel_top, col_w, panel_h)

        pad_x = 18 if is_spacious else 14
        inner_w = col_w - 2 * pad_x

        # 3. Linke Spalte: Pathogenauswahl
        tab_y = panel_top + (44 if is_spacious else 34)
        tab_h = 42 if is_spacious else 36
        tab_gap = 10
        tab_w = (inner_w - 2 * tab_gap) // 3

        for i, btn in enumerate(self.type_buttons):
            btn.rect = pygame.Rect(col1_x + pad_x + i * (tab_w + tab_gap), tab_y, tab_w, tab_h)

        p_card_y = tab_y + tab_h + (14 if is_spacious else 10)
        p_card_h = panel_top + panel_h - p_card_y - (18 if is_spacious else 12)
        self.pathogen_card_rect = pygame.Rect(col1_x + pad_x, p_card_y, inner_w, p_card_h)

        # 4. Rechte Spalte: Schwierigkeitsgrad & Bildschirmmodus
        diff_y = panel_top + (44 if is_spacious else 34)
        diff_h = 38 if is_spacious else 34
        diff_gap = 10
        diff_w = (inner_w - 2 * diff_gap) // 3

        for i, btn in enumerate(self.diff_buttons):
            btn.rect = pygame.Rect(col2_x + pad_x + i * (diff_w + diff_gap), diff_y, diff_w, diff_h)

        d_card_y = diff_y + diff_h + (12 if is_spacious else 8)
        d_card_h = 135 if is_spacious else 95
        self.diff_card_rect = pygame.Rect(col2_x + pad_x, d_card_y, inner_w, d_card_h)

        self.res_header_y = d_card_y + d_card_h + (18 if is_spacious else 10)
        res_y = self.res_header_y + (24 if is_spacious else 18)
        res_h = 36 if is_spacious else 30
        res_gap = 8
        res_w = (inner_w - 2 * res_gap) // 3

        for i, btn in enumerate(self.res_buttons):
            btn.rect = pygame.Rect(col2_x + pad_x + i * (res_w + res_gap), res_y, res_w, res_h)

        hint_y = res_y + res_h + (12 if is_spacious else 8)
        hint_h = max(36, panel_top + panel_h - hint_y - (18 if is_spacious else 12))
        self.hint_card_rect = pygame.Rect(col2_x + pad_x, hint_y, inner_w, hint_h)

        # 5. Fußbereich: Start- und Beenden-Buttons
        btn_start_w = 300 if is_spacious else 240
        btn_start_h = 48 if is_spacious else 42
        btn_quit_w = 140 if is_spacious else 120
        btn_quit_h = btn_start_h
        btn_gap = 18
        total_footer_w = btn_start_w + btn_gap + btn_quit_w

        footer_y = height - (footer_h // 2) - (btn_start_h // 2)
        start_x = width // 2 - total_footer_w // 2
        quit_x = start_x + btn_start_w + btn_gap

        self.btn_start.rect = pygame.Rect(start_x, footer_y, btn_start_w, btn_start_h)
        self.btn_quit.rect = pygame.Rect(quit_x, footer_y, btn_quit_w, btn_quit_h)

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, PathogenType, str, str]]:
        """
        Verarbeitet Tastatur- und Mauseingaben im Menü.
        Gibt 'quit' zurück, oder ein Tupel (name, type, diff, res), wenn das Spiel startet.
        """
        # Namens-Eingabefeld aktivieren / deaktivieren
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_editing_name = self.name_box_rect.collidepoint(event.pos)

        # Tastatureingabe für Erreger-Namen
        if event.type == pygame.KEYDOWN and self.is_editing_name:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.is_editing_name = False
            elif event.key == pygame.K_BACKSPACE:
                self.pathogen_name = self.pathogen_name[:-1]
            elif len(self.pathogen_name) < 18 and event.unicode and event.unicode.isprintable():
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

        # Start- & Beenden-Buttons
        if self.btn_quit.handle_event(event):
            return "quit"

        if self.btn_start.handle_event(event):
            clean_name = self.pathogen_name.strip() or "Plaque-X"
            return clean_name, self.selected_type, self.selected_diff, self.selected_res

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das responsive Menü."""
        w, h = surface.get_size()
        if (self.width, self.height) != (w, h):
            self.update_layout(w, h)

        surface.fill(COLOR_BG)
        is_spacious = (h >= 800)

        # Dekorative Gitter- und Flankenlinien bei Widescreen / Ultrawide
        if self.panel_left_rect.left > 80:
            flank_col = (18, 26, 38)
            # Linke Flanke
            for lx in range(40, self.panel_left_rect.left - 20, 60):
                pygame.draw.line(surface, flank_col, (lx, 60), (lx, h - 60), 1)
            # Rechte Flanke
            for rx in range(self.panel_right_rect.right + 20, w - 20, 60):
                pygame.draw.line(surface, flank_col, (rx, 60), (rx, h - 60), 1)

        # ==========================================
        # 1. KOPFBEREICH: Titel & Namenseingabe
        # ==========================================
        title_font = self.theme.font_huge if is_spacious else self.theme.font_title
        title_y = 38 if is_spacious else 22
        
        # Subtiler roter Glow-Effekt für den Haupttitel
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            UITheme.draw_text(surface, "PY-PLAQUE-INC", title_font, color=(140, 20, 20), pos=(w // 2 + ox, title_y + oy), align="center")
        UITheme.draw_text(surface, "PY-PLAQUE-INC", title_font, color=(240, 55, 55), pos=(w // 2, title_y), align="center")

        subtitle_y = title_y + (38 if is_spacious else 28)
        UITheme.draw_text(
            surface,
            "Globale Pandemie-Simulation | Erobere die Welt vor dem Heilmittel",
            self.theme.font_body,
            color=COLOR_TEXT_MUTED,
            pos=(w // 2, subtitle_y),
            align="center",
        )

        name_label_y = subtitle_y + (30 if is_spacious else 22)
        UITheme.draw_text(
            surface,
            "NAME DES ERREGERS (Klicke zum Bearbeiten):",
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(w // 2, name_label_y),
            align="center",
        )

        # Namenseingabefeld
        box_border = (0, 190, 255) if self.is_editing_name else COLOR_PANEL_BORDER
        box_bg = (24, 34, 48) if self.is_editing_name else COLOR_PANEL_BG
        UITheme.draw_panel(surface, self.name_box_rect, bg_color=box_bg, border_color=box_border, border_radius=6, border_width=2 if self.is_editing_name else 1)

        # Cursor-Blinken alle 500ms
        show_cursor = self.is_editing_name and ((pygame.time.get_ticks() // 500) % 2 == 0)
        display_name = self.pathogen_name + ("|" if show_cursor else "")
        UITheme.draw_text(
            surface,
            display_name,
            self.theme.font_header,
            color=(255, 255, 255),
            pos=self.name_box_rect.center,
            align="center",
        )

        # ==========================================
        # 2. LINKE SPALTE: Erreger-Typ & Eigenschaften
        # ==========================================
        UITheme.draw_panel(surface, self.panel_left_rect, bg_color=(15, 20, 30), border_color=COLOR_PANEL_BORDER, border_radius=8)

        # Spalten-Überschrift
        UITheme.draw_text(
            surface,
            "1. ERREGER-TYP AUSWÄHLEN",
            self.theme.font_body_bold,
            color=COLOR_DNA,
            pos=(self.panel_left_rect.left + 18, self.panel_left_rect.top + 14),
        )

        # Tab-Buttons für Pathogentyp zeichnen
        for btn in self.type_buttons:
            btn.draw(surface)

        # Pathogen-Detailkarte
        UITheme.draw_panel(surface, self.pathogen_card_rect, bg_color=(20, 26, 38), border_color=(40, 56, 78), border_radius=6)

        type_info = PATHOGEN_INFO[self.selected_type]
        type_title = f"{type_info['name']} ({self.selected_type.name})"
        UITheme.draw_text(
            surface,
            type_title,
            self.theme.font_header,
            color=(255, 255, 255),
            pos=(self.pathogen_card_rect.left + 16, self.pathogen_card_rect.top + 14),
        )

        # Beschreibungstext umbrechen
        desc_lines = UITheme.wrap_text(type_info["description"], self.theme.font_small, self.pathogen_card_rect.width - 32)
        cur_y = self.pathogen_card_rect.top + 42
        for line in desc_lines[:4]:
            UITheme.draw_text(surface, line, self.theme.font_small, color=COLOR_TEXT_PRIMARY, pos=(self.pathogen_card_rect.left + 16, cur_y))
            cur_y += 18

        # Spezialfähigkeiten & Attribut-Werte visualisieren
        cur_y += 8
        pygame.draw.line(surface, (32, 44, 60), (self.pathogen_card_rect.left + 16, cur_y), (self.pathogen_card_rect.right - 16, cur_y), 1)
        cur_y += 12

        # Attribut-Balken zeichnen
        bar_w = min(140, (self.pathogen_card_rect.width - 160) // 2)
        stats = self._get_pathogen_stats(self.selected_type)

        self._draw_mini_stat_bar(surface, "Übertragung", stats["infectivity"], 5, (self.pathogen_card_rect.left + 16, cur_y), bar_w, COLOR_DNA)
        self._draw_mini_stat_bar(surface, "Resistenz", stats["resistance"], 5, (self.pathogen_card_rect.left + 16, cur_y + 24), bar_w, COLOR_CURE)
        self._draw_mini_stat_bar(surface, "Mutationsrate", stats["mutation"], 5, (self.pathogen_card_rect.left + 16, cur_y + 48), bar_w, (220, 60, 60))

        # Spezialfähigkeit hervorheben
        cur_y += 78
        UITheme.draw_text(surface, "SPEZIALFÄHIGKEIT:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.pathogen_card_rect.left + 16, cur_y))
        cur_y += 14
        perk_lines = UITheme.wrap_text(stats["perk"], self.theme.font_body_bold, self.pathogen_card_rect.width - 32)
        for pline in perk_lines[:2]:
            UITheme.draw_text(surface, pline, self.theme.font_body_bold, color=COLOR_DNA_GLOW, pos=(self.pathogen_card_rect.left + 16, cur_y))
            cur_y += 18

        # ==========================================
        # 3. RECHTE SPALTE: Kampagne & Anzeige
        # ==========================================
        UITheme.draw_panel(surface, self.panel_right_rect, bg_color=(15, 20, 30), border_color=COLOR_PANEL_BORDER, border_radius=8)

        # 3.1 Schwierigkeitsgrad Überschrift & Tabs
        UITheme.draw_text(
            surface,
            "2. SCHWIERIGKEITSGRAD",
            self.theme.font_body_bold,
            color=COLOR_DNA,
            pos=(self.panel_right_rect.left + 18, self.panel_right_rect.top + 14),
        )

        for btn in self.diff_buttons:
            btn.draw(surface)

        # Schwierigkeit Detailkarte
        UITheme.draw_panel(surface, self.diff_card_rect, bg_color=(20, 26, 38), border_color=(40, 56, 78), border_radius=6)

        diff_info = DIFFICULTIES[self.selected_diff]
        UITheme.draw_text(
            surface,
            f"Modus: {self.selected_diff}",
            self.theme.font_body_bold,
            color=(255, 255, 255),
            pos=(self.diff_card_rect.left + 16, self.diff_card_rect.top + 12),
        )

        diff_lines = UITheme.wrap_text(diff_info["description"], self.theme.font_small, self.diff_card_rect.width - 32)
        dcur_y = self.diff_card_rect.top + 34
        for dline in diff_lines[:3]:
            UITheme.draw_text(surface, dline, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.diff_card_rect.left + 16, dcur_y))
            dcur_y += 16

        # Start-DNA Badge in Schwierigkeitskarte
        dna_tag = f"Start-DNA: {diff_info['starting_dna']} Punkte  |  Forschung: {int(diff_info['cure_speed_multiplier'] * 100)}%"
        UITheme.draw_text(surface, dna_tag, self.theme.font_tiny, color=COLOR_DNA, pos=(self.diff_card_rect.left + 16, self.diff_card_rect.bottom - 18))

        # 3.2 Bildschirmmodus Überschrift & Tabs
        UITheme.draw_text(
            surface,
            "3. BILDSCHIRMMODUS & ANZEIGE",
            self.theme.font_body_bold,
            color=COLOR_DNA,
            pos=(self.panel_right_rect.left + 18, self.res_header_y),
        )

        for btn in self.res_buttons:
            btn.draw(surface)

        # Steuerungs- und Tastaturhinweise
        UITheme.draw_panel(surface, self.hint_card_rect, bg_color=(18, 24, 34), border_color=(35, 45, 60), border_radius=6)
        hint_text_1 = "Tipp: Vollbild kann jederzeit mit F11 oder Alt+Enter umgeschaltet werden."
        hint_text_2 = "Steuerung: Leertaste pausiert | Zifferntasten 1-3 steuern das Tempo | ESC öffnet Menü."
        
        UITheme.draw_text(surface, hint_text_1, self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.hint_card_rect.left + 12, self.hint_card_rect.top + 10))
        if self.hint_card_rect.height > 38:
            UITheme.draw_text(surface, hint_text_2, self.theme.font_tiny, color=COLOR_TEXT_PRIMARY, pos=(self.hint_card_rect.left + 12, self.hint_card_rect.top + 26))

        # ==========================================
        # 4. FUSSBEREICH: Start & Beenden Buttons
        # ==========================================
        self.btn_start.draw(surface)
        self.btn_quit.draw(surface)

    def _get_pathogen_stats(self, ptype: PathogenType) -> dict:
        """Liefert grafische Attributwerte und Spezialfähigkeiten für den gewählten Typ."""
        if ptype == PathogenType.BACTERIA:
            return {
                "infectivity": 3,
                "resistance": 5,
                "mutation": 2,
                "perk": "Bakterien-Hülle: Schützt zuverlässig vor extremen Klimata.",
            }
        elif ptype == PathogenType.VIRUS:
            return {
                "infectivity": 5,
                "resistance": 3,
                "mutation": 5,
                "perk": "Virale Instabilität: Mutiert spontan kostenlose Symptome.",
            }
        else:
            return {
                "infectivity": 2,
                "resistance": 4,
                "mutation": 1,
                "perk": "Sporenausbruch: Überwindet Ozeane und Grenzen per Knopfdruck.",
            }

    def _draw_mini_stat_bar(
        self,
        surface: pygame.Surface,
        label: str,
        value: int,
        max_value: int,
        pos: Tuple[int, int],
        bar_w: int,
        color: Tuple[int, int, int],
    ) -> None:
        """Zeichnet eine dezente Segment-Statistikleiste."""
        x, y = pos
        UITheme.draw_text(surface, label, self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(x, y))

        bar_x = x + 100
        bar_h = 8
        seg_w = max(10, (bar_w - (max_value - 1) * 3) // max_value)

        for s in range(max_value):
            seg_rect = pygame.Rect(bar_x + s * (seg_w + 3), y + 2, seg_w, bar_h)
            seg_col = color if s < value else (30, 40, 55)
            pygame.draw.rect(surface, seg_col, seg_rect, border_radius=2)
