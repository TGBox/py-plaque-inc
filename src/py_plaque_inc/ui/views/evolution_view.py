"""Vollbild-Evolutionsbaum mit Knoten-Netzwerk, Detail-Panel und DNA-Kauf."""

from typing import Dict, List, Optional, Tuple
import math
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_DNA,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
)
from py_plaque_inc.model.pathogen import Pathogen, PATHOGEN_INFO
from py_plaque_inc.model.upgrades import Upgrade, UpgradeCategory
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button, TabButton, ProgressBar


def format_node_label(name: str) -> str:
    """Kürzt den Namen für den Tech-Tree, behält aber römische Ziffern wie I / II bei."""
    if name.endswith(" II"):
        base = name[:-3].strip()
        return f"{base[:7]} II"
    elif name.endswith(" I"):
        base = name[:-2].strip()
        return f"{base[:7]} I"
    if len(name) > 11:
        return name[:10] + "."
    return name


class EvolutionView:
    """Interaktiver Forschungsbaum für Übertragungswege, Symptome und Resistenzen."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.current_category = UpgradeCategory.TRANSMISSION
        self.selected_upgrade_id: Optional[str] = None

        # Tab-Buttons (oben)
        self.tabs = [
            TabButton(pygame.Rect(40, 20, 180, 40), "ÜBERTRAGUNG", theme.font_header, UpgradeCategory.TRANSMISSION.value, is_active=True),
            TabButton(pygame.Rect(230, 20, 180, 40), "SYMPTOME", theme.font_header, UpgradeCategory.SYMPTOMS.value, is_active=False),
            TabButton(pygame.Rect(420, 20, 180, 40), "FÄHIGKEITEN", theme.font_header, UpgradeCategory.ABILITIES.value, is_active=False),
        ]

        # Zurück-Button (oben rechts)
        self.btn_back = Button(
            pygame.Rect(SCREEN_WIDTH - 210, 20, 180, 40),
            "<- ZURÜCK ZUR KARTE",
            theme.font_body_bold,
            bg_color=(35, 45, 60),
            hover_color=(50, 65, 90),
        )

        # Erforschen-Button (unten im Detail-Panel)
        self.btn_unlock = Button(
            pygame.Rect(SCREEN_WIDTH - 320, SCREEN_HEIGHT - 90, 280, 46),
            "JETZT ERFORSCHEN",
            theme.font_header,
            bg_color=(35, 140, 70),
            hover_color=(45, 175, 85),
            border_color=COLOR_SUCCESS,
        )

        # Tech-Tree Grid Bereich
        self.tree_rect = pygame.Rect(40, 80, 860, 520)
        self.detail_rect = pygame.Rect(920, 80, 320, 520)

        # Doppelklick-Verwaltung für schnelles Kaufen / Verkaufen
        self._last_left_click_time: int = 0
        self._last_left_click_id: Optional[str] = None
        self._last_right_click_time: int = 0
        self._last_right_click_id: Optional[str] = None
        self._double_click_threshold_ms: int = 450

    def _is_visible(self, upgrade: Upgrade, pathogen: Pathogen) -> bool:
        """Prüft, ob ein Upgrade für den aktuellen Erregertyp sichtbar ist."""
        if upgrade.is_pathogen_exclusive:
            pathogen_id = PATHOGEN_INFO[pathogen.pathogen_type]["id"]
            if upgrade.is_pathogen_exclusive != pathogen_id:
                return False
        return True

    def handle_event(self, event: pygame.event.Event, pathogen: Pathogen) -> bool:
        """
        Verarbeitet Benutzereingaben.
        Gibt True zurück, wenn zur Weltkarte zurückgekehrt werden soll.
        """
        # Zurück-Button
        if self.btn_back.handle_event(event):
            return True

        # Tab-Wechsel
        for tab in self.tabs:
            clicked_tab = tab.handle_event(event)
            if clicked_tab:
                self.current_category = UpgradeCategory(clicked_tab)
                for t in self.tabs:
                    t.is_active = (t.tab_id == clicked_tab)
                # Ersten passenden Knoten auswählen
                for u in pathogen.upgrades.values():
                    if u.category == self.current_category and self._is_visible(u, pathogen):
                        self.selected_upgrade_id = u.id
                        break

        # Klick auf Baum-Knoten (Links-Klick: Auswählen / Doppelklick: Kaufen)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_id = self._get_node_at_pos(event.pos, pathogen)
            if clicked_id:
                now = pygame.time.get_ticks()
                is_double_click = (
                    clicked_id == self._last_left_click_id
                    and (now - self._last_left_click_time) <= self._double_click_threshold_ms
                )
                self.selected_upgrade_id = clicked_id

                if is_double_click:
                    # Doppelklick links: Kaufen / Erforschen
                    self._last_left_click_time = 0
                    self._last_left_click_id = None
                    upgrade = pathogen.upgrades[clicked_id]
                    if not upgrade.unlocked:
                        can_buy, _ = pathogen.can_unlock(clicked_id)
                        if can_buy:
                            pathogen.unlock_upgrade(clicked_id)
                else:
                    self._last_left_click_time = now
                    self._last_left_click_id = clicked_id

        # Klick auf Baum-Knoten (Rechts-Klick: Auswählen / Doppel-Rechtsklick: Verkaufen)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            clicked_id = self._get_node_at_pos(event.pos, pathogen)
            if clicked_id:
                now = pygame.time.get_ticks()
                is_double_right = (
                    clicked_id == self._last_right_click_id
                    and (now - self._last_right_click_time) <= self._double_click_threshold_ms
                )
                self.selected_upgrade_id = clicked_id

                if is_double_right:
                    # Doppel-Rechtsklick: Verkaufen / Rückentwickeln
                    self._last_right_click_time = 0
                    self._last_right_click_id = None
                    upgrade = pathogen.upgrades[clicked_id]
                    if upgrade.unlocked:
                        can_devolve, _ = pathogen.can_devolve(clicked_id)
                        if can_devolve:
                            pathogen.devolve_upgrade(clicked_id)
                else:
                    self._last_right_click_time = now
                    self._last_right_click_id = clicked_id

        # Erforschen- / Rückentwickeln-Button (Klick auf Button)
        if self.selected_upgrade_id and self.btn_unlock.handle_event(event):
            upgrade = pathogen.upgrades[self.selected_upgrade_id]
            if upgrade.unlocked:
                if pathogen.can_devolve(self.selected_upgrade_id)[0]:
                    pathogen.devolve_upgrade(self.selected_upgrade_id)
            else:
                can_buy, _ = pathogen.can_unlock(self.selected_upgrade_id)
                if can_buy:
                    pathogen.unlock_upgrade(self.selected_upgrade_id)

        return False

    def _get_node_screen_pos(self, grid_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Rechnet Grid-Koordinaten (0..6, 0..4) in Bildschirmkoordinaten um."""
        gx, gy = grid_pos
        start_x = self.tree_rect.left + 70
        start_y = self.tree_rect.top + 60
        spacing_x = 125
        spacing_y = 110
        return start_x + gx * spacing_x, start_y + gy * spacing_y

    def _get_node_at_pos(self, pos: Tuple[int, int], pathogen: Pathogen) -> Optional[str]:
        """Gibt die Upgrade-ID des angeklickten Knotens zurück."""
        mx, my = pos
        for u in pathogen.upgrades.values():
            if u.category == self.current_category and self._is_visible(u, pathogen):
                nx, ny = self._get_node_screen_pos(u.grid_pos)
                if math.hypot(mx - nx, my - ny) <= 28:
                    return u.id
        return None

    def draw(self, surface: pygame.Surface, pathogen: Pathogen) -> None:
        """Rendert den gesamten Evolutionsbildschirm."""
        surface.fill(COLOR_BG)

        # 1. Tabs & Kopfzeile
        for tab in self.tabs:
            tab.draw(surface)
        self.btn_back.draw(surface)

        # DNA-Anzeige oben rechts
        dna_rect = pygame.Rect(SCREEN_WIDTH - 410, 20, 180, 40)
        UITheme.draw_panel(surface, dna_rect, bg_color=(35, 25, 12), border_color=COLOR_DNA, border_radius=6)
        UITheme.draw_text(surface, f"DNA: {pathogen.dna_points}", self.theme.font_header, color=COLOR_DNA, pos=dna_rect.center, align="center")

        # 2. Tech-Tree Panel
        UITheme.draw_panel(surface, self.tree_rect, bg_color=(15, 20, 30), border_color=(30, 42, 60), border_radius=8)

        # Verbindungslinien zwischen Voraussetzungen zeichnen
        for u in pathogen.upgrades.values():
            if u.category == self.current_category and self._is_visible(u, pathogen):
                nx, ny = self._get_node_screen_pos(u.grid_pos)
                for req_id in u.requires:
                    if req_id in pathogen.upgrades:
                        req_u = pathogen.upgrades[req_id]
                        if req_u.category == self.current_category and self._is_visible(req_u, pathogen):
                            rx, ry = self._get_node_screen_pos(req_u.grid_pos)
                            line_color = (60, 180, 90) if req_u.unlocked else (40, 55, 75)
                            pygame.draw.line(surface, line_color, (rx, ry), (nx, ny), 2)

        # Knoten zeichnen
        for u in pathogen.upgrades.values():
            if u.category == self.current_category and self._is_visible(u, pathogen):
                nx, ny = self._get_node_screen_pos(u.grid_pos)
                is_selected = (u.id == self.selected_upgrade_id)
                can_buy, _ = pathogen.can_unlock(u.id)

                if u.unlocked:
                    node_bg = (30, 100, 50)
                    node_border = (80, 240, 120)
                elif can_buy:
                    node_bg = (55, 40, 20)
                    node_border = COLOR_DNA
                else:
                    node_bg = (20, 25, 35)
                    node_border = (50, 65, 85)

                if is_selected:
                    # Ausgewählter Ring
                    pygame.draw.circle(surface, (0, 180, 255), (nx, ny), 32, width=2)

                pygame.draw.circle(surface, node_bg, (nx, ny), 26)
                pygame.draw.circle(surface, node_border, (nx, ny), 26, width=2)

                # Name / Kosten im Knoten
                if u.unlocked:
                    # Vektor-Häkchen zeichnen (keine Font-Glyph-Probleme)
                    check_pts = [(nx - 7, ny), (nx - 2, ny + 5), (nx + 7, ny - 5)]
                    pygame.draw.lines(surface, (255, 255, 255), False, check_pts, width=3)
                else:
                    cost_txt = f"{u.cost} DNA"
                    txt_col = (255, 255, 255) if can_buy else COLOR_TEXT_MUTED
                    UITheme.draw_text(surface, cost_txt, self.theme.font_tiny, color=txt_col, pos=(nx, ny - 6), align="center")
                
                # Kurzer Titel unter dem Knoten
                short_name = format_node_label(u.name)
                UITheme.draw_text(surface, short_name, self.theme.font_tiny, color=COLOR_TEXT_PRIMARY, pos=(nx, ny + 32), align="center")

        # 3. Detail-Sidebar (rechts)
        self._draw_detail_panel(surface, pathogen)

        # 4. Fußzeile mit Pathogen-Gesamtwerten
        self._draw_stats_bar(surface, pathogen)

    def _draw_detail_panel(self, surface: pygame.Surface, pathogen: Pathogen) -> None:
        """Zeichnet das Infopanel für das aktuell ausgewählte Upgrade."""
        UITheme.draw_panel(surface, self.detail_rect, bg_color=(18, 24, 36), border_color=(40, 55, 75), border_radius=8)

        if not self.selected_upgrade_id or self.selected_upgrade_id not in pathogen.upgrades:
            UITheme.draw_text(surface, "Wähle einen Knoten aus", self.theme.font_body, color=COLOR_TEXT_MUTED, pos=self.detail_rect.center, align="center")
            return

        upgrade = pathogen.upgrades[self.selected_upgrade_id]

        # Titel & Kategorie
        UITheme.draw_text(surface, upgrade.name, self.theme.font_header, color=(255, 255, 255), pos=(self.detail_rect.left + 16, self.detail_rect.top + 16))
        UITheme.draw_text(surface, f"Kategorie: {upgrade.category.value}", self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.detail_rect.left + 16, self.detail_rect.top + 40))

        # Status & Kosten
        if upgrade.unlocked:
            status_txt = "BEREITS ERFORSCHT"
            status_col = COLOR_SUCCESS
        else:
            status_txt = f"Kosten: {upgrade.cost} DNA"
            status_col = COLOR_DNA
        UITheme.draw_text(surface, status_txt, self.theme.font_body_bold, color=status_col, pos=(self.detail_rect.left + 16, self.detail_rect.top + 70))

        # Beschreibung (Mehrzeilig umbrechen)
        desc_rect = pygame.Rect(self.detail_rect.left + 16, self.detail_rect.top + 105, 288, 120)
        UITheme.draw_panel(surface, desc_rect, bg_color=(12, 16, 24), border_color=(30, 42, 60), border_radius=4)
        words = upgrade.description.split(" ")
        lines = []
        cur = []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 32:
                lines.append(" ".join(cur))
                cur = []
        if cur:
            lines.append(" ".join(cur))

        for i, l in enumerate(lines[:6]):
            UITheme.draw_text(surface, l, self.theme.font_small, color=(220, 220, 220), pos=(desc_rect.left + 8, desc_rect.top + 8 + i * 16))

        # Modifikatoren-Übersicht
        stat_y = self.detail_rect.top + 245
        UITheme.draw_text(surface, "EFFEKTE:", self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.detail_rect.left + 16, stat_y))
        stat_y += 20

        stats = [
            ("Infektiosität:", f"+{upgrade.infectivity:.1f}", (255, 100, 100) if upgrade.infectivity > 0 else COLOR_TEXT_MUTED),
            ("Schweregrad:", f"+{upgrade.severity:.1f}", (255, 160, 50) if upgrade.severity > 0 else COLOR_TEXT_MUTED),
            ("Tödlichkeit:", f"+{upgrade.lethality:.1f}", (180, 50, 50) if upgrade.lethality > 0 else COLOR_TEXT_MUTED),
            ("Resistenzen:", f"Kälte +{int(upgrade.cold_res*100)}% / Hitze +{int(upgrade.heat_res*100)}%", (0, 180, 255) if (upgrade.cold_res or upgrade.heat_res) else COLOR_TEXT_MUTED),
            ("Heilmittel-Verlangsamung:", f"+{int(upgrade.cure_slow*100)}%", (0, 200, 255) if upgrade.cure_slow > 0 else COLOR_TEXT_MUTED),
        ]

        for label, val, col in stats:
            UITheme.draw_text(surface, label, self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.detail_rect.left + 16, stat_y))
            UITheme.draw_text(surface, val, self.theme.font_tiny, color=col, pos=(self.detail_rect.right - 16, stat_y), align="right")
            stat_y += 18

        # Kauf- / Rückentwickeln-Button
        UITheme.draw_text(
            surface,
            "Doppelklick: Kaufen  |  Doppel-Rechtsklick: Verkaufen",
            self.theme.font_tiny,
            color=COLOR_TEXT_MUTED,
            pos=(self.btn_unlock.rect.centerx, self.btn_unlock.rect.top - 12),
            align="center",
        )

        if upgrade.unlocked:
            can_devolve, reason = pathogen.can_devolve(upgrade.id)
            self.btn_unlock.enabled = can_devolve
            self.btn_unlock.text = "RÜCKENTWICKELN (+2 DNA)"
            if can_devolve:
                self.btn_unlock.bg_color = (130, 35, 35)
                self.btn_unlock.hover_color = (175, 50, 50)
                self.btn_unlock.border_color = (255, 90, 90)
            else:
                self.btn_unlock.bg_color = (35, 25, 25)
                self.btn_unlock.border_color = (65, 45, 45)
            self.btn_unlock.draw(surface)
            if not can_devolve:
                UITheme.draw_text(surface, reason, self.theme.font_tiny, color=(255, 120, 120), pos=(self.detail_rect.centerx, self.detail_rect.bottom - 24), align="center")
        else:
            can_buy, reason = pathogen.can_unlock(upgrade.id)
            self.btn_unlock.enabled = can_buy
            if can_buy:
                self.btn_unlock.text = f"ERFORSCHEN ({upgrade.cost} DNA)"
                self.btn_unlock.bg_color = (35, 140, 70)
                self.btn_unlock.hover_color = (45, 175, 85)
                self.btn_unlock.border_color = COLOR_SUCCESS
            else:
                self.btn_unlock.text = "NICHT VERFÜGBAR"
                self.btn_unlock.bg_color = (30, 35, 45)
                self.btn_unlock.border_color = (50, 60, 75)
            self.btn_unlock.draw(surface)
            if not can_buy:
                UITheme.draw_text(surface, reason, self.theme.font_tiny, color=(255, 120, 120), pos=(self.detail_rect.centerx, self.detail_rect.bottom - 24), align="center")

    def _draw_stats_bar(self, surface: pygame.Surface, pathogen: Pathogen) -> None:
        """Zeichnet Balken für Gesamt-Infektiosität, Schweregrad und Tödlichkeit."""
        bar_y = SCREEN_HEIGHT - 95
        # Infektiosität
        UITheme.draw_text(surface, f"INFEKTIOSITÄT: {pathogen.total_infectivity:.1f}", self.theme.font_tiny, color=(255, 100, 100), pos=(50, bar_y))
        ProgressBar(pygame.Rect(50, bar_y + 14, 250, 12), fill_color=(230, 50, 50)).draw(surface, value=pathogen.total_infectivity, max_value=25.0)

        # Schweregrad
        UITheme.draw_text(surface, f"SCHWEREGRAD: {pathogen.total_severity:.1f}", self.theme.font_tiny, color=(255, 160, 50), pos=(330, bar_y))
        ProgressBar(pygame.Rect(330, bar_y + 14, 250, 12), fill_color=(255, 160, 50)).draw(surface, value=pathogen.total_severity, max_value=25.0)

        # Tödlichkeit
        UITheme.draw_text(surface, f"TÖDLICHKEIT: {pathogen.total_lethality:.1f}", self.theme.font_tiny, color=(160, 40, 40), pos=(610, bar_y))
        ProgressBar(pygame.Rect(610, bar_y + 14, 250, 12), fill_color=(160, 40, 40)).draw(surface, value=pathogen.total_lethality, max_value=25.0)
