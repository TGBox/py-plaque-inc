"""UI-Design-System, Typografie und Zeichenhelfer für Plague Inc. Optik."""

from typing import Tuple, Optional
import pygame

from py_plaque_inc.config import (
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
)


class UITheme:
    """Verwaltet geladene Schriften und konsistente Styling-Regeln."""

    def __init__(self):
        pygame.font.init()
        # Systemschriften mit Fallbacks für moderne, klare Lesbarkeit
        self.font_title = pygame.font.SysFont("Segoe UI, Arial, Helvetica", 24, bold=True)
        self.font_header = pygame.font.SysFont("Segoe UI, Arial, Helvetica", 18, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI, Arial, Helvetica", 14)
        self.font_body_bold = pygame.font.SysFont("Segoe UI, Arial, Helvetica", 14, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI, Arial, Helvetica", 12)
        self.font_tiny = pygame.font.SysFont("Segoe UI, Arial, Helvetica", 10)

    @staticmethod
    def draw_panel(
        surface: pygame.Surface,
        rect: pygame.Rect,
        bg_color: Tuple[int, int, int] = COLOR_PANEL_BG,
        border_color: Tuple[int, int, int] = COLOR_PANEL_BORDER,
        border_radius: int = 6,
        border_width: int = 1,
    ) -> None:
        """Zeichnet ein sauberes Panel im Plague-Inc.-Stil."""
        pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        if border_width > 0:
            pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)

    @staticmethod
    def draw_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int] = COLOR_TEXT_PRIMARY,
        pos: Tuple[int, int] = (0, 0),
        align: str = "left",  # "left", "center", "right"
    ) -> pygame.Rect:
        """Rendert Text mit horizontaler Ausrichtung."""
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        if align == "left":
            rect.topleft = pos
        elif align == "center":
            rect.center = pos
        elif align == "right":
            rect.topright = pos
        surface.blit(rendered, rect)
        return rect
