import json, math, sys
sys.path.insert(0,'tools/trailmap')
import pdf_resort as pr
R=pr.Resort('deer-valley')
P={p['id']:p for p in R.load('pieces.json')['polylines']}
def at(pid, f):
    pts=R.pts_of(P[pid]); L=sum(math.dist(a,b) for a,b in zip(pts,pts[1:])); t=f*L
    for a,b in zip(pts,pts[1:]):
        d=math.dist(a,b)
        if t<=d: return (round(a[0]+(b[0]-a[0])*t/d), round(a[1]+(b[1]-a[1])*t/d))
        t-=d
    return tuple(round(v) for v in pts[-1])
for arg in sys.argv[1:]:
    pid,f=arg.split('@') if '@' in arg else (arg,'0.5')
    print(pid, f, at(int(pid), float(f)))
