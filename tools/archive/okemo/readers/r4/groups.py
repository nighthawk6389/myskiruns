import json, math, pymupdf
page = pymupdf.open('okemo.pdf')[1]
classes = {(0.05,0.53,0.26):'green',(0.21,0.33,0.65):'blue',(0.01,0.02,0.02):'black',(0.96,0.51,0.12):'freestyle'}
polys = json.load(open('linePolylines_v1.json'))['polylines']
W,H=4374,2739
def src(p): return (p[0]*W/100, p[1]*H/100)
starts = [(p['id'], src(p['points'][0]), src(p['points'][-1])) for p in polys]
def match(pt):
    best=min(starts, key=lambda s: math.dist(s[1],pt))
    return best[0] if math.dist(best[1],pt)<3 else None
groups=[]
for di,d in enumerate(page.get_drawings()):
    if d['type']!='s' or not d.get('color') or (d.get('width') or 0)>0.8: continue
    cls=classes.get(tuple(round(v,2) for v in d['color']))
    if not cls: continue
    runs=[]; run=[]
    for it in d['items']:
        if it[0] in ('l','c'):
            start=it[1]; end=it[-1]
            if run and math.hypot(run[-1][0]-start.x, run[-1][1]-start.y)>0.5:
                runs.append(run); run=[]
            if not run: run=[(start.x,start.y)]
            run.append((end.x,end.y))
    if run: runs.append(run)
    ids=[match((r[0][0]*3, r[0][1]*3)) for r in runs]
    groups.append((di, d.get('seqno'), cls, ids, d.get('layer'), d.get('closePath')))
mine={22,23,24,25,28,161,164,165,166,167,168,169,170,171,174,175,178,183,184,185,186,187,188,189,190,191,194,195,196,197,198,199,211,212,213,214,215,216,217,218,221,222}
for g in groups:
    if set(i for i in g[3] if i is not None) & mine or len(g[3])>1 and any(i in mine for i in g[3]):
        print(g)
print(len(groups))
