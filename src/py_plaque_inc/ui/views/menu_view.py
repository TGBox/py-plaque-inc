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
    COLOR_SUCCESS,
    DIFFICULTIES,
)
from py_plaque_inc.model.pathogen import PathogenType, PATHOGEN_INFO
from py_plaque_inc.engine.save_manager import get_save_manager, PATHOGEN_UNLOCK_ORDER
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button, TabButton


class MenuView:
    """Startbildschirm mit responsiver Anordnung für alle Fenster- und Bildschirmauflösungen."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.save_mgr = get_save_manager()

        # Fenstermaße
        self.width: int = SCREEN_WIDTH
        self.height: int = SCREEN_HEIGHT

        # Ausgewählte Optionen
        self.pathogen_name: str = "Plaque-X"
        self.is_editing_name: bool = False
        
        # Alle 8 Erregertypen in Reihenfolge
        self.pathogen_types: List[PathogenType] = list(PATHOGEN_UNLOCK_ORDER)
        self.current_type_index: int = 0
        self.selected_type: PathogenType = self.pathogen_types[self.current_type_index]
        
        self.selected_diff: str = "Normal"
        self.selected_res: str = "1280x720"
        self.on_change_resolution = None
        self.lock_warning_timer: int = 0

        dummy_rect = pygame.Rect(0, 0, 10, 10)

        # Karussell-Navigation für Erreger
        self.btn_prev_type = Button(
            dummy_rect,
            "< ZURÜCK",
            theme.font_small,
            bg_color=(28, 38, 54),
            hover_color=(42, 58, 80),
            border_color=(50, 70, 95),
            border_radius=6,
        )
        self.btn_next_type = Button(
            dummy_rect,
            "WEITER >",
            theme.font_small,
            bg_color=(28, 38, 54),
            hover_color=(42, 58, 80),
            border_color=(50, 70, 95),
            border_radius=6,
        )

        # Schnellauswahl-Buttons für alle 8 Erreger (Abwärtskompatibilität mit Tests & Direktwahl)
        self.type_buttons: List[TabButton] = []
        for ptype in self.pathogen_types:
            pinfo = PATHOGEN_INFO[ptype]
            is_first = (ptype == self.selected_type)
            self.type_buttons.append(
                TabButton(dummy_rect, pinfo["name"], theme.font_tiny, pinfo["id"], is_active=is_first)
            )

        # Entwicklermodus / Cheat-Toggle Button
        self.btn_toggle_cheat = Button(
            dummy_rect,
            "Entwicklermodus: Alle Erreger freischalten",
            theme.font_tiny,
            bg_color=(24, 32, 44),
            hover_color=(38, 50, 70),
            border_color=(45, 60, 80),
            border_radius=5,
        )

        # Schwierigkeitsgrad-Tabs
        self.diff_buttons: List[TabButton] = [
            TabButton(dummy_rect, "Leicht", theme.font_body_bold, "Leicht", is_active=False),
            TabButton(dummy_rect, "Normal", theme.font_body_bold, "Normal", is_active=True),
            TabButton(dummy_rect, "Schwer", theme.font_body_bold, "Schwer", is_active=False),
        ]

        # Bildschirmmodus-Tabs
        self.res_buttons: List[TabButton] = [
            TabButton(dummy_rect, "1280x720 (Fenster)", theme.font_tiny, "1280x720", is_active=True),
            TabButton(dummy_rect, "1920x1080 (Vollbild)", theme.font_tiny, "1920x1080", is_active=False),
            TabButton(dummy_rect, "2560x1080 (Ultrawide)", theme.font_tiny, "2560x1080", is_active=False),
        ]

        # Haupt-Aktionsbuttons
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
        self.carousel_header_rect = dummy_rect
        self.diff_card_rect = dummy_rect
        self.hint_card_rect = dummy_rect
        self.res_header_y = 0

        self.update_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

    def select_type_by_index(self, index: int) -> None:
        """Wählt einen Erreger per Index im Karussell aus."""
        self.current_type_index = index % len(self.pathogen_types)
        self.selected_type = self.pathogen_types[self.current_type_index]
        selected_id = PATHOGEN_INFO[self.selected_type]["id"]
        for btn in self.type_buttons:
            btn.is_active = (btn.tab_id == selected_id)

    def select_type_by_id(self, type_id: str) -> None:
        """Wählt einen Erreger anhand seiner internen String-ID aus."""
        for i, ptype in enumerate(self.pathogen_types):
            if PATHOGEN_INFO[ptype]["id"] == type_id:
                self.select_type_by_index(i)
                break

    def update_layout(self, width: int, height: int) -> None:
        """Passt das Menü-Layout dynamisch an verfügbare Fenstergröße, Vollbild und Widescreen an."""
        self.width = width
        self.height = height

        is_spacious = (height >= 800)

        # Horizontale Aufteilung: 2 Hauptspalten
        if width >= 2200:
            content_width = min(int(width * 0.82), 1960)
            col_gap = 48
        elif width >= 1500:
            content_width = min(int(width * 0.86), 1520)
            col_gap = 36
        else:
            content_width = min(width - 60, 1160)
            col_gap = 24

        col_w = (content_width - col_gap) // 2
        col1_x = (width - content_width) // 2
        col2_x = col1_x + col_w + col_gap

        # 1. Kopfbereich: Titel & Namenseingabe
        title_y = 36 if is_spacious else 20
        subtitle_y = title_y + (36 if is_spacious else 26)
        name_label_y = subtitle_y + (30 if is_spacious else 22)

        name_box_w = 440 if is_spacious else 360
        name_box_h = 40 if is_spacious else 34
        name_box_y = name_label_y + (22 if is_spacious else 16)
        self.name_box_rect = pygame.Rect(width // 2 - name_box_w // 2, name_box_y, name_box_w, name_box_h)

        # 2. Hauptspalten Vertikalmaße
        panel_top = name_box_y + name_box_h + (20 if is_spacious else 14)
        footer_h = 75 if is_spacious else 62
        panel_bottom = height - footer_h - (16 if is_spacious else 10)
        panel_h = max(280, panel_bottom - panel_top)

        self.panel_left_rect = pygame.Rect(col1_x, panel_top, col_w, panel_h)
        self.panel_right_rect = pygame.Rect(col2_x, panel_top, col_w, panel_h)

        pad_x = 18 if is_spacious else 14
        inner_w = col_w - 2 * pad_x

        # 3. Linke Spalte: Karussell-Steuerung & Erregerauswahl
        car_y = panel_top + (42 if is_spacious else 32)
        car_btn_w = 95 if is_spacious else 80
        car_btn_h = 36 if is_spacious else 30
        
        self.btn_prev_type.rect = pygame.Rect(col1_x + pad_x, car_y, car_btn_w, car_btn_h)
        self.btn_next_type.rect = pygame.Rect(col1_x + pad_x + inner_w - car_btn_w, car_y, car_btn_w, car_btn_h)
        self.carousel_header_rect = pygame.Rect(
            col1_x + pad_x + car_btn_w + 8,
            car_y,
            inner_w - 2 * car_btn_w - 16,
            car_btn_h,
        )

        # 8 Quick-Select Buttons (2 Reihen à 4)
        q_y1 = car_y + car_btn_h + (10 if is_spacious else 6)
        q_h = 30 if is_spacious else 24
        q_gap = 6
        q_w = (inner_w - 3 * q_gap) // 4
        q_y2 = q_y1 + q_h + q_gap

        for i, btn in enumerate(self.type_buttons):
            row = 0 if i < 4 else 1
            col = i % 4
            by = q_y1 if row == 0 else q_y2
            bx = col1_x + pad_x + col * (q_w + q_gap)
            btn.rect = pygame.Rect(bx, by, q_w, q_h)

        # Entwickler / Cheat-Button ganz unten im linken Panel
        cheat_h = 28 if is_spacious else 24
        cheat_y = panel_top + panel_h - cheat_h - (12 if is_spacious else 8)
        self.btn_toggle_cheat.rect = pygame.Rect(col1_x + pad_x, cheat_y, inner_w, cheat_h)

        # Pathogen-Detailkarte
        p_card_y = q_y2 + q_h + (10 if is_spacious else 6)
        p_card_h = cheat_y - p_card_y - (10 if is_spacious else 6)
        self.pathogen_card_rect = pygame.Rect(col1_x + pad_x, p_card_y, inner_w, max(120, p_card_h))

        # 4. Rechte Spalte: Schwierigkeitsgrad & Bildschirmmodus
        diff_y = panel_top + (42 if is_spacious else 32)
        diff_h = 38 if is_spacious else 32
        diff_gap = 10
        diff_w = (inner_w - 2 * diff_gap) // 3

        for i, btn in enumerate(self.diff_buttons):
            btn.rect = pygame.Rect(col2_x + pad_x + i * (diff_w + diff_gap), diff_y, diff_w, diff_h)

        d_card_y = diff_y + diff_h + (12 if is_spacious else 8)
        d_card_h = 135 if is_spacious else 95
        self.diff_card_rect = pygame.Rect(col2_x + pad_x, d_card_y, inner_w, d_card_h)

        self.res_header_y = d_card_y + d_card_h + (18 if is_spacious else 10)
        res_y = self.res_header_y + (24 if is_spacious else 18)
        res_h = 36 if is_spacious else 28
        res_gap = 8
        res_w = (inner_w - 2 * res_gap) // 3

        for i, btn in enumerate(self.res_buttons):
            btn.rect = pygame.Rect(col2_x + pad_x + i * (res_w + res_gap), res_y, res_w, res_h)

        hint_y = res_y + res_h + (12 if is_spacious else 8)
        hint_h = max(36, panel_top + panel_h - hint_y - (18 if is_spacious else 12))
        self.hint_card_rect = pygame.Rect(col2_x + pad_x, hint_y, inner_w, hint_h)

        # 5. Fußbereich: Start- und Beenden-Buttons
        btn_start_w = 340 if is_spacious else 280
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

        # Karussell-Navigation
        if self.btn_prev_type.handle_event(event):
            self.select_type_by_index(self.current_type_index - 1)

        if self.btn_next_type.handle_event(event):
            self.select_type_by_index(self.current_type_index + 1)

        # Schnellauswahl der 8 Erregertypen
        for btn in self.type_buttons:
            tab = btn.handle_event(event)
            if tab:
                self.select_type_by_id(tab)

        # Entwicklermodus / Cheat-Toggle
        if self.btn_toggle_cheat.handle_event(event):
            self.save_mgr.toggle_all_unlocked()

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

        # Beenden-Button
        if self.btn_quit.handle_event(event):
            return "quit"

        # Start-Button
        if self.btn_start.handle_event(event):
            # Prüfen, ob Erreger freigeschaltet ist
            if not self.save_mgr.is_unlocked(self.selected_type):
                self.lock_warning_timer = 120  # Warnung für ~2 Sekunden aufblinken lassen
                return None

            clean_name = self.pathogen_name.strip() or "Plaque-X"
            return clean_name, self.selected_type, self.selected_diff, self.selected_res

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das responsive Menü."""
        w, h = surface.get_size()
        if (self.width, self.height) != (w, h):
            self.update_layout(w, h)

        if self.lock_warning_timer > 0:
            self.lock_warning_timer -= 1

        surface.fill(COLOR_BG)
        is_spacious = (h >= 800)

        # Dekorative Linien bei Widescreen / Ultrawide
        if self.panel_left_rect.left > 80:
            flank_col = (18, 26, 38)
            for lx in range(40, self.panel_left_rect.left - 20, 60):
                pygame.draw.line(surface, flank_col, (lx, 60), (lx, h - 60), 1)
            for rx in range(self.panel_right_rect.right + 20, w - 20, 60):
                pygame.draw.line(surface, flank_col, (rx, 60), (rx, h - 60), 1)

        # ==========================================
        # 1. KOPFBEREICH: Titel & Namenseingabe
        # ==========================================
        title_font = self.theme.font_huge if is_spacious else self.theme.font_title
        title_y = 38 if is_spacious else 20
        
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            UITheme.draw_text(surface, "PY-PLAQUE-INC", title_font, color=(140, 20, 20), pos=(w // 2 + ox, title_y + oy), align="center")
        UITheme.draw_text(surface, "PY-PLAQUE-INC", title_font, color=(240, 55, 55), pos=(w // 2, title_y), align="center")

        subtitle_y = title_y + (38 if is_spacious else 26)
        UITheme.draw_text(
            surface,
            "Globale Pandemie-Simulation | Erobere die Welt vor dem Heilmittel",
            self.theme.font_body,
            color=COLOR_TEXT_MUTED,
            pos=(w // 2, subtitle_y),
            align="center",
        )

        name_label_y = subtitle_y + (28 if is_spacious else 20)
        UITheme.draw_text(
            surface,
            "NAME DES ERREGERS (Klicke zum Bearbeiten):",
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(w // 2, name_label_y),
            align="center",
        )

        box_border = (0, 190, 255) if self.is_editing_name else COLOR_PANEL_BORDER
        box_bg = (24, 34, 48) if self.is_editing_name else COLOR_PANEL_BG
        UITheme.draw_panel(surface, self.name_box_rect, bg_color=box_bg, border_color=box_border, border_radius=6, border_width=2 if self.is_editing_name else 1)

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
        # 2. LINKE SPALTE: Erreger-Auswahl & Karussell
        # ==========================================
        UITheme.draw_panel(surface, self.panel_left_rect, bg_color=(15, 20, 30), border_color=COLOR_PANEL_BORDER, border_radius=8)

        # Spalten-Überschrift mit Zähler
        header_text = f"1. ERREGER-TYP ({self.current_type_index + 1} / {len(self.pathogen_types)})"
        UITheme.draw_text(
            surface,
            header_text,
            self.theme.font_body_bold,
            color=COLOR_DNA,
            pos=(self.panel_left_rect.left + 18, self.panel_left_rect.top + 12),
        )

        # Karussell Buttons zeichnen
        self.btn_prev_type.draw(surface)
        self.btn_next_type.draw(surface)

        # Karussell-Titel mittig zwischen den Pfeilen
        is_unlocked = self.save_mgr.is_unlocked(self.selected_type)
        cur_info = PATHOGEN_INFO[self.selected_type]
        
        status_tag = "[ BEREIT ]" if is_unlocked else "[ GESPERRT ]"
        status_color = COLOR_SUCCESS if is_unlocked else (235, 75, 75)
        
        UITheme.draw_text(
            surface,
            cur_info["name"].upper(),
            self.theme.font_header,
            color=(255, 255, 255),
            pos=(self.carousel_header_rect.centerx, self.carousel_header_rect.centery - 8),
            align="center",
        )
        UITheme.draw_text(
            surface,
            status_tag,
            self.theme.font_tiny,
            color=status_color,
            pos=(self.carousel_header_rect.centerx, self.carousel_header_rect.centery + 10),
            align="center",
        )

        # 8 Quick-Select Buttons zeichnen (mit Sperr-Indikator)
        for i, btn in enumerate(self.type_buttons):
            pt = self.pathogen_types[i]
            pt_unlocked = self.save_mgr.is_unlocked(pt)
            
            # Sperr-Badge über gesperrten Knöpfen
            btn.draw(surface)
            if not pt_unlocked:
                # Leicht abdunkeln und kleinen roten Punkt als Sperr-Indikator zeichnen
                dim_surf = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                dim_surf.fill((10, 15, 25, 120))
                surface.blit(dim_surf, btn.rect.topleft)
                pygame.draw.circle(surface, (230, 70, 70), (btn.rect.right - 8, btn.rect.top + 8), 3)

        # Pathogen-Detailkarte
        card_border = (40, 56, 78) if is_unlocked else (120, 40, 40)
        UITheme.draw_panel(surface, self.pathogen_card_rect, bg_color=(20, 26, 38), border_color=card_border, border_radius=6)

        # Kartentitel
        type_title = f"{cur_info['name']} ({self.selected_type.name})"
        UITheme.draw_text(
            surface,
            type_title,
            self.theme.font_header,
            color=(255, 255, 255) if is_unlocked else (230, 160, 160),
            pos=(self.pathogen_card_rect.left + 16, self.pathogen_card_rect.top + 12),
        )

        cur_y = self.pathogen_card_rect.top + 36

        # Wenn gesperrt: Auffälliger Sperr-Hinweis
        if not is_unlocked:
            lock_box = pygame.Rect(self.pathogen_card_rect.left + 12, cur_y, self.pathogen_card_rect.width - 24, 44)
            UITheme.draw_panel(surface, lock_box, bg_color=(45, 18, 22), border_color=(180, 45, 55), border_radius=4)
            
            reason = self.save_mgr.get_lock_reason(self.selected_type)
            UITheme.draw_text(surface, reason, self.theme.font_body_bold, color=(255, 180, 180), pos=(lock_box.left + 10, lock_box.top + 6))
            UITheme.draw_text(surface, "Tipp: Nutze unten den Entwicklermodus, um sofort alle Erreger zu testen.", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(lock_box.left + 10, lock_box.top + 26))
            cur_y += 52

        # Beschreibungstext
        desc_lines = UITheme.wrap_text(cur_info["description"], self.theme.font_small, self.pathogen_card_rect.width - 32)
        max_desc_lines = 3 if not is_unlocked else (4 if is_spacious else 3)
        for line in desc_lines[:max_desc_lines]:
            UITheme.draw_text(surface, line, self.theme.font_small, color=COLOR_TEXT_PRIMARY, pos=(self.pathogen_card_rect.left + 16, cur_y))
            cur_y += 18

        # Trennlinie
        cur_y += 6
        pygame.draw.line(surface, (32, 44, 60), (self.pathogen_card_rect.left + 16, cur_y), (self.pathogen_card_rect.right - 16, cur_y), 1)
        cur_y += 10

        # Attribut-Balken für den Erreger
        stats = self._get_pathogen_stats(self.selected_type)
        bar_w = min(140, (self.pathogen_card_rect.width - 160) // 2)

        self._draw_mini_stat_bar(surface, "Übertragung", stats["infectivity"], 5, (self.pathogen_card_rect.left + 16, cur_y), bar_w, COLOR_DNA)
        self._draw_mini_stat_bar(surface, "Resistenz", stats["resistance"], 5, (self.pathogen_card_rect.left + 16, cur_y + 22), bar_w, COLOR_CURE)
        self._draw_mini_stat_bar(surface, "Mutationsrate", stats["mutation"], 5, (self.pathogen_card_rect.left + 16, cur_y + 44), bar_w, (220, 60, 60))

        # Spezialfähigkeit hervorheben
        cur_y += 72
        UITheme.draw_text(surface, "SPEZIALFÄHIGKEIT:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.pathogen_card_rect.left + 16, cur_y))
        cur_y += 14
        perk_lines = UITheme.wrap_text(stats["perk"], self.theme.font_body_bold, self.pathogen_card_rect.width - 32)
        for pline in perk_lines[:2]:
            UITheme.draw_text(surface, pline, self.theme.font_body_bold, color=COLOR_DNA_GLOW, pos=(self.pathogen_card_rect.left + 16, cur_y))
            cur_y += 16

        # Entwicklermodus / Cheat-Toggle zeichnen
        cheat_active = self.save_mgr.all_unlocked_cheat
        if cheat_active:
            self.btn_toggle_cheat.text = "Entwicklermodus: ALLE ERREGER FREI (AKTIV)"
            self.btn_toggle_cheat.bg_color = (25, 80, 45)
            self.btn_toggle_cheat.border_color = COLOR_SUCCESS
        else:
            self.btn_toggle_cheat.text = "Test-Modus: Alle 8 Erreger freischalten"
            self.btn_toggle_cheat.bg_color = (24, 32, 44)
            self.btn_toggle_cheat.border_color = (45, 60, 80)
        self.btn_toggle_cheat.draw(surface)

        # ==========================================
        # 3. RECHTE SPALTE: Kampagne & Anzeige
        # ==========================================
        UITheme.draw_panel(surface, self.panel_right_rect, bg_color=(15, 20, 30), border_color=COLOR_PANEL_BORDER, border_radius=8)

        # 3.1 Schwierigkeitsgrad
        UITheme.draw_text(
            surface,
            "2. SCHWIERIGKEITSGRAD",
            self.theme.font_body_bold,
            color=COLOR_DNA,
            pos=(self.panel_right_rect.left + 18, self.panel_right_rect.top + 12),
        )

        for btn in self.diff_buttons:
            btn.draw(surface)

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

        dna_tag = f"Start-DNA: {diff_info['starting_dna']} Punkte  |  Forschung: {int(diff_info['cure_speed_multiplier'] * 100)}%"
        UITheme.draw_text(surface, dna_tag, self.theme.font_tiny, color=COLOR_DNA, pos=(self.diff_card_rect.left + 16, self.diff_card_rect.bottom - 18))

        # 3.2 Bildschirmmodus
        UITheme.draw_text(
            surface,
            "3. BILDSCHIRMMODUS & ANZEIGE",
            self.theme.font_body_bold,
            color=COLOR_DNA,
            pos=(self.panel_right_rect.left + 18, self.res_header_y),
        )

        for btn in self.res_buttons:
            btn.draw(surface)

        UITheme.draw_panel(surface, self.hint_card_rect, bg_color=(18, 24, 34), border_color=(35, 45, 60), border_radius=6)
        hint_text_1 = "Tipp: Vollbild kann jederzeit mit F11 oder Alt+Enter umgeschaltet werden."
        hint_text_2 = "Steuerung: Leertaste pausiert | Zifferntasten 1-3 steuern das Tempo | ESC öffnet Menü."
        
        UITheme.draw_text(surface, hint_text_1, self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.hint_card_rect.left + 12, self.hint_card_rect.top + 10))
        if self.hint_card_rect.height > 38:
            UITheme.draw_text(surface, hint_text_2, self.theme.font_tiny, color=COLOR_TEXT_PRIMARY, pos=(self.hint_card_rect.left + 12, self.hint_card_rect.top + 26))

        # ==========================================
        # 4. FUSSBEREICH: Start & Beenden Buttons
        # ==========================================
        if is_unlocked:
            self.btn_start.text = "SEUCHE FREISETZEN"
            self.btn_start.bg_color = (180, 32, 32)
            self.btn_start.hover_color = (225, 45, 45)
            self.btn_start.border_color = (255, 100, 100)
        else:
            if self.lock_warning_timer > 0:
                self.btn_start.text = "ERREGER IST NOCH GESPERRT!"
                self.btn_start.bg_color = (120, 25, 25)
                self.btn_start.border_color = (240, 70, 70)
            else:
                self.btn_start.text = "GESPERRT (Erreger freispielen)"
                self.btn_start.bg_color = (40, 48, 62)
                self.btn_start.hover_color = (52, 62, 78)
                self.btn_start.border_color = (70, 85, 105)

        self.btn_start.draw(surface)
        self.btn_quit.draw(surface)

    def _get_pathogen_stats(self, ptype: PathogenType) -> dict:
        """Liefert grafische Attributwerte und Spezialfähigkeiten für alle 8 Erregertypen."""
        if ptype == PathogenType.BACTERIA:
            return {
                "infectivity": 3,
                "resistance": 5,
                "mutation": 2,
                "perk": "Bakterien-Hülle: Robuste Zellwand schützt in allen Klimazonen.",
            }
        elif ptype == PathogenType.VIRUS:
            return {
                "infectivity": 5,
                "resistance": 3,
                "mutation": 5,
                "perk": "Virale Instabilität: Mutiert spontan kostenlose Symptome.",
            }
        elif ptype == PathogenType.FUNGUS:
            return {
                "infectivity": 2,
                "resistance": 4,
                "mutation": 1,
                "perk": "Sporenausbruch: Überwindet Ozeane und Grenzen per Knopfdruck.",
            }
        elif ptype == PathogenType.PARASITE:
            return {
                "infectivity": 4,
                "resistance": 3,
                "mutation": 2,
                "perk": "Symbiotische Tarnung: Späte Entdeckung; passive DNA im Verborgenen.",
            }
        elif ptype == PathogenType.PRION:
            return {
                "infectivity": 3,
                "resistance": 5,
                "mutation": 1,
                "perk": "Neural-Atrophie: Globale Heilmittelforschung dauerhaft massiv verlangsamt.",
            }
        elif ptype == PathogenType.NANO_VIRUS:
            return {
                "infectivity": 5,
                "resistance": 2,
                "mutation": 3,
                "perk": "Cyber-Interferenz: Startet mit aktiver WHO-Forschung; Code-Fragmentierung senkt Heilmittel.",
            }
        elif ptype == PathogenType.BIO_WEAPON:
            return {
                "infectivity": 4,
                "resistance": 4,
                "mutation": 4,
                "perk": "Lethale Eskalation: Tödlichkeit steigt automatisch; Gen-Kompression zähmt Virus.",
            }
        elif ptype == PathogenType.BRAINROT:
            return {
                "infectivity": 5,
                "resistance": 2,
                "mutation": 4,
                "perk": "Doomscrolling: Rasante Ansteckung in reichen Ländern; Forscher doomscrollen statt forschen.",
            }
        return {
            "infectivity": 3,
            "resistance": 3,
            "mutation": 3,
            "perk": "Standard-Pathogen",
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
