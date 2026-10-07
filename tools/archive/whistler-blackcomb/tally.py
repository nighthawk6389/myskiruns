import sys, collections, pymupdf
pdf = '/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'
pg = int(sys.argv[1]); clip = tuple(map(float, sys.argv[2].split(','))) if len(sys.argv) > 2 else None
p = pymupdf.open(pdf)[pg]
D = p.get_drawings()
st = collections.Counter(); fl = collections.Counter(); flsize = collections.defaultdict(list)
for d in D:
    r = d['rect']
    if clip and not (clip[0] <= (r.x0+r.x1)/2 <= clip[2] and clip[1] <= (r.y0+r.y1)/2 <= clip[3]):
        continue
    col = tuple(round(v, 2) for v in d['color']) if d.get('color') else None
    fil = tuple(round(v, 2) for v in d['fill']) if d.get('fill') else None
    if d['type'] in ('s', 'fs') and col:
        st[(col, round(d.get('width') or 0, 2), d.get('dashes') not in (None, '[] 0', '[] 0.0'))] += 1
    if d['type'] in ('f', 'fs') and fil:
        sz = max(r.width, r.height)
        fl[(fil, 'small' if sz < 10.5 else 'big')] += 1
print('STROKES (colour, width, dashed): count')
for k, v in st.most_common(60): print(' ', k, v)
print('FILLS (fill, size class): count')
for k, v in fl.most_common(60): print(' ', k, v)
