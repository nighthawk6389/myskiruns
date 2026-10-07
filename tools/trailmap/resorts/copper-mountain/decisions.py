"""Copper Mountain: the naming decisions settled on zoomed crops (was cu_checked.py). reading.py and regen.sh read it.

CHECKED: piece id (lines.py's numbering of linePolylines.json) -> the name as printed (glyph spelling, upper case,
curly apostrophe). It overrides build.py's automatic match. The pieces come from the PDF's vectors, so their ids are
stable for this edition of the PDF; a change to lines.py's thresholds or another edition renumbers them, and then
every id here must be checked again (checks/fine.py draws given pieces on the PDF).
UNNAMED: piece id -> why it is a link the map prints no name for (none at Copper).

The crops named in the comments were made in the original working folder (reg/t_*.jpg: checks/zoom.py over the
map's regions, each piece tagged id:auto-name; f_*.png: checks/fine.py; z_*.png: checks/crop.py or checks/show.py);
they were not kept.
"""
# Copper Mountain pieces settled on zoomed crops (reg/t_*.jpg, f_*.png): piece id -> name as printed
CHECKED = {
    # Lillie-G Traverse runs under its own label (f_lillie.png)
    71: 'LILLIE G TRAVERSE',
    # East Village side (f_bee.png, f_tz.png, f_ohno.png): Bee Traverse's upper part crosses Formidable; Free Fall
    # Glade's line carries its own label; Hodson's Cut runs up to Triple Zero's label (Triple Zero's line is the one
    # under its name), Sawtooth carries its label (Resolution Bowl is the bowl's name: a marker); Slot Car Track
    # is its own line beside Oh No
    58: 'BEE TRAVERSE', 48: 'FREE FALL GLADE', 45: 'HODSON’S CUT', 40: 'SAWTOOTH', 28: 'SLOT CAR TRACK',
    # Union Peak / Flyer's (f_lt.png): each line under its own label
    66: 'LITTLE TREES', 67: 'SPILLWAY',
    # Timberline (f_cf.png): Jacque's Pique's line carries its label and joins Copperfield's
    8: 'JACQUE’S PIQUE',
    # I-Dropper / Liberty (z_usr2.png, z_usr3.png): Liberty's label is on piece 17; Upper Skid Road has no line
    17: 'LIBERTY',
    # Minor Matter junction (f_mm.png, f_ef.png): Woodwinds runs on through it to Woodwinds Traverse; the two scraps
    # at the junction are Minor Matter's line
    78: 'WOODWINDS', 79: 'MINOR MATTER', 81: 'MINOR MATTER',
    # Woodwinds Traverse (f_ef.png, f_hv2.png): from the lift base under its label, across Easy Feelin', Vein Glory
    # and Hidden Vein, on to Loverly
    83: 'WOODWINDS TRAVERSE', 102: 'WOODWINDS TRAVERSE', 92: 'WOODWINDS TRAVERSE', 93: 'WOODWINDS TRAVERSE',
    # Kokomo (f_fw.png): Timber Road and Prospector carry their labels (Kokomo Glade is a marker)
    123: 'TIMBER ROAD', 87: 'PROSPECTOR',
    # West Village (f_hv.png, f_hv_plain.png): Scooter's line (Peace Park is the park beside it); Hidden Vein's
    # upper part branches off Vein Glory; Sno Deal's second branch has its own square
    91: 'SCOOTER', 95: 'HIDDEN VEIN', 90: 'SNO DEAL',
    # Leap Frog junction (f_lf.png): Coppertone ends just below Leap Frog, Leap Frog runs on past its circle to
    # Loverly
    104: 'LEAP FROG', 106: 'COPPERTONE', 109: 'LEAP FROG',
    # the dark casing of Loverly's line across the coaster (f_122.png)
    122: 'LOVERLY',
}
UNNAMED = {}
