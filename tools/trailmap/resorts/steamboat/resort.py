"""Steamboat's 2026-27 trail map (the resort's image, 2400x1682 px; its Morningside Park inset top left) with its
interactive map's SVG as the vector layer (resorts-interactive.com map 1800: every trail's line, letters and symbol
grouped under the trail's name). prepare.py extracts it; read by tools/trailmap/pdf_resort.py."""
import json
import os

CLIP = (0, 0, 2400, 1682)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the SVG's units on the image (px): registered on its painting (register_pages.py --ref background.png
# --ref-scale 2.17205: 435 inliers, median 0.23 px), then fitted on the image's blue line ink (vicomap.py fit-ink:
# median 0.5 px to the nearest ink pixel)
VICOMAP_AFFINE = (0.6435679, -0.0001260, 46.3595, -0.0000327, 0.6512624, 58.6890)
SOURCE = ("Steamboat 2026-27 trail map image (steamboat.com) with its interactive map's SVG lines "
          '(resorts-interactive.com map 1800), tools/trailmap/resorts/steamboat/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its group's name (pdf_resort.py names it by that)
SYMBOL_REACH = 12  # px from a name's first or last letter to its symbol
END_REACH = 8  # px from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 3  # px: a name printed beside its line


def is_name(label):
    return True


# the resort's trail report (report.json: the mtnpowder feed). Its areas are one (Steamboat), its snowshoe trails,
# parks and boundary gates apart
REPORT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.json')))['trails']
NAMES = sorted({n for n, a, _r in REPORT if a != 'Boundary Access Gates'})
AS_PRINTED = True
# one area, the report's: its elevation the summit's, Mt. Werner's as printed
AREAS = [('steamboat', 'Steamboat', 10568)]


def area(c):
    return 'steamboat'


JOIN = []
TWO_LINE = set()
NO_STRETCH = set()
LABEL_LINE = set()
# All Out, printed "(closed to public)", is no run the report lists (the mogul course's): left out with its lines;
# Duster and Chisholm Trail are the snowshoe trails (purple dashes; the report's Snowshoe Trails); the SVG's Over Easy
# in the Morningside inset is printed nowhere there (miss/oe crops)
DROP = [('All Out', (1515, 1343)), ('Duster', None), ('Chisholm Trail', None), ('Over Easy', (529, 113))]
RENAME = {}
# the terrain parks, printed in their orange areas and in no group of the interactive map: placed where printed
# (miss/parks crops), named as printed (the report has Maverick's Half Pipe for the Superpipe and Lil' Rodeo Park,
# and neither Maverick's Terrain Park nor Mini Mav's Pipe, printed under Lil' Rodeo's name)
EXTRA = [('Rabbit Ears Terrain Park', 1170, 1262), ("Maverick's Superpipe", 1295, 1253),
         ("Maverick's Terrain Park", 1315, 1290), ("Lil' Rodeo Terrain Park", 1655, 1478),
         ("Mini Mav's Pipe", 1631, 1496)]
SYMBOL_FIX = []
DISPLAY = {}
GLADES = set()
PARKS = {e[0] for e in EXTRA}
NO_LINE = {}
