import pymupdf, sys
# usage: seq.py x0 y0 x1 y1 : list trail-coloured strokes with seqno touching the box, sorted by seqno
x0,y0,x1,y1 = [float(v) for v in sys.argv[1:5]]
S = 2.5
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'); pg = doc[1]
r = pymupdf.Rect(x0/S, y0/S, x1/S, y1/S)
rows = []
for d in pg.get_drawings():
    if d.get('type') != 's' or d.get('color') is None or not d['rect'].intersects(r): continue
    col = tuple(round(c,2) for c in d['color'])
    if col in [(0.9,0.91,0.91)]: continue
    R = d['rect']
    if R.width*S > 1500 or R.height*S > 1500: continue
    pts = []
    for it in d['items']:
        for p in it[1:]:
            if isinstance(p, pymupdf.Point): pts.append((round(p.x*S), round(p.y*S)))
    rows.append((d.get('seqno'), col, round(d['width'],2), d.get('dashes') if col==(1.0,1.0,1.0) else '', pts[0], pts[-1]))
for r_ in sorted(rows): print(r_)
