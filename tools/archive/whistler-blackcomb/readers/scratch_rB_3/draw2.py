import pymupdf, sys
# usage: draw2.py x0 y0 x1 y1 [color-filter]  -> full point lists of trail-coloured strokes touching the box
x0,y0,x1,y1 = [float(v) for v in sys.argv[1:5]]
S = 2.5
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
pg = doc[1]
r = pymupdf.Rect(x0/S, y0/S, x1/S, y1/S)
for d in pg.get_drawings():
    if not d['rect'].intersects(r) or d.get('color') is None or d.get('type') != 's':
        continue
    col = tuple(round(c,2) for c in d['color'])
    if col in [(0.9,0.91,0.91), (1.0,1.0,1.0)]:
        continue
    R = d['rect']
    if R.width*S > 900 or R.height*S > 900: continue
    pts = []
    for it in d['items']:
        for p in it[1:]:
            if isinstance(p, pymupdf.Point):
                q = (round(p.x*S), round(p.y*S))
                if not pts or pts[-1] != q: pts.append(q)
    print(col, round(d['width'],2), d.get('dashes'), pts)
