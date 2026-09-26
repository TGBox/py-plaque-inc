"""Zentraler Game-Loop und State-Machine für Py-Plaque-Inc."""

from enum import Enum
import sys
from typing import Optional, Tuple
import pygame

from py_plaque_inc.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BG, COLOR_OCEAN_DEEP
from py_plaque_inc.model.pathogen import Pathogen, PathogenType
from py_plaque_inc.model.world import World, GameOutcome
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.views.menu_view import MenuView
from py_plaque_inc.ui.views.game_view import GameView
from py_plaque_inc.ui.views.evolution_view import EvolutionView
from py_plaque_inc.ui.views.game_over_view import GameOverView


class GameState(str, Enum):
    MENU = "menu"
    PLAYING = "playing"
    EVOLUTION = "evolution"
    GAME_OVER = "game_over"


class PlagueGame:
    """Hauptspielklasse: initialisiert Pygame, Views, Auflösung und leitet Frames weiter."""

    def __init__(self):
        # Windows DPI-Awareness aktivieren für verzerrungsfreie Mauskoordinaten
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                try:
                    import ctypes
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

        pygame.init()
        pygame.display.set_caption(TITLE)

        # Basis-Auflösung (virtuelle Zeichenfläche 1280x720)
        self.virtual_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.current_res = "1280x720"
        self.is_fullscreen = False

        # Fenster initialisieren
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Skalierungs-Parameter
        self.scale = 1.0
        self.scaled_w = SCREEN_WIDTH
        self.scaled_h = SCREEN_HEIGHT
        self.offset_x = 0
        self.offset_y = 0
        self._recalc_scaling()

        # Design-System
        self.theme = UITheme()

        # Views
        self.menu_view = MenuView(self.theme)
        self.menu_view.on_change_resolution = self.set_resolution
        self.game_view = GameView(self.theme)
        self.evolution_view = EvolutionView(self.theme)
        self.game_over_view = GameOverView(self.theme)

        # Aktueller Spielzustand
        self.state = GameState.MENU
        self.world: Optional[World] = None

    def _recalc_scaling(self) -> None:
        """Berechnet Seitenverhältnis, Skalierung und Zentrierungs-Offsets neu."""
        w, h = self.screen.get_size()
        self.scale = min(w / SCREEN_WIDTH, h / SCREEN_HEIGHT)
        self.scaled_w = int(SCREEN_WIDTH * self.scale)
        self.scaled_h = int(SCREEN_HEIGHT * self.scale)
        self.offset_x = (w - self.scaled_w) // 2
        self.offset_y = (h - self.scaled_h) // 2

    def set_resolution(self, res_str: str, fullscreen: Optional[bool] = None) -> None:
        """Ändert Fenstergröße / Vollbildmodus."""
        self.current_res = res_str
        w, h = map(int, res_str.split("x"))

        # Wenn Vollbild nicht explizit vorgegeben: 1280x720 ist Fenster, 1080p ist Vollbild
        if fullscreen is None:
            self.is_fullscreen = (res_str != "1280x720")
        else:
            self.is_fullscreen = fullscreen

        flags = pygame.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pygame.display.set_mode((w, h), flags)
        self._recalc_scaling()

        # Menü-Layout an die neue Bildschirmgröße anpassen
        self.menu_view.update_layout(w, h)
        self.menu_view.selected_res = res_str
        for b in self.menu_view.res_buttons:
            b.is_active = (b.tab_id == res_str)

    def toggle_fullscreen(self) -> None:
        """Schaltet zwischen Fenster- und Vollbildmodus um (F11)."""
        if self.is_fullscreen:
            self.set_resolution("1280x720", fullscreen=False)
        else:
            # Desktop-Größe ermitteln (z.B. Ultrawide 2560x1080 oder 1920x1080)
            sizes = pygame.display.get_desktop_sizes()
            target_res = "1920x1080"
            if sizes:
                dw, dh = sizes[0]
                target_res = f"{dw}x{dh}"
            self.set_resolution(target_res, fullscreen=True)

    def start_new_game(
        self,
        pathogen_name: str,
        pathogen_type: PathogenType,
        difficulty: str,
        res_mode: Optional[str] = None,
    ) -> None:
        """Erstellt eine neue Spielwelt und wechselt in den Spielmodus."""
        if res_mode and res_mode != self.current_res:
            self.set_resolution(res_mode)

        pathogen = Pathogen(name=pathogen_name, pathogen_type=pathogen_type)
        self.world = World(pathogen=pathogen, difficulty_name=difficulty)
        self.game_view = GameView(self.theme)
        self.evolution_view = EvolutionView(self.theme)
        self.game_over_view = GameOverView(self.theme)
        self.state = GameState.PLAYING

    def run(self) -> None:
        """Hauptschleife des Spiels."""
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta-Time in Sekunden

            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    break

                self._handle_event(event)

            # 2. Simulation & Update
            self._update(dt)

            # 3. Rendering
            self._draw()

            pygame.display.flip()

        pygame.quit()

    def _handle_event(self, event: pygame.event.Event) -> None:
        """Leitet Events nach Koordinaten-Transformation an die aktive View weiter."""
        # 1. Globale Hotkeys
        if event.type == pygame.KEYDOWN:
            # F11 oder Alt+Enter: Vollbild umschalten
            if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)):
                self.toggle_fullscreen()
                return

            # Zeitsteuerung während des Spiels
            if self.state == GameState.PLAYING and self.world:
                # Leertaste: Pause / Tempo wiederherstellen
                if event.key == pygame.K_SPACE:
                    self.world.toggle_pause()
                    return

                # Tasten 1, 2, 3: Geschwindigkeitsstufen
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    self.world.set_speed(1)
                    return
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.world.set_speed(2)
                    return
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.world.set_speed(3)
                    return
                elif event.key in (pygame.K_0, pygame.K_KP0):
                    self.world.set_speed(0)
                    return

        # 2. Im Hauptmenü: Direkte Verarbeitung mit nativen Bildschirmkoordinaten
        if self.state == GameState.MENU:
            config = self.menu_view.handle_event(event)
            if config == "quit":
                self.is_running = False
            elif config:
                p_name, p_type, diff, res_mode = config
                self.start_new_game(p_name, p_type, diff, res_mode)
            return

        # 3. Maus-Koordinaten auf virtuelle 1280x720 Canvas umrechnen (für Spiel, Evolution, Game Over)
        if hasattr(event, "pos"):
            mx, my = event.pos
            if self.scale > 0:
                if (
                    mx < self.offset_x
                    or mx >= self.offset_x + self.scaled_w
                    or my < self.offset_y
                    or my >= self.offset_y + self.scaled_h
                ):
                    # Klick/Bewegung außerhalb der Spielfläche (in den Letterbox-Rändern)
                    vx, vy = -9999, -9999
                else:
                    vx = int((mx - self.offset_x) / self.scale)
                    vy = int((my - self.offset_y) / self.scale)
                    vx = max(0, min(SCREEN_WIDTH - 1, vx))
                    vy = max(0, min(SCREEN_HEIGHT - 1, vy))
                event = pygame.event.Event(event.type, {**event.__dict__, "pos": (vx, vy)})

        # 4. Weiterleitung an aktive Ansicht
        if self.state == GameState.PLAYING and self.world:
            action = self.game_view.handle_event(event, self.world)
            if action == "evolution":
                self.state = GameState.EVOLUTION
            elif action == "menu":
                self.state = GameState.MENU
                w, h = self.screen.get_size()
                self.menu_view.update_layout(w, h)
            elif action == "quit":
                self.is_running = False
            elif action == "game_over" or self.world.outcome != GameOutcome.ONGOING:
                self.state = GameState.GAME_OVER

        elif self.state == GameState.EVOLUTION and self.world:
            wants_back = self.evolution_view.handle_event(event, self.world.pathogen)
            if wants_back:
                self.state = GameState.PLAYING

        elif self.state == GameState.GAME_OVER:
            action = self.game_over_view.handle_event(event)
            if action == "quit":
                self.is_running = False
            elif action == "restart":
                self.state = GameState.MENU
                w, h = self.screen.get_size()
                self.menu_view.update_layout(w, h)

    def _update(self, dt: float) -> None:
        """Aktualisiert Spielzustand und Views."""
        if self.state == GameState.PLAYING and self.world:
            self.world.update(dt)
            self.game_view.update(dt, self.world)
            if self.world.outcome != GameOutcome.ONGOING:
                self.state = GameState.GAME_OVER

    def _draw(self) -> None:
        """Rendert die aktive Ansicht."""
        # 1. Hauptmenü rendert direkt auf die Bildschirmoberfläche für volle Widescreen-/Vollbild-Anpassung
        if self.state == GameState.MENU:
            self.menu_view.draw(self.screen)
            return

        # 2. In virtuelle 1280x720 Fläche zeichnen (Spiel, Evolution, Game Over)
        if self.state == GameState.PLAYING and self.world:
            self.game_view.draw(self.virtual_screen, self.world)
        elif self.state == GameState.EVOLUTION and self.world:
            self.evolution_view.draw(self.virtual_screen, self.world.pathogen)
        elif self.state == GameState.GAME_OVER and self.world:
            self.game_over_view.draw(self.virtual_screen, self.world)

        # 3. Skaliertes Blitting auf den physischen Bildschirm
        w, h = self.screen.get_size()
        if w == SCREEN_WIDTH and h == SCREEN_HEIGHT:
            self.screen.blit(self.virtual_screen, (0, 0))
        else:
            self.screen.fill(COLOR_BG)

            # Bei Ultrawide (offset_x > 0): Dekorative Gitterlinien an den Rändern
            if self.offset_x > 0:
                grid_col = (16, 22, 32)
                # Linker Rand
                for x in range(0, self.offset_x, 60):
                    pygame.draw.line(self.screen, grid_col, (x, 0), (x, h), 1)
                # Rechter Rand
                for x in range(self.offset_x + self.scaled_w, w, 60):
                    pygame.draw.line(self.screen, grid_col, (x, 0), (x, h), 1)
                for y in range(0, h, 60):
                    pygame.draw.line(self.screen, grid_col, (0, y), (self.offset_x, y), 1)
                    pygame.draw.line(self.screen, grid_col, (self.offset_x + self.scaled_w, y), (w, y), 1)

            scaled_surf = pygame.transform.smoothscale(self.virtual_screen, (self.scaled_w, self.scaled_h))
            self.screen.blit(scaled_surf, (self.offset_x, self.offset_y))
