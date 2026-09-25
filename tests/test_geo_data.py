"""Tests für Geometriedaten, Landesgrenzen und Routen."""

import pytest
from py_plaque_inc.map.geo_data import create_world_countries
from py_plaque_inc.model.transport import REGIONAL_ROUTES


def test_countries_polygons_valid():
    """Prüft, dass alle 51 Territorien existieren und gültige Polygone haben."""
    countries = create_world_countries()
    assert len(countries) == 51

    # Spezifische Anforderung: Deutschland darf NICHT mit Italien verbunden sein!
    assert "ita" not in countries["deu"].neighbors, "Deutschland darf nicht direkt an Italien grenzen!"
    assert "deu" not in countries["ita"].neighbors, "Italien darf nicht direkt an Deutschland grenzen!"
    assert "ceu" in countries["deu"].neighbors, "Deutschland muss an Zentraleuropa grenzen!"
    assert "ceu" in countries["ita"].neighbors, "Italien muss an Zentraleuropa grenzen!"

    total_pop = sum(c.population for c in countries.values())
    assert 7_000_000_000 <= total_pop <= 8_500_000_000, f"Weltbevölkerung unplausibel: {total_pop}"

    for c_id, country in countries.items():
        assert country.id == c_id
        assert len(country.name) > 0
        assert country.population > 0
        assert len(country.polygons) >= 1

        # Polygone prüfen
        for poly in country.polygons:
            assert len(poly) >= 3, f"Polygon in {country.name} hat weniger als 3 Punkte."
            for pt in poly:
                assert len(pt) == 2
                x, y = pt
                assert 20 <= x <= 1260, f"X-Koordinate {x} in {country.name} außerhalb des Kartenbereichs."
                assert 64 <= y <= 644, f"Y-Koordinate {y} in {country.name} außerhalb des Kartenbereichs."

        # Hauptstadt prüfen
        cx, cy = country.capital_pos
        assert 20 <= cx <= 1260, f"Hauptstadt X {cx} in {country.name} außerhalb."
        assert 64 <= cy <= 644, f"Hauptstadt Y {cy} in {country.name} außerhalb."

        # Nachbarn müssen existieren
        for n_id in country.neighbors:
            assert n_id in countries, f"Nachbarland {n_id} von {country.name} existiert nicht in der Weltkarte!"
            # Bidirektionale Nachbarschaft prüfen
            assert country.id in countries[n_id].neighbors, f"Nachbarschaft zwischen {country.id} und {n_id} ist nicht symmetrisch!"


def test_point_in_polygon_contains_capital():
    """Prüft, dass die Hauptstadt jedes Landes innerhalb eines seiner Polygone liegt."""
    from py_plaque_inc.map.geo_data import create_world_countries

    def point_in_polygon(x, y, polygon):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    countries = create_world_countries()
    for c_id, country in countries.items():
        cx, cy = country.capital_pos
        inside = any(point_in_polygon(cx, cy, poly) for poly in country.polygons)
        assert inside, f"Hauptstadt {c_id} ({cx}, {cy}) liegt außerhalb aller Polygone von {country.name}!"


def test_transport_routes_valid():
    """Prüft, dass alle Routen in REGIONAL_ROUTES auf existierende Länder verweisen."""
    countries = create_world_countries()
    for orig, dests in REGIONAL_ROUTES.items():
        assert orig in countries, f"Ursprungsland {orig} in REGIONAL_ROUTES nicht in Ländern!"
        for dest in dests:
            assert dest in countries, f"Zielland {dest} in REGIONAL_ROUTES[{orig}] nicht in Ländern!"
