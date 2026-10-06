"""Sugarloaf's 2025-26 trail map (sugarloaf.com, Mountain Maps): one vector PDF page over a low-resolution painting.
Trail lines are strokes in the difficulty colours; names are outlined glyphs in white label boxes along their lines,
each run's symbol printed on its line. Glades and connecting trails are red numbered circles that refer to the key
below the map; The Snowfields (the summit) is drawn in an inset. prepare.py extracts it; read by
tools/trailmap/pdf_resort.py."""

CLIP = (0, 0, 1530, 955)  # PDF points: the map above the key
SCALE = 2.5  # map px per PDF point
SOURCE = ('Sugarloaf 2025-26 trail map PDF (sugarloaf.com mountain maps): 1.2 pt green and blue and 1.15 pt black '
          'strokes, tools/trailmap/resorts/sugarloaf/prepare.py; percent of the map image')
SYMBOL_REACH = 12  # pt from a name's first or last character to its symbol (on the line, past the label box)
END_REACH = 6  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 2  # pt: a piece this close to most of a name's characters runs along it
JOIN_GAP = 9
ON_CIRCLE = 5.5  # pt: a numbered circle (a key name) printed over a line names the line under it

# the key below the map, read off it: number -> name
KEY = {
    1: 'HIGH RIGGER', 2: 'HARD TACK', 3: 'PURE HEAT', 4: 'JAGGER', 5: 'IGNITOR', 6: 'POWDER KEG',
    7: 'WHITE NITRO EXT.', 8: 'BUBBLECUFFER EXT.', 9: 'GONDOLA LINE EXT.', 10: 'NARROW GAUGE EXT.',
    11: 'WINTER’S WAY EXT.', 70: 'ADRENALINE RUSH', 71: 'BALL AND CHAIN', 72: 'EXTREME CHUTE', 73: 'AWESOME',
    74: 'HELL’S GATE',
    13: 'OLD WINTER’S WAY', 14: 'CANT HOOK GLADE', 15: 'WHITE NITRO', 16: 'BLADE GLADE', 17: 'STUMP SHOT GLADE',
    18: 'SLUICE CHUTE', 19: 'SLUICE HEADWALL', 20: 'WEST SLUICE CHUTE', 21: 'GIN POLE', 22: 'U. DOUBLE BITTER',
    23: 'PICK POLE', 24: 'PINCH', 25: 'TIN PANTS', 26: 'BRIDLE CHAIN', 27: 'FRED’S PITCH GLADE', 28: 'BOOMER GLADE',
    29: 'MID STATION X-CUT', 30: 'CRIBWORKS', 31: 'UPPER SHEER BOOM', 32: 'KICKBACK', 33: 'SWEDISH FIDDLE GLADE',
    34: 'BIRCH HOOK', 35: 'WINDROW EXT.', 36: 'BUCKSAW X-CUT', 37: 'RAKER TOOTH GLADE', 38: 'BROCCOLI GARDEN',
    39: 'STUB’S GLADE', 40: 'MOOSE ALLEY', 41: 'BLUEBERRY’S GROVE', 42: 'ROOKIE RIVER', 43: 'LOWER ROOKIE RIVER',
    44: 'KERF GLADE', 45: 'PICAROON', 46: 'LOWER SPILLWAY', 47: 'TOTE ROAD X-CUT', 48: 'RAM PASTURE GLADE',
    49: 'BOOMSCOOTER', 50: 'SCHIPPER’S STREAK', 51: 'BARBER CHAIR GLADE', 52: 'SKID ROAD', 53: 'JACKPOT GLADE',
    54: 'BRANDING AX GLADE', 69: 'GREENHORN GLADE', 77: 'GONDI GLADE', 80: 'ALICE’S WINTERLAND GLADE',
    55: 'GOLDEN ROAD', 56: 'BIRLER GLADE 1', 57: 'BIRLER GLADE 2', 58: 'EDGER GLADE 1', 59: 'EDGER GLADE 2',
    60: 'SWEEPER GLADE 1', 61: 'SWEEPER GLADE 2', 62: 'ROUGH CUT GLADE', 63: 'RED HORSE GLADE',
    64: 'BLACKSMITH GLADE', 65: 'HIGH BALL GLADE', 66: 'LOGGING ROAD', 67: 'CANT DOG GLADE 1',
    68: 'CANT DOG GLADE 2', 75: 'ANDROSCOGGIN GLADE', 76: 'SLASHFIRE GLADE', 78: 'LITTLE ANDROSCOGGIN GLADE',
    79: 'KENNEBEC GLADE',
}


def is_name(label):
    # glyphs read as '*' are icons (lift towers, lodges, the compass): a label of them isn't a name
    return label.get('color') in ('black', 'key') and label['text'].count('*') < 2


# names printed in two parts (a wide word gap splits the glyph run): joined, in reading order
JOIN = [('U. POLE', 'LINE'), ('L. POLE', 'LINE'), ('HAUL', 'BACK'), ('M.', 'NARROW GAUGE')]
TWO_LINE = set()
NO_STRETCH = set()
# names whose label is all the line they have: U. Bubblecuffer's label fills the gap of its line from the Spillway
# X-Cut to its double diamond, below which the Wild Things sign covers it down to L. Bubblecuffer (p_ub.png)
LABEL_LINE = {'U. BUBBLECUFFER'}
# text in the name style that isn't a trail: the summit, notes along lines, places, freestyle pills (S/M, M/L, BX)
DROP = [('SUMMIT 4,237*', None), ('CLOSED TO SKIING', None), ('CONDO ACCESS ONLY', None),
        ('UPPER LOG YARD', None), ('LOWER LOG YARD', None), ('SIM', None), ('MIL', None), ('BX', None)]
RENAME = {'HIGH RIGGER (backside(': 'HIGH RIGGER', 'L* DOUBLE BITTER': 'L. DOUBLE BITTER'}
EXTRA = []
SYMBOL_FIX = []
# ((x, y), NAME): a symbol printed beside its name but out of SYMBOL_REACH: Winter's Way Ext.'s double diamond above
# its circle 11 (sl_ngx.png)
SYMBOL_OF = [((2312, 376), 'WINTER’S WAY EXT.')]
DISPLAY = {'BALL AND CHAIN': 'Ball and Chain', 'BINDER EXT.': 'Binder Ext.', 'BUBBLECUFFER EXT.': 'Bubblecuffer Ext.',
           'GONDOLA LINE EXT.': 'Gondola Line Ext.', 'NARROW GAUGE EXT.': 'Narrow Gauge Ext.',
           'TOTE ROAD EXT.': 'Tote Road Ext.', 'WHITE NITRO EXT.': 'White Nitro Ext.', 'WINDROW EXT.': 'Windrow Ext.',
           'WINTER’S WAY EXT.': "Winter's Way Ext."}  # NAME -> as printed, where the trail list would drop the dot
# key names printed as a circle in the trees with no line, as the key's glades are: tree skiing
GLADES = {'ROOKIE RIVER', 'LOWER ROOKIE RIVER', 'BROCCOLI GARDEN', 'BLUEBERRY’S GROVE', 'PICAROON', 'KICKBACK',
          'SKID ROAD', 'BOOMSCOOTER', 'SCHIPPER’S STREAK'}
# the six freestyle pills (S, M, L, S/M, M/L, BX: the legend's FREESTYLE TERRAIN), each on one of these lines
PARKS = {'U. CRUISER', 'L. CRUISER', 'SKYBOUND', 'THE YARD', 'DROP LINE', 'SIDEWINDER'}
_BACK = 'The back side of the summit, drawn only in the Snowfields inset as a numbered circle with no line: marker there'
NO_LINE = {
    'WINTER’S WAY EXT.': 'Circle 11 below Narrow Gauge Ext. at the summit, with its double diamond and no line: marker '
                         'at the circle',
    'WEST SLUICE CHUTE': 'Circle 20 beside the summit lift line, with no line or symbol: marker at the circle',
    'ADRENALINE RUSH': _BACK, 'BALL AND CHAIN': _BACK, 'EXTREME CHUTE': _BACK, 'AWESOME': _BACK, 'HELL’S GATE': _BACK,
}
# names with no symbol printed and no line to take a colour from (seed_roster.py would make them blue): the back
# side's chutes are in the key's Snowfields, every run of which the inset prints with a double diamond; West Sluice
# Chute is between Sluice Chute and Sluice Headwall, both single diamonds
DEFAULT_SYMBOL = {'ADRENALINE RUSH': 'double-diamond', 'BALL AND CHAIN': 'double-diamond',
                  'EXTREME CHUTE': 'double-diamond', 'AWESOME': 'double-diamond', 'HELL’S GATE': 'double-diamond',
                  'WEST SLUICE CHUTE': 'diamond'}
AREAS = [('sugarloaf', 'Sugarloaf', 4237)]  # id, name, elevation (ft, the summit as printed)


def area(c):
    """The area (AREAS id) of a name printed at c (map px)."""
    return 'sugarloaf'
