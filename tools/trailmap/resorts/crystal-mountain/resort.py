"""Crystal Mountain's 2025-26 trail map (VistaMap's painting) in two panels: the trail map PDF's one page (the main
map: panels/main/resort.py) and the Northway inset image the trail-maps page shows beside it (the Northway lift's
terrain, behind the main map's ridge: panels/northway/resort.py, read on crops in names.py). What both share: the
trail report, its areas, the names' spellings. Read by tools/trailmap/pdf_resort.py; prepare.py extracts both."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = [('main', 'Crystal Mountain'), ('northway', 'Northway')]

# the trail report (report.json: the conditions widget's mtnpowder feed): every run with its area
REPORT = json.load(open(os.path.join(HERE, 'report.json')))['trails']
# its areas, each with its highest point printed: Silver King (7,012 ft) for the Frontside and High Campbell, Northway
# Peak (6,776 ft) for the North, Silver Queen (7,002 ft) for the South; the Lower Mountain's the Quicksilver and
# Chinook tops (about 5,000 ft: OpenStreetMap's lift lines on the USGS's 10 m elevation model)
AREAS = [('frontside', 'Frontside', 7012), ('north', 'North', 6776), ('high-campbell', 'High Campbell', 7012),
         ('south', 'South', 7002), ('lower-mountain', 'Lower Mountain', 5000)]
_AREA_ID = {name: aid for aid, name, _e in AREAS}


def key(name):
    """A name with case, spaces and punctuation left out (pdf_resort.py's spelling_key)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


# the names the report lists, and those it doesn't but the resort's interactive map spells (the map prints capitals)
VICOMAP_NAMES = ['Big Shot', 'Bluebell Trail to Parking Lot C', 'CMAC', 'Cutover', 'Easy Street', 'Green Valley Bowl',
                 'I-405', "Jack's Cut", "Jeremy's Road", 'Jump Hill', 'Lower Grub', 'Lumpy Lane', 'Snake Pit',
                 'The Plunge', 'To Lot H', '13F', 'Boxcar Cornice', "Double 00's Left", "Double 00's Right", 'Frisco',
                 'Hamburger', 'K2 Face', 'Lower Chance', 'Neanderthal', 'S.E. Trees', 'Southback', 'Three Way Exit']
# and the names neither lists, as printed (the parks, a ridge, a glade)
PRINTED_NAMES = ["Arwine's Park", 'Disco Park', 'Sudden Drop Park', 'Gun Tower Ridge', 'The Airstrip', 'Pixie Trees',
                 'Rolling Knolls Chutes']
NAMES = sorted({n for n, *_r in REPORT} | set(VICOMAP_NAMES) | set(PRINTED_NAMES))
# runs the map prints that the report doesn't list, with their areas (where each is printed: the North for the Northway
# side, the South for Silver Basin's and Southback's, High Campbell for the Campbell Basin chutes, the Lower Mountain for
# the base and the parks, the Frontside for the rest)
NOT_IN_REPORT = {
    'Northway Bowl': 'north', 'Horseshoe Cliffs': 'north', 'To Lot H': 'north', 'Niagaras': 'north',
    'O-Meadows': 'north', '13F': 'north', 'I-405': 'north', 'Gun Tower Ridge': 'north',
    'Boxcar Cornice': 'south', 'S.E. Trees': 'south', 'Southback': 'south', 'Three Way Exit': 'south',
    'Hamburger': 'high-campbell', "Double 00's Left": 'high-campbell', "Double 00's Right": 'high-campbell',
    'Big Shot': 'frontside', 'Cutover': 'frontside', 'Green Valley Bowl': 'frontside', "Jack's Cut": 'frontside',
    "Jeremy's Road": 'north', 'K2 Face': 'frontside', 'Frisco': 'frontside', 'Lower Chance': 'frontside',
    'Lower Grub': 'frontside', 'Neanderthal': 'frontside', 'Snake Pit': 'frontside', 'The Plunge': 'frontside',
    'Pixie Trees': 'frontside', 'Rolling Knolls Chutes': 'frontside', 'Easy Street': 'lower-mountain',
    'Lumpy Lane': 'lower-mountain', 'CMAC': 'lower-mountain', 'Jump Hill': 'lower-mountain',
    'Bluebell Trail to Parking Lot C': 'lower-mountain', 'The Airstrip': 'south', "Arwine's Park": 'lower-mountain',
    'Disco Park': 'lower-mountain', 'Sudden Drop Park': 'lower-mountain'}
NAMES = sorted(set(NAMES) | set(NOT_IN_REPORT))
AS_PRINTED = False
AREA_OF = dict(NOT_IN_REPORT)
for _n, _a, *_r in REPORT:
    AREA_OF.setdefault(_n, _AREA_ID[_a])
PARKS = {"Arwine's Park", 'Disco Park', 'Sudden Drop Park'}  # the Crystal Parks' orange pills
# printed otherwise than the report spells them
RENAME = {'DOUBLE OO’s LEFT': "Double 00's Left", 'DOUBLE OO’s RIGHT': "Double 00's Right", 'YAWECIULS': 'Sluiceway',
          'TOHS GIB': 'Big Shot', 'NIAGRAS': 'Niagaras', '0-MEADOWS': 'O-Meadows', 'DISCOVERY MEADOW': 'Discover Meadow',
          'GOLD HILLS RUN': 'Gold Hills', 'OTTO BAHN': 'Upper Otto Bahn', 'LOWER BRAND-X CLIFFS': 'Lower Brand-X Cliff',
          'ACK’S CUT': "Jack's Cut"}  # its curved letters, the J set in another font


def is_name(label):
    """The runs' names: FuturaPTCond-Medium 12 pt."""
    return label['font'] == 'FuturaPTCond-Medium' and abs(label['size'] - 12) < 0.2


def spelled(n):
    """A printed name as the report spells it (RENAME, else NAMES by its letters)."""
    n = RENAME.get(n, n)
    return {key(x): x for x in NAMES}.get(key(n), n)
