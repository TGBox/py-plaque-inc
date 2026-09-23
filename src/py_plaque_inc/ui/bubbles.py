"""Klickbare schwebende DNA- und Heilmittelblasen auf der Weltkarte."""

from typing import List, Tuple, Optional
import math
import pygame

from py_plaque_inc.config import (
    COLOR_DNA_BUBBLE_RED,
    COLOR_DNA_BUBBLE_ORANGE,
    COLOR_CURE_BUBBLE_BLUE,
    COLOR_DNA,
)


class BubbleView:
    """Verwaltet und zeichnet klickbare Blasen mit Schwebeanimation."""

    def __init__(self):
        self.time: float = 0.0

    def update(self, dt: float) -> None:
        self.time += dt * 4.0

    def get_bubble_at_pos(self, pos: Tuple[int, int], bubbles: List[dict]) -> Optional[dict]:
        """Prüft, ob der Klick innerhalb einer Blase liegt."""
        mx, my = pos
        # Rückwärts iterieren, um oberste Blase zuerst zu treffen
        for b in reversed(bubbles):
            bx, by = b["pos"]
            # Berechne aktuellen Bobbing-Offset
            bob = math.sin(self.time + hash(b.get("country_id", "")) % 10) * 3.0
            actual_y = by + bob
            dist = math.hypot(mx - bx, my - actual_y)
            if dist <= 16:  # Klick-Radius
                return b
        return None

    def draw(self, surface: pygame.Surface, bubbles: List[dict], font: pygame.font.Font) -> None:
        """Zeichnet alle aktiven Blasen mit Glüheffekt und Symbol."""
        for b in bubbles:
            b_type = b.get("type", "red")
            bx, by = b["pos"]
            bob = math.sin(self.time + hash(b.get("country_id", "")) % 10) * 3.0
            y = int(by + bob)
            x = int(bx)

            if b_type == "red":
                main_col = COLOR_DNA_BUBBLE_RED
                glow_col = (255, 100, 100)
                icon_text = "!"
            elif b_type == "orange":
                main_col = COLOR_DNA_BUBBLE_ORANGE
                glow_col = (255, 200, 50)
                icon_text = "DNA"
            else:  # blue
                main_col = COLOR_CURE_BUBBLE_BLUE
                glow_col = (100, 220, 255)
                icon_text = "+"

            # Pulsierender äußerer Glühring
            pulse_r = int(14 + math.sin(self.time * 2.0) * 2.5)
            glow_surf = pygame.Surface((pulse_r * 2 + 6, pulse_r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (glow_col[0], glow_col[1], glow_col[2], 90),
                (pulse_r + 3, pulse_r + 3),
                pulse_r,
                width=2,
            )
            surface.blit(glow_surf, (x - pulse_r - 3, y - pulse_r - 3))

            # Fester innerer Kreis
            pygame.draw.circle(surface, main_col, (x, y), 12)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 12, width=1)

            # Glanzpunkt oben links
            pygame.draw.circle(surface, (255, 255, 255, 180), (x - 4, y - 4), 3)

            # Icon-Text
            if icon_text:
                txt = font.render(icon_text, True, (255, 255, 255))
                surface.blit(txt, txt.get_rect(center=(x, y)))
