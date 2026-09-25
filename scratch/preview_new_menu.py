"""Rendert Menü und Evolution mit den neuen Erregern als Screenshots zur visuellen Prüfung."""

import os
import pygame

from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.views.menu_view import MenuView
from py_plaque_inc.model.pathogen import PathogenType, Pathogen
from py_plaque_inc.ui.views.evolution_view import EvolutionView
from py_plaque_inc.model.upgrades import UpgradeCategory

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

theme = UITheme()
menu = MenuView(theme)

# 1. Menü 1280x720 mit Bakterie
surf1 = pygame.Surface((1280, 720))
menu.draw(surf1)
pygame.image.save(surf1, "scratch/preview_menu_bacteria.png")

# 2. Menü mit Brainrot (gesperrt)
menu.select_type_by_id("brainrot")
surf2 = pygame.Surface((1280, 720))
menu.draw(surf2)
pygame.image.save(surf2, "scratch/preview_menu_brainrot_locked.png")

# 3. Menü mit Entwicklermodus aktiv (alle frei)
menu.save_mgr.toggle_all_unlocked()
surf3 = pygame.Surface((1280, 720))
menu.draw(surf3)
pygame.image.save(surf3, "scratch/preview_menu_brainrot_unlocked.png")

# 4. Evolution-View für Brainrot (Fähigkeiten-Tab)
p_brainrot = Pathogen(name="TikTok-Overdrive", pathogen_type=PathogenType.BRAINROT, starting_dna=40)
evo = EvolutionView(theme)
evo.current_category = UpgradeCategory.ABILITIES
surf4 = pygame.Surface((1280, 720))
evo.draw(surf4, p_brainrot)
pygame.image.save(surf4, "scratch/preview_evolution_brainrot.png")

# 5. Menü auf 1920x1080 Full HD
surf5 = pygame.Surface((1920, 1080))
menu.draw(surf5)
pygame.image.save(surf5, "scratch/preview_menu_1080p.png")

# Cheat wieder zurücksetzen
menu.save_mgr.toggle_all_unlocked()
print("Screenshots erfolgreich generiert!")
pygame.quit()
