"""List PDF drawings (strokes) passing within r map px of a point. usage: pdfnear.py x y [r] [colorfilter]"""
import sys, math, pickle, os
import pymupdf
PDF='/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'
cache='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rA_1/draw.pkl'
if os.path.exists(cache):
    D=pickle.load(open(cache,'rb'))
else:
    doc=pymupdf.open(PDF); page=doc[1]
    D=[]
    for i,d in enumerate(page.get_drawings()):
        pts=[]
        for it in d['items']:
            if it[0]=='l': pts+=[(it[1].x,it[1].y),(it[2].x,it[2].y)]
            elif it[0]=='c':
                a,b,c,e=it[1:5]
                pts+=[((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x,(1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y) for t in [k/8 for k in range(9)]]
            elif it[0]=='re':
                r=it[1]; pts+=[(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1),(r.x0,r.y0)]
            elif it[0]=='qu':
                q=it[1]; pts+=[(q.ul.x,q.ul.y),(q.ur.x,q.ur.y),(q.lr.x,q.lr.y),(q.ll.x,q.ll.y)]
        D.append(dict(i=i,type=d['type'],color=d.get('color'),fill=d.get('fill'),width=d.get('width'),dashes=d.get('dashes'),closePath=d.get('closePath'),pts=pts,seqno=d.get('seqno')))
    pickle.dump(D,open(cache,'wb'))
x,y=float(sys.argv[1])/2.5,float(sys.argv[2])/2.5
r=(float(sys.argv[3]) if len(sys.argv)>3 else 10)/2.5
for d in D:
    if not d['pts']: continue
    dm=min(math.hypot(px-x,py-y) for px,py in d['pts'])
    if dm<=r:
        col=tuple(round(v,2) for v in d['color']) if d['color'] else None
        fil=tuple(round(v,2) for v in d['fill']) if d['fill'] else None
        P=[(round(px*2.5),round(py*2.5)) for px,py in d['pts']]
        L=sum(math.dist(a,b) for a,b in zip(P,P[1:]))
        print(d['i'], d['type'], 'col',col,'fill',fil,'w',round(d['width'],2) if d['width'] else None,'dash',d['dashes'],'close',d['closePath'],'n',len(P),'len',round(L),'start',P[0],'end',P[-1], 'seq', d['seqno'])
