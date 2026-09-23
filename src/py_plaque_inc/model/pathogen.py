"""Pathogen-Klassenmodell und Typ-Spezialisierungen."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random

from py_plaque_inc.model.upgrades import Upgrade, UpgradeCategory, get_default_upgrades


class PathogenType(str, Enum):
    BACTERIA = "Bakterie"
    VIRUS = "Virus"
    FUNGUS = "Pilz"


PATHOGEN_INFO = {
    PathogenType.BACTERIA: {
        "id": "bacteria",
        "name": "Bakterie",
        "description": "Die häufigste Ursache von Seuchen. Standard-Übertragung und robuste Wand, die Schutz in allen Klimaten gewährt.",
        "base_infectivity": 1.0,
        "base_severity": 0.0,
        "base_lethality": 0.0,
        "mutation_rate": 0.02,
    },
    PathogenType.VIRUS: {
        "id": "virus",
        "name": "Virus",
        "description": "Ein sich rasch verändernder Erreger. Mutiert unkontrolliert neue Symptome völlig kostenlos, ist aber schwerer zu kontrollieren.",
        "base_infectivity": 1.3,
        "base_severity": 0.0,
        "base_lethality": 0.0,
        "mutation_rate": 0.09,
    },
    PathogenType.FUNGUS: {
        "id": "fungus",
        "name": "Pilz",
        "description": "Pilzsporen reisen nur schwer über weite Ozeane. Verfügt über die mächtige Fähigkeit 'Sporenausbruch', um beliebige Länder schlagartig zu infizieren.",
        "base_infectivity": 0.75,
        "base_severity": 0.0,
        "base_lethality": 0.0,
        "mutation_rate": 0.01,
    },
}


class Pathogen:
    """Verwaltet Eigenschaften, Gen-Evolution und DNA-Punkte des Erregers."""

    def __init__(self, name: str, pathogen_type: PathogenType, starting_dna: int = 10):
        self.name = name
        self.pathogen_type = pathogen_type
        self.dna_points: int = starting_dna
        self.upgrades: Dict[str, Upgrade] = get_default_upgrades()
        
        info = PATHOGEN_INFO[pathogen_type]
        self.base_infectivity: float = info["base_infectivity"]
        self.base_severity: float = info["base_severity"]
        self.base_lethality: float = info["base_lethality"]
        self.mutation_rate: float = info["mutation_rate"]

        # Kumulative Modifikatoren
        self.bonus_infectivity: float = 0.0
        self.bonus_severity: float = 0.0
        self.bonus_lethality: float = 0.0
        self.cold_res: float = 0.0
        self.heat_res: float = 0.0
        self.drug_res: float = 0.0
        self.cure_slow: float = 0.0

        # Zähler für freigeschaltete Upgrades
        self.unlocked_count: int = 0

    @property
    def total_infectivity(self) -> float:
        return max(0.1, self.base_infectivity + self.bonus_infectivity)

    @property
    def total_severity(self) -> float:
        return max(0.0, self.base_severity + self.bonus_severity)

    @property
    def total_lethality(self) -> float:
        return max(0.0, self.base_lethality + self.bonus_lethality)

    def can_unlock(self, upgrade_id: str) -> Tuple[bool, str]:
        """Prüft, ob ein Upgrade gekauft werden kann."""
        if upgrade_id not in self.upgrades:
            return False, "Upgrade existiert nicht."
        
        upgrade = self.upgrades[upgrade_id]
        if upgrade.unlocked:
            return False, "Bereits erforscht."
        
        # Pathogen-Exklusivität prüfen
        if upgrade.is_pathogen_exclusive is not None:
            expected_type_id = PATHOGEN_INFO[self.pathogen_type]["id"]
            if upgrade.is_pathogen_exclusive != expected_type_id:
                return False, f"Nur für {upgrade.is_pathogen_exclusive} verfügbar."

        # DNA-Punkte prüfen
        if self.dna_points < upgrade.cost:
            return False, f"Zu wenig DNA ({upgrade.cost} benötigt, {self.dna_points} vorhanden)."

        # Voraussetzungen prüfen
        for req in upgrade.requires:
            if req in self.upgrades and not self.upgrades[req].unlocked:
                req_name = self.upgrades[req].name
                return False, f"Benötigt '{req_name}'."

        return True, "Bereit zur Freischaltung."

    def unlock_upgrade(self, upgrade_id: str, free_mutation: bool = False) -> bool:
        """Schaltet ein Upgrade frei und wendet die Boni an."""
        can_buy, _ = self.can_unlock(upgrade_id)
        if not can_buy and not free_mutation:
            return False

        upgrade = self.upgrades[upgrade_id]
        if not free_mutation:
            self.dna_points -= upgrade.cost

        upgrade.unlocked = True
        self.unlocked_count += 1

        # Boni aufschlagen
        self.bonus_infectivity += upgrade.infectivity
        self.bonus_severity += upgrade.severity
        self.bonus_lethality += upgrade.lethality
        self.cold_res = min(1.0, self.cold_res + upgrade.cold_res)
        self.heat_res = min(1.0, self.heat_res + upgrade.heat_res)
        self.drug_res = min(1.0, self.drug_res + upgrade.drug_res)
        self.cure_slow = min(0.8, self.cure_slow + upgrade.cure_slow)

        return True

    def can_devolve(self, upgrade_id: str) -> Tuple[bool, str]:
        """Prüft, ob eine Mutation zurückentwickelt (verkauft) werden kann."""
        if upgrade_id not in self.upgrades:
            return False, "Upgrade existiert nicht."

        upgrade = self.upgrades[upgrade_id]
        if not upgrade.unlocked:
            return False, "Nicht erforscht."

        # Prüfen, ob andere freigeschaltete Upgrades dieses als Voraussetzung haben
        for other_id, other_u in self.upgrades.items():
            if other_u.unlocked and upgrade_id in other_u.requires:
                return False, f"Wird noch von '{other_u.name}' benötigt."

        return True, "Kann zurückentwickelt werden (+2 DNA)."

    def devolve_upgrade(self, upgrade_id: str, dna_refund: int = 2) -> bool:
        """Entwickelt eine Mutation zurück und erstattet DNA-Punkte."""
        can_sell, _ = self.can_devolve(upgrade_id)
        if not can_sell:
            return False

        upgrade = self.upgrades[upgrade_id]
        upgrade.unlocked = False
        self.unlocked_count = max(0, self.unlocked_count - 1)
        self.dna_points += dna_refund

        # Boni abziehen
        self.bonus_infectivity = max(0.0, self.bonus_infectivity - upgrade.infectivity)
        self.bonus_severity = max(0.0, self.bonus_severity - upgrade.severity)
        self.bonus_lethality = max(0.0, self.bonus_lethality - upgrade.lethality)
        self.cold_res = max(0.0, self.cold_res - upgrade.cold_res)
        self.heat_res = max(0.0, self.heat_res - upgrade.heat_res)
        self.drug_res = max(0.0, self.drug_res - upgrade.drug_res)
        self.cure_slow = max(0.0, self.cure_slow - upgrade.cure_slow)

        return True

    def check_spontaneous_mutation(self) -> Optional[Upgrade]:
        """Prüft auf eine spontane Mutation (vor allem beim Virus)."""
        rate = self.mutation_rate
        if self.upgrades.get("spec_virus_instability", None) and self.upgrades["spec_virus_instability"].unlocked:
            rate *= 2.0

        if random.random() < rate:
            # Zufälliges gesperrtes Symptom finden, dessen Voraussetzungen erfüllt sind
            candidates = []
            for u in self.upgrades.values():
                if u.category == UpgradeCategory.SYMPTOMS and not u.unlocked:
                    # Voraussetzungen prüfen
                    reqs_met = all(self.upgrades[r].unlocked for r in u.requires if r in self.upgrades)
                    if reqs_met:
                        candidates.append(u)
            
            if candidates:
                chosen = random.choice(candidates)
                self.unlock_upgrade(chosen.id, free_mutation=True)
                return chosen

        return None
