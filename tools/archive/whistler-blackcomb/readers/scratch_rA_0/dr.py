# dump the PDF page-1 drawings (strokes) to a pickle for quick queries
import pymupdf, pickle
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
pg = doc[1]
dr = pg.get_drawings(extended=False)
out = []
for i, p in enumerate(dr):
    pts = []
    for it in p['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            pts += [(it[1].x, it[1].y), (it[4].x, it[4].y)]
        elif it[0] == 're':
            r = it[1]; pts += [(r.x0, r.y0), (r.x1, r.y1)]
        elif it[0] == 'qu':
            q = it[1]; pts += [(q.ul.x, q.ul.y), (q.lr.x, q.lr.y)]
    out.append(dict(i=i, seq=p.get('seqno'), type=p.get('type'), color=p.get('color'), fill=p.get('fill'),
                    width=p.get('width'), layer=p.get('layer'), dashes=p.get('dashes'), rect=tuple(p['rect']), pts=pts))
pickle.dump(out, open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rA_0/dr.pkl', 'wb'))
print(len(out))
from collections import Counter
print(Counter(o['layer'] for o in out).most_common(20))
