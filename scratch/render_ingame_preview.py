import os
import pygame

# Headless setup for pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.font.init()

from py_plaque_inc.model.pathogen import Pathogen, PathogenType
from py_plaque_inc.model.world import World
from py_plaque_inc.map.renderer import MapRenderer
from py_plaque_inc.ui.hud import HUDView
from py_plaque_inc.ui.theme import UITheme

surface = pygame.Surface((1280, 720))
surface.fill((10, 15, 24))

theme = UITheme()
pathogen = Pathogen(name="T-Virus", pathogen_type=PathogenType.BACTERIA, starting_dna=42)
world = World(pathogen=pathogen)
world.countries["deu"].infected = 14_200_000
world.countries["deu"].dead = 250_000

world.countries["ceu"].infected = 850_000

map_rect = pygame.Rect(20, 64, 1240, 580)
map_renderer = MapRenderer(map_rect)

# Hover über Deutschland simulieren
map_renderer.handle_mouse_motion((640, 291), world.countries)

# 1. Karte rendern
map_renderer.draw(surface, world.countries, world.transport_mgr, theme.font_small)

# 2. HUD rendern
hud = HUDView(theme)
hud.draw(surface, world, selected_country_name="Deutschland")

out_path = "scratch/ingame_preview_final.png"
pygame.image.save(surface, out_path)
print(f"Rendered in-game preview to {out_path}")
