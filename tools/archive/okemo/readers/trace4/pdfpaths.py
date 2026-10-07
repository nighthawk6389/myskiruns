import pymupdf, math, json
doc=pymupdf.open('../okemo.pdf')
page=doc[1]
S=3.0
dr=page.get_drawings()
cols={'green':(0.05,0.53,0.26),'blue':(0.21,0.33,0.65),'black':(0.01,0.02,0.02)}
def near(c,t): return c and all(abs(a-b)<0.03 for a,b in zip(c,t))
res=[]
for i,d in enumerate(dr):
    if d.get('type') not in ('s','fs'): continue
    c=d.get('color'); w=d.get('width') or 0
    name=None
    for k,t in cols.items():
        if near(c,t): name=k
    if not name or w>0.8: continue
    # split into runs
    runs=[]; cur=[]
    last=None
    for it in d['items']:
        if it[0] in ('l','c'):
            p0=it[1]
            if last is not None and (abs(p0.x-last.x)>0.01 or abs(p0.y-last.y)>0.01):
                runs.append(cur); cur=[]
            if not cur: cur.append((p0.x*S,p0.y*S))
            pe=it[-1]
            cur.append((pe.x*S,pe.y*S)); last=pe
        else:
            print('other item',it[0])
    if cur: runs.append(cur)
    res.append((d['seqno'],i,name,[ (tuple(map(round,r[0])),tuple(map(round,r[-1]))) for r in runs]))
multi=[r for r in res if len(r[3])>1]
print('stroke drawings',len(res),'with multiple runs',len(multi))
for r in multi[:40]: print(r)
json.dump(res,open('pdfpaths.json','w'))
