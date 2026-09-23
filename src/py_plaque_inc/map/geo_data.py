"""Geografische Vektordaten, Landesgrenzen und Routen für Py-Plaque-Inc."""

from typing import List, Dict
from py_plaque_inc.model.country import Country, Climate, Wealth


def create_world_countries() -> Dict[str, Country]:
    """
    Erstellt die Weltkarte mit ~37 detaillierten Territorien.
    Die Koordinaten sind auf das Spielfenster (1280x720) ausgerichtet
    (Kartenbereich X: 30..1250, Y: 80..630).
    """
    countries: List[Country] = [
        # ==========================================
        # NORDAMERIKA & ARKTIS
        # ==========================================
        Country(
            id="gln",
            name="Grönland",
            population=56_000,
            climate=Climate.COLD,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(455, 115),
            polygons=[
                [(415, 95), (480, 80), (510, 110), (475, 155), (435, 150), (410, 120)]
            ],
            neighbors=[],
        ),
        Country(
            id="can",
            name="Kanada",
            population=39_000_000,
            climate=Climate.COLD,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(280, 175),
            polygons=[
                # Hauptland Kanada
                [(160, 140), (220, 125), (320, 130), (370, 160), (390, 205), (340, 215), (280, 220), (190, 215), (145, 190)],
                # Arktische Inseln
                [(240, 100), (320, 95), (310, 120), (230, 115)]
            ],
            neighbors=["usa"],
        ),
        Country(
            id="usa",
            name="USA",
            population=335_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(260, 270),
            polygons=[
                # US-Hauptland
                [(145, 220), (280, 225), (340, 220), (375, 235), (360, 310), (310, 315), (260, 340), (200, 315), (150, 275)],
                # Alaska
                [(75, 130), (140, 135), (135, 180), (85, 175)]
            ],
            neighbors=["can", "mex"],
        ),
        Country(
            id="mex",
            name="Mexiko",
            population=128_000_000,
            climate=Climate.HOT,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(220, 365),
            polygons=[
                [(190, 320), (260, 345), (275, 375), (250, 395), (215, 375), (180, 340)]
            ],
            neighbors=["usa", "col"],
        ),
        Country(
            id="cub",
            name="Karibik",
            population=44_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(320, 365),
            polygons=[
                [(295, 360), (345, 355), (350, 375), (300, 380)]
            ],
            neighbors=[],
        ),

        # ==========================================
        # SÜDAMERIKA
        # ==========================================
        Country(
            id="col",
            name="Kolumbien",
            population=52_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(285, 415),
            polygons=[
                [(255, 400), (310, 405), (315, 440), (270, 445), (255, 420)]
            ],
            neighbors=["mex", "bra", "per"],
        ),
        Country(
            id="bra",
            name="Brasilien",
            population=215_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(375, 480),
            polygons=[
                [(315, 415), (380, 420), (430, 460), (405, 525), (345, 520), (315, 465)]
            ],
            neighbors=["col", "per", "arg"],
        ),
        Country(
            id="per",
            name="Peru",
            population=34_000_000,
            climate=Climate.ARID,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(280, 485),
            polygons=[
                [(265, 445), (310, 450), (300, 520), (265, 500)]
            ],
            neighbors=["col", "bra", "arg"],
        ),
        Country(
            id="arg",
            name="Argentinien",
            population=46_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(320, 575),
            polygons=[
                [(290, 520), (350, 525), (340, 620), (305, 630), (285, 560)]
            ],
            neighbors=["bra", "per"],
        ),

        # ==========================================
        # EUROPA
        # ==========================================
        Country(
            id="isl",
            name="Island",
            population=380_000,
            climate=Climate.COLD,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(545, 155),
            polygons=[
                [(530, 150), (565, 145), (560, 170), (530, 165)]
            ],
            neighbors=[],
        ),
        Country(
            id="gbr",
            name="Großbritannien",
            population=68_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(575, 225),
            polygons=[
                [(560, 205), (585, 195), (595, 235), (565, 245)]
            ],
            neighbors=[],
        ),
        Country(
            id="fra",
            name="Frankreich",
            population=68_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(605, 270),
            polygons=[
                [(585, 250), (625, 250), (630, 285), (595, 295), (580, 270)]
            ],
            neighbors=["deu", "esp", "ita"],
        ),
        Country(
            id="esp",
            name="Spanien",
            population=48_000_000,
            climate=Climate.HOT,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(565, 315),
            polygons=[
                [(545, 295), (590, 295), (585, 335), (540, 330)]
            ],
            neighbors=["fra"],
        ),
        Country(
            id="deu",
            name="Deutschland",
            population=84_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(640, 240),
            polygons=[
                [(625, 225), (655, 225), (660, 260), (625, 255)]
            ],
            neighbors=["fra", "pol", "ita"],
        ),
        Country(
            id="ita",
            name="Italien",
            population=59_000_000,
            climate=Climate.HOT,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(645, 305),
            polygons=[
                [(630, 280), (655, 280), (660, 325), (645, 335), (635, 305)]
            ],
            neighbors=["fra", "deu"],
        ),
        Country(
            id="sca",
            name="Skandinavien",
            population=27_000_000,
            climate=Climate.COLD,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(645, 160),
            polygons=[
                [(615, 175), (635, 130), (675, 125), (665, 195), (630, 195)]
            ],
            neighbors=["rus"],
        ),
        Country(
            id="pol",
            name="Polen",
            population=38_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(675, 235),
            polygons=[
                [(660, 225), (700, 225), (695, 255), (660, 255)]
            ],
            neighbors=["deu", "ukr", "rus"],
        ),
        Country(
            id="ukr",
            name="Ukraine",
            population=41_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(725, 245),
            polygons=[
                [(698, 230), (755, 230), (750, 270), (695, 265)]
            ],
            neighbors=["pol", "rus", "tur"],
        ),

        # ==========================================
        # RUSSLAND & NORDASIEN
        # ==========================================
        Country(
            id="rus",
            name="Russland",
            population=144_000_000,
            climate=Climate.COLD,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(860, 165),
            polygons=[
                [(680, 135), (820, 115), (1030, 125), (1110, 155), (1050, 210), (880, 205), (750, 215), (700, 215)]
            ],
            neighbors=["sca", "pol", "ukr", "kaz", "chn"],
        ),

        # ==========================================
        # NAHER OSTEN & ZENTRALASIEN
        # ==========================================
        Country(
            id="tur",
            name="Türkei",
            population=85_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(720, 295),
            polygons=[
                [(690, 280), (755, 285), (750, 315), (685, 310)]
            ],
            neighbors=["ukr", "irn", "sau", "egy"],
        ),
        Country(
            id="sau",
            name="Saudi-Arabien",
            population=36_000_000,
            climate=Climate.ARID,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(755, 365),
            polygons=[
                [(725, 335), (780, 340), (790, 395), (745, 400), (720, 360)]
            ],
            neighbors=["tur", "irn", "egy"],
        ),
        Country(
            id="irn",
            name="Iran",
            population=88_000_000,
            climate=Climate.ARID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(795, 315),
            polygons=[
                [(760, 295), (830, 300), (825, 345), (765, 340)]
            ],
            neighbors=["tur", "sau", "kaz", "ind"],
        ),
        Country(
            id="kaz",
            name="Zentralasien",
            population=75_000_000,
            climate=Climate.ARID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=False,
            capital_pos=(830, 235),
            polygons=[
                [(760, 215), (890, 215), (885, 275), (765, 275)]
            ],
            neighbors=["rus", "irn", "chn"],
        ),

        # ==========================================
        # ASIEN
        # ==========================================
        Country(
            id="chn",
            name="China",
            population=1_410_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(965, 285),
            polygons=[
                [(890, 225), (1010, 220), (1050, 290), (1020, 355), (935, 355), (880, 305)]
            ],
            neighbors=["rus", "kaz", "ind", "sea", "kor"],
        ),
        Country(
            id="ind",
            name="Indien",
            population=1_428_000_000,
            climate=Climate.HOT,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(885, 375),
            polygons=[
                [(845, 315), (925, 315), (920, 375), (895, 435), (855, 385)]
            ],
            neighbors=["irn", "chn", "sea"],
        ),
        Country(
            id="kor",
            name="Korea",
            population=52_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(1065, 285),
            polygons=[
                [(1052, 270), (1075, 270), (1070, 305), (1050, 300)]
            ],
            neighbors=["chn"],
        ),
        Country(
            id="jpn",
            name="Japan",
            population=124_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(1115, 285),
            polygons=[
                [(1095, 255), (1125, 255), (1135, 315), (1100, 315)]
            ],
            neighbors=[],
        ),
        Country(
            id="sea",
            name="Südostasien",
            population=380_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(975, 410),
            polygons=[
                [(940, 360), (1005, 360), (1000, 440), (965, 445), (945, 395)]
            ],
            neighbors=["chn", "ind"],
        ),
        Country(
            id="idn",
            name="Indonesien",
            population=275_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(1025, 495),
            polygons=[
                [(960, 475), (1040, 465), (1085, 490), (1060, 520), (970, 510)]
            ],
            neighbors=[],
        ),

        # ==========================================
        # AFRIKA
        # ==========================================
        Country(
            id="egy",
            name="Ägypten",
            population=110_000_000,
            climate=Climate.ARID,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(690, 355),
            polygons=[
                [(650, 335), (715, 335), (710, 390), (645, 385)]
            ],
            neighbors=["tur", "sau", "waf", "caf", "eaf"],
        ),
        Country(
            id="waf",
            name="Westafrika",
            population=420_000_000,
            climate=Climate.HOT,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(585, 425),
            polygons=[
                [(535, 370), (645, 385), (635, 460), (550, 460), (525, 410)]
            ],
            neighbors=["egy", "caf"],
        ),
        Country(
            id="caf",
            name="Zentralafrika",
            population=180_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(665, 465),
            polygons=[
                [(640, 410), (695, 410), (700, 510), (640, 500)]
            ],
            neighbors=["egy", "waf", "eaf", "zaf"],
        ),
        Country(
            id="eaf",
            name="Ostafrika",
            population=350_000_000,
            climate=Climate.HOT,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(735, 455),
            polygons=[
                [(705, 395), (765, 415), (750, 510), (700, 495)]
            ],
            neighbors=["egy", "caf", "zaf"],
        ),
        Country(
            id="zaf",
            name="Südafrika",
            population=60_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(685, 575),
            polygons=[
                [(650, 515), (730, 515), (715, 615), (660, 610)]
            ],
            neighbors=["caf", "eaf"],
        ),
        Country(
            id="mdg",
            name="Madagaskar",
            population=29_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(775, 555),
            polygons=[
                [(765, 530), (785, 530), (780, 580), (760, 575)]
            ],
            neighbors=[],
        ),

        # ==========================================
        # OZEANIEN
        # ==========================================
        Country(
            id="aus",
            name="Australien",
            population=26_000_000,
            climate=Climate.ARID,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(1095, 555),
            polygons=[
                [(1020, 515), (1140, 515), (1165, 595), (1060, 610), (1025, 560)]
            ],
            neighbors=[],
        ),
        Country(
            id="nzl",
            name="Neuseeland",
            population=5_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(1210, 615),
            polygons=[
                [(1195, 595), (1220, 595), (1215, 635), (1190, 630)]
            ],
            neighbors=[],
        ),
    ]

    return {c.id: c for c in countries}
