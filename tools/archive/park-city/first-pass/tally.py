"""tally.py PAGE: stroke colours x widths (count, total length) and fill colours (count, median size)."""
import sys, math, collections, statistics, pymupdf
doc = pymupdf.open('/home/user/myskiruns/work/park-city/20251114_PC_winter-trail_map_001.pdf')
p = doc[int(sys.argv[1])]
st = collections.defaultdict(lambda: [0, 0.0, None]); fi = collections.defaultdict(list)
for d in p.get_drawings():
    r = d['rect']
    if d['type'] in ('s', 'fs') and d.get('color'):
        L = 0
        for it in d['items']:
            if it[0] == 'l': L += math.dist((it[1].x, it[1].y), (it[2].x, it[2].y))
            elif it[0] == 'c': L += math.dist((it[1].x, it[1].y), (it[4].x, it[4].y))
            elif it[0] == 're': L += 2 * (it[1].width + it[1].height)
        k = (tuple(round(v, 2) for v in d['color']), round(d.get('width') or 0, 2), bool(d.get('dashes') not in (None, '[] 0')))
        st[k][0] += 1; st[k][1] += L; st[k][2] = st[k][2] or tuple(round(v) for v in r)
    if d['type'] in ('f', 'fs') and d.get('fill'):
        fi[tuple(round(v, 2) for v in d['fill'])].append(max(r.width, r.height))
print('STROKES (colour, width, dashed): count, length pt, example rect')
for k, v in sorted(st.items(), key=lambda kv: -kv[1][1])[:45]:
    print(' ', k, v[0], round(v[1]), v[2])
print('FILLS: colour count median-size')
for k, v in sorted(fi.items(), key=lambda kv: -len(kv[1]))[:30]:
    print(' ', k, len(v), round(statistics.median(v), 2))
