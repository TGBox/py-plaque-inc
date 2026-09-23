"""Einstiegspunkt für Py-Plaque-Inc."""

import sys
from py_plaque_inc.engine.game import PlagueGame


def main() -> None:
    """Startet das Spiel."""
    game = PlagueGame()
    game.run()


if __name__ == "__main__":
    main()
