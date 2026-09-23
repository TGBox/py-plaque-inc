"""Hauptansicht des laufenden Spiels: Weltkarte, Blasen, Partikel, HUD und Modals."""

from typing import Optional, Tuple
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    MAP_X,
    MAP_Y,
    MAP_WIDTH,
    MAP_HEIGHT,
    COLOR_BG,
    COLOR_DNA,
    COLOR_DANGER,
    COLOR_CURE,
)
from py_plaque_inc.model.world import World, GameOutcome
from py_plaque_inc.map.renderer import MapRenderer
from py_plaque_inc.engine.particles import ParticleSystem
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.hud import HUDView
from py_plaque_inc.ui.bubbles import BubbleView
from py_plaque_inc.ui.views.country_view import CountryDetailView


class GameView:
    """Verbindet Karte, HUD, Blasen und Animationen im Spiel."""

    def __init__(self, theme: UITheme):
        self.theme = theme

        # Karten-Renderer (zentraler Bereich)
        self.map_renderer = MapRenderer(pygame.Rect(MAP_X, MAP_Y, MAP_WIDTH, MAP_HEIGHT))
        
        # Systeme
        self.particles = ParticleSystem()
        self.bubble_view = BubbleView()
        self.hud = HUDView(theme)
        self.country_detail = CountryDetailView(theme)

        # Zustand
        self.is_showing_country_detail: bool = False
        self.selected_country_id: Optional[str] = None

    def handle_event(self, event: pygame.event.Event, world: World) -> Optional[str]:
        """
        Verarbeitet Events im In-Game-Modus.
        Gibt 'evolution', 'game_over' oder None zurück.
        """
        # Wenn Spiel vorbei ist
        if world.outcome != GameOutcome.ONGOING:
            return "game_over"

        # Wenn Country-Detail offen ist
        if self.is_showing_country_detail and self.selected_country_id:
            country = world.countries.get(self.selected_country_id)
            if country and self.country_detail.handle_event(event):
                self.is_showing_country_detail = False
            return None

        # HUD Events
        country_name = world.countries[self.selected_country_id].name if self.selected_country_id else None
        hud_action = self.hud.handle_event(event, world)
        
        if hud_action == "evolution":
            return "evolution"
        elif hud_action == "country" and self.selected_country_id:
            self.is_showing_country_detail = True
            return None
        elif hud_action == "spore":
            target = world.trigger_spore_burst()
            if target:
                self.particles.emit_bubble_pop(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, (190, 80, 220), f"Sporen in {target}!")
            return None

        # Mausbewegung über Karte
        if event.type == pygame.MOUSEMOTION:
            self.map_renderer.handle_mouse_motion(event.pos, world.countries)

        # Klick-Events auf der Karte
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 1. Wurde eine schwebende Blase angeklickt?
            clicked_bubble = self.bubble_view.get_bubble_at_pos(event.pos, world.pending_bubbles)
            if clicked_bubble:
                b_type = clicked_bubble.get("type", "red")
                bx, by = clicked_bubble["pos"]
                dna_gain = world.pop_bubble(clicked_bubble)
                world.pending_bubbles.remove(clicked_bubble)

                if b_type == "blue":
                    self.particles.emit_bubble_pop(bx, by, COLOR_CURE, "-Heilmittel!")
                elif b_type == "orange":
                    self.particles.emit_bubble_pop(bx, by, COLOR_DNA, f"+{dna_gain} DNA")
                else:
                    self.particles.emit_bubble_pop(bx, by, (255, 60, 60), f"+{dna_gain} DNA")
                return None

            # 2. Wurde ein Land angeklickt?
            clicked_country = self.map_renderer.get_country_at_pos(event.pos, world.countries)
            if clicked_country:
                # Vor Spielstart: Erstes Land auswählen und Spiel beginnen
                if not world.has_started:
                    world.select_starting_country(clicked_country.id)
                    cx, cy = clicked_country.capital_pos
                    self.particles.emit_country_pulse(cx, cy, (255, 50, 50))
                    self.particles.emit_bubble_pop(cx, cy, (255, 50, 50), "Patient Null!")
                    self.selected_country_id = clicked_country.id
                    self.map_renderer.selected_country_id = clicked_country.id
                else:
                    # Land selektieren und ggf. per Doppelklick / Klick öffnen
                    if self.selected_country_id == clicked_country.id:
                        self.is_showing_country_detail = True
                    else:
                        self.selected_country_id = clicked_country.id
                        self.map_renderer.selected_country_id = clicked_country.id

        return None

    def update(self, dt: float, world: World) -> None:
        """Aktualisiert Animationen, Partikel und Blasen."""
        self.map_renderer.update(dt)
        self.bubble_view.update(dt)
        self.particles.update()

        # Puls-Effekte von Ländern reduzieren
        for c in world.countries.values():
            if c.infected_pulse > 0:
                c.infected_pulse = max(0.0, c.infected_pulse - dt * 2.0)

    def draw(self, surface: pygame.Surface, world: World) -> None:
        """Rendert die Spieloberfläche."""
        surface.fill(COLOR_BG)

        # 1. Weltkarte
        self.map_renderer.draw(surface, world.countries, world.transport_mgr, self.theme.font_small)

        # 2. Blasen
        self.bubble_view.draw(surface, world.pending_bubbles, self.theme.font_tiny)

        # 3. Partikel & Effekte
        self.particles.draw(surface, self.theme.font_body_bold)

        # Vor Spielbeginn: Banner zur Auswahl des Startlandes
        if not world.has_started:
            banner_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, 80, 560, 42)
            UITheme.draw_panel(surface, banner_rect, bg_color=(20, 26, 38), border_color=(0, 180, 255), border_radius=6)
            UITheme.draw_text(
                surface,
                "👉 Klicke auf ein beliebiges Land, um den ersten Patienten zu infizieren!",
                self.theme.font_body_bold,
                color=(255, 255, 255),
                pos=banner_rect.center,
                align="center",
            )

        # 4. HUD (Kopf- & Fußzeile)
        country_name = world.countries[self.selected_country_id].name if self.selected_country_id else None
        self.hud.draw(surface, world, country_name)

        # 5. Detail-Popup falls aktiv
        if self.is_showing_country_detail and self.selected_country_id:
            c = world.countries.get(self.selected_country_id)
            if c:
                self.country_detail.draw(surface, c)
