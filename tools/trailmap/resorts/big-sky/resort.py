"""Big Sky Resort's 2025-26 trail maps (bigskyresort.com, its trail-maps page; the PDFs are on cdn.sanity.io): three
PDFs, each one vector page over a painting: the main map and its two insets, the South Face (Shedhorn, Dakota and
the south side of Lone Peak) and the Bowl (Lone Peak's bowl under the tram). Read by tools/trailmap/pdf_resort.py,
panel by panel (panels/<panel>/resort.py and decisions.py, which take NAMES and AREA_OF from here); prepare.py
extracts them."""
import json
import os

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'All three mountains'), ('south-face', 'South Face'), ('bowl', 'The Bowl')]
# the mountains, each with its summit elevation as printed (Lone Mountain 11,166 ft; Andesite Mountain 8,800 ft;
# Spirit Mountain 8,028 ft, above the Spanish Peaks)
AREAS = [('lone-mountain', 'Lone Mountain', 11166), ('andesite', 'Andesite Mountain', 8800),
         ('spanish-peaks', 'Spanish Peaks', 8028)]

# the resort's trail report (report.json: every trail with its lift area and rating)
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
# names as the report spells them (the maps print capitals): pdf_resort.py matches each printed name to one
NAMES = [name for name, _area, _rating in REPORT]
# the report's lift areas on Andesite Mountain and the Spanish Peaks; the rest are on Lone Mountain
MOUNTAIN = {'Ramcharger Area': 'andesite', 'Thunder Wolf Area': 'andesite', 'Southern Comfort Area': 'andesite',
            'Lone Moose Area': 'andesite', 'Spanish Peaks Area': 'spanish-peaks'}
AREA_OF = {name: MOUNTAIN.get(area, 'lone-mountain') for name, area, _rating in REPORT}


# text in the names' style that isn't a run: elevations, lodges and clubs, pointers to the insets
NOT_NAMES = ('ELEV', 'Members Only', 'www', 'LODGE', 'MID-STATION', 'SEE INSET', 'SEE SOUTH FACE', 'FOR BOWL',
             'FOR SHEDHORN', 'TERRAIN SEE')
# the terrain parks (orange names on orange lines)
PARKS = {'Plain Jane Park', 'Swifty Park', 'The Cache', 'Wolf Pup Park', 'Explorer Park', 'Cowpoke Park'}


def is_name(label):
    """Dark text in the names' font (the terrain parks' names are orange); not the white halo copies."""
    col = label.get('color') or (1, 1, 1)
    dark, orange = max(col) < 0.2, max(abs(a - b) for a, b in zip(col, (0.96, 0.51, 0.12))) < 0.03
    if 'Semi' not in label.get('font', '') or not (dark or orange):
        return False
    t = ' '.join(label['text'].split())
    return not any(w in t for w in NOT_NAMES)
