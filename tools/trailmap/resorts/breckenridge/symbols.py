"""Breckenridge difficulty symbols (fills): green circle, blue square, black diamond; two diamonds side by side
= double diamond; two diamonds each holding a white letter (E, X) = EX (extreme terrain).

    python3 tools/trailmap/resorts/breckenridge/symbols.py      # regen.sh runs it (scratch: br_syms.py)

Reads the PDF's fills (work/breckenridge.pdf), leaving out the panels printed on the map (legend, terrain-park
list, lift stats, Epic box, emergency box). Writes work/symbols.json: [{t, c, s[, ends]}] in PDF points, t one of
circle, square, diamond, double-diamond, ex. names.py attaches each symbol to the name it is printed beside: the
symbol is the trail's difficulty.
"""
import collections, json, math, os, sys
import pymupdf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PDF, work  # noqa: E402
p = pymupdf.open(PDF)[0]
PANELS = [(1326, 395, 1458, 925), (1222, 525, 1326, 573), (1094, 573, 1326, 925), (964, 685, 1086, 915),
          (8, 735, 168, 925)]  # legend, terrain parks, lift stats, Epic box, emergency box


def side_ok(items):
    ls = [math.dist(it[1], it[2]) for it in items if it[0] == 'l']
    return len(ls) == 4 and max(ls) < 1.35 * min(ls)


raw, letters = [], []
for d in p.get_drawings():
    if d['type'] not in ('f', 'fs') or not d.get('fill'):
        continue
    r = d['rect']
    if r.y1 < 80 or r.y0 > 930 or max(r.width, r.height) > 12:
        continue
    if any(b[0] <= r.x0 <= b[2] and b[1] <= r.y0 <= b[3] for b in PANELS):
        continue
    f = tuple(round(v, 2) for v in d['fill']); k = ''.join(it[0] for it in d['items'])
    c = ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2); s = max(r.width, r.height)
    t = None
    if f == (0.02, 0.53, 0.02) and k.count('c') >= 4 and abs(r.width - r.height) < 0.6 and 4.5 <= s <= 8: t = 'circle'
    elif f == (0.01, 0.28, 0.82) and (k == 're' or (k == 'llll' and side_ok(d['items']))) and 4.5 <= s <= 9.5: t = 'square'
    elif f == (0.0, 0.0, 0.0) and k == 'llll' and side_ok(d['items']) and 2.5 <= s <= 7.5: t = 'diamond'
    elif f == (1.0, 1.0, 1.0) and k == 'l' * 12 and s <= 3: letters.append(c)  # white E / X inside an EX diamond
    if t:
        raw.append({'t': t, 'c': c, 's': s})
syms = []
for s in raw:
    if not any(q['t'] == s['t'] and math.dist(q['c'], s['c']) < 0.8 for q in syms):
        syms.append(s)
dia = [s for s in syms if s['t'] == 'diamond']
out = [s for s in syms if s['t'] != 'diamond']
used = set()
for i, a in enumerate(dia):
    if i in used:
        continue
    best = min(((math.dist(a['c'], b['c']), j) for j, b in enumerate(dia) if j != i and j not in used), default=None)
    if best and best[0] < 1.7 * a['s']:
        b = dia[best[1]]; used |= {i, best[1]}
        ex = any(math.dist(g, a['c']) < 1.8 for g in letters) and any(math.dist(g, b['c']) < 1.8 for g in letters)
        out.append({'t': 'ex' if ex else 'double-diamond', 'c': ((a['c'][0] + b['c'][0]) / 2, (a['c'][1] + b['c'][1]) / 2),
                    's': a['s'], 'ends': [a['c'], b['c']]})
    else:
        used.add(i)
        if any(math.dist(g, a['c']) < 1.8 for g in letters):
            print('lone lettered diamond at', [round(v) for v in a['c']])
        out.append(a)
json.dump(out, open(work('symbols.json'), 'w'))
print(collections.Counter(s['t'] for s in out), len(letters), 'white letters')
