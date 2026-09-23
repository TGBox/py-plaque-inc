"""Haupt-Welt-Simulation und Koordination aller Spielsysteme."""

from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
import random

from py_plaque_inc.config import DIFFICULTIES
from py_plaque_inc.model.country import Country
from py_plaque_inc.model.pathogen import Pathogen, PathogenType
from py_plaque_inc.model.transport import TransportManager
from py_plaque_inc.model.events import NewsManager, NewsPriority
from py_plaque_inc.map.geo_data import create_world_countries


class GameOutcome:
    ONGOING = "ongoing"
    VICTORY = "victory"     # Menschheit ausgelöscht
    DEFEAT_CURE = "defeat_cure"       # Heilmittel 100%
    DEFEAT_EXTINCT = "defeat_extinct" # Seuche erloschen, Gesunde überleben


class World:
    """Verwaltet den weltweiten Zustand, Zeitverlauf, Ausbreitung und Heilmittel."""

    def __init__(self, pathogen: Pathogen, difficulty_name: str = "Normal"):
        self.pathogen = pathogen
        self.difficulty_name = difficulty_name
        self.difficulty_cfg = DIFFICULTIES.get(difficulty_name, DIFFICULTIES["Normal"])
        
        self.countries: Dict[str, Country] = create_world_countries()
        self.transport_mgr = TransportManager()
        self.news_mgr = NewsManager()

        # Zeitrechnung
        self.start_date = date(2026, 1, 1)
        self.current_day: int = 0
        self.sim_speed: int = 1  # 0: Pause, 1: Normal, 2: Schnell, 3: Ultra
        self.last_sim_speed: int = 1
        self.time_accumulator: float = 0.0

        # Heilmittelforschung
        self.cure_progress: float = 0.0          # 0.0 bis 100.0
        self.cure_active: bool = False
        self.cure_daily_rate: float = 0.0

        # Ausstehende klickbare Blasen auf der Karte: List of dicts
        # { 'type': 'red'|'orange'|'blue', 'country_id': str, 'pos': (x, y), 'dna_value': int }
        self.pending_bubbles: List[dict] = []
        self._last_orange_bubble_day: int = 0

        # Historie für das Endauswertungs-Diagramm: (Tag, Gesunde, Infizierte, Tote, Heilmittel%)
        self.history: List[Tuple[int, int, int, int, float]] = []

        # Gesamtwerte berechnen
        self._initial_population = sum(c.population for c in self.countries.values())
        self.has_started: bool = False
        self.outcome = GameOutcome.ONGOING

        # Ersten Datenpunkt sichern
        self._record_history()

    def toggle_pause(self) -> None:
        """Pausiert das Spiel oder stellt die vorherige Geschwindigkeit wieder her."""
        if self.sim_speed == 0:
            self.sim_speed = self.last_sim_speed or 1
        else:
            self.last_sim_speed = self.sim_speed
            self.sim_speed = 0

    def set_speed(self, speed: int) -> None:
        """Setzt eine Geschwindigkeitsstufe (0..3)."""
        if speed in (0, 1, 2, 3):
            if speed > 0:
                self.last_sim_speed = speed
            elif self.sim_speed > 0:
                self.last_sim_speed = self.sim_speed
            self.sim_speed = speed

    @property
    def current_calendar_date(self) -> date:
        return self.start_date + timedelta(days=self.current_day)

    @property
    def total_population(self) -> int:
        return self._initial_population

    @property
    def total_infected(self) -> int:
        return sum(c.infected for c in self.countries.values())

    @property
    def total_dead(self) -> int:
        return sum(c.dead for c in self.countries.values())

    @property
    def total_healthy(self) -> int:
        return max(0, self.total_population - self.total_infected - self.total_dead)

    @property
    def infected_countries_count(self) -> int:
        return sum(1 for c in self.countries.values() if c.is_infected or c.dead > 0)

    def select_starting_country(self, country_id: str) -> bool:
        """Startet das Spiel mit Patient Null im gewählten Land."""
        if self.has_started or country_id not in self.countries:
            return False

        country = self.countries[country_id]
        country.infect_initial(count=10, current_day=self.current_day)
        self.has_started = True

        # Erste rote Blase für das Startland
        self.pending_bubbles.append({
            "type": "red",
            "country_id": country.id,
            "pos": country.capital_pos,
            "dna_value": 3,
        })

        self.news_mgr.add_news(
            f"Erster Ausbruch gemeldet: '{self.pathogen.name}' hat seinen Ursprung in {country.name}.",
            NewsPriority.ALERT,
            self.current_day,
        )
        return True

    def trigger_spore_burst(self) -> Optional[str]:
        """Spezialfähigkeit für Pilz: Infiziert sofort ein unberührtes Land."""
        uninfected = [c for c in self.countries.values() if not c.is_infected and c.healthy > 0]
        if not uninfected:
            return None

        target = random.choice(uninfected)
        target.infect_initial(count=random.randint(10, 50), current_day=self.current_day)
        
        self.pending_bubbles.append({
            "type": "red",
            "country_id": target.id,
            "pos": target.capital_pos,
            "dna_value": 3,
        })
        self.news_mgr.add_news(
            f"Sporenausbruch: Pilzsporen überwinden Meere und infizieren {target.name}!",
            NewsPriority.INFO,
            self.current_day,
        )
        return target.name

    def pop_bubble(self, bubble_dict: dict) -> int:
        """Spieler klickt eine DNA- oder Heilmittelblase an."""
        b_type = bubble_dict.get("type", "red")
        dna_gain = bubble_dict.get("dna_value", 1)

        if b_type == "blue":
            # Heilmittel verlangsamen / zurückwerfen
            self.cure_progress = max(0.0, self.cure_progress - 1.5)
            self.pathogen.dna_points += 1
            return 1
        else:
            self.pathogen.dna_points += dna_gain
            return dna_gain

    def update(self, dt_seconds: float) -> None:
        """
        Haupt-Update-Schritt (wird jeden Frame aufgerufen).
        dt_seconds: Vergangene Zeit in Sekunden seit letztem Frame.
        """
        if self.outcome != GameOutcome.ONGOING or not self.has_started:
            return

        speed_factor = self.sim_speed
        if speed_factor <= 0:
            return

        # Zeitfortschritt: 1.0 = Normal (1 Tag / Sekunde)
        self.time_accumulator += dt_seconds * speed_factor
        days_to_advance = int(self.time_accumulator)
        if days_to_advance > 0:
            self.time_accumulator -= days_to_advance
            for _ in range(days_to_advance):
                self._advance_day()

        # Fahrzeuge zwischen den Tagen updaten
        arrivals = self.transport_mgr.update(float(speed_factor), self.countries)
        for dest_id, was_infected in arrivals:
            if was_infected and dest_id in self.countries:
                dest = self.countries[dest_id]
                if not dest.is_infected and dest.healthy > 0:
                    dest.infect_initial(count=random.randint(5, 25), current_day=self.current_day)
                    self.pending_bubbles.append({
                        "type": "red",
                        "country_id": dest.id,
                        "pos": dest.capital_pos,
                        "dna_value": random.randint(2, 4),
                    })
                    self.news_mgr.add_news(
                        f"Infiziertes Fahrzeug erreicht {dest.name}! Der Erreger breitet sich aus.",
                        NewsPriority.INFO,
                        self.current_day,
                    )

    def _advance_day(self) -> None:
        """Führt alle Simulationsberechnungen für einen einzelnen Tag durch."""
        self.current_day += 1

        # 1. Lokale Länderberechnung
        diff_trans = self.difficulty_cfg["transmission_multiplier"]
        for country in self.countries.values():
            if country.is_infected:
                new_inf, new_dead = country.update_day(
                    base_infectivity=self.pathogen.total_infectivity,
                    base_severity=self.pathogen.total_severity,
                    base_lethality=self.pathogen.total_lethality,
                    cold_res=self.pathogen.cold_res,
                    heat_res=self.pathogen.heat_res,
                    drug_res=self.pathogen.drug_res,
                    difficulty_mult=diff_trans,
                    current_day=self.current_day,
                )

                # Bonus-Blasen bei Infektionswachstum im Land
                if (new_inf >= 15 or country.infected in (10, 50, 100, 500, 1000)) and random.random() < 0.10:
                    if len([b for b in self.pending_bubbles if b["country_id"] == country.id and b["type"] == "orange"]) == 0:
                        self.pending_bubbles.append({
                            "type": "orange",
                            "country_id": country.id,
                            "pos": (country.capital_pos[0] + random.randint(-15, 15), country.capital_pos[1] + random.randint(-15, 15)),
                            "dna_value": random.randint(2, 4),
                        })

        # 1b. Regelmäßige orange DNA-Blase in einem infizierten Land (garantiert stetigen DNA-Zufluss)
        if self.current_day - self._last_orange_bubble_day >= 12:
            infected_countries = [c for c in self.countries.values() if c.is_infected]
            if infected_countries and len([b for b in self.pending_bubbles if b["type"] == "orange"]) < 3:
                chosen_c = random.choice(infected_countries)
                self._last_orange_bubble_day = self.current_day
                self.pending_bubbles.append({
                    "type": "orange",
                    "country_id": chosen_c.id,
                    "pos": (chosen_c.capital_pos[0] + random.randint(-15, 15), chosen_c.capital_pos[1] + random.randint(-15, 15)),
                    "dna_value": random.randint(2, 4),
                })

        # 2. Ausbreitung über Landgrenzen
        self._simulate_land_borders()

        # 3. Flug- und Schiffsverkehr spawnen (mit Upgrades für Luft und Wasser)
        if random.random() < 0.70:
            has_air = self.pathogen.upgrades["trans_air_1"].unlocked
            has_water = self.pathogen.upgrades["trans_water_1"].unlocked
            self.transport_mgr.spawn_random_transport(
                self.countries,
                allow_air=True,
                allow_sea=True,
                cure_active=self.cure_active,
                air_bonus=has_air,
                water_bonus=has_water,
            )

        # 4. Spontane Mutation prüfen (besonders Virus)
        mutated = self.pathogen.check_spontaneous_mutation()
        if mutated:
            self.news_mgr.add_news(
                f"Spontane Mutation! '{self.pathogen.name}' hat das Symptom '{mutated.name}' ohne DNA-Kosten entwickelt.",
                NewsPriority.MILESTONE,
                self.current_day,
            )

        # 5. Heilmittelforschung berechnen
        self._simulate_cure()

        # 6. Meilensteine und Nachrichten
        self.news_mgr.check_milestones(
            total_healthy=self.total_healthy,
            total_infected=self.total_infected,
            total_dead=self.total_dead,
            total_population=self.total_population,
            cure_percent=self.cure_progress,
            pathogen_name=self.pathogen.name,
            current_day=self.current_day,
        )

        # 7. Historie aufzeichnen (alle 2 Tage)
        if self.current_day % 2 == 0:
            self._record_history()

        # 8. Sieg-/Niederlage-Bedingungen prüfen
        self._check_game_over()

    def _simulate_land_borders(self) -> None:
        """Überträgt Infektionen über offene Landgrenzen."""
        for country in list(self.countries.values()):
            if country.is_infected and country.borders_open:
                # Höhere Chance mit Vögeln / Nagetieren
                border_chance = 0.015 * self.pathogen.total_infectivity
                if self.pathogen.upgrades["trans_bird_1"].unlocked:
                    border_chance += 0.02
                if self.pathogen.upgrades["trans_rodent_1"].unlocked:
                    border_chance += 0.02

                for neighbor_id in country.neighbors:
                    neighbor = self.countries.get(neighbor_id)
                    if neighbor and not neighbor.is_infected and neighbor.borders_open:
                        if random.random() < border_chance:
                            neighbor.infect_initial(count=random.randint(5, 30), current_day=self.current_day)
                            self.pending_bubbles.append({
                                "type": "red",
                                "country_id": neighbor.id,
                                "pos": neighbor.capital_pos,
                                "dna_value": 2,
                            })
                            self.news_mgr.add_news(
                                f"Grenzübertritt: '{self.pathogen.name}' breitet sich über Land nach {neighbor.name} aus.",
                                NewsPriority.INFO,
                                self.current_day,
                            )

    def _simulate_cure(self) -> None:
        """Berechnet den globalen Fortschritt des Heilmittels."""
        # Heilmittel-Aktivierungsschwelle: Schweregrad > 1.0 ODER erste Tote ODER >5 Mio Infizierte
        if not self.cure_active:
            if self.total_dead > 50 or self.pathogen.total_severity >= 1.5 or self.total_infected >= 5_000_000:
                self.cure_active = True
                self.news_mgr.add_news(
                    "WHO schlägt globalen Alarm: Internationale Forschung an einem Heilmittel gestartet!",
                    NewsPriority.ALERT,
                    self.current_day,
                )

        if not self.cure_active:
            return

        # Summe aller Forschungskapazitäten weltweit
        total_effort = sum(c.cure_effort for c in self.countries.values())
        
        # Resistenz-Modifikator
        slowdown = 1.0 - self.pathogen.cure_slow
        diff_cure = self.difficulty_cfg["cure_speed_multiplier"]
        
        # Basis-Geschwindigkeit des Heilmittels
        daily_increase = (total_effort * 0.0075) * slowdown * diff_cure
        self.cure_daily_rate = daily_increase
        self.cure_progress = min(100.0, self.cure_progress + daily_increase)

        # Gelegentlich blaue Heilmittel-Blasen in forschenden Ländern spawnen
        if random.random() < 0.08:
            research_countries = [c for c in self.countries.values() if c.cure_effort > 0.5]
            if research_countries and len([b for b in self.pending_bubbles if b["type"] == "blue"]) < 2:
                rc = random.choice(research_countries)
                self.pending_bubbles.append({
                    "type": "blue",
                    "country_id": rc.id,
                    "pos": (rc.capital_pos[0] + random.randint(-15, 15), rc.capital_pos[1] + random.randint(-15, 15)),
                    "dna_value": 1,
                })

    def _record_history(self) -> None:
        """Speichert aktuellen Zustand für das Abschlussdiagramm."""
        self.history.append((
            self.current_day,
            self.total_healthy,
            self.total_infected,
            self.total_dead,
            self.cure_progress,
        ))

    def _check_game_over(self) -> None:
        """Prüft, ob Sieg oder Niederlage eingetreten ist."""
        # 1. Sieg: Menschheit ausgelöscht
        if self.total_dead >= self.total_population or (self.total_healthy == 0 and self.total_infected == 0):
            self.outcome = GameOutcome.VICTORY
            self.news_mgr.add_news(
                f"SIEG: '{self.pathogen.name}' hat die gesamte Menschheit erfolgreich vernichtet!",
                NewsPriority.ALERT,
                self.current_day,
            )
            self._record_history()
            return

        # 2. Niederlage: Heilmittel 100%
        if self.cure_progress >= 100.0:
            self.outcome = GameOutcome.DEFEAT_CURE
            self.news_mgr.add_news(
                "NIEDERLAGE: Das Heilmittel wurde weltweit erfolgreich verteilt und hat die Seuche besiegt.",
                NewsPriority.ALERT,
                self.current_day,
            )
            self._record_history()
            return

        # 3. Niederlage: Seuche erloschen, aber Gesunde existieren noch
        if self.total_infected == 0 and self.total_healthy > 0 and self.current_day > 5:
            self.outcome = GameOutcome.DEFEAT_EXTINCT
            self.news_mgr.add_news(
                f"NIEDERLAGE: Alle Infizierten von '{self.pathogen.name}' sind gestorben, bevor die Seuche die Welt anstecken konnte.",
                NewsPriority.ALERT,
                self.current_day,
            )
            self._record_history()
            return
