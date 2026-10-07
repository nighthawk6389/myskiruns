"""List PDF drawings with index in [a,b]. usage: pdfseq.py a b"""
import sys, math, pickle
D=pickle.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rA_1/draw.pkl','rb'))
a,b=int(sys.argv[1]),int(sys.argv[2])
for d in D[a:b+1]:
    col=tuple(round(v,2) for v in d['color']) if d['color'] else None
    fil=tuple(round(v,2) for v in d['fill']) if d['fill'] else None
    P=[(round(px*2.5),round(py*2.5)) for px,py in d['pts']]
    L=sum(math.dist(p,q) for p,q in zip(P,P[1:]))
    print(d['i'], d['type'], 'col',col,'fill',fil,'w',round(d['width'],2) if d['width'] else None,'dash',d['dashes'],'n',len(P),'len',round(L),'start',P[0] if P else None,'end',P[-1] if P else None)
