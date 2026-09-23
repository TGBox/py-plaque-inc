"""Nachrichten-Ticker, Meilensteine und dynamische Welt-Ereignisse."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import random


class NewsPriority(str, Enum):
    FLAVOR = "flavor"        # Grauer/heller Informationstext
    INFO = "info"            # Blauer Hinweis (z.B. neue Ausbreitung)
    MILESTONE = "milestone"  # Orange/Gelbe Meilenstein-Meldung
    ALERT = "alert"          # Rote Alarmmeldung (WHO, Schließungen, Tote)


@dataclass
class NewsItem:
    text: str
    priority: NewsPriority
    day: int


FLAVOR_HEADLINES = [
    "Bürger hamstern Toilettenpapier und Nudeln in Supermärkten.",
    "Neue Streaming-Serie bricht alle Rekorde während häuslicher Quarantäne.",
    "Wissenschaftler fordern mehr Kaffee für Nachtschichten in Laboren.",
    "Haustiere wundern sich über die ständige Anwesenheit ihrer Besitzer.",
    "Sportevents und Konzerte weltweit bis auf Weiteres verschoben.",
    "Aktienmärkte verzeichnen turbulente Kursschwankungen.",
    "Meteorologen melden ungewöhnlich ruhigen Luftraum.",
    "Impfgegner diskutieren Verschwörungstheorien in sozialen Medien.",
    "Regierungen raten dringend vom Händeschütteln ab.",
    "Videokonferenz-Anbieter melden historische Nutzerrekorde.",
]


class NewsManager:
    """Verwaltet und generiert Schlagzeilen für den oberen/unteren Laufbalken."""

    def __init__(self):
        self.news_history: List[NewsItem] = []
        self.current_headline: str = "Willkommen bei Py-Plaque-Inc. Wähle ein Startland, um die Seuche freizusetzen."
        self.current_priority: NewsPriority = NewsPriority.FLAVOR
        
        # Flags um doppelte Meilensteine zu verhindern
        self._milestone_first_infected = False
        self._milestone_10k_infected = False
        self._milestone_1m_infected = False
        self._milestone_100m_infected = False
        self._milestone_1b_infected = False
        self._milestone_all_infected = False
        self._milestone_first_death = False
        self._milestone_100k_dead = False
        self._milestone_10m_dead = False
        self._milestone_cure_25 = False
        self._milestone_cure_50 = False
        self._milestone_cure_75 = False
        self._milestone_cure_90 = False

    def add_news(self, text: str, priority: NewsPriority, day: int) -> None:
        """Fügt eine neue Schlagzeile hinzu und setzt sie als aktuellen Ticker-Text."""
        item = NewsItem(text=text, priority=priority, day=day)
        self.news_history.append(item)
        self.current_headline = text
        self.current_priority = priority

    def check_milestones(
        self,
        total_healthy: int,
        total_infected: int,
        total_dead: int,
        total_population: int,
        cure_percent: float,
        pathogen_name: str,
        current_day: int,
    ) -> None:
        """Prüft globale Schwellenwerte und wirft Meilenstein-Nachrichten aus."""
        # Erste Infektion
        if total_infected >= 1 and not self._milestone_first_infected:
            self._milestone_first_infected = True
            self.add_news(
                f"Patient Null identifiziert: Neuer mysteriöser Krankheitserreger '{pathogen_name}' registriert.",
                NewsPriority.INFO,
                current_day,
            )

        # 10.000 Infizierte
        if total_infected >= 10_000 and not self._milestone_10k_infected:
            self._milestone_10k_infected = True
            self.add_news(
                f"Ausbruch außer Kontrolle: Über 10.000 Menschen mit '{pathogen_name}' infiziert.",
                NewsPriority.INFO,
                current_day,
            )

        # 1 Million Infizierte
        if total_infected >= 1_000_000 and not self._milestone_1m_infected:
            self._milestone_1m_infected = True
            self.add_news(
                f"WHO warnt: '{pathogen_name}' erreicht 1 Million Infizierte weltweit!",
                NewsPriority.ALERT,
                current_day,
            )

        # 100 Millionen Infizierte
        if total_infected >= 100_000_000 and not self._milestone_100m_infected:
            self._milestone_100m_infected = True
            self.add_news(
                f"Globale Pandemie: Mehr als 100 Millionen Menschen tragen das Pathogen in sich.",
                NewsPriority.ALERT,
                current_day,
            )

        # 1 Milliarde Infizierte
        if total_infected >= 1_000_000_000 and not self._milestone_1b_infected:
            self._milestone_1b_infected = True
            self.add_news(
                f"Menschheit in Panik: 1 Milliarde Menschen mit '{pathogen_name}' infiziert!",
                NewsPriority.ALERT,
                current_day,
            )

        # Niemand mehr gesund
        if total_healthy == 0 and total_population > 0 and not self._milestone_all_infected:
            self._milestone_all_infected = True
            self.add_news(
                f"Kein einziger gesunder Mensch mehr auf der Erde! Jeder lebt mit '{pathogen_name}'.",
                NewsPriority.ALERT,
                current_day,
            )

        # Erster Todesfall
        if total_dead >= 1 and not self._milestone_first_death:
            self._milestone_first_death = True
            self.add_news(
                f"Erster Todesfall durch '{pathogen_name}' bestätigt. Weltgesundheitsorganisation alarmiert.",
                NewsPriority.ALERT,
                current_day,
            )

        # 100k Tote
        if total_dead >= 100_000 and not self._milestone_100k_dead:
            self._milestone_100k_dead = True
            self.add_news(
                f"Tragödie: Mehr als 100.000 Todesopfer durch '{pathogen_name}'.",
                NewsPriority.ALERT,
                current_day,
            )

        # 10 Mio Tote
        if total_dead >= 10_000_000 and not self._milestone_10m_dead:
            self._milestone_10m_dead = True
            self.add_news(
                f"Kollaps droht: Über 10 Millionen Tote weltweit. Gesundheitssysteme überlastet.",
                NewsPriority.ALERT,
                current_day,
            )

        # Heilmittel-Meilensteine
        if cure_percent >= 25.0 and not self._milestone_cure_25:
            self._milestone_cure_25 = True
            self.add_news(
                "Wissenschaftler entschlüsseln Gensequenz: Heilmittelforschung erreicht 25%.",
                NewsPriority.INFO,
                current_day,
            )

        if cure_percent >= 50.0 and not self._milestone_cure_50:
            self._milestone_cure_50 = True
            self.add_news(
                "Klinische Studien begonnen: Heilmittel zu 50% entwickelt!",
                NewsPriority.INFO,
                current_day,
            )

        if cure_percent >= 75.0 and not self._milestone_cure_75:
            self._milestone_cure_75 = True
            self.add_news(
                "Heilmittel zu 75% fertiggestellt: Pharmaunternehmen bereiten Massenproduktion vor.",
                NewsPriority.ALERT,
                current_day,
            )

        if cure_percent >= 90.0 and not self._milestone_cure_90:
            self._milestone_cure_90 = True
            self.add_news(
                "ALARM: Heilmittel zu 90% fertig! Die Zeit läuft gegen die Seuche ab!",
                NewsPriority.ALERT,
                current_day,
            )

        # Gelegentlich Flavour-News einstreuen (alle ~12 Tage)
        if current_day > 0 and current_day % 14 == 0:
            flavor = random.choice(FLAVOR_HEADLINES)
            self.add_news(flavor, NewsPriority.FLAVOR, current_day)
