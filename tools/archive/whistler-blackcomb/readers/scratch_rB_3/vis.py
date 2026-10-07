import pymupdf, sys, math
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
# usage: vis.py x0 y0 x1 y1 r,g,b  -> for each stroke of that colour touching the box: the visible fraction along its path,
# printed as a run-length string over the path (V = line colour seen within 1px, . = not)
x0,y0,x1,y1 = [float(v) for v in sys.argv[1:5]]
filt = tuple(float(v) for v in sys.argv[5].split(','))
S = 2.5
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
pg = doc[1]
r = pymupdf.Rect(x0/S, y0/S, x1/S, y1/S)
im = Image.open('/home/user/myskiruns/work/whistler-blackcomb/main/map.png').convert('RGB')
px = im.load()
W, H = im.size
target = tuple(int(c*255) for c in filt)
def bez(p0,p1,p2,p3,n=24):
    return [(( (1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0]), ((1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1])) for t in [i/n for i in range(n+1)]]
def near(x, y, tol=60):
    best = 1e9
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            X, Y = int(round(x))+dx, int(round(y))+dy
            if 0<=X<W and 0<=Y<H:
                c = px[X,Y]
                best = min(best, sum(abs(a-b) for a,b in zip(c,target)))
    return best < tol
k = 0
for d in pg.get_drawings():
    if d.get('type') != 's' or d.get('color') is None or not d['rect'].intersects(r): continue
    col = tuple(round(c,2) for c in d['color'])
    if max(abs(a-b) for a,b in zip(col,filt)) > 0.05: continue
    pts = []
    for it in d['items']:
        if it[0] == 'l': pts += [(it[1].x,it[1].y),(it[2].x,it[2].y)]
        elif it[0] == 'c': pts += bez(*[(p.x,p.y) for p in it[1:5]])
    P = [(x*S, y*S) for x,y in pts]
    # resample every 2 px
    samp = []
    for (ax,ay),(bx,by) in zip(P, P[1:]):
        L = math.hypot(bx-ax, by-ay); n = max(1, int(L/2))
        for i in range(n): samp.append((ax+(bx-ax)*i/n, ay+(by-ay)*i/n))
    s = ''.join('V' if near(x,y) else '.' for x,y in samp)
    print(k, 'from', tuple(round(v) for v in P[0]), 'to', tuple(round(v) for v in P[-1]), 'len~', 2*len(samp), 'vis %.0f%%' % (100*s.count('V')/max(1,len(s))))
    # compress string into 4px chunks markers with positions every 20 samples
    out = []
    for i in range(0, len(s), 20):
        x, y = samp[i]
        out.append('(%d,%d)%s' % (x, y, s[i:i+20]))
    print('   ', ' '.join(out))
    k += 1
