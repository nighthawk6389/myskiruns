"""Winter Park difficulty symbols (fills): green circle, blue square, light-blue square with a black diamond
(advanced intermediate), black diamond, and EX: two touching black diamonds with a white E and X in them
(extreme terrain). Was the scratch wp_syms.py.

    python3 tools/trailmap/resorts/winter-park/symbols.py      # regen.sh runs it, from the repo root

Reads $WINTER_PARK_WORK/winterpark.pdf (default work/winter-park); writes $WINTER_PARK_WORK/wp_syms.json:
[{t, c, s}], t one of circle, square, blue-black, diamond, ex; c the centre in PDF points; s the size. Only fills
on the map up to 14 pt (not the legend panel, right of x 1405 pt, nor the logo band above y 160). A fill repeated
at one spot counts once; a diamond inside a light-blue square is part of that square's blue-black symbol; two
diamonds each holding a white 12-line glyph (the E and the X) make one EX, which tells them from the black
rounded-square service icons. names.py attaches each symbol to its name.
"""
import collections, json, math, os, pymupdf
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
p = pymupdf.open(os.path.join(WORK, 'winterpark.pdf'))[0]
raw, glyphs = [], []
for d in p.get_drawings():
    if d['type'] not in ('f', 'fs') or not d.get('fill'):
        continue
    r = d['rect']
    if r.x0 > 1405 or r.y1 < 160 or max(r.width, r.height) > 14:
        continue
    f = tuple(round(v, 2) for v in d['fill']); k = ''.join(it[0] for it in d['items'])
    c = ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2); s = max(r.width, r.height)
    t = None
    if f in ((0.08, 0.63, 0.3), (0.09, 0.63, 0.29)) and k == 'cccc' and 6 <= s <= 10: t = 'circle'
    elif f in ((0.08, 0.54, 0.79), (0.09, 0.54, 0.79)) and k == 'llll' and 6 <= s <= 10: t = 'square'
    elif f == (0.11, 0.66, 0.88) and k == 'llll' and 6 <= s <= 10: t = 'lightsquare'
    elif f in ((0.01, 0.02, 0.02), (0.14, 0.12, 0.13)) and k == 'llll' and 3.5 <= s <= 8: t = 'diamond'
    elif f == (1.0, 1.0, 1.0) and k == 'l' * 12 and s <= 4.5: glyphs.append(c)  # the white E / X in an EX diamond
    if t:
        raw.append({'t': t, 'c': c, 's': s})
syms = []
for s in raw:  # dedupe exact repeats
    if not any(q['t'] == s['t'] and math.dist(q['c'], s['c']) < 0.8 for q in syms):
        syms.append(s)
light = [s for s in syms if s['t'] == 'lightsquare']
dia = [s for s in syms if s['t'] == 'diamond' and not any(math.dist(q['c'], s['c']) < 2 for q in light)]
lettered = [s for s in dia if any(math.dist(g, s['c']) < 1.5 for g in glyphs)]
out = [s for s in syms if s['t'] in ('circle', 'square')] + [dict(s, t='blue-black') for s in light]
used = set()
for i, a in enumerate(lettered):
    if i in used: continue
    best = min(((math.dist(a['c'], b['c']), j) for j, b in enumerate(lettered) if j != i and j not in used), default=None)
    assert best and best[0] < 7, ('lone lettered diamond', a['c'])
    used |= {i, best[1]}; b = lettered[best[1]]
    out.append({'t': 'ex', 'c': ((a['c'][0] + b['c'][0]) / 2, (a['c'][1] + b['c'][1]) / 2), 's': 11})
out += [s for s in dia if s not in lettered]
json.dump(out, open(os.path.join(WORK, 'wp_syms.json'), 'w'))
print(collections.Counter(s['t'] for s in out), len(glyphs), 'white E/X glyphs')
