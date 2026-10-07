import json, math
W,H=4374,2739
P={p['id']:[(x*W/100,y*H/100) for x,y in p['points']] for p in json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']}
JOIN_NEAR=40; JOIN_FAR=250; COL=math.cos(math.radians(45))
def outward(s,atEnd):
    n=len(s); e=s[-1] if atEnd else s[0]; k=s[max(0,n-4)] if atEnd else s[min(n-1,3)]
    dx,dy=e[0]-k[0],e[1]-k[1]; L=math.hypot(dx,dy) or 1; return dx/L,dy/L
def joinEnds(segs):
    segs=[list(s) for s in segs]
    while True:
        best=None
        for i in range(len(segs)):
            for j in range(i+1,len(segs)):
                for ei in (False,True):
                    for ej in (False,True):
                        p=segs[i][-1] if ei else segs[i][0]; q=segs[j][-1] if ej else segs[j][0]
                        d=math.dist(p,q)
                        if d>JOIN_FAR or (best and d>=best[4]): continue
                        if d>JOIN_NEAR:
                            c=((q[0]-p[0])/d,(q[1]-p[1])/d); di=outward(segs[i],ei); dj=outward(segs[j],ej)
                            if di[0]*c[0]+di[1]*c[1]<COL or -(dj[0]*c[0]+dj[1]*c[1])<COL: continue
                        best=(i,j,ei,ej,d)
        if not best: return segs
        i,j,ei,ej,d=best
        a=segs[i] if ei else segs[i][::-1]; b=segs[j][::-1] if ej else segs[j]
        m=a+(b[1:] if d<1 else b)
        segs=[s for k,s in enumerate(segs) if k not in (i,j)]+[m]
for name,ids in [('mountain-road',[142,141]),('lower-mountain-road',[140,234,231,232,203,202]),('kettle-brook',[156,155,157])]:
    r=joinEnds([P[i] for i in ids])
    print(name,len(r),[ (tuple(map(round,s[0])),tuple(map(round,s[-1])),len(s)) for s in r])
