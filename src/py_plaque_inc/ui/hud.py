"""Kopf- und Fußzeile (HUD) für Datum, Tempo, DNA, Heilmittel, News-Ticker und Statistik."""

from typing import Tuple, Optional, Callable
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_DNA,
    COLOR_CURE,
    COLOR_DANGER,
    COLOR_SUCCESS,
)
from py_plaque_inc.model.world import World
from py_plaque_inc.model.events import NewsPriority
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button, ProgressBar


def format_number(val: int) -> str:
    """Formatiert große Zahlen lesbar (z.B. 1.4 Mrd, 24.5 Mio, 120k)."""
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f} Mrd"
    elif val >= 1_000_000:
        return f"{val / 1_000_000:.1f} Mio"
    elif val >= 1_000:
        return f"{val / 1_000:.1f}k"
    return str(val)


class HUDView:
    """Verwaltet und zeichnet das gesamte Head-Up-Display."""

    def __init__(self, theme: UITheme):
        self.theme = theme

        # Geschwindigkeits-Buttons (oben rechts)
        self.speed_buttons = [
            Button(pygame.Rect(SCREEN_WIDTH - 210, 12, 32, 28), "||", theme.font_small),
            Button(pygame.Rect(SCREEN_WIDTH - 172, 12, 32, 28), ">", theme.font_small),
            Button(pygame.Rect(SCREEN_WIDTH - 134, 12, 32, 28), ">>", theme.font_small),
            Button(pygame.Rect(SCREEN_WIDTH - 96, 12, 32, 28), ">>>", theme.font_small),
        ]

        # Cure-Fortschrittsbalken (oben Mitte)
        self.cure_bar = ProgressBar(
            pygame.Rect(440, 16, 220, 20),
            fill_color=COLOR_CURE,
        )

        # Aktions-Buttons (unten rechts)
        self.btn_evolution = Button(
            pygame.Rect(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 48, 150, 36),
            "🧬 EVOLUTION",
            theme.font_header,
            bg_color=(35, 50, 72),
            hover_color=(50, 75, 110),
            border_color=COLOR_DNA,
            text_color=(255, 255, 255),
        )

        self.btn_country = Button(
            pygame.Rect(SCREEN_WIDTH - 330, SCREEN_HEIGHT - 48, 150, 36),
            "🌍 LAND-INFO",
            theme.font_body_bold,
            bg_color=(25, 34, 48),
            hover_color=(38, 50, 70),
        )

        self.btn_spore = Button(
            pygame.Rect(SCREEN_WIDTH - 490, SCREEN_HEIGHT - 48, 150, 36),
            "🍄 SPOREN",
            theme.font_body_bold,
            bg_color=(45, 30, 48),
            hover_color=(65, 45, 70),
            border_color=(190, 80, 220),
        )

        # Nachrichten-Kasten (unten links, klickbar für Volltext)
        self.news_rect = pygame.Rect(20, SCREEN_HEIGHT - 56, 450, 48)
        self.is_news_hovered: bool = False

    def handle_event(self, event: pygame.event.Event, world: World) -> Optional[str]:
        """
        Verarbeitet HUD-Interaktionen.
        Gibt Aktions-Strings zurück: 'evolution', 'country', 'news', 'spore', None.
        """
        # Hover über News-Box
        if event.type == pygame.MOUSEMOTION:
            self.is_news_hovered = self.news_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.news_rect.collidepoint(event.pos):
                return "news"

        # Geschwindigkeits-Klicks
        for idx, btn in enumerate(self.speed_buttons):
            if btn.handle_event(event):
                world.set_speed(idx)
                return None

        # Aktions-Buttons
        if self.btn_evolution.handle_event(event):
            return "evolution"

        if self.btn_country.handle_event(event):
            return "country"

        if self.btn_spore.handle_event(event):
            return "spore"

        return None

    def draw(self, surface: pygame.Surface, world: World, selected_country_name: Optional[str] = None) -> None:
        """Zeichnet Kopf- und Fußzeile."""
        # ==========================================
        # 1. KOPFZEILE (Top Bar)
        # ==========================================
        top_bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 54)
        UITheme.draw_panel(surface, top_bar_rect, bg_color=(14, 18, 26), border_color=(28, 38, 52), border_radius=0)

        # Titel & Pathogen
        pathogen_txt = f"{world.pathogen.name} ({world.pathogen.pathogen_type.value})"
        UITheme.draw_text(surface, pathogen_txt, self.theme.font_header, color=(255, 255, 255), pos=(20, 10))

        # Datum
        date_str = world.current_calendar_date.strftime("%d. %B %Y")
        day_str = f"Tag {world.current_day}  •  {date_str}"
        UITheme.draw_text(surface, day_str, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(20, 32))

        # DNA-Punkte (Hexagon/Pill Badge)
        dna_rect = pygame.Rect(290, 12, 120, 30)
        UITheme.draw_panel(surface, dna_rect, bg_color=(35, 26, 12), border_color=COLOR_DNA, border_radius=15)
        dna_txt = f"🧬 {world.pathogen.dna_points} DNA"
        UITheme.draw_text(surface, dna_txt, self.theme.font_body_bold, color=COLOR_DNA, pos=dna_rect.center, align="center")

        # Heilmittelforschung
        cure_txt = f"Heilmittel: {world.cure_progress:.1f}%"
        self.cure_bar.draw(
            surface,
            value=world.cure_progress,
            max_value=100.0,
            text=cure_txt,
            font=self.theme.font_small,
        )

        # Geschwindigkeits-Buttons zeichnen & aktiven Button hervorheben
        for idx, btn in enumerate(self.speed_buttons):
            if world.sim_speed == idx:
                btn.border_color = (0, 190, 255)
                btn.text_color = (0, 190, 255)
            else:
                btn.border_color = COLOR_PANEL_BORDER
                btn.text_color = COLOR_TEXT_PRIMARY
            btn.draw(surface)

        # ==========================================
        # 2. FUSSZEILE (Bottom Bar)
        # ==========================================
        bot_bar_rect = pygame.Rect(0, SCREEN_HEIGHT - 64, SCREEN_WIDTH, 64)
        UITheme.draw_panel(surface, bot_bar_rect, bg_color=(14, 18, 26), border_color=(28, 38, 52), border_radius=0)

        # Nachrichten-Laufband (News Ticker - klickbar für Volltext)
        news_rect = self.news_rect
        
        # Farbe nach Priorität
        prio = world.news_mgr.current_priority
        if prio == NewsPriority.ALERT:
            n_bg = (45, 18, 20)
            n_border = COLOR_DANGER
            n_icon = "⚠️ ALARM:"
        elif prio == NewsPriority.MILESTONE:
            n_bg = (38, 32, 16)
            n_border = COLOR_DNA
            n_icon = "⭐ MEILENSTEIN:"
        elif prio == NewsPriority.INFO:
            n_bg = (18, 32, 45)
            n_border = (0, 150, 220)
            n_icon = "ℹ️ INFO:"
        else:
            n_bg = (18, 22, 30)
            n_border = (35, 45, 60)
            n_icon = "📰 NEWS:"

        # Hover-Effekt
        border_width = 1
        if self.is_news_hovered:
            n_bg = tuple(min(255, c + 15) for c in n_bg)
            n_border = (120, 180, 240)
            border_width = 2

        UITheme.draw_panel(surface, news_rect, bg_color=n_bg, border_color=n_border, border_radius=4, border_width=border_width)
        UITheme.draw_text(surface, n_icon, self.theme.font_tiny, color=n_border, pos=(news_rect.left + 8, news_rect.top + 6))
        
        # Klick-Hinweis rechts oben
        hint_col = (160, 215, 255) if self.is_news_hovered else (90, 115, 140)
        UITheme.draw_text(
            surface,
            "Volltext 🔍",
            self.theme.font_tiny,
            color=hint_col,
            pos=(news_rect.right - 8, news_rect.top + 6),
            align="right",
        )

        # Headline mit Abschnitten
        headline = world.news_mgr.current_headline
        if len(headline) > 58:
            headline = headline[:55] + "..."
        UITheme.draw_text(surface, headline, self.theme.font_body, color=(240, 240, 240), pos=(news_rect.left + 8, news_rect.top + 22))

        # Globale Weltstatistik (Mitte)
        stats_x = 485
        stats_y = SCREEN_HEIGHT - 54

        # Gesunde
        h_str = f"Gesund: {format_number(world.total_healthy)}"
        UITheme.draw_text(surface, h_str, self.theme.font_small, color=COLOR_SUCCESS, pos=(stats_x, stats_y))

        # Infizierte
        i_str = f"Infiziert: {format_number(world.total_infected)}"
        UITheme.draw_text(surface, i_str, self.theme.font_small, color=COLOR_DANGER, pos=(stats_x, stats_y + 16))

        # Tote
        d_str = f"Tot: {format_number(world.total_dead)}"
        UITheme.draw_text(surface, d_str, self.theme.font_small, color=COLOR_TEXT_MUTED, pos=(stats_x, stats_y + 32))

        # Buttons unten rechts
        self.btn_evolution.draw(surface)

        if selected_country_name:
            self.btn_country.text = f"🌍 {selected_country_name[:11].upper()}"
            self.btn_country.enabled = True
        else:
            self.btn_country.text = "🌍 LAND-INFO"
            self.btn_country.enabled = False
        self.btn_country.draw(surface)

        # Sporen-Button nur für Pilz
        has_spore = (
            world.pathogen.pathogen_type.value == "Pilz"
            and world.pathogen.upgrades["spec_fungus_spore_1"].unlocked
        )
        if has_spore:
            self.btn_spore.draw(surface)
