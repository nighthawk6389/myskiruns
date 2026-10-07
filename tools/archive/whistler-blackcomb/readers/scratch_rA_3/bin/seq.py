# list PDF strokes with seqno in a range: colour, width, first/last points in map px
import sys, pymupdf
S = 2.5
lo, hi = int(sys.argv[1]), int(sys.argv[2])
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
page = doc[1]
for d in page.get_drawings():
    sq = d.get('seqno')
    if sq is None or not (lo <= sq <= hi):
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
    print(sq, d['type'], 'col', col, 'fill', fill, 'w', round(w, 2) if w else None, 'dash', d.get('dashes'), 'n', len(pts), pts[:1], pts[-1:])
