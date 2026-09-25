"""Simuliert einen Durchlauf mit News-Events und prüft Ticker & Nachrichten."""

import os
import pygame

from py_plaque_inc.model.pathogen import Pathogen, PathogenType
from py_plaque_inc.model.world import World, GameOutcome
from py_plaque_inc.engine.save_manager import get_save_manager

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

# Starte mit Biowaffe
p = Pathogen(name="Biowaffe-Alpha", pathogen_type=PathogenType.BIO_WEAPON, starting_dna=100)
world = World(p, difficulty_name="Normal")

# Patient Null in Deutschland
world.select_starting_country("deu")
print("Startland gewählt. Letzte Nachricht:", world.news_mgr.current_headline)

# Simuliere 30 Tage
for d in range(1, 31):
    world._advance_day()
    if d % 5 == 0:
        print(f"Tag {d}: Headline = {world.news_mgr.current_headline}")

# Schalte Symptome und Fähigkeiten frei
p.unlock_upgrade("symp_coughing")
print("Upgrade Husten:", world.news_mgr.current_headline)

p.unlock_upgrade("spec_bio_suppression")
print("Upgrade Bio-Suppression:", world.news_mgr.current_headline)

# Zeige die letzten 10 Nachrichten
print("\n--- Letzte 10 Nachrichten in der Historie ---")
for item in world.news_mgr.news_history[-10:]:
    print(f"[Tag {item.day:3d}] ({item.priority.value:9s}) {item.text}")

pygame.quit()
