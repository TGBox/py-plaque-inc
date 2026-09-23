"""Länder-Datenmodell und Zustandssimulation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional
import math


class Climate(str, Enum):
    TEMPERATE = "Gemäßigt"
    COLD = "Kalt"
    HOT = "Heiß"
    HUMID = "Feucht"
    ARID = "Trocken"


class Wealth(str, Enum):
    POOR = "Arm"
    MEDIUM = "Mittel"
    RICH = "Reich"


@dataclass
class Country:
    id: str                                  # z.B. "deu", "usa", "chn"
    name: str                                # z.B. "Deutschland", "USA"
    population: int                          # Gesamtbevölkerung
    climate: Climate                         # Klimatyp
    wealth: Wealth                           # Wohlstand
    has_airport: bool                        # Besitzt internationalen Großflughafen
    has_seaport: bool                        # Besitzt Seehafen
    capital_pos: Tuple[int, int]             # Zentroid / Hauptstadt (X, Y) auf Map
    polygons: List[List[Tuple[int, int]]]    # Vektor-Koordinaten (ein oder mehrere Polygone)
    neighbors: List[str] = field(default_factory=list)  # IDs der Landnachbarn

    # Dynamischer Simulationszustand
    infected: int = 0
    dead: int = 0
    airports_open: bool = True
    seaports_open: bool = True
    borders_open: bool = True
    cure_effort: float = 0.0                 # Aktueller Beitrag zur Heilmittelforschung (pro Tag)
    first_infected_day: Optional[int] = None # Wann das Land zum ersten Mal infiziert wurde

    # Visuelle Hilfswerte
    infected_pulse: float = 0.0              # Pulsiereffekt bei Neuinfektion

    @property
    def healthy(self) -> int:
        return max(0, self.population - self.infected - self.dead)

    @property
    def is_infected(self) -> bool:
        return self.infected > 0

    @property
    def is_destroyed(self) -> bool:
        return self.dead >= self.population

    @property
    def infection_ratio(self) -> float:
        if self.population <= 0:
            return 0.0
        return min(1.0, self.infected / self.population)

    @property
    def dead_ratio(self) -> float:
        if self.population <= 0:
            return 0.0
        return min(1.0, self.dead / self.population)

    def infect_initial(self, count: int = 10, current_day: int = 0) -> None:
        """Infiziert erste Patienten (z.B. Patient Null)."""
        actual_count = min(count, self.healthy)
        self.infected += actual_count
        if self.first_infected_day is None:
            self.first_infected_day = current_day
        self.infected_pulse = 1.0

    def update_day(
        self,
        base_infectivity: float,
        base_severity: float,
        base_lethality: float,
        cold_res: float,
        heat_res: float,
        drug_res: float,
        difficulty_mult: float,
        current_day: int,
    ) -> Tuple[int, int]:
        """
        Simuliert einen Spieltag im Land.
        Gibt (neue_infizierte, neue_tote) zurück.
        """
        if self.infected <= 0 or self.is_destroyed:
            return 0, 0

        # Klimamodifikatoren
        climate_factor = 1.0
        if self.climate == Climate.COLD:
            climate_factor = 0.6 + 0.5 * cold_res
        elif self.climate == Climate.HOT:
            climate_factor = 0.6 + 0.5 * heat_res
        elif self.climate == Climate.ARID:
            climate_factor = 0.7 + 0.4 * heat_res
        elif self.climate == Climate.HUMID:
            climate_factor = 0.7 + 0.4 * cold_res

        # Wohlstandsmodifikator (Medizinische Infrastruktur hemmt Infektion)
        wealth_factor = 1.0
        if self.wealth == Wealth.RICH:
            wealth_factor = 0.55 + 0.45 * drug_res
        elif self.wealth == Wealth.MEDIUM:
            wealth_factor = 0.80 + 0.25 * drug_res
        elif self.wealth == Wealth.POOR:
            wealth_factor = 1.20  # Arme Länder breiten sich schneller aus

        # Logistisches Infektionsmodell
        # S: Healthy, I: Infected, N: Population
        effective_infectivity = (
            base_infectivity * climate_factor * wealth_factor * difficulty_mult * 0.12
        )
        
        susceptible_ratio = self.healthy / self.population if self.population > 0 else 0
        new_infections = int(self.infected * effective_infectivity * susceptible_ratio)
        
        # Garantiere organisches Mindestwachstum, auch bei niedriger Infektionsbasis
        if self.healthy > 0 and self.infected > 0:
            min_growth = max(1, int(self.infected * 0.05 * climate_factor * difficulty_mult))
            new_infections = max(new_infections, min_growth)

        new_infections = min(self.healthy, max(0, new_infections))
        self.infected += new_infections

        # Tödlichkeit & Todesfälle
        new_deaths = 0
        if base_lethality > 0:
            death_factor = base_lethality * 0.04
            new_deaths = int(self.infected * death_factor)
            if new_deaths == 0 and base_lethality >= 1.0:
                new_deaths = 1
            new_deaths = min(self.infected, max(0, new_deaths))
            self.infected -= new_deaths
            self.dead += new_deaths

        # Panik-Reaktionen des Landes (Grenzen/Häfen schließen)
        self._check_lockdowns(base_severity)

        # Heilmittelforschungs-Beitrag berechnen
        # Reiche Länder mit aktiven Laboren forschen mehr, solange sie nicht entvölkert sind
        if self.wealth == Wealth.RICH:
            lab_capacity = 2.0
        elif self.wealth == Wealth.MEDIUM:
            lab_capacity = 1.0
        else:
            lab_capacity = 0.25

        active_workforce = max(0.0, 1.0 - (self.dead_ratio + 0.7 * self.infection_ratio))
        self.cure_effort = lab_capacity * active_workforce

        return new_infections, new_deaths

    def _check_lockdowns(self, severity: float) -> None:
        """Schließt Flughäfen, Häfen und Grenzen bei hohem Infektions-/Schweregrad."""
        threshold = self.infection_ratio * 100 + severity * 0.8
        
        if self.wealth == Wealth.RICH:
            lockdown_trigger = 30
        elif self.wealth == Wealth.MEDIUM:
            lockdown_trigger = 50
        else:
            lockdown_trigger = 75

        if threshold > lockdown_trigger and self.has_airport:
            self.airports_open = False
        if threshold > lockdown_trigger + 15 and self.has_seaport:
            self.seaports_open = False
        if threshold > lockdown_trigger + 25:
            self.borders_open = False
