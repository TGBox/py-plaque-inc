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


def test_quit_buttons_and_pause_menu():
    """Prüft die Beenden-Buttons im Hauptmenü, Pausenmenü und Game-Over-Screen."""
    # 1. Beenden im Hauptmenü
    game = PlagueGame()
    assert game.state == GameState.MENU
    assert game.is_running is True
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.menu_view.btn_quit.rect.center, "button": 1}))
    assert game.is_running is False
    pygame.quit()

    # 2. Pausenmenü im Spiel
    game = PlagueGame()
    game.start_new_game(pathogen_name="Pause-Test", pathogen_type=PathogenType.BACTERIA, difficulty="Normal")
    game.world.select_starting_country("deu")
    assert game.state == GameState.PLAYING

    # Klick auf Menü-Button im HUD
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.hud.btn_menu.rect.center, "button": 1}))
    assert game.game_view.is_showing_pause_menu is True
    game._draw()

    # Weiterspielen
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.pause_menu.btn_resume.rect.center, "button": 1}))
    assert game.game_view.is_showing_pause_menu is False

    # ESC öffnet Pausenmenü erneut
    game._handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0}))
    assert game.game_view.is_showing_pause_menu is True

    # Klick auf 'Zum Hauptmenü'
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.pause_menu.btn_to_menu.rect.center, "button": 1}))
    assert game.state == GameState.MENU

    # Beenden im Pausenmenü
    game.state = GameState.PLAYING
    game.game_view.is_showing_pause_menu = True
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_view.pause_menu.btn_quit.rect.center, "button": 1}))
    assert game.is_running is False
    pygame.quit()

    # 3. Beenden im Game-Over-Screen
    game = PlagueGame()
    game.state = GameState.GAME_OVER
    game.world = game.world or PlagueGame().world
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.game_over_view.btn_quit.rect.center, "button": 1}))
    assert game.is_running is False
    pygame.quit()


def test_pathogen_specific_upgrades_exclusivity():
    """Prüft, dass erregerspezifische Fähigkeiten nicht überlappen und nur passende Upgrades sichtbar sind."""
    # Pilz-Spiel starten
    game = PlagueGame()
    game.start_new_game(pathogen_name="Pilz-Test", pathogen_type=PathogenType.FUNGUS, difficulty="Normal")
    game.world.select_starting_country("deu")
    game.state = GameState.EVOLUTION

    # Fähigkeiten-Tab anwählen
    from py_plaque_inc.model.upgrades import UpgradeCategory
    game.evolution_view.current_category = UpgradeCategory.ABILITIES

    # Für Pilz müssen spec_fungus_spore_1 und spec_fungus_spore_2 sichtbar sein
    assert game.evolution_view._is_visible(game.world.pathogen.upgrades["spec_fungus_spore_1"], game.world.pathogen) is True
    assert game.evolution_view._is_visible(game.world.pathogen.upgrades["spec_fungus_spore_2"], game.world.pathogen) is True

    # Bakterien- und Viren-Spezialfähigkeiten dürfen NICHT sichtbar sein
    assert game.evolution_view._is_visible(game.world.pathogen.upgrades["spec_bacteria_shell"], game.world.pathogen) is False
    assert game.evolution_view._is_visible(game.world.pathogen.upgrades["spec_virus_instability"], game.world.pathogen) is False

    # Klick auf Position (3, 1) muss genau spec_fungus_spore_1 auswählen (nicht Bakterie!)
    spore1_pos = game.evolution_view._get_node_screen_pos((3, 1))
    game.evolution_view.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": spore1_pos, "button": 1}),
        game.world.pathogen,
    )
    assert game.evolution_view.selected_upgrade_id == "spec_fungus_spore_1"

    # Sporenausbruch I kann für 10 DNA freigeschaltet werden
    game.world.pathogen.dna_points = 20
    can_buy, _ = game.world.pathogen.can_unlock("spec_fungus_spore_1")
    assert can_buy is True
    game.evolution_view.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.evolution_view.btn_unlock.rect.center, "button": 1}),
        game.world.pathogen,
    )
    assert game.world.pathogen.upgrades["spec_fungus_spore_1"].unlocked is True

    # Rendern des Evolutionsbaums (mit Vektor-Häkchen)
    game._draw()

    pygame.quit()


def test_dna_badge_click_opens_evolution_view():
    """Prüft, dass ein Klick auf das DNA-Badge im HUD oben direkt in das Evolutionsmenü führt."""
    game = PlagueGame()
    game.start_new_game(pathogen_name="DNA-Click-Test", pathogen_type=PathogenType.BACTERIA, difficulty="Normal")
    game.world.select_starting_country("deu")
    assert game.state == GameState.PLAYING

    hud = game.game_view.hud
    assert hud.dna_rect.width > 0

    # Maus über das DNA-Badge bewegen -> is_dna_hovered
    game._handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": hud.dna_rect.center}))
    assert hud.is_dna_hovered is True

    # Klick auf das DNA-Badge -> Wechsel in den Zustand EVOLUTION
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": hud.dna_rect.center, "button": 1}))
    assert game.state == GameState.EVOLUTION

    # Rendern der Evolution View prüfen
    game._draw()
    pygame.quit()


def test_menu_view_responsive_layout_widescreen_and_fullscreen():
    """Prüft, dass sich das Hauptmenü-Layout bei Vollbild und Ultrawide dem verfügbaren Platz anpasst."""
    game = PlagueGame()
    assert game.state == GameState.MENU

    # 1. Standard 1280x720 Fenster
    game.menu_view.update_layout(1280, 720)
    col1_w_720 = game.menu_view.panel_left_rect.width
    assert col1_w_720 >= 500
    assert game.menu_view.panel_right_rect.right <= 1280
    assert game.menu_view.btn_start.rect.bottom <= 720
    game._draw()

    # 2. 1920x1080 (Vollbild 16:9)
    game.set_resolution("1920x1080", fullscreen=True)
    assert game.screen.get_size() == (1920, 1080)
    assert game.menu_view.width == 1920
    assert game.menu_view.height == 1080
    col1_w_1080 = game.menu_view.panel_left_rect.width
    assert col1_w_1080 > col1_w_720  # Spalten sind breiter und nutzen den Platz aus
    assert game.menu_view.panel_right_rect.right <= 1920
    assert game.menu_view.btn_start.rect.bottom <= 1080
    game._draw()

    # 3. 2560x1080 (Ultrawide 21:9)
    game.set_resolution("2560x1080", fullscreen=False)
    assert game.screen.get_size() == (2560, 1080)
    assert game.menu_view.width == 2560
    col1_w_ultrawide = game.menu_view.panel_left_rect.width
    assert col1_w_ultrawide > col1_w_1080  # Noch mehr Platz für Pathogen-Attribute und Lore
    assert game.menu_view.panel_right_rect.right <= 2560
    game._draw()

    # Klick auf "Virus"-Tab auf 2560x1080 testen
    virus_btn = game.menu_view.type_buttons[1]
    assert virus_btn.tab_id == "virus"
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": virus_btn.rect.center, "button": 1}))
    assert game.menu_view.selected_type == PathogenType.VIRUS

    # Klick auf "Schwer"-Tab auf 2560x1080 testen
    hard_btn = game.menu_view.diff_buttons[2]
    assert hard_btn.tab_id == "Schwer"
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": hard_btn.rect.center, "button": 1}))
    assert game.menu_view.selected_diff == "Schwer"

    # Klick auf "SEUCHE FREISETZEN" startet das Spiel
    game._handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game.menu_view.btn_start.rect.center, "button": 1}))
    assert game.state == GameState.PLAYING
    assert game.world.pathogen.pathogen_type == PathogenType.VIRUS
    assert game.world.difficulty_name == "Schwer"

    pygame.quit()



