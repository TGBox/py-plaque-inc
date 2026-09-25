"""Speicher- und Profilverwaltung für freigeschaltete Erreger und Spielstatistiken."""

import json
import os
from typing import Dict, List, Optional
from py_plaque_inc.model.pathogen import PathogenType


PATHOGEN_UNLOCK_ORDER = [
    PathogenType.BACTERIA,
    PathogenType.VIRUS,
    PathogenType.FUNGUS,
    PathogenType.PARASITE,
    PathogenType.PRION,
    PathogenType.NANO_VIRUS,
    PathogenType.BIO_WEAPON,
    PathogenType.BRAINROT,
]


class SaveManager:
    """Verwaltet den persistenten Freischaltfortschritt der Erreger in einer lokalen JSON-Datei."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            # Speichere standardmäßig in user_data/save_game.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "..", "..", "user_data", "save_game.json")
            file_path = os.path.abspath(file_path)

        self.file_path = file_path
        self.unlocked_pathogens: List[str] = ["bacteria", "virus", "fungus"]
        self.all_unlocked_cheat: bool = False
        self.wins: Dict[str, int] = {}

        self.load()

    def load(self) -> None:
        """Lädt den Speicherstand aus der Datei, falls vorhanden."""
        if not os.path.exists(self.file_path):
            self.save()
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.unlocked_pathogens = data.get("unlocked_pathogens", ["bacteria", "virus", "fungus"])
                # Standard-Erreger sicherstellen
                for base_p in ["bacteria", "virus", "fungus"]:
                    if base_p not in self.unlocked_pathogens:
                        self.unlocked_pathogens.append(base_p)
                self.all_unlocked_cheat = data.get("all_unlocked_cheat", False)
                self.wins = data.get("wins", {})
        except Exception:
            # Fallback bei beschädigter Datei
            self.unlocked_pathogens = ["bacteria", "virus", "fungus"]
            self.all_unlocked_cheat = False
            self.wins = {}

    def save(self) -> None:
        """Speichert den aktuellen Fortschritt persistent ab."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            data = {
                "unlocked_pathogens": self.unlocked_pathogens,
                "all_unlocked_cheat": self.all_unlocked_cheat,
                "wins": self.wins,
            }
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def is_unlocked(self, ptype: PathogenType) -> bool:
        """Prüft, ob ein Erregertyp spielbar ist."""
        if self.all_unlocked_cheat:
            return True
        from py_plaque_inc.model.pathogen import PATHOGEN_INFO
        pid = PATHOGEN_INFO[ptype]["id"]
        return pid in self.unlocked_pathogens

    def get_lock_reason(self, ptype: PathogenType) -> str:
        """Gibt eine Erklärung zurück, warum ein Erreger gesperrt ist."""
        if self.is_unlocked(ptype):
            return "Freigeschaltet"

        # Finde vorherigen Erreger
        for i, t in enumerate(PATHOGEN_UNLOCK_ORDER):
            if t == ptype and i > 0:
                prev_type = PATHOGEN_UNLOCK_ORDER[i - 1]
                return f"Gesperrt: Gewinne mit {prev_type.value}, um freizuschalten!"

        return "Gesperrt"

    def record_win(self, ptype: PathogenType) -> Optional[PathogenType]:
        """Vermerkt einen Sieg und schaltet den nächsten Erreger frei."""
        from py_plaque_inc.model.pathogen import PATHOGEN_INFO
        pid = PATHOGEN_INFO[ptype]["id"]
        self.wins[pid] = self.wins.get(pid, 0) + 1

        unlocked_next = None
        for i, t in enumerate(PATHOGEN_UNLOCK_ORDER):
            if t == ptype and i + 1 < len(PATHOGEN_UNLOCK_ORDER):
                next_t = PATHOGEN_UNLOCK_ORDER[i + 1]
                next_pid = PATHOGEN_INFO[next_t]["id"]
                if next_pid not in self.unlocked_pathogens:
                    self.unlocked_pathogens.append(next_pid)
                    unlocked_next = next_t
                break

        self.save()
        return unlocked_next

    def toggle_all_unlocked(self) -> bool:
        """Schaltet den Testmodus (alle Erreger frei) um."""
        self.all_unlocked_cheat = not self.all_unlocked_cheat
        self.save()
        return self.all_unlocked_cheat

    def reset_progress(self) -> None:
        """Setzt den Freischaltfortschritt auf den Anfangszustand zurück."""
        self.unlocked_pathogens = ["bacteria"]
        self.all_unlocked_cheat = False
        self.wins = {}
        self.save()


# Globales Singleton für bequemen Zugriff
_GLOBAL_SAVE_MGR: Optional[SaveManager] = None

def get_save_manager() -> SaveManager:
    global _GLOBAL_SAVE_MGR
    if _GLOBAL_SAVE_MGR is None:
        _GLOBAL_SAVE_MGR = SaveManager()
    return _GLOBAL_SAVE_MGR
