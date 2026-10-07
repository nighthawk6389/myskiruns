"""Winter Park: the name of every line piece, settled on zoomed crops (was the scratch wp_checked.py).

CHECKED: piece id -> the name as printed (upper case, curly apostrophes as the PDF prints them). UNNAMED: piece id
-> why it has no name (connectors the map prints no name for). Every piece of linePolylines.json is in exactly one of
the two. Read by reading.py (the reading and the label-gap stretches), checks/collinear.py and, as `_unnamed`, by
regen.sh into linePolylines.json.

Piece ids are those of tools/trailmap/extract_pdf_vectors.py run with regen.sh's flags on the 2025-26 PDF: a vector
extraction is deterministic, so they stay put as long as the PDF and those flags do (a new edition needs new
decisions anyway). The crops that settled them (work/winter-park/reg/r_*.jpg, z*_0.jpg, chutes_0.jpg, with every
piece drawn and tagged id:auto-name) come from checks/zoom.py; the README lists the boxes.
"""
# pieces settled on zoomed crops (reg/r_*.jpg, reg/chutes_0.jpg): piece id -> name as printed (upper case)
CHECKED = {
    # 14: Easy Way's band runs on past the Discovery Park callout to TO VILLAGE WAY, where it meets Village Way
    85: "PARRY’S PEEK", 83: "PARRY’S PEEK", 84: "PARRY’S PEEK", 146: 'FOREVER EVA',
    150: 'FORGET-ME-NOT', 149: 'FORGET-ME-NOT', 121: 'JUNIPER', 187: 'CALYPSO', 86: 'PAINTBRUSH',
    218: 'KINNIKINNIC', 219: 'KINNIKINNIC', 216: "WILLETT’S WAY", 217: "WILLETT’S WAY", 125: 'JOHNSTONE JUNCTION',
    119: 'LARKSPUR', 120: 'LARKSPUR', 56: 'SKY PILOT', 57: 'SKY PILOT', 147: 'FIREBERRY GLADE', 148: 'FIREBERRY GLADE',
    102: 'LUPIN', 24: 'VILLAGE WAY', 25: 'VILLAGE WAY', 23: 'VILLAGE WAY',
    26: 'VASQUEZ CIRQUE ACCESS', 27: 'VASQUEZ CIRQUE ACCESS', 205: 'BELLE FOURCHE', 206: 'BELLE FOURCHE',
    28: 'UPPER EGRESS', 215: "100’S", 69: 'ROLLOVER', 153: 'ELDORADO',
    154: 'EDELWEISS', 155: 'EDELWEISS', 156: 'EDELWEISS', 198: 'BLUEBELL', 199: 'BLUEBELL',
    178: 'COLUMBINE', 179: 'COLUMBINE', 65: 'ROUNDHOUSE', 66: 'ROUNDHOUSE', 67: 'ROUNDHOUSE',
    33: 'TRESTLE', 34: 'TRESTLE', 203: 'BETTER NOT', 204: 'KEY HOLE', 136: 'HOLE-IN-THE-WALL',
    210: 'AWE CHUTE', 209: "BALDY’S", 122: "JEFF’S", 167: 'DERAILER', 166: 'DERAILER',
    80: 'PRIMROSE', 81: 'PRIMROSE', 70: 'ROLLINS RIDGE', 53: 'SLEEPER', 54: 'SLEEPER',
    110: 'FREERIDERS', 58: 'SIDE TRACK', 9: 'WHISTLESTOP', 10: 'WHISTLESTOP', 41: 'SWITCHYARD',
    109: 'LONESOME WHISTLE', 108: 'LONESOME WHISTLE', 37: 'THUNDERBIRD TRAVERSE', 38: 'THUNDERBIRD TRAVERSE',
    39: 'THUNDERBIRD', 40: 'THUNDERBIRD', 114: 'LEFT HAND', 115: 'LEFT HAND', 200: 'BLACK COAL', 96: 'BLACK COAL',
    94: 'MEDICINE MAN', 95: 'MEDICINE MAN', 111: 'LITTLE RAVEN', 112: 'LITTLE RAVEN', 61: 'SHARP NOSE', 62: 'SHARP NOSE',
    159: 'EAGLE WIND', 160: 'EAGLE WIND', 29: 'UPPER EGRESS', 103: 'LOWER EGRESS', 11: 'WATERFALL', 93: 'MRC',
    138: 'GUNBARREL', 176: 'CORONA WAY', 185: 'CANNONBALL', 186: 'CANNONBALL', 106: 'LONG HAUL', 107: 'LONG HAUL',
    59: 'SHORT HAUL', 192: 'BRAKEMAN', 193: 'BRAKEMAN', 173: 'COUPLER', 197: 'BOILER', 91: "NEEDLE’S EYE",
    92: "NEEDLE’S EYE", 76: 'RAILBENDER', 77: 'RAILBENDER', 82: 'PHANTOM BRIDGE', 42: 'SUPER GAUGE TRAIL',
    74: 'RAINBOW CUT', 104: 'LOWER ARROWHEAD LOOP', 105: 'LOWER ARROWHEAD LOOP', 30: 'UPPER ARROWHEAD LOOP',
    139: 'GOLDEN SPIKE', 140: 'GOLDEN SPIKE', 47: 'STERLING WAY', 48: 'STERLING WAY', 101: 'MARY JANE', 99: 'MARY JANE', 133: 'MARY JANE', 142: 'GANDY DANCER', 52: 'SOBER ENGLISHMAN',
    43: 'SUPER GAUGE TRAIL', 126: 'IRON HORSE TRAIL', 145: 'FREERIDERS',
    162: 'DRUNKEN FRENCHMAN', 161: 'DRUNKEN FRENCHMAN', 135: 'HOOKUP', 134: 'HOOKUP', 163: 'DORMOUSE', 98: 'MARCH HARE',
    51: 'SOBER ENGLISHMAN', 8: 'WHISTLESTOP', 7: 'WHISTLESTOP', 228: 'JABBERWOCKY', 229: 'JABBERWOCKY', 230: 'JABBERWOCKY',
    222: 'WHITE RABBIT', 221: 'WHITE RABBIT', 223: 'WHITE RABBIT', 169: 'CRANMER', 168: 'CRANMER', 170: 'CRANMER', 171: 'CRANMER',
    87: 'OUTRIGGER TRAIL', 71: "RETTA’S RUN", 194: "BRADLEY’S BASH", 207: 'BALCH', 132: 'HUGHES', 97: 'MARCH HARE',
    137: 'GUNBARREL', 22: 'VILLAGE WAY', 225: 'LONESOME WHISTLE', 226: 'LONESOME WHISTLE',
    183: 'CHESHIRE CAT', 182: 'CHESHIRE CAT', 184: 'CHESHIRE CAT', 143: 'GAMBLER', 144: 'GAMBLER', 4: 'WILD SPUR TRAIL',
    3: 'WILD SPUR TRAIL', 213: 'ACES AND EIGHTS', 45: 'SUNDANCE', 44: 'SUNDANCE', 49: 'STAGECOACH', 78: 'QUICKDRAW',
    79: 'QUICKDRAW', 60: 'SHOOTOUT', 191: 'BUCKAROO', 180: 'CHUCK WAGON', 181: 'CHUCK WAGON',
    # auto-matched and/or grouped with the name in the PDF's own object order, seen on the crops
    5: 'WHITE RABBIT', 6: 'WHITE RABBIT', 12: 'WAGON TRAIN', 13: 'VISTA DOME', 14: 'EASY WAY', 15: 'VILLAGE WAY',
    16: 'VILLAGE WAY', 17: 'VILLAGE WAY', 18: 'VILLAGE WAY', 19: 'VILLAGE WAY', 20: 'VILLAGE WAY', 21: 'VILLAGE WAY',
    31: 'TURNPIKE', 32: 'TURNPIKE', 35: 'TIN HORN', 36: 'TIN HORN', 46: 'SUNDANCE', 50: 'STAGECOACH', 55: 'SLEEPER',
    63: 'RUNAWAY', 64: 'RUNAWAY', 72: "RETTA’S RUN", 73: 'RENDEZVOUS', 75: 'RAINBOW CUT', 88: 'OUTRIGGER TRAIL',
    100: 'MARY JANE', 113: 'LITTLE PIERRE', 196: 'LITTLE PIERRE', 116: 'LARRY SALE', 117: 'LARRY SALE', 118: 'LARRY SALE',
    123: 'JACK KENDRICK', 124: 'JACK KENDRICK', 127: 'LOWER HUGHES', 128: 'LOWER HUGHES', 129: 'HUGHES', 130: 'HUGHES',
    131: 'HUGHES', 141: 'GANDY DANCER', 151: 'ENGELDIVE', 152: 'ENGELDIVE', 157: 'EASY WAY', 158: 'EASY WAY',
    164: 'DOGPATCH', 165: 'DOGPATCH', 172: 'COUPLER', 174: 'CORRIDOR', 175: 'CORRIDOR', 177: 'CORONA WAY',
    188: "BUTCH’S BREEZEWAY", 189: "BUTCH’S BREEZEWAY", 190: 'BUCKAROO', 195: "BRADLEY’S BASH", 201: 'BIG VALLEY',
    202: 'BIG VALLEY', 208: 'BALCH', 211: 'ALLAN PHIPPS', 212: 'ALLAN PHIPPS', 214: 'ACES AND EIGHTS',
    220: 'OVER ‘N’ UNDERWOOD', 224: 'LOWER PARKWAY', 227: 'LONESOME WHISTLE', 231: 'JABBERWOCKY', 89: 'OUTHOUSE', 90: 'OUTHOUSE',
}
UNNAMED = {
    0: 'black dashed connector (advanced-intermediate symbol) from Cheshire Cat down to the Village Way band; no name printed',
    1: 'the same dashed connector, below its symbol',
    2: 'black dashed stretch (advanced-intermediate symbol) below Jabberwocky; the PDF groups it with 0 and 1, not with a name',
    68: 'short black arrow with an advanced-intermediate symbol at the bottom of Roundhouse; no name printed',
}
