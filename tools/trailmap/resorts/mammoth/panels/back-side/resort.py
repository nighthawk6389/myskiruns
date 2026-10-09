"""Mammoth Mountain, the back-side inset (page 2 of the 2025-26 map PDF, its lower right corner: the back side,
Chairs 13 and 14, drawn larger than on the main map). Names are text on a white halo, the symbol before the name;
no trail lines are drawn: the lines are the interactive map's (resorts-interactive.com map 1819). Read by
tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('mammoth', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

CLIP = (1148, 797, 1728, 1183.5)  # PDF points: the inset
SCALE = 2.5  # map px per PDF point
# the interactive map's SVG units on the map image (px): registered on its painting (register_pages.py --ref
# background.jpeg --ref-scale 1.24853: 1019 inliers, median 0.33 px; the painting's offset in the SVG folded in)
VICOMAP_AFFINE = (0.5959620, 0.0000078, -18.3427495, -0.0000277, 0.5959958, -38.2511454)
EXCLUDE = []
SOURCE = ("Mammoth Mountain 2025-26 trail map PDF (skimap.org 42347), back-side inset, with its interactive map's SVG "
          'lines (resorts-interactive.com map 1819), tools/trailmap/resorts/mammoth/prepare.py; percent of the map image')
GROUPED = True  # every line piece carries its group's name (pdf_resort.py names it by that)
MATCH_ENDS = False  # no lines are printed: names are beside their runs, not in a gap of a line
SYMBOL_REACH = 8  # pt from a name's first or last character (or its middle) to its symbol
SYMBOL_CENTRE = True  # a name printed level, centred under its symbol (the bowls', chutes' and peaks')
END_REACH = 8
ALONG = 4

is_name = TOP.is_name
NAMES, AREA_OF, AS_PRINTED, area = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED, TOP.area

JOIN = []
TWO_LINE = set()
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
RENAME = dict(TOP.RENAME)
RENAME_AT = []
EXTRA = []
SYMBOL_FIX = []
SYMBOL_OF = []
DEFAULT_SYMBOL = dict(TOP.DEFAULT_SYMBOL)
DISPLAY = {}
GLADES = set()
PARKS = TOP.PARKS
NO_LINE = {}
