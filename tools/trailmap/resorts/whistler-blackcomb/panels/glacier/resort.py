"""Whistler Blackcomb, the Blackcomb Glacier inset (the PDF's first page): the glacier and the bowls off Spanky's
Ladder behind Blackcomb, which the main map leaves out. Lines are thin black strokes; names black, with their
symbols. Read by tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""

CLIP = (1449.5, 963, 1728, 1215)  # PDF points: the inset's frame (it runs off the page on the right)
SCALE = 4  # map px per PDF point
SOURCE = ('Whistler Blackcomb 2025-26 trail map PDF (whistlerblackcomb.com, the Mountain Atlas), Blackcomb Glacier '
          'inset: 0.6 pt black strokes, tools/trailmap/resorts/whistler-blackcomb/prepare.py; percent of the map image')
SYMBOL_REACH = 8
END_REACH = 5
ALONG = 4
ALONG_NEAREST = True
NO_STRETCH_BESIDE = True


def is_name(label):
    return label.get('color') == 'black' and not label['text'].count('*')


# names printed in parts; the provincial parks' labels first, so the glacier run keeps its own words
JOIN = [('BLACKCOMB', 'GLACIER', 'PROVINCIAL', 'PARK'), ('GARIBALDI', 'PROVINCIAL', 'PARK'),
        ('BLACKCOMB', 'GLACIER'), ('BLOW', 'HOLE'), ('SAPPHIRE', 'BOWL'), ('GARNET', 'BOWL'), ('DIAMOND', 'BOWL'),
        ('RUBY', 'BOWL'), ('SPANKY’S', 'LADDER'), ('ENTRANCE TO', 'GARNET, DIAMOND,', 'RUBY&SAPPHIRE', 'BOWLS'),
        ('ENTRANCE TO', 'BLACKCOMB GLACIER'), ('PERMANENTLY', 'CLOSEDAREA')]
TWO_LINE = {'BLOW HOLE', 'BLACKCOMB GLACIER', 'SAPPHIRE BOWL', 'GARNET BOWL', 'DIAMOND BOWL', 'RUBY BOWL', 'SPANKY’S LADDER'}
NO_STRETCH = set()
LABEL_LINE = set()
# notes and places: the parks, closed areas, cliffs, the hut, the note under Spanky's Ladder
DROP = [('BLACKCOMB GLACIER PROVINCIAL PARK', None), ('GARIBALDI PROVINCIAL PARK', None),
        ('PERMANENTLY CLOSEDAREA', None), ('CLIFF AREA', None), ('HORSTMAN HUT', None),
        ('ELEVATION:2,284m 7,494ft', None), ('ENTRANCE TO GARNET, DIAMOND, RUBY&SAPPHIRE BOWLS', None)]
RENAME = {}
EXTRA = []
SYMBOL_FIX = []
# the inset rates Glacier Road's top on the glacier (a diamond), the main map the road (a square): the resort's trail
# report has its upper part black and the rest blue, so it's blue
RATING = {'GLACIER ROAD': 'square'}
DISPLAY = {}
GLADES = set()
PARKS = set()
NO_LINE = {}


def area(c):
    return 'blackcomb'
