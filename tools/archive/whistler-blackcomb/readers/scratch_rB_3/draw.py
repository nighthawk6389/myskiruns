import pymupdf, sys
# usage: draw.py x0 y0 x1 y1 (map px) -> list strokes intersecting the box (PDF page 2)
x0,y0,x1,y1 = [float(v) for v in sys.argv[1:5]]
S = 2.5
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
pg = doc[1]
r = pymupdf.Rect(x0/S, y0/S, x1/S, y1/S)
out = []
for d in pg.get_drawings():
    if not d['rect'].intersects(r):
        continue
    col = d.get('color'); fill = d.get('fill'); w = d.get('width')
    pts = []
    for it in d['items']:
        for p in it[1:]:
            if isinstance(p, pymupdf.Point):
                pts.append((round(p.x*S), round(p.y*S)))
    R = d['rect']
    if R.width*S > 600 or R.height*S > 600: 
        continue
    def c(v): return None if v is None else tuple(round(x,2) for x in v)
    out.append((d.get('type'), c(col), c(fill), None if w is None else round(w,2), d.get('dashes'), [round(R.x0*S),round(R.y0*S),round(R.x1*S),round(R.y1*S)], len(pts), pts[:3], pts[-2:]))
for o in out:
    if o[0] in ('s','fs') and o[1] is not None:
        print(o)
