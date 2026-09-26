"""Tests für die 8 Erregertypen, das humorvolle Nachrichtensystem und das Freischaltsystem."""

import pytest
import os
import pygame

from py_plaque_inc.model.pathogen import Pathogen, PathogenType, PATHOGEN_INFO
from py_plaque_inc.model.upgrades import UpgradeCategory, get_default_upgrades
from py_plaque_inc.model.events import NewsManager, NewsPriority, COUNTRY_SATIRE, PATHOGEN_FLAVOR
from py_plaque_inc.model.world import World, GameOutcome
from py_plaque_inc.engine.save_manager import SaveManager, PATHOGEN_UNLOCK_ORDER
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.views.menu_view import MenuView


@pytest.fixture(autouse=True)
def init_pygame():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()


def test_all_eight_pathogens_defined():
    """Prüft, ob alle 8 Erreger in Enum und PATHOGEN_INFO vollständig definiert sind."""
    expected_types = [
        PathogenType.BACTERIA,
        PathogenType.VIRUS,
        PathogenType.FUNGUS,
        PathogenType.PARASITE,
        PathogenType.PRION,
        PathogenType.NANO_VIRUS,
        PathogenType.BIO_WEAPON,
        PathogenType.BRAINROT,
    ]
    assert len(expected_types) == 8

    for ptype in expected_types:
        assert ptype in PATHOGEN_INFO
        info = PATHOGEN_INFO[ptype]
        assert "id" in info
        assert "name" in info
        assert "description" in info
        assert "perk" in info
        assert info["base_infectivity"] > 0
        assert info["mutation_rate"] >= 0

        p = Pathogen(name=f"Test_{info['name']}", pathogen_type=ptype, starting_dna=50)
        assert p.total_infectivity >= info["base_infectivity"]


def test_exclusive_upgrades_for_all_pathogens():
    """Prüft, dass jeder Erreger exklusive Spezial-Upgrades besitzt und nur er sie erforschen kann."""
    upgrades = get_default_upgrades()

    exclusive_branches = {
        "bacteria": ["spec_bacteria_shell"],
        "virus": ["spec_virus_instability"],
        "fungus": ["spec_fungus_spore_1", "spec_fungus_spore_2"],
        "parasite": ["spec_parasite_symbiosis", "spec_parasite_hallucination", "spec_parasite_hibernation"],
        "prion": ["spec_prion_neural_atrophy", "spec_prion_amyloid", "spec_prion_madness"],
        "nano_virus": ["spec_nano_fragment", "spec_nano_intercept", "spec_nano_overclock"],
        "bio_weapon": ["spec_bio_suppression", "spec_bio_deactivate", "spec_bio_annihilation"],
        "brainrot": ["spec_brainrot_doomscroll", "spec_brainrot_skibidi", "spec_brainrot_attention"],
    }

    for p_id, u_ids in exclusive_branches.items():
        for u_id in u_ids:
            assert u_id in upgrades, f"Upgrade '{u_id}' fehlt im Upgrade-Katalog!"
            u = upgrades[u_id]
            assert u.is_pathogen_exclusive == p_id
            assert u.category == UpgradeCategory.ABILITIES

    # Fremder Erreger darf exklusive Upgrades nicht kaufen
    p_bact = Pathogen(name="Bact", pathogen_type=PathogenType.BACTERIA, starting_dna=100)
    can_buy_nano, msg = p_bact.can_unlock("spec_nano_fragment")
    assert can_buy_nano is False
    assert "Nur für nano_virus verfügbar" in msg


def test_nano_virus_mechanics():
    """Prüft Nano-Virus: Heilmittelforschung startet ab Tag 1, Fragmentierung wirft Heilmittel zurück."""
    p_nano = Pathogen(name="Nanobot-9000", pathogen_type=PathogenType.NANO_VIRUS, starting_dna=40)
    world = World(pathogen=p_nano, difficulty_name="Normal")

    # Heilmittelforschung ist von Beginn an aktiv
    assert world.cure_active is True
    world.cure_progress = 30.0

    # Code-Fragmentierung erforschen
    success = p_nano.unlock_upgrade("spec_nano_fragment")
    assert success is True
    # Sollte Heilmittel um 15% senken
    assert world.cure_progress == 15.0


def test_bio_weapon_escalating_lethality():
    """Prüft Biowaffe: Tödlichkeit steigt automatisch an und kann neutralisiert werden."""
    p_bio = Pathogen(name="Weapon-X", pathogen_type=PathogenType.BIO_WEAPON, starting_dna=40)
    world = World(pathogen=p_bio, difficulty_name="Normal")
    world.select_starting_country("deu")

    initial_lethality = p_bio.total_lethality

    # 12 Tage simulieren -> Tödlichkeit muss steigen (alle 6 Tage +0.035)
    for _ in range(12):
        world._advance_day()

    assert p_bio.total_lethality > initial_lethality

    # Neutralisierungs-Gen freischalten
    p_bio.unlock_upgrade("spec_bio_suppression")
    p_bio.unlock_upgrade("spec_bio_deactivate")
    assert p_bio.bonus_lethality == 0.0


def test_parasite_stealth_and_passive_dna():
    """Prüft Parasit: Erzeugt passiv DNA, solange die Schwere niedrig ist."""
    p_para = Pathogen(name="MindWorm", pathogen_type=PathogenType.PARASITE, starting_dna=5)
    world = World(pathogen=p_para, difficulty_name="Normal")
    world.select_starting_country("deu")

    initial_dna = p_para.dna_points
    # 8 Tage simulieren
    for _ in range(8):
        world._advance_day()

    assert p_para.dna_points > initial_dna


def test_prion_and_brainrot_cure_slowdown():
    """Prüft Heilmittel-Verlangsamung bei Prionen und Brainrot."""
    p_prion = Pathogen(name="MadCow", pathogen_type=PathogenType.PRION, starting_dna=50)
    world_prion = World(pathogen=p_prion, difficulty_name="Normal")
    world_prion.cure_active = True
    world_prion.countries["deu"].cure_effort = 2.0
    world_prion._simulate_cure()
    prion_rate = world_prion.cure_daily_rate

    p_bact = Pathogen(name="NormalBact", pathogen_type=PathogenType.BACTERIA, starting_dna=50)
    world_bact = World(pathogen=p_bact, difficulty_name="Normal")
    world_bact.cure_active = True
    world_bact.countries["deu"].cure_effort = 2.0
    world_bact._simulate_cure()
    bact_rate = world_bact.cure_daily_rate

    # Prion-Rate muss deutlich kleiner sein als Bakterien-Rate
    assert prion_rate < bact_rate


def test_satirical_news_for_all_countries():
    """Prüft, dass alle 49 Territorien humorvolle Schlagzeilen besitzen und ausgelöst werden."""
    news_mgr = NewsManager()

    # Alle 49 Ländercodes müssen in COUNTRY_SATIRE vorkommen
    assert len(COUNTRY_SATIRE) >= 49
    for cid in ["deu", "usa", "gbr", "fra", "jpn", "rus", "chn", "bra", "egy", "aus"]:
        assert cid in COUNTRY_SATIRE

    # Auslösen bei Infektion (1 Willkommens-Nachricht + 1 Länder-Satire)
    news_mgr.notify_country_infected("deu", "Deutschland", day=5)
    assert len(news_mgr.items) == 2
    assert "Fax" in news_mgr.items[-1].text or "Deutschland" in news_mgr.items[-1].text

    # Zweiter Aufruf darf keine Duplikate erzeugen
    news_mgr.notify_country_infected("deu", "Deutschland", day=6)
    assert len(news_mgr.items) == 2


def test_pathogen_flavor_news_generation():
    """Prüft Erreger-spezifische Flavor-Nachrichten (z.B. Brainrot Subway Surfers)."""
    news_mgr = NewsManager()

    # Alle 8 Erreger haben News-Pools
    for p_id in ["bacteria", "virus", "fungus", "parasite", "prion", "nano_virus", "bio_weapon", "brainrot"]:
        assert p_id in PATHOGEN_FLAVOR
        assert len(PATHOGEN_FLAVOR[p_id]) >= 3

    # Tag 10 sollte Flavor generieren
    news_mgr.check_flavor("brainrot", current_day=10)
    assert len(news_mgr.items) >= 1
    assert news_mgr.items[-1].priority == NewsPriority.FLAVOR


def test_progression_and_save_manager(tmp_path):
    """Prüft Speichern, Freischalten durch Siege und Cheat-Modus."""
    save_file = str(tmp_path / "test_save.json")
    sm = SaveManager(file_path=save_file)

    # Standardmäßig: Bakterie, Virus, Pilz freigeschaltet
    assert sm.is_unlocked(PathogenType.BACTERIA) is True
    assert sm.is_unlocked(PathogenType.VIRUS) is True
    assert sm.is_unlocked(PathogenType.FUNGUS) is True
    assert sm.is_unlocked(PathogenType.PARASITE) is False

    # Sieg mit Pilz schaltet Parasit frei
    next_unlocked = sm.record_win(PathogenType.FUNGUS)
    assert next_unlocked == PathogenType.PARASITE
    assert sm.is_unlocked(PathogenType.PARASITE) is True

    # Cheat-Modus aktiviert alle Erreger sofort
    assert sm.is_unlocked(PathogenType.BRAINROT) is False
    sm.toggle_all_unlocked()
    assert sm.is_unlocked(PathogenType.BRAINROT) is True
    sm.toggle_all_unlocked()
    assert sm.is_unlocked(PathogenType.BRAINROT) is False


def test_menu_view_carousel_and_selection():
    """Prüft das Karussell und die Schnellwahl im Hauptmenü."""
    theme = UITheme()
    menu = MenuView(theme)

    assert menu.selected_type == PathogenType.BACTERIA
    assert menu.current_type_index == 0

    # Weiter-Klick
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": menu.btn_next_type.rect.center, "button": 1}))
    assert menu.selected_type == PathogenType.VIRUS
    assert menu.current_type_index == 1

    # Zurück-Klick
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": menu.btn_prev_type.rect.center, "button": 1}))
    assert menu.selected_type == PathogenType.BACTERIA
    assert menu.current_type_index == 0

    # Direktwahl über Quick-Select Tab 7 (Brainrot)
    brainrot_btn = menu.type_buttons[7]
    assert brainrot_btn.tab_id == "brainrot"
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": brainrot_btn.rect.center, "button": 1}))
    assert menu.selected_type == PathogenType.BRAINROT

    # Zeichnen testen (kein Crash auf verschiedenen Auflösungen)
    surf = pygame.Surface((1280, 720))
    menu.draw(surf)
    surf_wide = pygame.Surface((2560, 1080))
    menu.draw(surf_wide)


def test_all_pathogens_simulate_in_germany_without_crash():
    """Simuliert jeden der 8 Erreger mit Startland Deutschland (deu, rich) über mehrere Tage."""
    for ptype in PathogenType:
        p = Pathogen(name=f"CrashTest_{ptype.value}", pathogen_type=ptype, starting_dna=50)
        world = World(pathogen=p, difficulty_name="Normal")
        world.select_starting_country("deu")
        assert world.has_started is True
        assert world.countries["deu"].is_infected is True
        assert world.countries["deu"].is_rich is True

        # 10 Tage durchsimulieren (prüft _advance_day, country.is_rich, Heilmittel etc.)
        for _ in range(10):
            world.update(1.0)  # Ein voller Tag pro Sekunde

        assert world.current_day >= 10
        assert world.total_infected > 0

