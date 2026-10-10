"""Schweitzer, the schweitzer-bowl panel (the resort's 2025-26 image, 3300x2550): names and symbols from the interactive map's groups
(resorts-interactive.com map 1826) and names.py, put on the print by ../../prepare.py. Read by
tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('schweitzer', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
PANEL = 'schweitzer-bowl'

CLIP = (0, 0, 3300, 2550)  # the whole image, in px: the map's units here are its pixels
SCALE = 1
# the interactive map's SVG units on the print (px): registered on its painting (register_pages.py --ref
# painting.jpg --ref-scale 2.77778: 808 inliers, median 0.33 px)
VICOMAP_AFFINE = (0.6731917, -0.0000568, -2.8837, 0.0000036, 0.6857442, -167.8979)
SOURCE = ("Schweitzer trail map (schweitzer-bowl), the interactive map's names and cat tracks (resorts-interactive.com map "
          '1826) on the print, tools/trailmap/resorts/schweitzer/prepare.py; percent of the map image')
GROUPED = True  # every line piece and symbol carries its trail's name (pdf_resort.py names it by that)
MATCH_ENDS = False  # the runs have no lines: names are printed along the painted slope
SYMBOL_REACH = 30  # px from a name's first or last letter to its symbol
END_REACH = 10
ALONG = 8  # px: a cat track's name is printed along its line

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
area = TOP.area_of_panel(PANEL)
COLOR_SYMBOL = TOP.COLOR_SYMBOL
JOIN = []
TWO_LINE = set()
# the runs have no lines: the stretch along each name, from its symbol, is the run's overlay (Heavenly's way); the
# names printed on two lines, and the glades, are markers at their names
LABEL_LINE = set(NAMES) | {'Southside Park', "Britt's Bowl", 'South Bowl Chutes'}
# (and the cat tracks printed beside their navy line, or along it: the line is their overlay)
NO_STRETCH = {'South Bowl Chutes', 'Bunny Hills', 'Cat Track to Village', 'Down the Hatch'}
NO_STRETCH_BESIDE = True
DROP = []
RENAME = {}
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = dict(TOP.DISPLAY)
GLADES = {'JR Trees'}
PARKS = TOP.PARKS
DEFAULT_SYMBOL = TOP.DEFAULT_SYMBOL
NO_LINE = {}
