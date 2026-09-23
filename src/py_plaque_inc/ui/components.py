"""Wiederverwendbare interaktive UI-Komponenten (Buttons, Tabs, Fortschrittsbalken)."""

from typing import Tuple, Optional, Callable, List
import pygame

from py_plaque_inc.config import (
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_PANEL_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_DNA,
    COLOR_CURE,
)
from py_plaque_inc.ui.theme import UITheme


class Button:
    """Interaktiver Button mit Hover-Animation, Klick-Erkennung und Deaktivierung."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        bg_color: Tuple[int, int, int] = COLOR_PANEL_BG,
        hover_color: Tuple[int, int, int] = COLOR_PANEL_HOVER,
        border_color: Tuple[int, int, int] = COLOR_PANEL_BORDER,
        text_color: Tuple[int, int, int] = COLOR_TEXT_PRIMARY,
        border_radius: int = 5,
        on_click: Optional[Callable[[], None]] = None,
        enabled: bool = True,
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.on_click = on_click
        self.enabled = enabled
        self.is_hovered: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Prüft Klicks. Gibt True zurück, wenn der Button geklickt wurde."""
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet den Button."""
        if not self.enabled:
            bg = (20, 25, 32)
            border = (40, 48, 58)
            txt_col = COLOR_TEXT_MUTED
        elif self.is_hovered:
            bg = self.hover_color
            border = (120, 150, 180)
            txt_col = (255, 255, 255)
        else:
            bg = self.bg_color
            border = self.border_color
            txt_col = self.text_color

        UITheme.draw_panel(surface, self.rect, bg_color=bg, border_color=border, border_radius=self.border_radius)
        UITheme.draw_text(surface, self.text, self.font, color=txt_col, pos=self.rect.center, align="center")


class TabButton:
    """Tab-Schalter für Menüs und den Evolutionsbaum."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        tab_id: str,
        is_active: bool = False,
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.tab_id = tab_id
        self.is_active = is_active
        self.is_hovered: bool = False

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Gibt tab_id zurück, falls angeklickt."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.tab_id
        return None

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_active:
            bg = (40, 56, 78)
            border = (100, 140, 190)
            txt_col = (255, 255, 255)
        elif self.is_hovered:
            bg = (26, 36, 52)
            border = (60, 80, 110)
            txt_col = (220, 230, 240)
        else:
            bg = (18, 24, 34)
            border = (35, 45, 60)
            txt_col = COLOR_TEXT_MUTED

        UITheme.draw_panel(surface, self.rect, bg_color=bg, border_color=border, border_radius=4)
        UITheme.draw_text(surface, self.text, self.font, color=txt_col, pos=self.rect.center, align="center")


class ProgressBar:
    """Eleganter Fortschrittsbalken mit optionaler Beschriftung."""

    def __init__(
        self,
        rect: pygame.Rect,
        fill_color: Tuple[int, int, int] = COLOR_CURE,
        bg_color: Tuple[int, int, int] = (15, 22, 32),
        border_color: Tuple[int, int, int] = COLOR_PANEL_BORDER,
        border_radius: int = 4,
    ):
        self.rect = rect
        self.fill_color = fill_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius

    def draw(self, surface: pygame.Surface, value: float, max_value: float = 100.0, text: str = "", font: Optional[pygame.font.Font] = None) -> None:
        """Zeichnet den Fortschrittsbalken."""
        ratio = max(0.0, min(1.0, value / max_value if max_value > 0 else 0.0))
        
        # Hintergrund
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        
        # Füllung
        if ratio > 0:
            fill_width = int(self.rect.width * ratio)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=self.border_radius)

        # Rahmen
        pygame.draw.rect(surface, self.border_color, self.rect, width=1, border_radius=self.border_radius)

        # Text zentriert
        if text and font:
            UITheme.draw_text(surface, text, font, color=(255, 255, 255), pos=self.rect.center, align="center")


def render_multiline_tooltip(
    surface: pygame.Surface,
    lines: List[str],
    font: pygame.font.Font,
    pos: Tuple[int, int],
    screen_bounds: pygame.Rect,
) -> None:
    """Zeichnet einen mehrzeiligen Tooltip nahe der Mausposition."""
    padding = 8
    rendered_lines = [font.render(l, True, (240, 240, 240)) for l in lines]
    max_w = max((r.get_width() for r in rendered_lines), default=60)
    total_h = sum(r.get_height() + 2 for r in rendered_lines)

    x, y = pos[0] + 12, pos[1] + 12
    # Bildschirmgrenzen beachten
    if x + max_w + padding * 2 > screen_bounds.right:
        x = pos[0] - max_w - padding * 2 - 4
    if y + total_h + padding * 2 > screen_bounds.bottom:
        y = pos[1] - total_h - padding * 2 - 4

    box_rect = pygame.Rect(x, y, max_w + padding * 2, total_h + padding * 2)
    pygame.draw.rect(surface, (12, 16, 24, 240), box_rect, border_radius=5)
    pygame.draw.rect(surface, (80, 110, 150), box_rect, width=1, border_radius=5)

    curr_y = y + padding
    for r in rendered_lines:
        surface.blit(r, (x + padding, curr_y))
        curr_y += r.get_height() + 2
