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


def test_ocean_click_selects_earth_and_shows_world_detail():
    """Prüft Klick ins Meer zur Selektion der gesamten Erde und Öffnen der Welt-Detailansicht."""
    game = PlagueGame()
    game.start_new_game(pathogen_name="Ocean-Test", pathogen_type=PathogenType.BACTERIA, difficulty="Normal")
    game.world.select_starting_country("deu")
    assert game.world.has_started is True

    # Klick ins Meer (z.B. Südpazifik bei x=200, y=500)
    ocean_pos = (200, 500)
    assert game.game_view.map_renderer.get_country_at_pos(ocean_pos, game.world.countries) is None
    assert game.game_view.map_renderer.rect.collidepoint(ocean_pos) is True

    # 1. Erster Klick ins Meer selektiert die Erde
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": ocean_pos, "button": 1}))
    assert game.game_view.selected_country_id == "world"
    assert game.game_view.map_renderer.selected_country_id == "world"
    assert game.game_view._get_selected_name(game.world) == "Erde"
    assert game.game_view.is_showing_world_detail is False

    # Frame rendern mit selektierter Erde
    game._draw()

    # 2. Zweiter Klick ins Meer öffnet die Welt-Detailansicht
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": ocean_pos, "button": 1}))
    assert game.game_view.is_showing_world_detail is True

    # Frame mit geöffneter Welt-Detailansicht rendern
    game._draw()

    # Per ESC schließen
    game._handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0}))
    assert game.game_view.is_showing_world_detail is False

    # 3. Klick auf den HUD-Button '🌍 ERDE' öffnet ebenfalls die Welt-Detailansicht
    assert game.game_view.hud.btn_country.enabled is True
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.hud.btn_country.rect.center, "button": 1}))
    assert game.game_view.is_showing_world_detail is True

    # Per Schließen-Button schließen
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.world_detail.btn_close.rect.center, "button": 1}))
    assert game.game_view.is_showing_world_detail is False

    pygame.quit()


def test_news_ticker_click_and_full_length_modal():
    """Prüft Klick auf den News-Ticker im Eck unten links und die vollständige Anzeige langer Meldungen."""
    game = PlagueGame()
    game.start_new_game(pathogen_name="News-Test", pathogen_type=PathogenType.VIRUS, difficulty="Normal")
    game.world.select_starting_country("deu")

    # Eine extra lange Nachricht hinzufügen
    very_long_news = (
        "EILMELDUNG: Forscherteams auf allen Kontinenten melden unerklärliche Mutationen des Pathogens. "
        "Internationale Quarantänezonen werden errichtet, während die Weltgesundheitsorganisation zu einer "
        "Dringlichkeitssitzung in Genf zusammenkommt, um Notfallmaßnahmen zu beschließen."
    )
    from py_plaque_inc.model.events import NewsPriority
    game.world.news_mgr.add_news(very_long_news, NewsPriority.ALERT, day=5)

    assert game.world.news_mgr.current_headline == very_long_news
    assert len(game.world.news_mgr.news_history) >= 2

    # HUD zeichnen
    game._draw()

    # Klick auf die News-Box links unten (news_rect)
    news_center = game.game_view.hud.news_rect.center
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": news_center, "button": 1}))
    assert game.game_view.is_showing_news_modal is True

    # Modal rendern (vollständiger Text ohne Abschneiden gerendert)
    game._draw()

    # Scrollen im News-Modal testen (Mausrad)
    game._handle_event(pygame.event.Event(pygame.MOUSEWHEEL, {"y": -1}))
    game._draw()

    # Per '✕' Button schließen
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.news_modal.btn_close_x.rect.center, "button": 1}))
    assert game.game_view.is_showing_news_modal is False

    # Erneut öffnen und per Schließen-Button schließen
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": news_center, "button": 1}))
    assert game.game_view.is_showing_news_modal is True
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.news_modal.btn_close.rect.center, "button": 1}))
    assert game.game_view.is_showing_news_modal is False

    pygame.quit()


def test_news_text_wrapping():
    """Prüft den Textumbruch-Helfer für sehr lange Strings."""
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 14)
    from py_plaque_inc.ui.views.news_view import wrap_text

    short_text = "Kurzer Text"
    lines_short = wrap_text(short_text, font, max_width=400)
    assert len(lines_short) == 1
    assert lines_short[0] == "Kurzer Text"

    long_text = "Dies ist ein sehr langer Text der über mehrere Zeilen umgebrochen werden muss damit man ihn vollständig lesen kann."
    lines_long = wrap_text(long_text, font, max_width=150)
    assert len(lines_long) > 1
    # Sicherstellen, dass kein Wort verloren geht
    reconstructed = " ".join(lines_long)
    assert reconstructed == long_text

