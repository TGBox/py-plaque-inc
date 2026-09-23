# Py-Plaque-Inc 🦠

Eine vollständige, hochwertige Desktop-Spieladaption des Klassikers **Plague Inc.** in Python unter Verwendung von **Pygame-ce**.

![Py-Plaque-Inc](https://img.shields.io/badge/Python-3.14-blue.svg)
![Pygame-ce](https://img.shields.io/badge/Engine-pygame--ce-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

---

## 🎮 Gameplay & Features

- **Interaktive Vektor-Weltkarte**:
  - Über 35 handgefertigte Länder und Territorien mit echten Grenzen und Klimazonen.
  - Dynamisches Farb-Shading: Gesunde Länder verfärben sich mit steigender Infektion in pulsierendes Blutrot und werden bei Entvölkerung aschgrau.
  - Klickbare Länder mit Detail-Drawer für Bevölkerung (Gesund, Infiziert, Tot), Klima, Wohlstand, Flughäfen, Häfen und Forschungsbeitrag.
- **Flug- und Schiffsverkehr**:
  - Animierte Flugzeuge und Frachtschiffe mit Bogenflugbahnen zwischen offenen Flughäfen und Häfen.
  - Infizierte Fahrzeuge tragen die Seuche über Meere und Kontinente hinweg.
  - Blaue Forschungsflieger transportieren Daten der internationalen Heilmittelforschung.
- **Drei spielbare Pathogentypen**:
  - **Bakterie**: Solide Basisresistenzen gegen Hitze und Kälte dank der Spezialfähigkeit *Bakterielle Schutzhülle*.
  - **Virus**: Hohe Mutationsrate mutiert automatisch und kostenlos neue Symptome (*Virale Instabilität*).
  - **Pilz**: Reist passiv schwer über Ozeane, kann aber mit dem *Sporenausbruch* auf Knopfdruck zufällige ferne Länder infizieren.
- **Vollständiger Evolutions-Tech-Tree**:
  - **Übertragung**: Luft I/II, Wasser I/II, Bio-Aerosol, Vögel I/II, Nagetiere I/II, Blut I/II, Insekten I/II.
  - **Symptome**: Übelkeit, Erbrechen, Husten, Niesen, Lungenentzündung, Hautausschlag, Schlaflosigkeit, Paranoia, Organversagen, Hämorrhagischer Schock, Totales Organversagen.
  - **Fähigkeiten**: Kälteresistenz I/II, Hitzeresistenz I/II, Arzneimittelresistenz I/II, Genetische Härtung I/II, Gen-Umstrukturierung sowie Pathogen-Exklusivupgrades.
- **Klickbare DNA- & Heilmittelblasen**:
  - Rote Blasen bei Erstinfektion neuer Länder.
  - Orange Bonusblasen bei Ausbrüchen.
  - Blaue Heilmittelblasen zur Sabotage der globalen Forschung.
  - Glüheffekte, Schwebeflüge und Funken-Partikelexplosionen beim Zerplatzen.
- **Nachrichten-Ticker & Meilensteine**:
  - Rollende Schlagzeilen für Ausbruchsmeilensteine, Grenz- und Flughafenschließungen, WHO-Alarme und humorvolle Weltnachrichten.
- **Geschwindigkeitsregler**:
  - Pause (`||`), Normaltempo (`>`), 2.5x (`>>`) und 5.0x (`>>>`).
- **Endauswertungs-Diagramm**:
  - Historischer Zeitverlaufsgraph mit Multikurven (Gesunde, Infizierte, Tote und Heilmittel %) über die gesamte Spieldauer.

---

## 🚀 Installation & Schnellstart

Das Projekt nutzt den modernen Paketmanager **uv**:

```bash
# Repository klonen & Verzeichnis betreten
cd py-plaque-inc

# Abhängigkeiten installieren
uv sync

# Spiel starten
uv run py-plaque-inc
```

Alternativ kann das Spiel direkt über das Modul gestartet werden:

```bash
uv run python -m py_plaque_inc.main
```

---

## 🧪 Tests ausführen

Das Projekt verfügt über eine automatisierte Testsuite für Simulationslogik, Geometriedaten und Headless-Rendering:

```bash
uv run pytest
```

---

## 🕹️ Steuerung & Tastatur-Kürzel

| Aktion | Steuerung |
| :--- | :--- |
| **Pause / Fortsetzen** | `Leertaste` (pausiert oder stellt vorheriges Tempo wieder her) oder `0` |
| **Geschwindigkeit 1x / 2.5x / 5x** | Zifferntasten `1`, `2`, `3` (auch auf dem Ziffernblock) |
| **Vollbild umschalten** | `F11` oder `Alt + Enter` (unterstützt 1920x1080 & 2560x1080 Ultrawide) |
| **Mutationen zurückentwickeln** | Im Evolutionsbaum auf erforschtes Upgrade klicken & `RÜCKENTWICKELN (+2 DNA)` wählen |
| **Startland wählen** | Vor Spielbeginn ein beliebiges Land auf der Karte anklicken |
| **Land selektieren** | Klick auf ein Land auf der Karte |
| **Land-Details öffnen** | Erneuter Klick auf das gewählte Land oder Button `🌍 LAND-INFO` |
| **Blasen platzen lassen** | Linksklick auf rote, orange oder blaue Blasen |
| **Evolution öffnen** | Klick auf `🧬 EVOLUTION` |
| **Upgrades erforschen** | Knoten im Evolutionsbaum auswählen und `JETZT ERFORSCHEN` klicken |
| **Sporenausbruch (Pilz)** | Klick auf `🍄 SPOREN` in der Fußzeile |
| **Menü / Beenden** | Fenster-Schließen-Button oder ESC |
