"""Automatisierte Tests für Simulationslogik, Pathogene und Weltzustände."""

import pytest
from py_plaque_inc.model.pathogen import Pathogen, PathogenType
from py_plaque_inc.model.country import Country, Climate, Wealth
from py_plaque_inc.model.world import World, GameOutcome
from py_plaque_inc.model.upgrades import UpgradeCategory


def test_pathogen_initialization_and_unlocks():
    """Prüft Initialisierung und Gen-Freischaltungen."""
    p = Pathogen(name="TestPest", pathogen_type=PathogenType.BACTERIA, starting_dna=20)
    assert p.dna_points == 20
    assert p.total_infectivity >= 1.0
    assert p.total_severity == 0.0

    # Luft I freischalten (kostet 9 DNA)
    can_buy, _ = p.can_unlock("trans_air_1")
    assert can_buy is True
    success = p.unlock_upgrade("trans_air_1")
    assert success is True
    assert p.dna_points == 11
    assert p.total_infectivity > 1.0

    # Luft II benötigt Luft I -> jetzt freischaltbar, falls genug DNA
    # Luft II kostet 14 DNA, wir haben 11 -> kann nicht gekauft werden
    can_buy_2, reason = p.can_unlock("trans_air_2")
    assert can_buy_2 is False
    assert "Zu wenig DNA" in reason

    # DNA aufstocken und kaufen
    p.dna_points += 10
    can_buy_2, _ = p.can_unlock("trans_air_2")
    assert can_buy_2 is True
    assert p.unlock_upgrade("trans_air_2") is True


def test_pathogen_devolve_upgrade():
    """Prüft das Zurückentwickeln (Verkaufen) von Mutationen gegen DNA."""
    p = Pathogen(name="TestPest", pathogen_type=PathogenType.BACTERIA, starting_dna=25)
    p.unlock_upgrade("trans_air_1")
    p.unlock_upgrade("trans_air_2")
    
    # trans_air_1 kann nicht zurückentwickelt werden, da trans_air_2 noch aktiv ist
    can_dev_1, reason_1 = p.can_devolve("trans_air_1")
    assert can_dev_1 is False
    assert "Wird noch von 'Luft II' benötigt" in reason_1

    # trans_air_2 zurückentwickeln (+2 DNA)
    dna_before = p.dna_points
    can_dev_2, _ = p.can_devolve("trans_air_2")
    assert can_dev_2 is True
    success = p.devolve_upgrade("trans_air_2")
    assert success is True
    assert p.dna_points == dna_before + 2
    assert p.upgrades["trans_air_2"].unlocked is False

    # Jetzt kann auch trans_air_1 zurückentwickelt werden
    can_dev_1_now, _ = p.can_devolve("trans_air_1")
    assert can_dev_1_now is True
    assert p.devolve_upgrade("trans_air_1") is True
    assert p.dna_points == dna_before + 4
    assert p.upgrades["trans_air_1"].unlocked is False


def test_world_time_controls():
    """Prüft Pause-Toggle und Geschwindigkeitsstufen der Weltzeit."""
    p = Pathogen(name="TestTime", pathogen_type=PathogenType.BACTERIA)
    world = World(pathogen=p)
    assert world.sim_speed == 1

    # Pause umschalten
    world.toggle_pause()
    assert world.sim_speed == 0
    assert world.last_sim_speed == 1

    # Erneut Leertaste / Pause umschalten -> stellt Tempo 1 wieder her
    world.toggle_pause()
    assert world.sim_speed == 1

    # Tempo 3 setzen
    world.set_speed(3)
    assert world.sim_speed == 3
    assert world.last_sim_speed == 3

    # Pause
    world.toggle_pause()
    assert world.sim_speed == 0

    # Pause beenden -> stellt Tempo 3 wieder her
    world.toggle_pause()
    assert world.sim_speed == 3


def test_country_infection_and_lockdown():
    """Prüft Infektionswachstum und Schließung von Flughäfen/Häfen."""
    country = Country(
        id="deu",
        name="Deutschland",
        population=80_000_000,
        climate=Climate.TEMPERATE,
        wealth=Wealth.RICH,
        has_airport=True,
        has_seaport=True,
        capital_pos=(640, 240),
        polygons=[[(620, 220), (660, 220), (660, 260), (620, 260)]],
    )

    assert country.healthy == 80_000_000
    assert country.airports_open is True

    country.infect_initial(count=100, current_day=1)
    assert country.infected == 100
    assert country.healthy == 80_000_000 - 100

    # Tagessimulation mit hoher Infektiosität
    new_inf, new_dead = country.update_day(
        base_infectivity=5.0,
        base_severity=40.0,
        base_lethality=2.0,
        cold_res=0.5,
        heat_res=0.5,
        drug_res=0.5,
        difficulty_mult=1.0,
        current_day=2,
    )

    assert new_inf > 0
    assert country.infected > 100
    # Bei hoher Severity (40.0 * 0.8 = 32 > 30) schließt der reiche Staat Flughäfen
    assert country.airports_open is False


def test_world_simulation_and_cure():
    """Prüft Welt-Ticks, Heilmittelforschung und Blasen."""
    p = Pathogen(name="TestVirus", pathogen_type=PathogenType.VIRUS, starting_dna=15)
    world = World(pathogen=p, difficulty_name="Normal")

    assert world.has_started is False
    # Startland wählen
    success = world.select_starting_country("deu")
    assert success is True
    assert world.has_started is True
    assert len(world.pending_bubbles) >= 1

    # Blase platzen lassen
    bubble = world.pending_bubbles[0]
    initial_dna = p.dna_points
    gain = world.pop_bubble(bubble)
    world.pending_bubbles.remove(bubble)
    assert p.dna_points == initial_dna + gain

    # 15 Tage simulieren
    for _ in range(15):
        world._advance_day()

    assert world.current_day == 15
    assert world.total_infected > 1
    assert len(world.history) > 1


def test_fungus_spore_burst():
    """Prüft Pilz-Spezialfähigkeit."""
    p = Pathogen(name="TestPilz", pathogen_type=PathogenType.FUNGUS, starting_dna=30)
    world = World(pathogen=p, difficulty_name="Normal")
    world.select_starting_country("deu")

    # Sporen-Ausbruch triggern
    target_name = world.trigger_spore_burst()
    assert target_name is not None
    assert world.infected_countries_count >= 2


def test_victory_condition():
    """Prüft Siegbedingung wenn Menschheit ausgelöscht wird."""
    p = Pathogen(name="SuperPlague", pathogen_type=PathogenType.BACTERIA)
    world = World(pathogen=p)
    world.select_starting_country("deu")

    # Alle Bürger als tot markieren
    for c in world.countries.values():
        c.dead = c.population
        c.infected = 0

    world._check_game_over()
    assert world.outcome == GameOutcome.VICTORY


def test_defeat_cure_condition():
    """Prüft Niederlage wenn Heilmittel 100% erreicht."""
    p = Pathogen(name="WeakPlague", pathogen_type=PathogenType.BACTERIA)
    world = World(pathogen=p)
    world.select_starting_country("deu")

    world.cure_progress = 100.0
    world._check_game_over()
    assert world.outcome == GameOutcome.DEFEAT_CURE
