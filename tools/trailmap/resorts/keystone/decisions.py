"""Keystone: the pieces settled on zoomed crops, where the automatic match (build.py) was wrong or found nothing
(scratch: k_checked.py).

Read by reading.py (CHECKED overrides build.py's names) and regen.sh (UNNAMED goes into linePolylines.json as
_unnamed). CHECKED: piece id -> the name as printed (curly apostrophes as in names.json). UNNAMED: piece id -> why
it carries no name (none on this map). Piece ids are stable: the extraction from the PDF is deterministic. The crops
named in the comments (f_*.png, reg/t_*.jpg, sh_q*.png) are remade by checks/fine.py, checks/zoom.py and
checks/show.py: the README's "Checks done" has each command.
"""
# Keystone pieces settled on zoomed crops (reg/t_*.jpg, f_*.png): piece id -> name as printed
CHECKED = {
    # Outback (f_toad.png, sh_q2.png): each line under its own label; The Black Forest and South Bowl Trees are
    # area labels (no line) at the top of these lines
    126: 'Goalpost Gully', 35: 'The Wolf Den', 39: 'Mr. Toad’s Wild Ride',
    # Timber Ridge (f_fox.png, f_52.png, f_trunk.png, f_nuchu.png): the Foxtrot loop ends at Anticipation's label;
    # Thorne runs on into the base; Nuchu's line runs on past the trunk as the left branch that Tenderfoot Glades and
    # Foxtrot Glades join
    123: 'Foxtrot', 52: 'Thorne', 122: 'Nuchu',
    # Oh, Bob runs on to Elk Run (f_oh.png)
    45: 'Oh, Bob',
    # River Run side (f_sfe.png, f_base.png, f_jay.png, f_mid.png, f_aca.png): one line under both Santa Fe
    # labels; the lower Whipsaw label's own line; Beger's line ends at Dercum's Dash's label; Silver Spoon starts at
    # Jaybird's circle; Freda's starts at Last Chance's circle; HooDoo's upper branch; Schoolmarm's junction scrap;
    # Acapulco Road starts at the end of Schoolmarm's "Family Ski Trail" label
    65: 'Santa Fe', 71: 'Whipsaw', 83: 'Beger', 94: 'Silver Spoon', 97: 'Freda’s', 99: 'HooDoo', 92: 'Schoolmarm',
    93: 'Schoolmarm', 96: 'Acapulco Road',
}
# one stroke carries two names (f_brahma.png): Brahma above the Outpost Gondola, Snake Pit below (cut there with
# split_pieces.py --split '2@2410.8,890.4=Brahma/Snake Pit')
CHECKED.update({2: 'Brahma', 134: 'Snake Pit'})
UNNAMED = {}
