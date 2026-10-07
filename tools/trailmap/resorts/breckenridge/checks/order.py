"""The PDF's drawing order around given Breckenridge pieces: each piece's drawing number (first pass, the split's
351 as its 250, and the second pass's stubs 352-359), with the reading's name for each, in a window around each
piece asked for. The artwork draws one trail's strokes one after another (the chutes' pairs: the line into the name,
the line on past it), so a piece drawn inside another trail's group is that trail's (Frosty's Freeway: stubs 352
and 353, then 16). Writes work/breckenridge/stubs/seq_of.json ({piece id: drawing number}).

    python3 tools/trailmap/resorts/breckenridge/checks/order.py 16 352 353
"""
import json, math, os, sys
import pymupdf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import PDF, work  # noqa: E402
from short_strokes import runs  # noqa: E402

page = pymupdf.open(PDF)[0]
seq_of = {i: s for i, (s, _, _) in enumerate(runs(page, 4, math.inf))}
seq_of[351] = seq_of[250]
seq_of.update({352 + k: s for k, (s, _, _) in enumerate(runs(page, 2.5, 4))})
name_of = {l['id']: l['mapName'] for l in json.load(open(work('tiles/result_breck.json')))['lines']}
os.makedirs(work('stubs'), exist_ok=True)
json.dump(seq_of, open(work('stubs/seq_of.json'), 'w'))
order = sorted(seq_of.items(), key=lambda kv: (kv[1], kv[0]))
ids = [k for k, _ in order]
for w in (int(v) for v in sys.argv[1:]):
    i = ids.index(w)
    print(f'-- around piece {w} (drawing {seq_of[w]}):')
    for pid, s in order[max(0, i - 6): i + 7]:
        print(f'   drawing {s:5d}  piece {pid:3d}  {name_of.get(pid, "-")}{"   <==" if pid == w else ""}')
