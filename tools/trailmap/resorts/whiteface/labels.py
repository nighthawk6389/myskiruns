"""Whiteface 2025-26: every label printed on the map, from the PDF's own text (scratch name: wf_labels.py).

    python3 tools/trailmap/resorts/whiteface/labels.py

Reads $WHITEFACE_WORK/whiteface.pdf (default work/whiteface). Writes $WHITEFACE_WORK/wf_labels.json: one label
per text object (its seqno) with the object's layer, colour, type, font and size, the centre of its characters
(`c`) and each character's centre in reading order (`pts`), all in PDF points.

Why: every trail name on this map is real text, coloured by its difficulty, on the PDF's "Green Names", "Blue
Names" and "Black Names" layers (lifts, lodges and the rest on other layers). So the trail list, the label
positions and the stretches drawn along names printed in a gap of their line (reading.py) all come from here,
with no readers. This predates tools/trailmap/pdf_labels.py (written next, for Winter Park) and differs from
it: it keeps the layer names (build.py picks the name layers by them) and keeps each text object whole.
"""
import collections
import json
import os

import pymupdf

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))

p = pymupdf.open(os.path.join(WORK, 'whiteface.pdf'))[0]
groups = collections.OrderedDict()
for s in p.get_texttrace():
    k = s['seqno']
    g = groups.setdefault(k, {'layer': s['layer'], 'color': tuple(round(x, 2) for x in s['color']), 'type': s['type'],
                              'font': s['font'], 'size': round(s['size'], 1), 'chars': []})
    for c in s['chars']:
        g['chars'].append((chr(c[0]), c[3]))  # char, bbox
out = []
for k, g in groups.items():
    txt = ''.join(ch for ch, _ in g['chars'])
    boxes = [b for ch, b in g['chars'] if ch.strip()]
    if not boxes:
        continue
    cx = sum((b[0] + b[2]) / 2 for b in boxes) / len(boxes)
    cy = sum((b[1] + b[3]) / 2 for b in boxes) / len(boxes)
    out.append({'seq': k, 'text': ' '.join(txt.split()), 'layer': g['layer'], 'color': g['color'], 'type': g['type'],
                'font': g['font'], 'size': g['size'], 'c': [round(cx, 1), round(cy, 1)],
                'pts': [[round((b[0] + b[2]) / 2, 1), round((b[1] + b[3]) / 2, 1)] for b in boxes]})
json.dump(out, open(os.path.join(WORK, 'wf_labels.json'), 'w'))
cnt = collections.Counter((o['layer'], o['color'], o['type']) for o in out)
print(len(out), 'text objects;', cnt.most_common())
