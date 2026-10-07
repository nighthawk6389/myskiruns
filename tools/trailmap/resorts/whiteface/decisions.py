"""Whiteface: what the crops settled, by piece id (scratch: the constants at the top of wf_reading.py).

Imported by reading.py and annotate.py; nothing to run. The ids are those of
src/data/resorts/whiteface/linePolylines.json: extract_pdf_vectors.py numbers the PDF's strokes in drawing order,
so they stay put as long as the PDF (its SHA-256 is checked in regen.sh) and the extraction flags don't change;
162-165 are the second parts of the four strokes regen.sh cuts with split_pieces.py (the other half of these
decisions: 1 Cloudspin / 162 Niagara, 34 The Slides / 163 Slide Out, 51 Riva Ridge / 164 Paron's Run, 69 Ilmar's
Alley / 165 Lower Northway).

Settled on zoomed crops with every piece tagged (checks/zoom_pieces.py: pr_*, zc_*, zz_* and sheet_*.jpg) and on
PDF renders of single spots (checks/pdf_crop.py: the Switchbacks, Victoria; checks/fragments.py: the labels
printed in fragments). The commands are in README.md, "Checks done".
"""

# a map typo: the 2022 trail printed "High County Road" is NY DEC's "High Country Road"
FIX = {'HIGH COUNTY ROAD': 'HIGH COUNTRY ROAD'}  # map typo (NY DEC: "High Country Road")
PRINT_FIX = {'High County Road': 'High Country Road'}

# pieces checked on zoomed crops (see the region audit); these replace the automatic assignment
OVERRIDE = {
    0: 'NIAGARA', 162: 'NIAGARA', 1: 'CLOUDSPIN',
    34: 'THE SLIDES', 35: 'THE SLIDES', 36: 'THE SLIDES', 37: 'THE SLIDES', 38: 'THE SLIDES', 163: 'SLIDE OUT',
    42: 'SUGAR VALLEY GLADES', 43: 'DEER VALLEY GLADES', 93: 'HOOT OWL GLADES', 94: 'BOBCAT GLADES', 118: 'BOBCAT GLADES',
    46: 'MOUNTAIN RUN', 18: 'MOUNTAIN RUN', 17: 'MOUNTAIN RUN', 19: 'WILDWAY',
    74: '1900 ROAD', 75: '1900 ROAD', 67: 'SUMMIT EXPRESS', 61: 'VICTORIA', 60: 'VICTORIA', 62: 'VICTORIA',
    84: 'LOWER PARKWAY', 87: 'PARKWAY EXIT', 106: "LADIES' BRIDGE", 105: 'LOWER GAP', 104: 'LOWER GAP',
    121: 'BOREEN', 52: 'UPPER SWITCHBACKS', 53: 'UPPER SWITCHBACKS', 54: 'LOWER SWITCHBACKS', 55: 'CROSSOVER LOOP',
    56: "WEBER'S WAY", 49: 'RIVA RIDGE', 51: 'RIVA RIDGE', 164: "PARON'S RUN", 48: 'THE FOLLIES',
    69: "ILMAR'S ALLEY", 165: 'LOWER NORTHWAY',
    116: 'HIGH COUNTRY ROAD', 117: '2200 ROAD', 32: 'ON RAMP', 108: 'BROADWAY',
    109: 'BROOKSIDE', 111: 'VALVEHOUSE ROAD', 112: "DANNY'S BRIDGE", 71: 'LOWER EMPIRE', 72: 'EMPIRE CUT',
    140: 'BEAR', 159: 'COYOTE CUT', 148: 'MIXING BOWL', 126: 'BOBCAT CHUTE', 129: 'MOOSE',
}
# pieces that are no trail's (also written to linePolylines.json's _unnamed by annotate.py)
UNNAMED = {130: 'green connector from Moose down to Porcupine Pass; nothing printed on it (crop checked)'}
