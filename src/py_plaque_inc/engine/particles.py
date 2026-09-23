"""Partikelsystem für Blasenexplosionen, Infektionspulse und schwebende Texte."""

from dataclasses import dataclass
from typing import List, Tuple
import math
import random
import pygame


@dataclass
class SparkParticle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    radius: float
    life: float        # 1.0 bis 0.0
    decay: float       # z.B. 0.03


@dataclass
class Shockwave:
    x: float
    y: float
    radius: float
    max_radius: float
    color: Tuple[int, int, int]
    life: float
    decay: float


@dataclass
class FloatingText:
    text: str
    x: float
    y: float
    vy: float
    color: Tuple[int, int, int]
    life: float
    decay: float


class ParticleSystem:
    """Zentrales Partikel- und Effektsystem."""

    def __init__(self):
        self.sparks: List[SparkParticle] = []
        self.shockwaves: List[Shockwave] = []
        self.floating_texts: List[FloatingText] = []

    def emit_bubble_pop(self, x: int, y: int, color: Tuple[int, int, int], text: str = "") -> None:
        """Erzeugt eine Explosion von leuchtenden Funken und schwebendem Text."""
        # 1. Funken
        for _ in range(18):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.5)
            self.sparks.append(
                SparkParticle(
                    x=float(x),
                    y=float(y),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    color=color,
                    radius=random.uniform(2.0, 4.0),
                    life=1.0,
                    decay=random.uniform(0.025, 0.045),
                )
            )

        # 2. Schockwelle
        self.shockwaves.append(
            Shockwave(
                x=float(x),
                y=float(y),
                radius=10.0,
                max_radius=32.0,
                color=color,
                life=1.0,
                decay=0.04,
            )
        )

        # 3. Floating Text
        if text:
            self.floating_texts.append(
                FloatingText(
                    text=text,
                    x=float(x),
                    y=float(y - 10),
                    vy=-1.2,
                    color=color,
                    life=1.0,
                    decay=0.02,
                )
            )

    def emit_country_pulse(self, x: int, y: int, color: Tuple[int, int, int] = (230, 40, 40)) -> None:
        """Erzeugt einen roten Infektions-Wellenkreis auf einem neu infizierten Land."""
        self.shockwaves.append(
            Shockwave(
                x=float(x),
                y=float(y),
                radius=6.0,
                max_radius=45.0,
                color=color,
                life=1.0,
                decay=0.025,
            )
        )

    def update(self) -> None:
        """Aktualisiert alle Partikel."""
        # Sparks
        live_sparks = []
        for s in self.sparks:
            s.x += s.vx
            s.y += s.vy
            s.vx *= 0.94
            s.vy *= 0.94
            s.life -= s.decay
            if s.life > 0:
                live_sparks.append(s)
        self.sparks = live_sparks

        # Shockwaves
        live_waves = []
        for w in self.shockwaves:
            w.radius += (w.max_radius - w.radius) * 0.12
            w.life -= w.decay
            if w.life > 0:
                live_waves.append(w)
        self.shockwaves = live_waves

        # Floating texts
        live_texts = []
        for t in self.floating_texts:
            t.y += t.vy
            t.life -= t.decay
            if t.life > 0:
                live_texts.append(t)
        self.floating_texts = live_texts

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Zeichnet alle Partikeleffekte auf die gegebene Oberfläche."""
        # 1. Shockwaves
        for w in self.shockwaves:
            alpha = int(max(0, min(255, w.life * 255)))
            if alpha > 0 and w.radius > 2:
                # Transparenter Kreis
                wave_surf = pygame.Surface((int(w.radius * 2 + 4), int(w.radius * 2 + 4)), pygame.SRCALPHA)
                pygame.draw.circle(
                    wave_surf,
                    (w.color[0], w.color[1], w.color[2], alpha),
                    (int(w.radius + 2), int(w.radius + 2)),
                    int(w.radius),
                    width=max(1, int(3 * w.life)),
                )
                surface.blit(wave_surf, (int(w.x - w.radius - 2), int(w.y - w.radius - 2)))

        # 2. Sparks
        for s in self.sparks:
            alpha = int(max(0, min(255, s.life * 255)))
            r = max(1, int(s.radius * s.life))
            spark_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (s.color[0], s.color[1], s.color[2], alpha), (r + 1, r + 1), r)
            surface.blit(spark_surf, (int(s.x - r - 1), int(s.y - r - 1)))

        # 3. Floating Texts
        for t in self.floating_texts:
            alpha = int(max(0, min(255, t.life * 255)))
            txt_surf = font.render(t.text, True, t.color)
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, (int(t.x - txt_surf.get_width() // 2), int(t.y)))
