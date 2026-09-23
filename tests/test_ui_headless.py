"""Headless UI- und Render-Tests für alle Ansichten und Screens."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
import pygame
from py_plaque_inc.engine.game import PlagueGame, GameState
from py_plaque_inc.model.pathogen import PathogenType


def test_game_headless_rendering_and_state_transitions():
    """Startet das Spiel headless, wechselt durch alle Ansichten und rendert Frames."""
    game = PlagueGame()
    assert game.state == GameState.MENU

    # Einen Frame im Menü rendern
    game._draw()

    # Spiel starten
    game.start_new_game(pathogen_name="Corona-Test", pathogen_type=PathogenType.VIRUS, difficulty="Normal")
    assert game.state == GameState.PLAYING
    assert game.world is not None

    # Startland Deutschland wählen
    game.world.select_starting_country("deu")
    assert game.world.has_started is True

    # 5 Frames rendern und simulieren
    for _ in range(5):
        game._update(0.016)
        game._draw()

    # Country-Detail Popup öffnen und rendern
    game.game_view.selected_country_id = "deu"
    game.game_view.is_showing_country_detail = True
    game._draw()
    game.game_view.is_showing_country_detail = False

    # Tastatur-Zeitsteuerung testen
    assert game.world.sim_speed == 1
    # Leertaste -> Pause
    game._handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE, "mod": 0}))
    assert game.world.sim_speed == 0
    # Leertaste -> Fortsetzen
    game._handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE, "mod": 0}))
    assert game.world.sim_speed == 1
    # Taste 3 -> Tempo 3
    game._handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_3, "mod": 0}))
    assert game.world.sim_speed == 3

    # Wechsel zu Evolution View
    game.state = GameState.EVOLUTION
    game._draw()

    # Upgrade freischalten und anschließend per Rückentwickeln-Button verkaufen
    game.world.pathogen.dna_points = 50
    game.evolution_view.selected_upgrade_id = "trans_air_1"
    # Klick auf Erforschen
    game.evolution_view.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.evolution_view.btn_unlock.rect.center, "button": 1}),
        game.world.pathogen,
    )
    assert game.world.pathogen.upgrades["trans_air_1"].unlocked is True
    # Klick auf Rückentwickeln
    game.evolution_view.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.evolution_view.btn_unlock.rect.center, "button": 1}),
        game.world.pathogen,
    )
    assert game.world.pathogen.upgrades["trans_air_1"].unlocked is False

    # Wechsel zu Game Over View
    game.state = GameState.GAME_OVER
    game._draw()

    # Auflösungswechsel testen: 1920x1080 (16:9)
    game.set_resolution("1920x1080", fullscreen=False)
    assert game.screen.get_size() == (1920, 1080)
    assert game.scaled_w == 1920 and game.scaled_h == 1080
    assert game.offset_x == 0
    game._draw()

    # Auflösungswechsel testen: 2560x1080 (21:9 Ultrawide)
    game.set_resolution("2560x1080", fullscreen=False)
    assert game.screen.get_size() == (2560, 1080)
    assert game.scaled_w == 1920 and game.scaled_h == 1080
    assert game.offset_x == (2560 - 1920) // 2  # 320px Rand links und rechts
    game._draw()

    # Wechsel zurück zu Menü
    game.state = GameState.MENU
    game._draw()

    pygame.quit()
