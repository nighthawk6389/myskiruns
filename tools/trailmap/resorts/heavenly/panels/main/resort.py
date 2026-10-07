"""Heavenly, the main painting: the California and Nevada sides (the 2024-25 image's top 2984 px; lines, names and
symbols from the 2022-23 PDF of the same artwork, ../../prepare.py). Trail lines are blue, green and dark outlines,
solid or dashed; most runs have no line of their own: their names are printed along the painted cuts. Names are
dark outlined glyphs, the symbol just before the name. Read by tools/trailmap/pdf_resort.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location('heavenly', os.path.join(os.path.dirname(__file__), '../../resort.py'))
TOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOP)

# the 2022-23 page (pt) on the panel's image: resort.AFFINE, its tiny shear left out (under 0.1 px here)
_A = TOP.AFFINE['main']
SCALE = (_A[0] + _A[4]) / 2  # map px per PDF point
_x0, _y0 = -_A[2] / _A[0], -_A[5] / _A[4]
CLIP = (_x0, _y0, _x0 + 3652 / SCALE, _y0 + 2984 / SCALE)
SOURCE = ("Heavenly 2024-25 trail map image (Vail Resorts' scene7 CDN), main painting; lines from the 2022-23 PDF of "
          'the same artwork (skimap.org 23043): outlined blue, green and dark lines, tools/trailmap/resorts/heavenly/'
          'prepare.py; percent of the map image')
SYMBOL_REACH = 8  # pt from a name's first or last character to its symbol
END_REACH = 6  # pt from a name's end (or its symbol) to the end of the line that runs into it
ALONG = 4.5  # pt: a name printed beside its line, about a character's height off it
ALONG_NEAREST = True
ALONG_FIRST = True
NO_STRETCH_BESIDE = True


def is_name(label):
    """The trail names: the layer of names drawn after the lines (lift names, elevations, peaks and the boundary
    are drawn later, from 15300 on)."""
    return 8600 <= label['seq'] < 13200


# names printed in parts (on two lines, or either side of a lift line), in reading order
JOIN = [('MILKY WAY', 'BOWL'), ('DIPPER', 'WOODS'), ('ARIES', 'WOODS'), ('STAGECOACH', 'WOODS'), ('NEVADA', 'WOODS'),
        ('THE', 'BURN'), ('SKI WAYS', 'GLADES'), ('SAND', 'DUNES'), ('UPPER', 'NORTH BOWL'),
        (('UPPER', (2780, 1418)), ('MOMBO', (2875, 1438))),
        ('POWDER BOWL', 'WOODS'), ('GROOVE', 'PARK'), ('EAST BOWL', 'WOODS'), ('ENCHANTED', 'FOREST'),
        ('KILLEBREW', 'CANYON'), ('MOTT', 'CANYON'), ('ROCKY', 'POINT'), ('BOUNDARY', 'CHUTES'), ('SKY', 'CANYON')]
JOIN_GAP = 16  # pt between the parts' glyph centres (UPPER MOMBO and SKY CANYON are printed either side of a lift)
# names printed on two lines (no stretch along them); Upper Mombo and Sky Canyon are one line either side of a lift
TWO_LINE = {' '.join(t if isinstance(t, str) else t[0] for t in p) for p in JOIN} - {'UPPER MOMBO', 'SKY CANYON'}
NO_STRETCH = set()
# runs drawn with no line, their names printed along them: the stretch along the printed name (from its symbol) is
# their overlay. Bowls, faces, woods, glades, the canyons' chutes, the parks and the learning areas are markers.
LABEL_LINE = {'Perimeter', 'Outlaw', 'Galaxy', 'Galaxy Line', 'Milky Way', 'Dipper Line', 'Meteor', "Orion's Belt",
              'Perimeter Upper', "Jack's", '$100 Saddle', 'Stagecoach', "Emily's Run", 'Boulder Chute',
              'Stagecoach Lower', 'Stagecoach Return', 'Cloud Nine', 'The Pines', 'Aries', '49er', 'Cascade',
              "Sam's Dream", 'Tamarack Return', 'Big Easy', "Ellie's Swing", 'Express Line', 'Sky Canyon',
              'Mombo Upper', 'Swing Trail', 'Fall Line', 'Waterfall', 'Powder Line', "Stein's Way", 'Pistol',
              'Gunbarrel', 'World Cup',
              # names printed below or beside their line's end, the run going on along the name: Nova's below the end of
              # its line from Big Dipper, Silver Spur's and Easy Street's off the lines at the top of the gondola;
              # Pinnacles, printed three times along its run
              'Nova', 'Silver Spur', 'Easy Street', 'Pinnacles'}
# the 2022 page's pointer to the inset (SEE INSET BELOW, a sign) and a terrain park's size pill
DROP = [(t, None) for t in ('SEE NSET', 'BELO', 'SMALL')]
# as the trail reports name them, where the map prints them another way (NAMES spells the rest): this season's
# report, else 2024-25's (the season the map was drawn for)
RENAME = {'SKI WAYS GLADES': 'Ski Way Glades', 'POWDER BOWL WOODS': 'Powderbowl Woods',
          'GROOVE PARK': 'Groove Terrain Park', 'CLOUD 9': 'Cloud Nine',
          'UPPER NORTH BOWL': 'North Bowl Upper', 'LOWER STAGECOACH': 'Stagecoach Lower',
          'UPPER DIPPER RETURN': 'Dipper Return Upper', 'LOWER DIPPER RETURN': 'Dipper Return Lower',
          'UPPER MOMBO': 'Mombo Upper', 'UPPER PERIMETER': 'Perimeter Upper',
          # read as printed: the glyphs' word gaps
          '$1 OO SADDLE': '$100 Saddle', 'POMA TR AIL': 'Poma Trail',
          # names neither report lists (the reports split the first seven into an upper and a lower part): as
          # printed, in the case the app shows
          'LIZ’S': "Liz's", 'CALIFORNIA TRAIL': 'California Trail', 'OLYMPIC DOWNHILL': 'Olympic Downhill',
          'VON SCHMIDT': 'Von Schmidt', 'MINESHAFT': 'Mineshaft', 'COMSTOCK': 'Comstock', 'GUNBARREL': 'Gunbarrel',
          'STAGECOACH': 'Stagecoach', 'RIM TRAIL': 'Rim Trail',
          # Mott and Killebrew Canyons' chutes and lines
          'STATELINE CHUTE': 'Stateline Chute', 'THE FINGERS': 'The Fingers', 'RAMARRAH’S': "Ramarrah's",
          'OUTER LIMITS': 'Outer Limits', 'PIPELINE': 'Pipeline', 'BOUNDARY CHUTES': 'Boundary Chutes',
          'ROCKY POINT': 'Rocky Point', 'PROMISE LAND': 'Promise Land', 'HEMLOCK': 'Hemlock', 'NORTH 40': 'North 40',
          'ERNIE’S': "Ernie's", 'BOB’S BOULEVARD': "Bob's Boulevard", 'SWEETWATER': 'Sweetwater', 'BILL’S': "Bill's",
          'SNAKE EYES': 'Snake Eyes', 'HULLY GULLY': 'Hully Gully', 'THE “Y”': 'The "Y"', 'PINENUTS': 'Pinenuts',
          'SOUTHERN COMFORT': 'Southern Comfort', 'ON HOLD': 'On Hold'}
# names the 2024-25 image prints and the 2022-23 page doesn't, or prints elsewhere (name, x, y[, symbol]; map px, the
# label's middle): Lakeview Park, new; Lone Wolf, Widow Maker's chute renamed; Upper Powderbowl's label moved up
# beside Ridge Run's (its square is the one at its start, SYMBOL_OF); Powderbowl Run's moved right, under the park
EXTRA = [('Lakeview Terrain Park', 2705, 1150), ('Lone Wolf', 561, 1216), ('Powderbowl Upper', 2595, 1040),
         ('Powderbowl Run', 2737, 1320, 'square')]
SYMBOL_FIX = []
# symbols out of reach of their names (printed under the middle of a name on two lines, or below a name): the
# woods', bowls' and faces' diamonds under their names, Hogsback's, East Bowl's, Maggie's Canyon's; Gunbarrel's and
# Bohemian Grove's before their names' starts; the third Ridge Run label's square
SYMBOL_OF = [((3067, 1946), 'East Bowl'), ((3047, 1753), 'The Face'), ((2960, 1941), 'East Bowl Woods'),
             ((2906, 1316), 'Powderbowl Woods'), ((3273, 1743), 'Hogsback'),
             ((1201, 2153), 'Nevada Woods'), ((907, 1896), 'Stagecoach Woods'), ((1144, 1346), 'Aries Woods'),
             ((835, 999), 'Dipper Woods'), ((902, 620), 'Milky Way Bowl'), ((2473, 989), 'Powderbowl Upper'),
             ((2045, 1531), "Maggie's Canyon"), ((3212, 1986), 'Gunbarrel'), ((1100, 2195), 'Bohemian Grove'),
             ((2499, 1048), 'Ridge Run')]
# Mott and Killebrew Canyons' chutes, printed with no symbol: the canyons' double diamond (expert terrain through
# gates, the trail report's Extreme)
DEFAULT_SYMBOL = {nm: 'double-diamond' for nm in (
    'Stateline Chute', 'The Fingers', "Bob's Boulevard", "Ramarrah's", 'Sweetwater', 'Outer Limits', 'Pipeline',
    'Lone Wolf', "Bill's", 'Boundary Chutes', 'Snake Eyes', 'The "Y"', 'Rocky Point', 'On Hold', 'Promise Land',
    'Hemlock', 'North 40', "Ernie's", 'Hully Gully', 'Pinenuts', 'Southern Comfort')}
# the trail report's spelling but for its case (the map prints SKYLINE TRAIL)
DISPLAY = {'The "Y"': 'The "Y"', 'Skyline trail': 'Skyline Trail'}
# tree skiing printed as an area
GLADES = {'Dipper Woods', 'Aries Woods', 'Stagecoach Woods', 'Nevada Woods', 'Powderbowl Woods', 'East Bowl Woods'}
PARKS = {'Groove Terrain Park', 'Lakeview Terrain Park'}
NO_LINE = {}
NAMES = TOP.NAMES
AREA_OF = TOP.AREA_OF


def area(c):
    """A name the trail report doesn't list: its side by where it is printed."""
    return 'nevada' if c[0] < 1800 else 'california'
