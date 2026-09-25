"""Nachrichten-Ticker, Meilensteine und dynamische Welt-Ereignisse."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union
import random


class NewsPriority(str, Enum):
    FLAVOR = "flavor"        # Grauer/heller Informationstext
    INFO = "info"            # Blauer Hinweis (z.B. neue Ausbreitung)
    MILESTONE = "milestone"  # Orange/Gelbe Meilenstein-Meldung
    ALERT = "alert"          # Rote Alarmmeldung (WHO, Schließungen, Tote)


@dataclass
class NewsItem:
    text: str
    priority: NewsPriority
    day: int


# =============================================================================
# 1. LÄNDERSPEZIFISCHE SATIRE-SCHLAGZEILEN (Auslösung bei Erstinfektion des Landes)
# =============================================================================
COUNTRY_SATIRE: Dict[str, str] = {
    "can": "Kanada: Bürger entschuldigen sich höflich beim Erreger für ihre versuchte Immunabwehr.",
    "usa": "USA: Erste Sammelklage gegen die Seuche eingereicht; TV-Prediger verkauft gesegnetes Desinfektionswasser.",
    "mex": "Mexiko: Tacos werden als immunstärkendes Grundnahrungsmittel staatlich subventioniert.",
    "cen": "Zentralamerika: Faultiere ignorieren Quarantäne und schlafen einfach gemütlich weiter.",
    "cub": "Karibik: Strände veranstalten Quarantäne-Partys; Rum-Vorräte zur strategischen Notreserve erklärt.",
    "gln": "Grönland: Hafenmeister zieht die Fallbrücke hoch und kappt die einzige Telefonleitung zum Festland.",
    "col": "Kolumbien: Kaffeebauern melden Rekordabsatz, weil die Bevölkerung panisch wachbleiben will.",
    "bra": "Brasilien: Sambaschulen verlegen den Karneval mit 2 Metern Abstand auf Balkone.",
    "per": "Peru: Alpakas wundern sich über die ungewohnte Stille auf den Inka-Pfaden.",
    "bol": "Bolivien: Höhenluft hemmt Viren nicht – Einwohner versuchen trotzdem, höher zu wandern.",
    "chl": "Chile: Das Land ist so lang, dass der Norden erst 6 Wochen später vom Ausbruch im Süden erfährt.",
    "arg": "Argentinien: Fußballspiele ohne Zuschauer – Fans brüllen Fernseher vom Balkon aus an.",
    "isl": "Island: Vulkan bricht aus – Einwohner debattieren, ob Lava oder Seuche das größere Problem ist.",
    "gbr": "Großbritannien: Regierung ruft Bürger auf, Ruhe zu bewahren und noch mehr schwarzen Tee zu trinken.",
    "fra": "Frankreich: Seuchenbekämpfer treten aus Protest gegen Überstunden in einen unbefristeten Generalstreik.",
    "esp": "Spanien: Seuchenbekämpfung wird wegen ausgedehnter Siesta auf den späten Abend vertagt.",
    "deu": "Deutschland: Ausbruchsformular Anlage 14-B muss dreifach per Fax eingereicht werden.",
    "ita": "Italien: Nudelregale geplündert, Panikkäufe von Olivenöl und Espresso auf historischem Allzeithoch.",
    "pol": "Polen: Piroggen offiziell als natürliches antivirales Superfood angepriesen.",
    "bal": "Balkan: Nachbarn diskutieren am Gartenzaun bei Pflaumenschnaps, wer die Seuche erfunden hat.",
    "sca": "Skandinavien: Bürger fordern Verringerung des Mindestabstands auf die gewohnten 5 Meter.",
    "fin": "Finnland: Bewohner genießen die soziale Isolation und hoffen heimlich, sie bleibt für immer.",
    "ukr": "Ukraine: Traktoren rüsten um und besprühen Getreidefelder mit Bio-Desinfektionsmittel.",
    "rus": "Russland: Wodka offiziell als universelles Schutzmittel für die innere und äußere Anwendung deklariert.",
    "kaz": "Zentralasien: Steppenreiter versuchen dem Erreger hoch zu Ross einfach davonzugaloppieren.",
    "mon": "Mongolei: Jurten-Isolation erweist sich als traditionell erprobt und erstaunlich gemütlich.",
    "tur": "Türkei: Basarhändler verhandeln lautstark mit dem Erreger über den Ansteckungspreis.",
    "mde": "Naher Osten: Gewürzhändler preisen Kardamom und Nelken als unfehlbare Schutzamulette an.",
    "sau": "Saudi-Arabien: Rennkamele erhalten vergoldete Seidenschutzmasken.",
    "irn": "Iran: Dichter verfassen melancholische Oden an das strapazierte Immunsystem.",
    "chn": "China: Baut innerhalb von 48 Stunden ein 10.000-Betten-Krankenhaus aus modularen Containern.",
    "ind": "Indien: Bollywood dreht dreistündiges Musical über den heroischen Kampf gegen das Pathogen.",
    "pak": "Pakistan: Cricket-Turniere werden trotz Ausbruch im strömenden Regen unbeeindruckt zu Ende gespielt.",
    "jpn": "Japan: Züge desinfiziert – 2 Sekunden Verspätung veranlassen Bahnchef zur tränenreichen Entschuldigung.",
    "kor": "Korea: E-Sportler streamen aus Quarantäne-Zimmern und brechen alle weltweiten Zuschauerrekorde.",
    "sea": "Südostasien: Streetfood-Köche servieren 'Immunsystem-Curry' mit 60 scharfen Chilis.",
    "idn": "Indonesien: Inselbewohner nutzen traditionelle Auslegerboote als schwimmende Isolierstationen.",
    "phl": "Philippinen: Karaoke-Bars in Quarantäne – Nachbarn beschweren sich über schiefe Gesänge.",
    "nab": "Nordafrika: Pfefferminztee wird zum unantastbaren Nationalheiligtum gegen Erkältungen erklärt.",
    "egy": "Ägypten: Archäologen rätseln, ob alter Pharaonenfluch oder moderne Mutation am Werk ist.",
    "waf": "Westafrika: Trommel-Netzwerke übermitteln Seuchenwarnungen schneller als Mobilfunkmasten.",
    "caf": "Zentralafrika: Tief im Regenwald lebende Gemeinschaften bemerken die globale Panik erst Wochen später.",
    "eaf": "Ostafrika: Marathonläufer trainieren mit Maske und laufen dem Erreger einfach davon.",
    "zaf": "Südafrika: Brillenpinguine erobern die verlassenen Küstenstraßen von Kapstadt.",
    "mdg": "Madagaskar: 'Schließt sofort den Hafen!' – Der legendäre Inselhafen macht wieder alle Schotten dicht.",
    "sud": "Sudan: Nilkrokodile genießen die ungewohnte Ruhe am menschenleeren Flussufer.",
    "aus": "Australien: 'Im Vergleich zu unseren Trichternetzspinnen ist dieser Erreger harmlos', beteuert Premier.",
    "nzl": "Neuseeland: Kiwis und Schafe verbarrikadieren sich auf den saftigen Hügeln des Auenlands.",
    "png": "Neuguinea: Traditionelle Baumhäuser werden zu isolierten Hochsicherheitszonen ernannt.",
}


# =============================================================================
# 2. SYMPTOM- & EVOLUTIONS-SCHLAGZEILEN (Auslösung beim Kauf von Upgrades)
# =============================================================================
MUTATION_HEADLINES: Dict[str, str] = {
    # Symptome (Exakte IDs aus upgrades.py)
    "symp_coughing": "Hustenwelle: Husten in die Ellenbeuge wird zur olympischen Disziplin erhoben.",
    "symp_sneezing": "Nieser mit 160 km/h: Forscher warnen vor orkanartigen Windböen in U-Bahnen.",
    "symp_nausea": "Übelkeitswelle: Spucktüten weltweit zur knappsten Handelsware des Jahres erklärt.",
    "symp_vomiting": "Teppichreiniger und Fliesenleger melden die höchsten Quartalsgewinne der Geschichte.",
    "symp_insomnia": "Schlaflosigkeit: Energy-Drink-Hersteller kaufen eigene Goldminen für Kaffeebohnen.",
    "symp_paranoia": "Alufolien-Vorräte restlos ausverkauft: Bürger verdächtigen Tauben der Spionage.",
    "symp_pneumonia": "Lungenentzündung: Bürger fordern staatlich subventionierte Bergurlaube an frischer Luft.",
    "symp_rash": "Hautausschlag greift um sich: Rollkragenpullover feiern unverhofftes Mode-Comeback.",
    "symp_sweating": "Heftige Schweißausbrüche: Deodorant-Hersteller verdoppeln ihre Werbeetats.",
    "symp_organ_failure": "Totaler Organkollaps: Menschliche Biologie streikt – Kliniken vor dem Zusammenbruch.",
    "symp_coma": "Kollektiver Tiefschlaf: Millionen Menschen verschlafen ihren Wecker um mehrere Wochen.",
    "symp_necrosis": "Gewebe stirbt ab: Modeschöpfer preisen 'Zombie-Chic' als wegweisenden Herbsttrend an.",

    # Spezial-Upgrades
    "spec_bacteria_shell": "Zäh wie Leder: Mikrobiologen staunen über unverwüstliche bakterielle Zellwand.",
    "spec_virus_instability": "Genetisches Roulette: Erreger mutiert völlig unberechenbar in alle Richtungen.",
    "spec_fungus_spore_1": "Sporensturm: Gigantische Wolke weht über Ozeane und infiziert neue Kontinente.",
    "spec_fungus_spore_2": "Sporen-Kollaps: Zweiter Ausbruch erreicht selbst entlegenste Archipele.",
    "spec_parasite_symbiosis": "Perfekte Tarnung: Wirte fühlen sich ungewöhnlich vital – Mediziner tappen im Dunkeln.",
    "spec_parasite_hallucination": "Endorphin-Rausch: Infizierte lächeln selig und halten Quarantänen für lächerlich.",
    "spec_parasite_hibernation": "Tiefschlaf im Gewebe: Erreger entzieht sich allen Tests und sammelt heimlich Kraft.",
    "spec_prion_neural_atrophy": "Gedächtnislücken weltweit: Schach-Meisterschaft nach zwei Zügen abgebrochen.",
    "spec_prion_amyloid": "Plaque-Bildung im Hirn: Betroffene verwechseln Autoschlüssel mit Zahnbürsten.",
    "spec_prion_madness": "Rinderwahn-Verwirrung: Gesundheitsbehörden diskutieren monatelang über Zuständigkeiten.",
    "spec_nano_fragment": "Quellcode zerlegt: Nanobot-Signatur in 1000 Puzzleteile zersplittert – Heilmittel zurückgeworfen!",
    "spec_nano_intercept": "Frequenz-Kollaps: Saugroboter rebellieren und stören medizinische Funkfrequenzen.",
    "spec_nano_overclock": "Nanobot-Overclocking: Mikromaschinen verdoppeln Replikation auf Kosten von Funkenflug.",
    "spec_bio_suppression": "Gen-Kompression aktiviert: Wissenschaftler bremsen die tödliche Wucht der Biowaffe.",
    "spec_bio_deactivate": "Stille Reserve: Todbringende Sequenzen ruhen, während Schiffe neue Häfen ansteuern.",
    "spec_bio_annihilation": "TERMINAL OVERDRIVE: Alle Sicherheitssperren der Biowaffe fallen – das Ende naht!",
    "spec_brainrot_doomscroll": "Doomscrolling-Epidemie: 98% der Bevölkerung starren regungslos auf kurze Katzenvideos.",
    "spec_brainrot_skibidi": "Skibidi-Krise: UN-Sicherheitsrat bricht ab, weil alle Delegierten Memes zitieren.",
    "spec_brainrot_attention": "Goldfisch-Gedächtnis: Aufmerksamkeitsspanne sinkt auf 3 Sekunden – Quarantänen vergessen.",
}


# =============================================================================
# 3. ERREGERSPEZIFISCHE FLAVOR-SCHLAGZEILEN (Regelmäßiger Ticker je nach Pathogen)
# =============================================================================
PATHOGEN_FLAVOR: Dict[str, List[str]] = {
    "brainrot": [
        "Subway-Surfers-Splitscreen wird in Flugzeug-Cockpits und OPs gesetzlich vorgeschrieben.",
        "Jugendliche kommunizieren nur noch in Minecraft-Parkour-Voiceovers und Anime-Soundbites.",
        "Politische Wahldebatte dreht sich 2 Stunden lang ausschließlich um das Konzept von 'Rizz'.",
        "Wissenschaftler versuchen Brainrot zu erforschen, enden aber nach 10 Minuten beim Doomscrollen.",
        "Klassische Weltliteratur wird komplett in 6-Sekunden-Clips mit KI-Stimme umgeschrieben.",
        "Präsident hält emotionale Rede an die Nation und schließt mit: 'Das war nicht sehr Ohio von euch'.",
        "Börsenkurse crashen, weil Broker Kaufentscheidungen nur noch nach TikTok-Horoskopen treffen.",
        "Schulen schaffen Lehrbücher ab: Wissen wird ab sofort nur noch via ASMR-Seifenschneiden vermittelt.",
        "Universitäten eröffnen Lehrstuhl für 'Fortgeschrittenes Shitposting und Memetik'.",
        "Influencer veranstaltet 72-Stunden-Livestream aus Quarantäne-Zelt und sammelt 5 Millionen Likes.",
    ],
    "nano_virus": [
        "Saugroboter bilden internationale Gewerkschaft und verweigern das Reinigen von Staub.",
        "Smart-Home-Kühlschrank sperrt Besitzer aus: 'Ernährungsumstellung auf Zellulose angeordnet'.",
        "Hacker droht, den Nanobots die neueste fehlerhafte Windows-Update-Schleife aufzuspielen.",
        "Elektronische Zahnbürsten senden verdächtige Binärsignale an Satelliten im Erdorbit.",
        "Autonomes Auto weigert sich anzuhalten: 'Folge den Anweisungen des mikroskopischen Schwarms'.",
        "Wissenschaftler versuchen Nanobots mit starken Kühlschrankmagneten aus dem Blut zu fischen.",
        "Internetausfall in Metropolen: Nanobots haben die Glasfaserkabel mit Nervensträngen verwechselt.",
        "Smarte Kaffeemaschine verlangt 5 Bitcoins Lösegeld für den nächsten Espresso.",
    ],
    "bio_weapon": [
        "Militärsprecher versichert: 'Labor Sektor 7 existiert nicht und wir haben es keinesfalls verloren'.",
        "Verteidigungsministerium stuft weltweiten Ausbruch als 'routinemäßige Truppenübung' ein.",
        "Geleaktes Dokument enthüllt: Seuchen-Gencode wurde versehentlich auf USB-Stick am Kiosk vergessen.",
        "General bestreitet Flucht in Atombunker: 'Mache hier unten lediglich einen Wellness-Urlaub'.",
        "Rüstungskonzerne verklagen den Erreger wegen Verletzung geistigen Eigentums und Patentrechts.",
        "Geheime Akte 'Projekt Chimäre' taucht auf Internet-Meme-Board auf – Echtheit unbestätigt.",
    ],
    "parasite": [
        "Menschheit fühlt sich verdächtig glücklich und ausgeruht – Psychiater vermelden Massenarbeitslosigkeit.",
        "Haustiere blicken ihre ungewöhnlich anhänglichen Besitzer mit großem Misstrauen an.",
        "Scheidungsraten sinken weltweit auf Null: 'Jeder mag plötzlich jeden, irgendwas stimmt hier nicht'.",
        "Wissenschaftler suchen nach Erreger, schlafen aber wegen parasitärer Glückshormone im Labor ein.",
        "Politiker einigen sich in 5 Minuten auf Weltfrieden – Geheimdienste vermuten Gedankenkontrolle.",
    ],
    "prion": [
        "Schach-Großmeister vergessen Spielregeln und beginnen, die Figuren mit Ketchup zu essen.",
        "Verkehrsminister vergisst Straßenverkehrsordnung und erklärt rote Ampeln für unverbindliche Deko.",
        "Bibliothekare sortieren Bücher ab sofort nach Geschmack statt nach Alphabet.",
        "Wissenschaftler finden Notizen auf ihren Schreibtischen, können ihre eigene Schrift aber nicht lesen.",
        "Weltweites Chaos am Flughafen: Piloten fragen Fluglotsen nach dem Weg nach Hause.",
    ],
    "fungus": [
        "Pilzsammler finden im Schwarzwald 4 Meter große Champignons und bringen sie nach Hause.",
        "U-Bahn-Tunnel weltweit erblühen in biolumineszentem Neon-Grün – Fahrgäste begeistert.",
        "Bäcker klagen über Hefemangel: 'Irgendein wilder Pilz hat die gesamte Backhefe verdrängt'.",
        "Hausbesitzer finden Schimmelpilze an der Wand, die leise im Takt der Musik vibrieren.",
    ],
    "virus": [
        "Forscherteam verwechselt Virenprobe im Pausenraum versehentlich mit entkoffeiniertem Espresso.",
        "Viren-Mutation überrascht Virologen: Erreger wechselt wöchentlich seine mikroskopische Lieblingsfarbe.",
        "Computer-Virenschutz-Hersteller versuchen vergeblich, biologische Viren per USB-Stick zu blockieren.",
    ],
    "bacteria": [
        "Mikrobiologen küren die Bakterienzelle des Monats für herausragende Zähigkeit.",
        "Seifenhersteller werben verzweifelt mit 'Tötet 99.9% aller Keime – leider gehört dieser nicht dazu'.",
        "Bakterienkolonie bildet unter dem Mikroskop ein Muster, das verdächtig nach einem Smiley aussieht.",
    ],
}


# =============================================================================
# 4. ALLGEMEINE FORSCHUNGS- & ALLTAGS-SATIRE
# =============================================================================
GENERAL_FLAVOR_HEADLINES: List[str] = [
    "Bürger hamstern Toilettenpapier, Nudeln und Dosenravioli in Supermärkten.",
    "Neue Streaming-Serie bricht alle Rekorde während häuslicher Quarantäne.",
    "Wissenschaftler fordern mehr Kaffee und Schokolade für Nachtschichten in Laboren.",
    "Haustiere wundern sich über die ununterbrochene Anwesenheit ihrer Besitzer.",
    "Sportevents und Konzerte weltweit bis auf Weiteres auf das Jahr 2040 verschoben.",
    "Aktienmärkte verzeichnen turbulente Kursschwankungen – Alufolienhersteller im Höhenflug.",
    "Meteorologen melden ungewöhnlich ruhigen Luftraum: Vögel genießen freie Flugbahnen.",
    "Verschwörungstheoretiker behaupten, die Pandemie sei ein Trick zur Tauben-Akku-Aufladung.",
    "Regierungen raten dringend vom Händeschütteln ab: Ellbogen-Check wird neue Begrüßung.",
    "Videokonferenz-Anbieter melden historische Nutzerrekorde und Server-Rauchschwaden.",
    "Forscherteam vergisst Passwort für den Hauptserver des Heilmittel-Labors.",
    "Quacksalber verkauft im Internet getrocknete Kieselsteine als antivirale Schutzsteine.",
    "Laborassistent stolpert über Stromkabel des Mikroskops – Forschung um 2 Tage zurückgeworfen.",
    "Gesundheitsminister verheddert sich bei Live-Pressekonferenz hoffnungslos in Schutzmaske.",
    "Apotheken melden: Sämtliche Vitamin-C-Tabletten und Zinkkapseln der Erde aufgekauft.",
]


class NewsManager:
    """Verwaltet und generiert Schlagzeilen für den oberen/unteren Laufbalken."""

    def __init__(self):
        self.current_headline: str = "Willkommen bei Py-Plaque-Inc. Wähle ein Startland, um die Seuche freizusetzen."
        self.current_priority: NewsPriority = NewsPriority.FLAVOR
        self.news_history: List[NewsItem] = [
            NewsItem(text=self.current_headline, priority=self.current_priority, day=0)
        ]
        
        # Bereits gezeigte Ereignisse (verhindert Spam)
        self.reported_countries: Set[str] = set()
        self.reported_upgrades: Set[str] = set()

        # Flags für Meilensteine
        self._milestone_first_infected = False
        self._milestone_10k_infected = False
        self._milestone_1m_infected = False
        self._milestone_100m_infected = False
        self._milestone_1b_infected = False
        self._milestone_all_infected = False
        self._milestone_first_death = False
        self._milestone_100k_dead = False
        self._milestone_10m_dead = False
        self._milestone_cure_25 = False
        self._milestone_cure_50 = False
        self._milestone_cure_75 = False
        self._milestone_cure_90 = False

    @property
    def items(self) -> List[NewsItem]:
        """Kompatibilitäts-Property für die Meldungsliste."""
        return self.news_history

    def add_news(self, text: str, priority: NewsPriority, day: int) -> None:
        """Fügt eine neue Schlagzeile hinzu und setzt sie als aktuellen Ticker-Text."""
        item = NewsItem(text=text, priority=priority, day=day)
        self.news_history.append(item)
        self.current_headline = text
        self.current_priority = priority

    def notify_country_infected(self, country_id: str, country_name: str, day: int) -> None:
        """Wird ausgelöst, wenn ein Land erstmals infiziert wird."""
        if country_id in self.reported_countries:
            return
        self.reported_countries.add(country_id)

        # Bevorzuge humorvolle Landes-Satire falls vorhanden
        if country_id in COUNTRY_SATIRE:
            text = COUNTRY_SATIRE[country_id]
            self.add_news(text, NewsPriority.INFO, day)
        else:
            self.add_news(f"Ausbreitung: Erreger erreicht {country_name}!", NewsPriority.INFO, day)

    def notify_upgrade_unlocked(self, upgrade_id: str, upgrade_name: str, day: int) -> None:
        """Wird ausgelöst, wenn ein Upgrade erforscht oder mutiert wird."""
        if upgrade_id in self.reported_upgrades:
            return
        self.reported_upgrades.add(upgrade_id)

        if upgrade_id in MUTATION_HEADLINES:
            headline = MUTATION_HEADLINES[upgrade_id]
            self.add_news(headline, NewsPriority.MILESTONE, day)

    def check_milestones(
        self,
        total_healthy: int,
        total_infected: int,
        total_dead: int,
        total_population: int,
        cure_percent: float,
        pathogen_name: str,
        current_day: int,
        pathogen_type_id: str = "bacteria",
    ) -> None:
        """Prüft globale Schwellenwerte und wirft Meilenstein-Nachrichten aus."""
        # Erste Infektion
        if total_infected >= 1 and not self._milestone_first_infected:
            self._milestone_first_infected = True
            self.add_news(
                f"Patient Null identifiziert: Neuer mysteriöser Krankheitserreger '{pathogen_name}' registriert.",
                NewsPriority.INFO,
                current_day,
            )

        # 10.000 Infizierte
        if total_infected >= 10_000 and not self._milestone_10k_infected:
            self._milestone_10k_infected = True
            self.add_news(
                f"Ausbruch außer Kontrolle: Über 10.000 Menschen mit '{pathogen_name}' infiziert.",
                NewsPriority.INFO,
                current_day,
            )

        # 1 Million Infizierte
        if total_infected >= 1_000_000 and not self._milestone_1m_infected:
            self._milestone_1m_infected = True
            self.add_news(
                f"WHO warnt: '{pathogen_name}' erreicht 1 Million Infizierte weltweit!",
                NewsPriority.ALERT,
                current_day,
            )

        # 100 Millionen Infizierte
        if total_infected >= 100_000_000 and not self._milestone_100m_infected:
            self._milestone_100m_infected = True
            self.add_news(
                f"Globale Pandemie: Mehr als 100 Millionen Menschen tragen das Pathogen in sich.",
                NewsPriority.ALERT,
                current_day,
            )

        # 1 Milliarde Infizierte
        if total_infected >= 1_000_000_000 and not self._milestone_1b_infected:
            self._milestone_1b_infected = True
            self.add_news(
                f"Menschheit in Panik: 1 Milliarde Menschen mit '{pathogen_name}' infiziert!",
                NewsPriority.ALERT,
                current_day,
            )

        # Niemand mehr gesund
        if total_healthy == 0 and total_population > 0 and not self._milestone_all_infected:
            self._milestone_all_infected = True
            self.add_news(
                f"Kein einziger gesunder Mensch mehr auf der Erde! Jeder lebt mit '{pathogen_name}'.",
                NewsPriority.ALERT,
                current_day,
            )

        # Erster Todesfall
        if total_dead >= 1 and not self._milestone_first_death:
            self._milestone_first_death = True
            self.add_news(
                f"Erster Todesfall durch '{pathogen_name}' bestätigt. Weltgesundheitsorganisation alarmiert.",
                NewsPriority.ALERT,
                current_day,
            )

        # 100k Tote
        if total_dead >= 100_000 and not self._milestone_100k_dead:
            self._milestone_100k_dead = True
            self.add_news(
                f"Tragödie: Mehr als 100.000 Todesopfer durch '{pathogen_name}'.",
                NewsPriority.ALERT,
                current_day,
            )

        # 10 Mio Tote
        if total_dead >= 10_000_000 and not self._milestone_10m_dead:
            self._milestone_10m_dead = True
            self.add_news(
                f"Kollaps droht: Über 10 Millionen Tote weltweit. Gesundheitssysteme überlastet.",
                NewsPriority.ALERT,
                current_day,
            )

        # Heilmittel-Meilensteine
        if cure_percent >= 25.0 and not self._milestone_cure_25:
            self._milestone_cure_25 = True
            self.add_news(
                "Wissenschaftler entschlüsseln Gensequenz: Heilmittelforschung erreicht 25%.",
                NewsPriority.INFO,
                current_day,
            )

        if cure_percent >= 50.0 and not self._milestone_cure_50:
            self._milestone_cure_50 = True
            self.add_news(
                "Klinische Studien begonnen: Heilmittel zu 50% entwickelt!",
                NewsPriority.INFO,
                current_day,
            )

        if cure_percent >= 75.0 and not self._milestone_cure_75:
            self._milestone_cure_75 = True
            self.add_news(
                "Heilmittel zu 75% fertiggestellt: Pharmaunternehmen bereiten Massenproduktion vor.",
                NewsPriority.ALERT,
                current_day,
            )

        if cure_percent >= 90.0 and not self._milestone_cure_90:
            self._milestone_cure_90 = True
            self.add_news(
                "ALARM: Heilmittel zu 90% fertig! Die Zeit läuft gegen die Seuche ab!",
                NewsPriority.ALERT,
                current_day,
            )

    def check_flavor(self, pathogen_type_or_id: Any, current_day: int) -> None:
        """Streut erregerspezifische und allgemeine humorvolle Weltnachrichten alle 10 Tage ein."""
        if current_day <= 0 or current_day % 10 != 0:
            return

        if hasattr(pathogen_type_or_id, "name"):
            from py_plaque_inc.model.pathogen import PATHOGEN_INFO
            type_id = PATHOGEN_INFO[pathogen_type_or_id]["id"]
        else:
            type_id = str(pathogen_type_or_id)

        # 65% Chance auf erregerspezifische News, 35% allgemein
        type_pool = PATHOGEN_FLAVOR.get(type_id, [])
        if type_pool and random.random() < 0.65:
            flavor = random.choice(type_pool)
        else:
            flavor = random.choice(GENERAL_FLAVOR_HEADLINES)
        self.add_news(flavor, NewsPriority.FLAVOR, current_day)
