"""Mammoth Mountain, the whole mountain (page 2 of the 2025-26 map PDF, right of the information panel and above the
Unbound panel; the back-side inset in its lower right corner is its own panel). Names are text on a white halo, the
symbol before the name, the label turned along its run; no trail lines are drawn: the lines are the interactive
map's (resorts-interactive.com map 1812). Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('mammoth', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (280, 0, 1728, 877)  # PDF points: the map, right of the information panel, above the Unbound panel
SCALE = 2.5  # map px per PDF point
# the interactive map's SVG units on the map image (px): registered on its painting (register_pages.py --ref
# background.jpeg --ref-scale 2.66634: 106 inliers, median 0.27 px; the painting's offset in the SVG folded in)
VICOMAP_AFFINE = (0.6863808, 0.0001300, -21.0375304, -0.0000752, 0.6860512, -112.5401922)
EXCLUDE = [(293, 17, 600, 211)]  # pt: the legend
SOURCE = ("Mammoth Mountain 2025-26 trail map PDF (skimap.org 42347) with its interactive map's SVG lines "
          '(resorts-interactive.com map 1812), tools/trailmap/resorts/mammoth/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its group's name (pdf_resort.py names it by that)
MATCH_ENDS = False  # no lines are printed: names are beside their runs, not in a gap of a line
SYMBOL_REACH = 10  # pt from a name's first or last character (or its middle) to its symbol
SYMBOL_CENTRE = True  # a name printed level, centred under its symbol (the bowls', chutes' and peaks')
END_REACH = 8
ALONG = 4.5

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED, area = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, TOP.area

JOIN = []
TWO_LINE = set()
NO_STRETCH = set()
# runs with no line of their own (or not along it) printed along their run: a stretch along the name (mm/f1 crops,
# the audit sheets): Antin Alley / Chickadee (the interactive map's line stops at the label's start) and Lower Shaft
# (no line in the interactive map). Snake Run, a park printed along its run too, stays a marker as the other parks
# with no line do
LABEL_LINE = {'Antin Alley / Chickadee', 'Lower Shaft'}
DROP = []
RENAME = dict(TOP.RENAME)
RENAME_AT = []
# the Hemlocks' terrain features (the report's park; the interactive map's orange line beside The Hemlocks' own): the
# orange park pill printed beside THE HEMLOCKS, before its double diamond (the pill's fill, map px)
EXTRA = [('The Hemlocks (Terrain Features)', 3301, 685)]
SYMBOL_FIX = []
SYMBOL_OF = []
DEFAULT_SYMBOL = dict(TOP.DEFAULT_SYMBOL)
DISPLAY = {}
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
