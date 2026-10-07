"""Sugarbush: what the zoomed crops settled about the line pieces (hand-made), applied by regen.sh.

    python3 tools/trailmap/resorts/sugarbush/decisions.py work/sugarbush/linePolylines.json \\
        work/sugarbush/tiles/result_splits.json

Reads the pieces that extract_pdf_vectors.py wrote (regen.sh, step 2: 118 pieces once Snowball is added) and
writes them back with
- the three pieces the readers reported as "SPLIT" cut where the next trail starts (SPLITS, through
  tools/trailmap/split_pieces.py, which also writes the two names of each as a "certain" reading, the
  second argument, for seed_roster.py and aggregate_readings.py);
- the two connectors the map prints no name for (UNNAMED -> `_unnamed`: aggregate_readings.py proposes no
  trail for them);
- a note on how the pieces were made (SOURCE -> `_source`).

In the session that built Sugarbush (2026-09-30, 12:41) these were one split_pieces.py command and an inline
edit of linePolylines.json; the values here are those, unchanged.
"""
import json
import os
import subprocess
import sys

# (piece, cut point in source px, name above the cut, name below it). Each piece runs on past the symbol of the
# next trail down; the readers flagged it SPLIT and the crop showed where (split_jester.png,
# split_northstar.png, split_crackerjack.png: the pieces drawn on the source at 3x).
SPLITS = [
    (25, (800, 1234), 'JESTER', "ALLYN'S TRAVERSE"),       # Allyn's Traverse starts at the Jester junction by Allyn's Lodge
    (85, (3581, 1520), 'NORTHSTAR', 'LWR NORTHSTAR'),
    (94, (3598, 1996), 'CRACKERJACK', 'LOWER CRACKERJACK'),
]

# connectors with nothing printed on them (unnamed.png: each piece alone on the source at 3x)
UNNAMED = {
    '98': 'short black link from Lift Line across to the Rumble line; nothing printed on it (crop checked)',
    '106': 'arrowed blue spur from Lower Downspout to the Castlerock Double base; nothing printed on it (crop checked)',
}

SOURCE = ("PDF vector strokes (tools/trailmap/extract_pdf_vectors.py): 0.75 pt blue/black/green strokes, plus "
          "--append runs for the pure-black and 1.0 pt black strokes, the filled Out Road outline (--filled) and "
          "Snowball, drawn as a filled outline (--outlined, piece 114)")

IMAGE_SIZE = '4333x2981'  # the map image: the page at 3.5 px/pt


def main() -> None:
    pieces, reading = sys.argv[1], sys.argv[2]
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'split_pieces.py')
    args = [sys.executable, tool, '--polylines', pieces, '--image-size', IMAGE_SIZE]
    for pid, (x, y), above, below in SPLITS:
        args += ['--split', f'{pid}@{x},{y}={above}/{below}']
    subprocess.run(args + ['--reading', reading], check=True, stdout=subprocess.DEVNULL)
    d = json.load(open(pieces))
    d['_source'] = SOURCE
    d['_unnamed'] = UNNAMED
    json.dump(d, open(pieces, 'w'))
    print(f"{pieces}: {len(d['polylines'])} pieces, {len(SPLITS)} split, {len(UNNAMED)} unnamed")


if __name__ == '__main__':
    main()
