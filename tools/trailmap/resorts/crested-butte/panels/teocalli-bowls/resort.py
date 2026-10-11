"""Crested Butte, the Teocalli Bowls panel: the map's inset of the bowls reached from the High Lift (a hike out to
Paradise Bowl), its runs numbered on the painting with a key below, none drawn as a line. Each run is a marker at its
number (../../prepare.py reads the numbers and the key into numbers.json). Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import json
import os

from PIL import Image

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('crested_butte', os.path.join(_here, '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)
PANEL = os.path.basename(_here)
_WORK = os.path.abspath(os.environ.get('CRESTED_BUTTE_WORK', os.path.join(_here, '../../../../../../work/crested-butte')))

# no lines; the names are given in map px (EXTRA): the clip is the map image itself, at 1 px per unit, so its size
# is the image's (the glades' markers are placed in percent of it)
with Image.open(os.path.join(_WORK, PANEL, 'map.png')) as _im:
    CLIP = (0, 0) + _im.size
SCALE = 1
SOURCE = ('Crested Butte 2025-26 trail map PDF (skicb.com), the Teocalli Bowls inset: no lines, its numbered runs '
          'as markers, tools/trailmap/resorts/crested-butte/prepare.py')
SYMBOL_REACH = 0
END_REACH = 0
ALONG = 0

NAMES, AREA_OF, AS_PRINTED = TOP.NAMES, TOP.AREA_OF, TOP.AS_PRINTED
is_name = TOP.is_name


def area(c):
    raise ValueError(f'a name at {c} that the report does not list: give it an area in AREA_OF')


JOIN, TWO_LINE, SPLIT = [], set(), {}
NO_STRETCH = set()
LABEL_LINE = set()
DROP = []
RENAME = dict(TOP.RENAME)
RENAME_AT = []
# the key's names that are no runs: the top of the High Lift (a place), the cat road out to Paradise Bowl
NOT_RUNS = {'Top of High Lift', 'Cat Road to Paradise Bowl'}
# every numbered run at its number, with the extreme terrain's double diamond printed under each
EXTRA = [(TOP.spelled(n['name']), n['x'], n['y'], 'double-diamond')
         for n in json.load(open(os.path.join(_WORK, PANEL, 'numbers.json'))) if n['name'] not in NOT_RUNS]
SYMBOL_FIX = []
SYMBOL_OF = []
DISPLAY = dict(TOP.DISPLAY)
GLADES = set()
PARKS = set()
RATING = {}
NO_LINE = {}
