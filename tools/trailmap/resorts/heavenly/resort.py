"""Heavenly's trail map: the resort's 2024-25 artwork, still its current map, as an image on Vail Resorts' scene7 CDN
(3652 x 4990 px; skiheavenly.com shows it on its trail-map page and links no winter PDF): the main painting of the
California and Nevada sides, and below it the Top of Gondola inset, as two panels. Its lines, names and symbols come
from the 2022-23 PDF of the same artwork (skimap.org map 23043), registered on the paintings, and every place the
two editions differ is checked on the image (prepare.py). Read by tools/trailmap/pdf_resort.py, panel by panel
(panels/<panel>/resort.py and decisions.py, which take NAMES and AREA_OF from here)."""
import json
import os

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'California and Nevada'), ('top-of-gondola', 'Top of Gondola')]
# the trail report's three areas, each with its highest point: as printed, the top of the Sky Express in California
# (10,040 ft) and the summit above Milky Way Bowl in Nevada (10,067 ft); the map prints none in the Top of Gondola
# area: the top of the Tamarack Express (9,725 ft, as Vail Resorts gives it: news.vailresorts.com, 2009-06-25)
AREAS = [('california', 'California', 10040), ('nevada', 'Nevada', 10067), ('top-of-gondola', 'Top of Gondola', 9725)]

# the resort's trail report (report.json: every trail with its area and rating), this season's and the one the map
# was drawn for (2024-25: some runs have been renamed or split into an upper and a lower part since)
_doc = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))
REPORT = _doc['trails'] + [t for t in _doc['trails_2024_25'] if t[0] not in {r[0] for r in _doc['trails']}]
# names as the report spells them (the map prints capitals): pdf_resort.py matches each printed name to one
NAMES = [name for name, _area, _rating in REPORT]
AREA_ID = {'California': 'california', 'Nevada': 'nevada', 'Top of Gondola': 'top-of-gondola'}
AREA_OF = {name: AREA_ID[area] for name, area, _rating in REPORT}
# names neither report lists: the runs the reports split into an upper and a lower part (their area), Upper
# Powderbowl's and Mombo's (the reports' Powderbowl Upper and Mombo Upper), and Mott and Killebrew Canyons' chutes
AREA_OF.update({'California Trail': 'top-of-gondola', "Liz's": 'california', 'Gunbarrel': 'california',
                'Comstock': 'nevada', 'Mineshaft': 'nevada', 'Olympic Downhill': 'nevada', 'Stagecoach': 'nevada',
                'Von Schmidt': 'top-of-gondola', 'Rim Trail': 'nevada'})

# the image's panels (px of the scene7 image: x0, y0, x1, y1)
BOX = {'main': (0, 0, 3652, 2984), 'top-of-gondola': (0, 3021, 2368, 4123)}
# the 2022-23 PDF's page (pt) on the image (px), registered on each painting (SIFT matches, RANSAC: 5837 inliers on
# the main painting, median residual 0.10 px; 4360 on the inset, 0.25 px):
# x = a pt_x + b pt_y + c, y = d pt_x + e pt_y + f
AFFINE = {'main': (3.1251050, -0.0000082, -3.7062, 0.0000042, 3.1255520, -8.5815),
          'top-of-gondola': (3.1248725, 0.0001776, -7.9272, 0.0001258, 3.1239900, -7.3672)}

# where the 2024-25 image differs from the 2022-23 page (every changed area checked on the image): what the image no
# longer prints there, left out of the page's reading by prepare.py (main-panel px): Upper Powderbowl's and Powderbowl
# Run's labels and squares (printed elsewhere since: panels/main/resort.py EXTRA) and Widow Maker (Lone Wolf now)
GONE = {'main': {'labels': [('UPPER POWDERBOWL', (2661, 1096)), ('POWDERBOML RUN', (2743, 1293)),
                            ('WIDOW MAKER', (561, 1216))],
                 'symbols': [(2562, 1044), (2712, 1203)]}}
