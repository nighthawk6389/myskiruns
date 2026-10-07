"""Whiteface: the notes in linePolylines.json (scratch: an inline step of the 2026-09-30 build).

    python3 tools/trailmap/resorts/whiteface/annotate.py

Reads and rewrites src/data/resorts/whiteface/linePolylines.json (after extract_pdf_vectors.py and
split_pieces.py): sets `_source`, saying what the pieces are, and `_unnamed`, the pieces checked on a crop to be
no trail's (UNNAMED in decisions.py), which aggregate_readings.py leaves without a name and the review page hides.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decisions import UNNAMED  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
f = os.path.join(REPO, 'src/data/resorts/whiteface/linePolylines.json')
d = json.load(open(f))
d['_source'] = ("PDF vector strokes (tools/trailmap/extract_pdf_vectors.py): 1.43-1.5 pt green, blue and black "
                "strokes of Whiteface's 2025-26 map (lifts are red); four pieces cut where two trails share a stroke")
d['_unnamed'] = {str(k): v for k, v in UNNAMED.items()}
json.dump(d, open(f, 'w'))
