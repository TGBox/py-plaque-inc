"""Spielende-Bildschirm mit Sieges-/Niederlage-Auswertung und historischem Kurvendiagramm."""

from typing import List, Tuple, Optional
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_CURE,
    COLOR_DNA,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
)
from py_plaque_inc.model.world import World, GameOutcome
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button
from py_plaque_inc.ui.hud import format_number


class GameOverView:
    """Zeigt Abschlussstatistiken und den zeitlichen Infektionsverlauf als Graph an."""

    def __init__(self, theme: UITheme):
        self.theme = theme

        self.btn_restart = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 70, 200, 46),
            "HAUPTMENÜ",
            theme.font_header,
            bg_color=(35, 55, 80),
            hover_color=(50, 75, 110),
            border_color=(0, 180, 255),
        )

        self.btn_quit = Button(
            pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 70, 200, 46),
            "SPIEL BEENDEN",
            theme.font_header,
            bg_color=(45, 20, 25),
            hover_color=(75, 30, 38),
            border_color=(190, 55, 65),
        )

        self.graph_rect = pygame.Rect(140, 220, 1000, 260)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Gibt 'restart', 'quit' oder None zurück."""
        if self.btn_restart.handle_event(event):
            return "restart"
        if self.btn_quit.handle_event(event):
            return "quit"
        return None

    def draw(self, surface: pygame.Surface, world: World) -> None:
        """Rendert den gesamten Game-Over-Screen mit Zeitverlaufskurven."""
        surface.fill(COLOR_BG)

        # 1. Titel & Ausgang
        if world.outcome == GameOutcome.VICTORY:
            title_text = "SIEG: DIE MENSCHHEIT WURDE AUSGELÖSCHT"
            title_col = (255, 50, 50)
            sub_text = f"'{world.pathogen.name}' hat jeden einzelnen Menschen auf der Erde infiziert und eliminiert."
        elif world.outcome == GameOutcome.DEFEAT_CURE:
            title_text = "NIEDERLAGE: HEILMITTEL ERFOLGREICH ENTWICKELT"
            title_col = (0, 200, 255)
            sub_text = f"Die Weltgemeinschaft hat das Heilmittel fertiggestellt und '{world.pathogen.name}' besiegt."
        else:
            title_text = "NIEDERLAGE: SEUCHE AUSGESTORBEN"
            title_col = (180, 180, 190)
            sub_text = f"Alle Infizierten von '{world.pathogen.name}' sind gestorben, bevor eine weltweite Ausbreitung gelang."

        UITheme.draw_text(surface, title_text, self.theme.font_title, color=title_col, pos=(SCREEN_WIDTH // 2, 45), align="center")
        UITheme.draw_text(surface, sub_text, self.theme.font_body, color=COLOR_TEXT_PRIMARY, pos=(SCREEN_WIDTH // 2, 80), align="center")

        # 2. Kennzahlen-Karten
        card_y = 115
        card_w = 230
        card_h = 75
        gap = 25
        start_x = (SCREEN_WIDTH - (4 * card_w + 3 * gap)) // 2

        kpis = [
            ("SPIELDAUER", f"{world.current_day} Tage", (255, 255, 255)),
            ("TODESOPFER", f"{format_number(world.total_dead)} ({world.total_dead / world.total_population * 100:.1f}%)", (220, 60, 60)),
            ("HEILMITTEL-STAND", f"{world.cure_progress:.1f}%", (0, 190, 255)),
            ("MUTATIONEN", f"{world.pathogen.unlocked_count} Upgrades", COLOR_DNA),
        ]

        for i, (label, val, col) in enumerate(kpis):
            r = pygame.Rect(start_x + i * (card_w + gap), card_y, card_w, card_h)
            UITheme.draw_panel(surface, r, bg_color=(18, 24, 34), border_color=(35, 48, 65), border_radius=6)
            UITheme.draw_text(surface, label, self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(r.centerx, r.top + 14), align="center")
            UITheme.draw_text(surface, val, self.theme.font_header, color=col, pos=(r.centerx, r.top + 38), align="center")

        # 3. Verlaufsgraph (Kurvendiagramm)
        self._draw_history_graph(surface, world.history, world.total_population)

        # 4. Buttons
        self.btn_restart.draw(surface)
        self.btn_quit.draw(surface)

    def _draw_history_graph(
        self,
        surface: pygame.Surface,
        history: List[Tuple[int, int, int, int, float]],
        total_pop: int,
    ) -> None:
        """Zeichnet das Liniendiagramm für Gesunde, Infizierte, Tote und Heilmittel."""
        # Panel-Hintergrund
        UITheme.draw_panel(surface, self.graph_rect, bg_color=(14, 18, 26), border_color=(35, 50, 70), border_radius=6)

        # Titel & Legende
        UITheme.draw_text(surface, "HISTORISCHER VERLAUF DER PANDEMIE", self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(self.graph_rect.left + 16, self.graph_rect.top + 12))

        # Legende oben rechts
        leg_x = self.graph_rect.right - 460
        leg_y = self.graph_rect.top + 12
        items = [
            ("- Gesunde", COLOR_SUCCESS),
            ("- Infizierte", COLOR_DANGER),
            ("- Tote", (140, 150, 160)),
            ("- Heilmittel %", COLOR_CURE),
        ]
        for name, col in items:
            UITheme.draw_text(surface, name, self.theme.font_tiny, color=col, pos=(leg_x, leg_y))
            leg_x += 110

        if len(history) < 2 or total_pop <= 0:
            return

        # Skalierungs-Parameter
        max_day = max(h[0] for h in history)
        if max_day <= 0:
            max_day = 1

        plot_rect = self.graph_rect.inflate(-40, -50)
        plot_rect.bottom = self.graph_rect.bottom - 15

        # Horizontale Hilfslinien
        for frac in [0.25, 0.5, 0.75, 1.0]:
            ly = int(plot_rect.bottom - frac * plot_rect.height)
            pygame.draw.line(surface, (22, 30, 42), (plot_rect.left, ly), (plot_rect.right, ly), 1)

        # Punkte interpolieren
        pts_healthy = []
        pts_infected = []
        pts_dead = []
        pts_cure = []

        for day, healthy, infected, dead, cure in history:
            x = int(plot_rect.left + (day / max_day) * plot_rect.width)
            
            # Bevölkerungs-Kurven (0 bis total_pop)
            y_h = int(plot_rect.bottom - (healthy / total_pop) * plot_rect.height)
            y_i = int(plot_rect.bottom - (infected / total_pop) * plot_rect.height)
            y_d = int(plot_rect.bottom - (dead / total_pop) * plot_rect.height)

            # Heilmittel (0 bis 100%)
            y_c = int(plot_rect.bottom - (cure / 100.0) * plot_rect.height)

            pts_healthy.append((x, y_h))
            pts_infected.append((x, y_i))
            pts_dead.append((x, y_d))
            pts_cure.append((x, y_c))

        # Linien zeichnen
        if len(pts_healthy) >= 2:
            pygame.draw.lines(surface, COLOR_SUCCESS, False, pts_healthy, 2)
            pygame.draw.lines(surface, COLOR_DANGER, False, pts_infected, 2)
            pygame.draw.lines(surface, (140, 150, 160), False, pts_dead, 2)
            pygame.draw.lines(surface, COLOR_CURE, False, pts_cure, 2)
