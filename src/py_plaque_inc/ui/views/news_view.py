"""Detailansicht und Archiv für Nachrichten (News-Modal mit Volltext)."""

from typing import List, Tuple, Optional
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_DANGER,
    COLOR_DNA,
)
from py_plaque_inc.model.world import World
from py_plaque_inc.model.events import NewsPriority, NewsItem
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Bricht Text anhand von Wörtern um, sodass jede Zeile <= max_width ist."""
    words = text.split(" ")
    lines: List[str] = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            # Falls ein einzelnes Wort breiter als max_width ist
            if font.size(word)[0] > max_width:
                part = ""
                for char in word:
                    if font.size(part + char)[0] <= max_width:
                        part += char
                    else:
                        lines.append(part)
                        part = char
                current_line = part
            else:
                current_line = word

    if current_line:
        lines.append(current_line)

    return lines or [text]


class NewsDetailModal:
    """Zeigt die aktuelle Nachricht in voller Länge sowie die gesamte Nachrichten-Historie."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 310, SCREEN_HEIGHT // 2 - 250, 620, 500)
        
        self.btn_close = Button(
            pygame.Rect(self.panel_rect.right - 96, self.panel_rect.bottom - 46, 80, 32),
            "SCHLIESSEN",
            theme.font_tiny,
            bg_color=(35, 45, 60),
            hover_color=(50, 65, 85),
        )

        self.btn_close_x = Button(
            pygame.Rect(self.panel_rect.right - 36, self.panel_rect.top + 14, 24, 24),
            "X",
            theme.font_body_bold,
            bg_color=(25, 34, 48),
            hover_color=(60, 30, 35),
            border_radius=3,
        )

        # Scroll-Buttons für die Historie
        self.btn_scroll_up = Button(
            pygame.Rect(self.panel_rect.right - 32, self.panel_rect.top + 195, 20, 20),
            "^",
            theme.font_tiny,
            bg_color=(25, 35, 48),
            border_radius=2,
        )
        self.btn_scroll_down = Button(
            pygame.Rect(self.panel_rect.right - 32, self.panel_rect.bottom - 68, 20, 20),
            "v",
            theme.font_tiny,
            bg_color=(25, 35, 48),
            border_radius=2,
        )

        self.scroll_y: float = 0.0
        self.max_scroll: float = 0.0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gibt True zurück, wenn das Modal geschlossen werden soll."""
        if self.btn_close.handle_event(event) or self.btn_close_x.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.panel_rect.collidepoint(event.pos):
                return True

        # Scroll-Buttons
        if self.btn_scroll_up.handle_event(event):
            self.scroll_y = max(0.0, self.scroll_y - 40.0)
            return False
        if self.btn_scroll_down.handle_event(event):
            self.scroll_y = min(self.max_scroll, self.scroll_y + 40.0)
            return False

        # Mausrad-Scrollen
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0.0, min(self.max_scroll, self.scroll_y - event.y * 36.0))
            return False

        return False

    def draw(self, surface: pygame.Surface, world: World) -> None:
        """Rendert das Nachrichten-Modal inklusive Volltext und Scroll-Historie."""
        # 1. Abdunkelungs-Layer im Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # 2. Panel-Hintergrund
        UITheme.draw_panel(
            surface,
            self.panel_rect,
            bg_color=(16, 22, 32),
            border_color=(45, 65, 90),
            border_radius=8,
            border_width=2,
        )

        # 3. Kopfzeile
        UITheme.draw_text(
            surface,
            "GLOBALE NACHRICHTENZENTRALE",
            self.theme.font_title,
            color=(255, 255, 255),
            pos=(self.panel_rect.left + 20, self.panel_rect.top + 16),
        )
        UITheme.draw_text(
            surface,
            "Eilmeldungen & Ereignis-Chronik in voller Länge",
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(self.panel_rect.left + 20, self.panel_rect.top + 46),
        )

        self.btn_close_x.draw(surface)

        # Trennlinie
        pygame.draw.line(
            surface,
            (35, 48, 65),
            (self.panel_rect.left + 20, self.panel_rect.top + 68),
            (self.panel_rect.right - 20, self.panel_rect.top + 68),
            1,
        )

        # ==========================================
        # 4. AKTUELLE MELDUNG (Fokus / Volltext)
        # ==========================================
        prio = world.news_mgr.current_priority
        if prio == NewsPriority.ALERT:
            card_bg = (42, 16, 18)
            card_border = COLOR_DANGER
            prio_badge = "[ALARM-MELDUNG]"
        elif prio == NewsPriority.MILESTONE:
            card_bg = (38, 30, 14)
            card_border = COLOR_DNA
            prio_badge = "[MEILENSTEIN]"
        elif prio == NewsPriority.INFO:
            card_bg = (16, 30, 44)
            card_border = (0, 150, 220)
            prio_badge = "[INFORMATION]"
        else:
            card_bg = (20, 26, 36)
            card_border = (50, 65, 85)
            prio_badge = "[SCHLAGZEILE]"

        text_max_w = self.panel_rect.width - 70
        full_headline = world.news_mgr.current_headline
        wrapped_headline = wrap_text(full_headline, self.theme.font_body_bold, text_max_w)
        line_height = 20
        card_h = 32 + len(wrapped_headline) * line_height + 10
        card_rect = pygame.Rect(self.panel_rect.left + 20, self.panel_rect.top + 78, self.panel_rect.width - 40, card_h)

        UITheme.draw_panel(surface, card_rect, bg_color=card_bg, border_color=card_border, border_radius=6, border_width=1)
        
        # Badge und Tag
        tag_str = f"{prio_badge}  |  Tag {world.current_day}"
        UITheme.draw_text(surface, tag_str, self.theme.font_tiny, color=card_border, pos=(card_rect.left + 12, card_rect.top + 8))

        # Volltext des aktuellen Eintrags
        ty = card_rect.top + 28
        for line in wrapped_headline:
            UITheme.draw_text(surface, line, self.theme.font_body_bold, color=(255, 255, 255), pos=(card_rect.left + 12, ty))
            ty += line_height

        # ==========================================
        # 5. NACHRICHTEN-HISTORIE (Scrollbar)
        # ==========================================
        hist_header_y = card_rect.bottom + 12
        history_items = list(reversed(world.news_mgr.news_history))
        count_txt = f"NACHRICHTEN-CHRONIK ({len(history_items)} Meldungen):"
        UITheme.draw_text(surface, count_txt, self.theme.font_body_bold, color=COLOR_TEXT_PRIMARY, pos=(self.panel_rect.left + 20, hist_header_y))

        # Viewport für Historie
        view_top = hist_header_y + 24
        view_bottom = self.panel_rect.bottom - 56
        view_h = view_bottom - view_top
        view_rect = pygame.Rect(self.panel_rect.left + 20, view_top, self.panel_rect.width - 64, view_h)

        # Panel-Hintergrund für Viewport
        pygame.draw.rect(surface, (12, 16, 24), view_rect, border_radius=4)
        pygame.draw.rect(surface, (30, 42, 58), view_rect, width=1, border_radius=4)

        # Gesamthöhe der Liste berechnen
        item_text_w = view_rect.width - 24
        rendered_items = []
        total_content_h = 8
        for item in history_items:
            lines = wrap_text(item.text, self.theme.font_small, item_text_w)
            item_h = 20 + len(lines) * 16 + 8
            rendered_items.append((item, lines, item_h))
            total_content_h += item_h

        self.max_scroll = max(0.0, float(total_content_h - view_h))
        self.scroll_y = max(0.0, min(self.max_scroll, self.scroll_y))

        # Mit Clipping zeichnen
        old_clip = surface.get_clip()
        surface.set_clip(view_rect)

        curr_y = view_top + 6 - int(self.scroll_y)
        for item, lines, item_h in rendered_items:
            # Nur sichtbare zeichnen
            if curr_y + item_h >= view_top and curr_y <= view_bottom:
                # Farbkodierung
                if item.priority == NewsPriority.ALERT:
                    i_col = COLOR_DANGER
                    i_icon = "[!]"
                elif item.priority == NewsPriority.MILESTONE:
                    i_col = COLOR_DNA
                    i_icon = "[*]"
                elif item.priority == NewsPriority.INFO:
                    i_col = (0, 160, 240)
                    i_icon = "[i]"
                else:
                    i_col = COLOR_TEXT_MUTED
                    i_icon = "[+]"

                # Tag-Badge
                UITheme.draw_text(
                    surface,
                    f"{i_icon} Tag {item.day}",
                    self.theme.font_tiny,
                    color=i_col,
                    pos=(view_rect.left + 8, curr_y),
                )

                # Textzeilen
                ly = curr_y + 16
                for l in lines:
                    UITheme.draw_text(surface, l, self.theme.font_small, color=(220, 225, 235), pos=(view_rect.left + 8, ly))
                    ly += 16

                # Dezente Trennlinie
                pygame.draw.line(
                    surface,
                    (24, 32, 44),
                    (view_rect.left + 8, curr_y + item_h - 4),
                    (view_rect.right - 8, curr_y + item_h - 4),
                    1,
                )

            curr_y += item_h

        surface.set_clip(old_clip)

        # Scrollbar / Buttons zeichnen falls scrollbar
        if self.max_scroll > 0:
            self.btn_scroll_up.draw(surface)
            self.btn_scroll_down.draw(surface)

            # Scrollbalken-Schiene
            bar_track = pygame.Rect(self.panel_rect.right - 28, view_top + 26, 12, view_h - 52)
            pygame.draw.rect(surface, (18, 25, 35), bar_track, border_radius=3)

            # Scroll-Daumen
            thumb_ratio = max(0.15, min(1.0, view_h / total_content_h))
            thumb_h = int(bar_track.height * thumb_ratio)
            scroll_pct = self.scroll_y / self.max_scroll if self.max_scroll > 0 else 0.0
            thumb_y = bar_track.top + int(scroll_pct * (bar_track.height - thumb_h))
            thumb_rect = pygame.Rect(bar_track.x, thumb_y, bar_track.width, thumb_h)
            pygame.draw.rect(surface, (55, 80, 115), thumb_rect, border_radius=3)

        # 6. Schließen-Button
        self.btn_close.draw(surface)
