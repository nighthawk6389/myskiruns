# list PDF drawings (strokes) intersecting a box given in MAP px; print colour, width, dashes, seq, points in map px
import sys, pymupdf
S = 2.5
x0, y0, x1, y1 = [float(v) / S for v in sys.argv[1].split(',')]
only_stroke = len(sys.argv) < 3 or sys.argv[2] != 'all'
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
page = doc[1]
r = pymupdf.Rect(x0, y0, x1, y1)
for d in page.get_drawings():
    if not d['rect'].intersects(r):
        continue
    if only_stroke and d['type'] not in ('s', 'fs'):
        continue
    col = tuple(round(v, 2) for v in d['color']) if d.get('color') else None
    fill = tuple(round(v, 2) for v in d['fill']) if d.get('fill') else None
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [it[1], it[2]]
        elif it[0] == 'c':
            pts += [it[1], it[4]]
        elif it[0] == 're':
            pts += [it[1].tl, it[1].br]
    pts = [(round(p.x * S), round(p.y * S)) for p in pts]
    w = d.get('width')
    print(d.get('seqno'), d['type'], 'col', col, 'fill', fill, 'w', round(w, 2) if w else None, 'dash', d.get('dashes'), 'n', len(pts), pts[:6], '...' if len(pts) > 6 else '', pts[-2:])
