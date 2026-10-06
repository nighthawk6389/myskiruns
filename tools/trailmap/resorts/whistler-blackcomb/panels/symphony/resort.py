"""Whistler Blackcomb, the Symphony Amphitheatre inset (the PDF's first page): Whistler Mountain's Symphony Bowl,
which the main map shows only from behind. Lines and names as on the main map, smaller. Read by
tools/trailmap/pdf_resort.py; ../../prepare.py extracts it."""

CLIP = (292, 874.5, 860, 1215)  # PDF points: the inset's frame
SCALE = 3  # map px per PDF point
SOURCE = ('Whistler Blackcomb 2025-26 trail map PDF (whistlerblackcomb.com, the Mountain Atlas), Symphony '
          'Amphitheatre inset: 0.77 pt green, blue and black strokes, tools/trailmap/resorts/whistler-blackcomb/'
          'prepare.py; percent of the map image')
SYMBOL_REACH = 8
END_REACH = 5
ALONG = 4
ALONG_NEAREST = True
NO_STRETCH_BESIDE = True


def is_name(label):
    return label.get('color') in ('green', 'blue', 'black') and not label['text'].count('*')


JOIN = [('RHAPSODY', 'BOWL'), ('NORTH', 'FLUTE', 'BOWL'), ('FLUTE', 'BOWL'), ('CAMEL', 'HUMPS'),
        ('HARMONY', 'HORSESHOES'), ('STACCATO', 'GLADES'), ('BOOMER', 'BOWL'), ('GUN', 'BARRELS'),
        ('GLISSANDO', 'GLADES')]
TWO_LINE = set()
NO_STRETCH = set()
LABEL_LINE = set()
# the peak and its elevation, and the end of "Burnt Stew Trail to Harmony"
DROP = [('LITTLE WHISTLER PEAK', None), ('ELEVATION: 2,115m/6,939ft', None), ('TO HARMONY', None)]
RENAME = {'MCCONKEY’S': 'McCONKEY’S'}  # as the main map prints it
EXTRA = []
SYMBOL_FIX = []
# Flute Bowl and North Flute Bowl print a diamond and a double diamond: the resort's trail report rates them black
RATING = {'FLUTE BOWL': 'diamond', 'NORTH FLUTE BOWL': 'diamond'}
DISPLAY = {}
GLADES = set()
NOT_GLADES = {'THE GLADES'}  # a groomed blue run, drawn as one (the map's glades have white dashes)
PARKS = set()
NO_LINE = {}


def area(c):
    return 'whistler'
