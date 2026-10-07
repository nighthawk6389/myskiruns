import pymupdf, sys
doc=pymupdf.open('../okemo.pdf')
page=doc[1]
S=3.0
x0,y0,x1,y1=[float(v)/S for v in sys.argv[1:5]]
box=pymupdf.Rect(x0,y0,x1,y1)
dr=page.get_drawings()
print('total drawings',len(dr))
n=0
for i,d in enumerate(dr):
    r=d['rect']
    if not r.intersects(box): continue
    col=d.get('color'); fill=d.get('fill'); w=d.get('width')
    typ=d.get('type')
    items=d['items']
    # summarize
    pts=[]
    for it in items:
        for p in it[1:]:
            if isinstance(p,pymupdf.Point): pts.append((round(p.x*S),round(p.y*S)))
            elif isinstance(p,pymupdf.Rect): pts.append((round(p.x0*S),round(p.y0*S)))
    area=r.width*r.height*S*S
    print(i,typ,'col',tuple(round(c,2) for c in col) if col else None,'fill',tuple(round(c,2) for c in fill) if fill else None,'w',round(w,2) if w else None,'rect',(round(r.x0*S),round(r.y0*S),round(r.x1*S),round(r.y1*S)),'nitems',len(items),'closePath',d.get('closePath'), 'seqno',d.get('seqno'))
    n+=1
print('n',n)
