"""Einstiegspunkt für Py-Plaque-Inc."""

import sys


def main() -> None:
    """Startet das Spiel."""
    # Windows DPI-Awareness aktivieren für verzerrungsfreie Mauskoordinaten
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    from py_plaque_inc.engine.game import PlagueGame
    game = PlagueGame()
    game.run()


if __name__ == "__main__":
    main()

