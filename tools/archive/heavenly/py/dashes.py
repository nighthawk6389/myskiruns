import sys, math, pymupdf
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from ribbon import subpaths, centre, length
pg = pymupdf.open(sys.argv[1])[0]
seq = int(sys.argv[2])
d = next(d for d in pg.get_drawings() if d['seqno'] == seq)
C = []
for s in subpaths(d):
    c, w = centre(s)
    if c: C.append((c, w))
print(len(C), 'subpaths; lengths', sorted(round(length(c), 2) for c, w in C)[:5], '...', sorted(round(length(c), 2) for c, w in C)[-5:])
print('widths', sorted(round(w, 2) for c, w in C)[:3], sorted(round(w, 2) for c, w in C)[-3:])
# gaps: for each dash, nearest other dash end
gaps = []
for k, (c, w) in enumerate(C):
    best = min(min(math.dist(e, f) for e in (c[0], c[-1]) for f in (o[0], o[-1])) for m, (o, _) in enumerate(C) if m != k)
    gaps.append(round(best, 2))
print('nearest-end gaps', sorted(gaps)[:5], sorted(gaps)[-8:])
