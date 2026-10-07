import pymupdf, math, json
page=pymupdf.open('okemo.pdf')[1]
x0,y0,x1,y1=0,0,1458,913
classes={(0.05,0.53,0.26):'green',(0.21,0.33,0.65):'blue',(0.01,0.02,0.02):'black'}
def bezier(p0,c1,c2,p3,n=8):
    out=[]
    for i in range(1,n+1):
        t=i/n;m=1-t
        out.append((m**3*p0.x+3*m*m*t*c1.x+3*m*t*t*c2.x+t**3*p3.x, m**3*p0.y+3*m*m*t*c1.y+3*m*t*t*c2.y+t**3*p3.y))
    return out
def run_pass(classes, maxw):
    pieces=[]
    for di,d in enumerate(page.get_drawings()):
        if d['type']!='s' or not d.get('color') or (d.get('width') or 0)>maxw: continue
        cls=classes.get(tuple(round(v,2) for v in d['color']))
        if not cls: continue
        run=[]
        for it in d['items']:
            if it[0]=='l': start,seg=it[1],[(it[2].x,it[2].y)]
            elif it[0]=='c': start,seg=it[1],bezier(*it[1:5])
            else: continue
            if run and math.hypot(run[-1][0]-start.x,run[-1][1]-start.y)>0.5:
                pieces.append((cls,run,di)); run=[]
            if not run: run=[(start.x,start.y)]
            run.extend(seg)
        if run: pieces.append((cls,run,di))
    res=[]
    for cls,run,di in pieces:
        length=sum(math.hypot(q[0]-p[0],q[1]-p[1]) for p,q in zip(run,run[1:]))
        if length<4.0: continue
        xs,ys=[p[0] for p in run],[p[1] for p in run]
        if math.dist(run[0],run[-1])<0.5 and math.hypot(max(xs)-min(xs),max(ys)-min(ys))<10: continue
        res.append((cls,di,run[0],run[-1]))
    return res
r=run_pass(classes,0.8)
print(len(r))
r2=run_pass({(0.96,0.51,0.12):'freestyle'},0.8)
print(len(r2))
allp=r+r2
m={}
for i,(cls,di,a,b) in enumerate(allp):
    m[i]={'cls':cls,'drawing':di,'a':[round(a[0]*3),round(a[1]*3)],'b':[round(b[0]*3),round(b[1]*3)]}
json.dump(m,open('r2/pathmap.json','w'))
