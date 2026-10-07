"""Copper Mountain: glyph clusters -> letters (read once per cluster on checks/sheet.py's contact sheets) -> labels.
Glyphs are drawn in reading order; a label is a run of consecutive glyphs of one colour; a word gap is a
gap between neighbouring outlines well over the label's usual letter gap.

    python3 tools/trailmap/resorts/copper-mountain/labels.py      # regen.sh runs it (was cu_labels.py)

Reads clusters.json (cluster.py), letters.json here (each glyph shape's letter, keyed by item kinds + signature,
read once on checks/sheet.py's contact sheets; was cu_letters.json) and the PDF (the small white fills inside an
EX symbol). Writes, in the working folder, glyph_labels.json (was cu_labels.json: each label's text, colour,
glyph centres, first drawing number) and syms.json (was cu_syms.json: the difficulty symbols, which are fills too).
- Symbols: a blue 4-line outline with even sides is a square, a pure black one a diamond; a pure black even 8-line
  outline a double diamond, or EX when it holds two or more small white fills (the E and X); a green 4-curve
  outline a circle.
- A label is a run of consecutive letters of one colour, each centre within 9 pt of the last and at most 6
  drawings after it; a word gap is an outline gap over max(2.3 x the label's median gap, median + 0.9 pt). A lone
  letter is not a label.
- Glyphs drawn twice (under and over their halo, or an old colour under the new) leave copies: a label whose
  glyphs all sit on a longer (or, of equal ones, a later) label's glyphs is dropped.
"""
import collections, json, math
import os
from common import HERE, PDF, work
C = json.load(open(work('clusters.json'))); G = C['glyphs']
TABLE = json.load(open(os.path.join(HERE, 'letters.json')))  # letter per glyph shape, read once on checks/sheet.py's sheets
import pymupdf
page = pymupdf.open(PDF)[0]
WHITE = []
for d in page.get_drawings():
    if d['type'] in ('f', 'fs') and d.get('fill') and tuple(round(v, 2) for v in d['fill']) == (1.0, 1.0, 1.0):
        r = d['rect']
        if max(r.width, r.height) < 3.5:
            WHITE.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))


def letter(g):
    for t in TABLE:
        if t['kinds'] == g['kinds'] and len(t['sig']) == len(g['sig']) and max(abs(a - b) for a, b in zip(t['sig'], g['sig'])) < 0.03:
            return t['ch']
    return None


for g in G:
    k = g['kinds']
    sides = g['sig']
    even = len(sides) and max(sides) < 1.4 * min(sides)
    g['ch'] = None
    if k == 'llll' and even and g['col'] in ('blue', 'k0'):
        g['sym'] = 'square' if g['col'] == 'blue' else 'diamond'
    elif k == 'llllllll' and g['col'] == 'k0' and even:
        x0, y0, x1, y1 = g['rect']
        inside = sum(1 for w in WHITE if x0 < w[0] < x1 and y0 < w[1] < y1)
        g['sym'] = 'ex' if inside >= 2 else 'double-diamond'
    elif k == 'cccc' and g['col'] == 'green':
        g['sym'] = 'circle'
    else:
        g['ch'] = letter(g)


def gap(a, b):
    return min(math.dist(p, q) for p in a['pts'][::2] for q in b['pts'][::2])


letters = [g for g in G if g.get('ch')]
labels, cur = [], []
for g in letters:
    if cur and (g['col'] != cur[-1]['col'] or math.dist(g['c'], cur[-1]['c']) > 9 or g['seq'] - cur[-1]['seq'] > 6):
        labels.append(cur); cur = []
    cur.append(g)
if cur:
    labels.append(cur)
out = []
for lab in labels:
    gaps = [gap(a, b) for a, b in zip(lab, lab[1:])]
    med = sorted(gaps)[len(gaps) // 2] if gaps else 0
    s = lab[0]['ch']
    if len(lab) == 1:
        continue  # a lone rectangle or mark, not a label
    for g, d in zip(lab[1:], gaps):
        s += (' ' if d > max(2.3 * med, med + 0.9) else '') + g['ch']
    pts = [g['c'] for g in lab]
    out.append({'text': s, 'col': lab[0]['col'], 'pts': pts, 'seq': lab[0]['seq'],
                'c': [round(sum(q[0] for q in pts) / len(pts), 1), round(sum(q[1] for q in pts) / len(pts), 1)]})
# glyphs drawn twice (under and over their halo, or an old colour under the new) leave copies: drop a label whose
# glyphs all sit on glyphs of a longer or later label
keep = []
for o in sorted(out, key=lambda o: (-len(o['pts']), -o['seq'])):  # of two equal copies the one drawn last shows
    if any(all(any(math.dist(q, r) < 0.8 for r in k['pts']) for q in o['pts']) for k in keep):
        continue
    keep.append(o)
out = sorted(keep, key=lambda o: o['seq'])
json.dump(out, open(work('glyph_labels.json'), 'w'))
syms = [{'t': g['sym'], 'c': g['c'], 'col': g['col'], 'seq': g['seq']} for g in G if g.get('sym')]
json.dump(syms, open(work('syms.json'), 'w'))
print(len(out), 'labels;', collections.Counter(s['t'] for s in syms))
for o in out:
    print(o['seq'], o['col'], [round(v) for v in o['c']], o['text'])
