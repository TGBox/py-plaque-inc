"""Tests für Geometriedaten und Nachbarschaftsbeziehungen."""

import pytest
from py_plaque_inc.map.geo_data import create_world_countries


def test_countries_polygons_valid():
    """Prüft, dass jedes Land gültige Polygone und Hauptstädte hat."""
    countries = create_world_countries()
    assert len(countries) >= 35

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
                assert 0 <= x <= 1280, f"X-Koordinate {x} in {country.name} außerhalb des Bildschirms."
                assert 0 <= y <= 720, f"Y-Koordinate {y} in {country.name} außerhalb des Bildschirms."

        # Zentroid / Hauptstadt prüfen
        cx, cy = country.capital_pos
        assert 0 <= cx <= 1280
        assert 0 <= cy <= 720

        # Nachbarn müssen existieren
        for n_id in country.neighbors:
            assert n_id in countries, f"Nachbarland {n_id} von {country.name} existiert nicht in der Weltkarte!"
