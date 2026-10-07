import pymupdf, sys, json
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
# usage: strokes.py x0 y0 x1 y1 zoom out.png [colorfilter r,g,b]
# draws every trail-coloured PDF stroke touching the box, each in its own colour, numbered, over the map crop
x0,y0,x1,y1,z = [float(v) for v in sys.argv[1:6]]
out = sys.argv[6]
filt = tuple(float(v) for v in sys.argv[7].split(',')) if len(sys.argv) > 7 else None
S = 2.5
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
pg = doc[1]
r = pymupdf.Rect(x0/S, y0/S, x1/S, y1/S)
im = Image.open('/home/user/myskiruns/work/whistler-blackcomb/main/map.png').convert('RGB').crop((int(x0),int(y0),int(x1),int(y1)))
im = im.resize((int((x1-x0)*z), int((y1-y0)*z)), Image.LANCZOS)
im = Image.blend(im, Image.new('RGB', im.size, (255,255,255)), 0.55)
dr = ImageDraw.Draw(im)
pal = [(230,25,75),(60,180,75),(0,130,200),(245,130,48),(145,30,180),(70,240,240),(240,50,230),(210,245,60),(128,0,0),(0,128,128),(170,110,40),(0,0,128),(128,128,0),(255,215,0),(0,0,0)]
def bez(p0,p1,p2,p3,n=16):
    pts=[]
    for i in range(n+1):
        t=i/n; u=1-t
        pts.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0], u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return pts
k = 0
for d in pg.get_drawings():
    if d.get('type') != 's' or d.get('color') is None or not d['rect'].intersects(r): continue
    col = tuple(round(c,2) for c in d['color'])
    if col in [(0.9,0.91,0.91),(1.0,1.0,1.0)]: continue
    if filt and max(abs(a-b) for a,b in zip(col,filt)) > 0.05: continue
    R = d['rect']
    if R.width*S > 1500 or R.height*S > 1500: continue
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            a, b = it[1], it[2]; seg = [(a.x,a.y),(b.x,b.y)]
        elif it[0] == 'c':
            seg = bez(*[(p.x,p.y) for p in it[1:5]])
        else:
            continue
        pts.extend(seg)
    if not pts: continue
    P = [((x*S-x0)*z, (y*S-y0)*z) for x,y in pts]
    c = pal[k % len(pal)]
    dr.line(P, fill=c, width=2)
    mid = P[len(P)//2]
    dr.text((mid[0]+3, mid[1]-10), str(k), fill=c)
    dr.text((P[0][0]+2, P[0][1]+2), 's%d'%k, fill=c)
    print(k, col, round(d['width'],2), 'from', (round(pts[0][0]*S),round(pts[0][1]*S)), 'to', (round(pts[-1][0]*S),round(pts[-1][1]*S)))
    k += 1
im.save(out)
