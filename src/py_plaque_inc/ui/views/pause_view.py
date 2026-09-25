"""Pausenmenü während des Spiels (Fortsetzen, Hauptmenü, Beenden)."""

from typing import Optional
import pygame

from py_plaque_inc.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT_MUTED
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button


class PauseMenuModal:
    """Modales Pausenmenü mit Optionen zur Fortsetzung, Rückkehr zum Hauptmenü oder Spielabbruch."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 135, 320, 270)

        bw = 240
        bh = 40
        bx = self.panel_rect.centerx - bw // 2
        by = self.panel_rect.top + 75

        self.btn_resume = Button(
            pygame.Rect(bx, by, bw, bh),
            "WEITERSPIELEN",
            theme.font_body_bold,
            bg_color=(25, 45, 35),
            hover_color=(35, 70, 50),
            border_color=(60, 160, 100),
        )

        self.btn_to_menu = Button(
            pygame.Rect(bx, by + 52, bw, bh),
            "ZUM HAUPTMENÜ",
            theme.font_body_bold,
            bg_color=(25, 35, 55),
            hover_color=(38, 55, 85),
            border_color=(60, 110, 170),
        )

        self.btn_quit = Button(
            pygame.Rect(bx, by + 104, bw, bh),
            "SPIEL BEENDEN",
            theme.font_body_bold,
            bg_color=(45, 20, 25),
            hover_color=(75, 30, 38),
            border_color=(190, 55, 65),
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Gibt 'resume', 'menu', 'quit' zurück, oder None."""
        if self.btn_resume.handle_event(event):
            return "resume"
        if self.btn_to_menu.handle_event(event):
            return "menu"
        if self.btn_quit.handle_event(event):
            return "quit"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.panel_rect.collidepoint(event.pos):
                return "resume"

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das Pausenmenü."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        UITheme.draw_panel(
            surface,
            self.panel_rect,
            bg_color=(16, 22, 32),
            border_color=(50, 70, 95),
            border_radius=8,
            border_width=2,
        )

        UITheme.draw_text(
            surface,
            "SPIEL PAUSIERT",
            self.theme.font_header,
            color=(255, 255, 255),
            pos=(self.panel_rect.centerx, self.panel_rect.top + 20),
            align="center",
        )

        UITheme.draw_text(
            surface,
            "Wähle eine Option:",
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(self.panel_rect.centerx, self.panel_rect.top + 46),
            align="center",
        )

        self.btn_resume.draw(surface)
        self.btn_to_menu.draw(surface)
        self.btn_quit.draw(surface)
