"""Copper Mountain: the trail names are outlined glyphs (vector fills, no text). Collect every glyph fill in a
trail colour, in drawing order, with a rotation- and scale-invariant shape signature, so identical glyphs can
be clustered and each cluster read once.

    python3 tools/trailmap/resorts/copper-mountain/glyphs.py      # regen.sh runs it (was cu_glyphs.py)

Reads the PDF. Writes glyphs.json in the working folder: per fill 0.6 to 10.5 pt in a name colour (COL; 'k0' is
the pure black of the diamonds and of some names), its drawing number, colour, box, centre, item kinds per subpath,
signature (each item's chord over their total: unchanged by rotation and size) and outline points (for measuring
gaps). A glyph drawn again at the same box with the same items (over its halo) is kept once.
"""
import collections, json, math, pymupdf
from common import PDF, work
p = pymupdf.open(PDF)[0]
COL = {(0.14, 0.12, 0.13): 'black', (0.04, 0.52, 0.78): 'blue', (0.0, 0.65, 0.3): 'green', (0.0, 0.0, 0.0): 'k0'}


def bez(a, b, c, e, n=6):
    return [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y)
            for t in [i / n for i in range(1, n + 1)]]


def subpaths(items):
    subs, cur, last = [], [], None
    for it in items:
        if it[0] == 're':
            r = it[1]; subs.append([('l', pymupdf.Point(r.x0, r.y0), pymupdf.Point(r.x1, r.y0))]); continue
        if it[0] == 'qu':
            continue
        s = it[1]
        if last is not None and math.dist((s.x, s.y), last) > 0.01:
            subs.append(cur); cur = []
        cur.append(it); e = it[-1]; last = (e.x, e.y)
    if cur:
        subs.append(cur)
    return subs


glyphs = []
seen = set()
for d in p.get_drawings():
    if d['type'] not in ('f', 'fs') or not d.get('fill'):
        continue
    col = COL.get(tuple(round(v, 2) for v in d['fill']))
    r = d['rect']
    if not col or max(r.width, r.height) >= 10.5 or max(r.width, r.height) < 0.6:
        continue
    key = (col, round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1), len(d['items']))
    if key in seen:
        continue  # the same glyph drawn again on top of its halo
    seen.add(key)
    subs = subpaths(d['items'])
    pts, lens, kinds = [], [], []
    for sp in subs:
        kinds.append(''.join(it[0] for it in sp))
        for it in sp:
            a, e = it[1], it[-1]
            lens.append(math.dist((a.x, a.y), (e.x, e.y)))
            pts += [(a.x, a.y)] + (bez(*it[1:5]) if it[0] == 'c' else [(e.x, e.y)])
    for it in d['items']:  # rectangles (a sans-serif I): their outline, for gap measuring
        if it[0] == 're':
            q = it[1]
            pts += [(q.x0 + (q.x1 - q.x0) * t / 4, y) for y in (q.y0, q.y1) for t in range(5)]
            pts += [(x, q.y0 + (q.y1 - q.y0) * t / 4) for x in (q.x0, q.x1) for t in range(5)]
    tot = sum(lens) or 1
    cx = sum(q[0] for q in pts) / len(pts); cy = sum(q[1] for q in pts) / len(pts)
    glyphs.append({'seq': d['seqno'], 'col': col, 'rect': [round(v, 2) for v in r], 'c': [round(cx, 2), round(cy, 2)],
                   'kinds': '|'.join(kinds), 'sig': [round(l / tot, 3) for l in lens], 'size': round(tot, 2),
                   'pts': [[round(x, 2), round(y, 2)] for x, y in pts]})
json.dump(glyphs, open(work('glyphs.json'), 'w'))
print(len(glyphs), 'glyph fills;', collections.Counter(g['col'] for g in glyphs))
