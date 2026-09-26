"""Detailansicht für das aktuell ausgewählte Land mit Schiffs-, Flug- und Infektionsanalyse."""

from typing import Optional, TYPE_CHECKING
import pygame

from py_plaque_inc.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
)
from py_plaque_inc.model.country import Country
from py_plaque_inc.model.transport import get_country_sea_routes
from py_plaque_inc.ui.theme import UITheme
from py_plaque_inc.ui.components import Button
from py_plaque_inc.ui.hud import format_number

if TYPE_CHECKING:
    from py_plaque_inc.model.world import World


class CountryDetailView:
    """Zeigt vertiefte Informationen, Schiffs-/Flugverkehr und Infektionsdiagnose eines Landes."""

    def __init__(self, theme: UITheme):
        self.theme = theme
        self.panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 275, SCREEN_HEIGHT // 2 - 265, 550, 530)
        
        self.btn_close = Button(
            pygame.Rect(self.panel_rect.right - 96, self.panel_rect.bottom - 44, 80, 32),
            "SCHLIESSEN",
            theme.font_tiny,
            bg_color=(35, 45, 60),
            hover_color=(50, 65, 85),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gibt True zurück, wenn die Detailansicht geschlossen werden soll."""
        if self.btn_close.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.panel_rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, country: Country, world: Optional["World"] = None) -> None:
        """Zeichnet das Infopanel zentriert über die Weltkarte."""
        # Abdunkelungs-Layer im Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Panel-Hintergrund
        UITheme.draw_panel(surface, self.panel_rect, bg_color=(15, 20, 30), border_color=(45, 65, 90), border_radius=8)

        # 1. Kopfzeile mit Landesname & Geografie-Typ
        UITheme.draw_text(
            surface,
            f"{country.name.upper()}",
            self.theme.font_title,
            color=(255, 255, 255),
            pos=(self.panel_rect.left + 24, self.panel_rect.top + 16),
        )

        is_island = len(country.neighbors) == 0
        if is_island:
            geo_type = "Inselstaat (Nur Seeweg & Flug)"
        elif not country.has_seaport:
            geo_type = "Binnenstaat (Kein Seehafen)"
        else:
            geo_type = "Küstenstaat"

        sub_txt = f"Klima: {country.climate.value}  |  Wohlstand: {country.wealth.value}  |  {geo_type}"
        UITheme.draw_text(
            surface,
            sub_txt,
            self.theme.font_small,
            color=COLOR_TEXT_MUTED,
            pos=(self.panel_rect.left + 24, self.panel_rect.top + 46),
        )

        # Trennlinie
        pygame.draw.line(
            surface,
            (32, 44, 60),
            (self.panel_rect.left + 24, self.panel_rect.top + 68),
            (self.panel_rect.right - 24, self.panel_rect.top + 68),
            1,
        )

        # ==========================================
        # 2. BEVÖLKERUNGSSTATUS
        # ==========================================
        y = self.panel_rect.top + 76
        UITheme.draw_text(surface, "BEVÖLKERUNGSSTATUS:", self.theme.font_body_bold, color=COLOR_TEXT_PRIMARY, pos=(self.panel_rect.left + 24, y))
        y += 20

        # Fortschrittsbalken für Infektion und Tod
        bar_rect = pygame.Rect(self.panel_rect.left + 24, y, self.panel_rect.width - 48, 16)
        pygame.draw.rect(surface, (25, 35, 45), bar_rect, border_radius=4)
        
        # Gesund (Grün)
        h_width = int(bar_rect.width * (country.healthy / country.population if country.population > 0 else 0))
        if h_width > 0:
            pygame.draw.rect(surface, (40, 160, 80), (bar_rect.left, bar_rect.top, h_width, bar_rect.height), border_radius=4)

        # Infiziert (Rot)
        i_width = int(bar_rect.width * (country.infected / country.population if country.population > 0 else 0))
        if i_width > 0:
            pygame.draw.rect(surface, (220, 45, 45), (bar_rect.left + h_width, bar_rect.top, i_width, bar_rect.height))

        # Tot (Grau/Schwarz)
        d_width = int(bar_rect.width * (country.dead / country.population if country.population > 0 else 0))
        if d_width > 0:
            pygame.draw.rect(surface, (30, 25, 30), (bar_rect.right - d_width, bar_rect.top, d_width, bar_rect.height), border_radius=4)

        pygame.draw.rect(surface, COLOR_PANEL_BORDER, bar_rect, width=1, border_radius=4)
        y += 24

        # Detaillierte Zähler
        counts = [
            ("Gesamtbevölkerung:", format_number(country.population), (255, 255, 255)),
            ("Gesunde Bürger:", f"{format_number(country.healthy)} ({country.healthy / country.population * 100:.1f}%)", COLOR_SUCCESS),
            ("Infizierte:", f"{format_number(country.infected)} ({country.infection_ratio * 100:.1f}%)", COLOR_DANGER),
            ("Todesopfer:", f"{format_number(country.dead)} ({country.dead_ratio * 100:.1f}%)", (150, 160, 175)),
        ]

        for label, val_str, col in counts:
            UITheme.draw_text(surface, label, self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
            UITheme.draw_text(surface, val_str, self.theme.font_tiny, color=col, pos=(self.panel_rect.right - 24, y), align="right")
            y += 16

        # Trennlinie
        y += 6
        pygame.draw.line(surface, (32, 44, 60), (self.panel_rect.left + 24, y), (self.panel_rect.right - 24, y), 1)
        y += 10

        # ==========================================
        # 3. SCHIFFS- & BOOTSVERKEHR (SEEWEGE)
        # ==========================================
        UITheme.draw_text(surface, "SCHIFFS- & BOOTSVERKEHR (SEEWEGE):", self.theme.font_body_bold, color=(80, 190, 255), pos=(self.panel_rect.left + 24, y))
        y += 20

        # 3.1 Hafenstatus
        if not country.has_seaport:
            port_status = "Nicht vorhanden (Binnenstaat)"
            port_col = COLOR_TEXT_MUTED
        elif country.seaports_open:
            port_status = "OFFEN (Schiffe können anlegen)"
            port_col = COLOR_SUCCESS
        else:
            port_status = "GESCHLOSSEN (Seeweg blockiert!)"
            port_col = COLOR_DANGER

        UITheme.draw_text(surface, "Übersee-Hafen:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
        UITheme.draw_text(surface, port_status, self.theme.font_tiny, color=port_col, pos=(self.panel_rect.right - 24, y), align="right")
        y += 17

        # 3.2 Aktive Schiffe & Boote in Fahrt
        in_c, out_c, in_inf, out_inf = 0, 0, 0, 0
        if world and country.has_seaport:
            in_ships, out_ships = world.transport_mgr.get_ships_for_country(country.id)
            in_c, out_c = len(in_ships), len(out_ships)
            in_inf = sum(1 for s in in_ships if s.is_infected)
            out_inf = sum(1 for s in out_ships if s.is_infected)

            if in_c == 0 and out_c == 0:
                ship_txt = "0 Schiffe in Fahrt (0 einlaufend, 0 auslaufend)"
                ship_col = COLOR_TEXT_MUTED
            else:
                inf_notes = []
                if in_inf > 0:
                    inf_notes.append(f"{in_inf} einlaufend infiziert!")
                if out_inf > 0:
                    inf_notes.append(f"{out_inf} auslaufend infiziert")
                suffix = f"  [{', '.join(inf_notes)}]" if inf_notes else ""
                ship_txt = f"{in_c} einlaufend, {out_c} auslaufend{suffix}"
                ship_col = (255, 90, 90) if in_inf > 0 else (120, 210, 255)
        elif not country.has_seaport:
            ship_txt = "Keine Seewege (Landumschlossen)"
            ship_col = COLOR_TEXT_MUTED
        else:
            ship_txt = "Hafenanlage vorhanden"
            ship_col = COLOR_TEXT_MUTED

        UITheme.draw_text(surface, "Schiffe in Fahrt:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
        UITheme.draw_text(surface, ship_txt, self.theme.font_tiny, color=ship_col, pos=(self.panel_rect.right - 24, y), align="right")
        y += 17

        # 3.3 Direkte Seerouten / Partnerhäfen
        routes = get_country_sea_routes(country.id, world.countries if world else None)
        if country.has_seaport and routes:
            if world:
                p_names = [world.countries[r].name for r in routes if r in world.countries]
                route_str = f"{len(routes)} Routen ({', '.join(p_names[:4])}" + ("...)" if len(p_names) > 4 else ")")
            else:
                route_str = f"{len(routes)} Seerouten: {', '.join([r.upper() for r in routes[:4]])}"
            route_col = (180, 215, 255)
        elif not country.has_seaport:
            route_str = "Keine Seerouten"
            route_col = COLOR_TEXT_MUTED
        else:
            route_str = "Regionale Routen vorhanden"
            route_col = COLOR_TEXT_MUTED

        UITheme.draw_text(surface, "Direkte Seerouten:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
        UITheme.draw_text(surface, route_str, self.theme.font_tiny, color=route_col, pos=(self.panel_rect.right - 24, y), align="right")
        y += 20

        # Trennlinie
        pygame.draw.line(surface, (32, 44, 60), (self.panel_rect.left + 24, y), (self.panel_rect.right - 24, y), 1)
        y += 10

        # ==========================================
        # 4. FLUG- & LANDVERKEHR
        # ==========================================
        UITheme.draw_text(surface, "FLUG- & LANDVERKEHR:", self.theme.font_body_bold, color=COLOR_TEXT_PRIMARY, pos=(self.panel_rect.left + 24, y))
        y += 20

        # 4.1 Flughafen
        in_a, out_a, in_a_inf = 0, 0, 0
        if world and country.has_airport:
            in_air, out_air = world.transport_mgr.get_airplanes_for_country(country.id)
            in_a, out_a = len(in_air), len(out_air)
            in_a_inf = sum(1 for a in in_air if a.is_infected)

        if not country.has_airport:
            air_status = "Nicht vorhanden"
            air_col = COLOR_TEXT_MUTED
        elif country.airports_open:
            flight_tag = f"  [{in_a} ein, {out_a} aus]" if (in_a > 0 or out_a > 0) else ""
            if in_a_inf > 0:
                flight_tag += " (1 infiziert!)"
            air_status = f"OFFEN{flight_tag}"
            air_col = (255, 90, 90) if in_a_inf > 0 else COLOR_SUCCESS
        else:
            air_status = "GESCHLOSSEN"
            air_col = COLOR_DANGER

        UITheme.draw_text(surface, "Flughafen & Flüge:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
        UITheme.draw_text(surface, air_status, self.theme.font_tiny, color=air_col, pos=(self.panel_rect.right - 24, y), align="right")
        y += 17

        # 4.2 Landgrenzen & Nachbarn
        if country.neighbors:
            border_txt = "OFFEN" if country.borders_open else "GESCHLOSSEN"
            border_col = COLOR_SUCCESS if country.borders_open else COLOR_DANGER
            if world:
                n_names = [world.countries[n].name for n in country.neighbors if n in world.countries]
                n_tag = f" ({len(country.neighbors)} Nachbarn: {', '.join(n_names[:3])}" + ("...)" if len(n_names) > 3 else ")")
            else:
                n_tag = f" ({len(country.neighbors)} Nachbarn)"
            land_txt = f"{border_txt}{n_tag}"
        else:
            land_txt = "Keine Landgrenzen (Insel)"
            border_col = COLOR_TEXT_MUTED

        UITheme.draw_text(surface, "Landgrenzen:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
        UITheme.draw_text(surface, land_txt, self.theme.font_tiny, color=border_col, pos=(self.panel_rect.right - 24, y), align="right")
        y += 17

        # 4.3 Forschungsbeitrag
        UITheme.draw_text(surface, "Forschungsbeitrag Heilmittel:", self.theme.font_tiny, color=COLOR_TEXT_MUTED, pos=(self.panel_rect.left + 24, y))
        UITheme.draw_text(surface, f"{country.cure_effort:.2f} Einheiten/Tag", self.theme.font_tiny, color=(0, 190, 255), pos=(self.panel_rect.right - 24, y), align="right")
        y += 22

        # Trennlinie vor Diagnose
        pygame.draw.line(surface, (32, 44, 60), (self.panel_rect.left + 24, y), (self.panel_rect.right - 24, y), 1)
        y += 8

        # ==========================================
        # 5. INFEKTIONS-DIAGNOSE (Warum dauert es?)
        # ==========================================
        diag_rect = pygame.Rect(self.panel_rect.left + 24, y, self.panel_rect.width - 48, 52)

        if country.is_infected:
            diag_title = "STATUS: ERREGER HAT DAS LAND ERREICHT"
            diag_desc = f"Die Infektion breitet sich aus ({country.infection_ratio * 100:.1f}% infiziert). Keine Seeweg-Barriere mehr."
            diag_bg = (35, 18, 22)
            diag_border = (200, 60, 60)
        elif in_inf > 0:
            diag_title = "DIAGNOSE: INFIZIERTES SCHIFF IM ANLAUF!"
            diag_desc = f"Ein Schiff mit Erregern ist auf See nach {country.name}! Ankunft steht kurz bevor."
            diag_bg = (42, 20, 25)
            diag_border = (255, 80, 80)
        elif in_a_inf > 0:
            diag_title = "DIAGNOSE: INFIZIERTES FLUGZEUG IM ANFLUG!"
            diag_desc = f"Ein Flugzeug mit Erregern nähert sich {country.name}! Infektion steht kurz bevor."
            diag_bg = (42, 20, 25)
            diag_border = (255, 80, 80)
        else:
            if is_island:
                if not country.seaports_open and not country.airports_open:
                    diag_title = "DIAGNOSE: VOLLSTÄNDIG ABGERIEGELT (ISOLIERT)"
                    diag_desc = "Seehafen und Flughafen geschlossen, keine Landgrenzen. Erfordert Sporen-Mutation!"
                    diag_bg = (40, 16, 20)
                    diag_border = (200, 50, 50)
                elif not country.seaports_open:
                    diag_title = "DIAGNOSE: SEEHAFEN GESCHLOSSEN"
                    diag_desc = "Schiffsverkehr blockiert! Infektion kann nur noch per Flugzeug eingeschleppt werden."
                    diag_bg = (42, 28, 16)
                    diag_border = (220, 120, 40)
                else:
                    diag_title = "DIAGNOSE: ISOLIERTER INSELSTAAT (WENIG SCHIFFE)"
                    has_water = world and (
                        world.pathogen.upgrades.get("trans_water_1") and world.pathogen.upgrades["trans_water_1"].unlocked
                    )
                    if has_water:
                        diag_desc = f"Wasser-Übertragung aktiv. Warte auf ein Schiff aus den {len(routes)} Partnerhäfen."
                    else:
                        diag_desc = "Schiffsverkehr selten. Tipp: 'Wasser-Übertragung' erforschen, um Seewege zu infizieren!"
                    diag_bg = (18, 26, 38)
                    diag_border = (60, 95, 140)
            elif not country.has_seaport:
                if not country.borders_open:
                    diag_title = "DIAGNOSE: BINNENGRENZEN GESCHLOSSEN"
                    diag_desc = "Landgrenzen dicht! Binnenland kann nur noch über den Luftverkehr erreicht werden."
                    diag_bg = (40, 24, 16)
                    diag_border = (200, 100, 40)
                else:
                    diag_title = "DIAGNOSE: BINNENLAND (KEIN SCHIFFSVERKEHR)"
                    diag_desc = "Kein Seehafen. Infektion breitet sich über Landgrenzen der Nachbarländer aus."
                    diag_bg = (18, 26, 38)
                    diag_border = (60, 95, 140)
            else:
                diag_title = "DIAGNOSE: VERNETZTES LAND"
                diag_desc = "Normal über Seewege, Flugrouten und Nachbarländer angebunden."
                diag_bg = (18, 26, 38)
                diag_border = (60, 95, 140)

        UITheme.draw_panel(surface, diag_rect, bg_color=diag_bg, border_color=diag_border, border_radius=6)
        UITheme.draw_text(surface, diag_title, self.theme.font_tiny, color=(255, 230, 230), pos=(diag_rect.left + 10, diag_rect.top + 8))
        UITheme.draw_text(surface, diag_desc, self.theme.font_tiny, color=COLOR_TEXT_PRIMARY, pos=(diag_rect.left + 10, diag_rect.top + 28))

        # Schließen-Button
        self.btn_close.draw(surface)
