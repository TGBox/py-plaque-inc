"""Flugzeug- und Schiffsverkehr zwischen Ländern."""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Optional
import math
import random


class TransportType(str, Enum):
    AIRPLANE = "airplane"
    SHIP = "ship"
    CURE_PLANE = "cure_plane"


@dataclass
class TransportRoute:
    origin_id: str
    destination_id: str
    transport_type: TransportType
    start_pos: Tuple[int, int]
    end_pos: Tuple[int, int]
    is_infected: bool
    progress: float = 0.0          # 0.0 bis 1.0
    speed: float = 0.005           # Fortschritt pro Frame / Tick
    curve_offset: float = 0.0      # Für gekrümmte Flug- und Seebahnen

    @property
    def current_pos(self) -> Tuple[int, int]:
        """Berechnet die aktuelle Position auf dem quadratischen Bézier-Bogen."""
        x0, y0 = self.start_pos
        x2, y2 = self.end_pos
        
        # Kontrollpunkt für Bogenkrümmung
        mid_x = (x0 + x2) / 2
        mid_y = (y0 + y2) / 2
        dx = x2 - x0
        dy = y2 - y0
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            nx = -dy / dist
            ny = dx / dist
            cx = mid_x + nx * self.curve_offset
            cy = mid_y + ny * self.curve_offset
        else:
            cx, cy = mid_x, mid_y

        t = self.progress
        # Bézier-Formel: (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
        cur_x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x2
        cur_y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y2
        return int(cur_x), int(cur_y)

    @property
    def angle_degrees(self) -> float:
        """Berechnet den Neigungswinkel in Grad für die Fahrzeug-Ausrichtung."""
        t1 = max(0.0, self.progress - 0.02)
        t2 = min(1.0, self.progress + 0.02)
        # Tangenten-Richtung
        x0, y0 = self.start_pos
        x2, y2 = self.end_pos
        dx = x2 - x0
        dy = y2 - y0
        return math.degrees(math.atan2(dy, dx))


REGIONAL_ROUTES = {
    "gln": ["can", "sca", "gbr", "isl", "usa"],
    "isl": ["gbr", "sca", "gln", "fra", "deu"],
    "mdg": ["eaf", "zaf", "ind", "sau"],
    "cub": ["usa", "mex", "cen", "col", "bra"],
    "nzl": ["aus", "sea", "usa", "jpn"],
    "aus": ["sea", "nzl", "ind", "jpn", "usa", "png", "idn"],
    "jpn": ["kor", "chn", "usa", "sea", "rus", "aus"],
    "idn": ["sea", "aus", "ind", "chn", "phl", "png"],
    "phl": ["sea", "chn", "jpn", "idn", "aus", "usa"],
    "png": ["idn", "aus", "sea"],
    "gbr": ["fra", "deu", "usa", "isl", "gln", "esp"],
    "usa": ["can", "mex", "cub", "gbr", "jpn", "aus", "bra", "deu", "fra"],
    "can": ["usa", "gln", "gbr", "fra", "rus"],
    "mex": ["usa", "cen", "cub", "col"],
    "cen": ["mex", "cub", "col", "usa"],
    "col": ["cen", "cub", "bra", "per", "usa"],
    "bra": ["usa", "col", "arg", "zaf", "fra", "esp"],
    "arg": ["bra", "chl", "bol", "zaf", "usa"],
    "chl": ["arg", "bol", "per", "aus"],
    "per": ["col", "chl", "bra", "mex", "aus"],
    "deu": ["fra", "gbr", "usa", "rus", "chn", "pol", "ceu", "sca"],
    "ceu": ["deu", "fra", "ita", "gbr", "usa", "pol", "bal"],
    "fra": ["gbr", "deu", "esp", "ita", "usa", "bra", "ceu"],
    "esp": ["fra", "nab", "bra", "gbr", "ita"],
    "ita": ["fra", "ceu", "bal", "egy", "nab"],
    "pol": ["deu", "bal", "ukr", "fin", "rus", "blt", "ceu"],
    "blt": ["pol", "fin", "rus", "deu", "sca"],
    "bal": ["ita", "pol", "ukr", "tur", "egy", "ceu"],
    "sca": ["fin", "rus", "deu", "gbr", "isl", "blt"],
    "fin": ["sca", "pol", "rus", "ukr", "blt"],
    "ukr": ["pol", "fin", "bal", "rus", "tur"],
    "rus": ["sca", "fin", "ukr", "kaz", "mon", "chn", "jpn", "deu", "usa"],
    "chn": ["rus", "jpn", "kor", "sea", "ind", "usa", "deu", "aus"],
    "kor": ["chn", "jpn", "usa", "sea"],
    "ind": ["pak", "chn", "sea", "sau", "gbr", "aus", "eaf"],
    "pak": ["irn", "kaz", "ind", "chn", "sau"],
    "sea": ["chn", "ind", "idn", "phl", "jpn", "aus"],
    "tur": ["bal", "ukr", "mde", "irn", "egy", "deu"],
    "mde": ["tur", "sau", "irn", "egy", "fra"],
    "sau": ["mde", "egy", "eaf", "ind", "pak", "gbr"],
    "irn": ["tur", "mde", "kaz", "pak", "ind"],
    "nab": ["esp", "egy", "waf", "fra", "ita"],
    "egy": ["tur", "mde", "sau", "ita", "fra", "eaf", "sud"],
    "sud": ["egy", "caf", "eaf", "waf", "sau"],
    "waf": ["nab", "caf", "sud", "fra", "bra"],
    "caf": ["waf", "sud", "eaf", "zaf"],
    "eaf": ["sud", "caf", "zaf", "sau", "ind", "mdg"],
    "zaf": ["bra", "eaf", "caf", "ind", "gbr", "aus", "mdg"],
}


LANDLOCKED_COUNTRIES = {"ceu", "bol", "kaz", "mon"}


def get_country_sea_routes(country_id: str, countries: Optional[dict] = None) -> List[str]:
    """Gibt alle Ziel-Länder-IDs zurück, zu denen von diesem Land aus Seerouten führen."""
    if countries is not None:
        c = countries.get(country_id)
        if c and not getattr(c, "has_seaport", True):
            return []
        routes = REGIONAL_ROUTES.get(country_id, [])
        return [dest for dest in routes if countries.get(dest) and getattr(countries[dest], "has_seaport", True)]

    if country_id in LANDLOCKED_COUNTRIES:
        return []
    return [dest for dest in REGIONAL_ROUTES.get(country_id, []) if dest not in LANDLOCKED_COUNTRIES]


class TransportManager:
    """Verwaltet alle aktiven Flugzeuge und Schiffe auf der Weltkarte."""

    def __init__(self):
        self.active_transports: List[TransportRoute] = []

    def get_ships_for_country(self, country_id: str) -> Tuple[List[TransportRoute], List[TransportRoute]]:
        """Gibt (eingehende_schiffe, ausgehende_schiffe) als Routen-Listen zurück."""
        inbound = [t for t in self.active_transports if t.destination_id == country_id and t.transport_type == TransportType.SHIP]
        outbound = [t for t in self.active_transports if t.origin_id == country_id and t.transport_type == TransportType.SHIP]
        return inbound, outbound

    def get_ship_count_for_country(self, country_id: str) -> Tuple[int, int]:
        """Gibt (anzahl_eingehend, anzahl_ausgehend) für Schiffe/Boote eines Landes zurück."""
        inbound, outbound = self.get_ships_for_country(country_id)
        return len(inbound), len(outbound)

    def get_airplanes_for_country(self, country_id: str) -> Tuple[List[TransportRoute], List[TransportRoute]]:
        """Gibt (eingehende_fluege, ausgehende_fluege) als Routen-Listen zurück."""
        inbound = [t for t in self.active_transports if t.destination_id == country_id and t.transport_type in (TransportType.AIRPLANE, TransportType.CURE_PLANE)]
        outbound = [t for t in self.active_transports if t.origin_id == country_id and t.transport_type in (TransportType.AIRPLANE, TransportType.CURE_PLANE)]
        return inbound, outbound

    def get_airplane_count_for_country(self, country_id: str) -> Tuple[int, int]:
        """Gibt (anzahl_eingehend, anzahl_ausgehend) für Flüge eines Landes zurück."""
        inbound, outbound = self.get_airplanes_for_country(country_id)
        return len(inbound), len(outbound)

    def spawn_random_transport(
        self,
        countries: dict,
        allow_air: bool = True,
        allow_sea: bool = True,
        cure_active: bool = False,
        air_bonus: bool = False,
        water_bonus: bool = False,
    ) -> Optional[TransportRoute]:
        """Erzeugt ein zufälliges Flugzeug oder Schiff zwischen zwei gültigen Ländern."""
        if not countries:
            return None

        # Max 22 Fahrzeuge gleichzeitig
        if len(self.active_transports) >= 22:
            return None

        # 10% Chance für Cure-Plane wenn Heilmittel aktiv
        if cure_active and random.random() < 0.15:
            rich_countries = [c for c in countries.values() if c.cure_effort > 0.5 and c.airports_open]
            dest_candidates = [c for c in countries.values() if c.has_airport and c.airports_open]
            if rich_countries and dest_candidates:
                orig = random.choice(rich_countries)
                dest = random.choice(dest_candidates)
                if orig.id != dest.id:
                    route = TransportRoute(
                        origin_id=orig.id,
                        destination_id=dest.id,
                        transport_type=TransportType.CURE_PLANE,
                        start_pos=orig.capital_pos,
                        end_pos=dest.capital_pos,
                        is_infected=False,
                        speed=random.uniform(0.004, 0.007),
                        curve_offset=random.uniform(-40, 40),
                    )
                    self.active_transports.append(route)
                    return route

        # Regulärer Verkehr
        is_air = allow_air and (not allow_sea or random.random() < 0.55)
        if is_air:
            origin_pool = [c for c in countries.values() if c.has_airport and c.airports_open]
            dest_pool = [c for c in countries.values() if c.has_airport and c.airports_open]
            t_type = TransportType.AIRPLANE
            speed = random.uniform(0.004, 0.008)
        else:
            origin_pool = [c for c in countries.values() if c.has_seaport and c.seaports_open]
            dest_pool = [c for c in countries.values() if c.has_seaport and c.seaports_open]
            t_type = TransportType.SHIP
            speed = random.uniform(0.002, 0.004)

        if not origin_pool or not dest_pool:
            return None

        # Infizierte Länder bevorzugt als Startpunkt wählen (50% Chance wenn vorhanden)
        infected_origins = [c for c in origin_pool if c.is_infected]
        if infected_origins and random.random() < 0.50:
            orig = random.choice(infected_origins)
        else:
            orig = random.choice(origin_pool)

        # Regionale / Insel-Routen bevorzugen
        possible_dest = [d for d in dest_pool if d.id != orig.id]
        if orig.id in REGIONAL_ROUTES and random.random() < 0.65:
            matching = [d for d in possible_dest if d.id in REGIONAL_ROUTES[orig.id]]
            if matching:
                dest = random.choice(matching)
            else:
                dest = random.choice(possible_dest) if possible_dest else None
        else:
            dest = random.choice(possible_dest) if possible_dest else None

        if not dest:
            return None

        # Infektionswahrscheinlichkeit für den Transport
        is_infected = False
        if orig.is_infected:
            base_prob = 0.22 + min(0.60, orig.infection_ratio * 2.0)
            if t_type == TransportType.AIRPLANE and air_bonus:
                base_prob += 0.35
            elif t_type == TransportType.SHIP and water_bonus:
                base_prob += 0.35
            is_infected = random.random() < min(0.95, base_prob)

        route = TransportRoute(
            origin_id=orig.id,
            destination_id=dest.id,
            transport_type=t_type,
            start_pos=orig.capital_pos,
            end_pos=dest.capital_pos,
            is_infected=is_infected,
            speed=speed,
            curve_offset=random.uniform(-50, 50),
        )
        self.active_transports.append(route)
        return route

    def update(self, speed_mult: float, countries: dict) -> List[Tuple[str, bool]]:
        """
        Aktualisiert alle Fahrzeuge.
        Gibt eine Liste von (zielland_id, war_infiziert) für angekommene Fahrzeuge zurück.
        """
        arrivals: List[Tuple[str, bool]] = []
        remaining: List[TransportRoute] = []

        for route in self.active_transports:
            route.progress += route.speed * max(0.2, speed_mult)
            if route.progress >= 1.0:
                # Angekommen
                dest = countries.get(route.destination_id)
                if dest:
                    # Prüfen ob Flughafen/Hafen noch offen ist
                    can_enter = True
                    if route.transport_type == TransportType.AIRPLANE and not dest.airports_open:
                        can_enter = False
                    elif route.transport_type == TransportType.SHIP and not dest.seaports_open:
                        can_enter = False
                    
                    if can_enter and route.is_infected:
                        arrivals.append((route.destination_id, True))
            else:
                remaining.append(route)

        self.active_transports = remaining
        return arrivals
