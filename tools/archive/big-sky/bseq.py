"""bseq.py RESORT/PANEL id[,id...] [--k 3]: each piece's PDF strokes (seqno) and the strokes drawn k before and after,
with the pieces they gave and those pieces' names (one run's strokes are usually drawn one after another)."""
import contextlib, io, json, math, sys
import pymupdf
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap/resorts/big-sky')
import prepare as pp
r = pr.Resort(sys.argv[1]); ids = [int(v) for v in sys.argv[2].split(',')]
K = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 3
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
N = json.load(open(r.work('names.json')))
S = pp.SETUP[r.panel]
page = pymupdf.open(f"/home/user/myskiruns/work/big-sky/{S['pdf']}")[0]
cls = {pp.col(c): k for k, cs in S['lines'].items() for c in cs}
lo, hi = S['widths']
strokes = []
for d in page.get_drawings():
    k = cls.get(pp.col(d.get('color'))) if d['type'] in ('s', 'fs') else None
    if k and lo <= (d.get('width') or 0) <= hi:
        strokes.append((d['seqno'], k, pp.dense(pp.outline(d), 1.0)))
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
x0, y0 = r.R.CLIP[:2]
def topt(q): return (q[0] / r.R.SCALE + x0, q[1] / r.R.SCALE + y0)
owner = {}
for i, q in P.items():
    qq = [topt(v) for v in q]
    for s in strokes:
        if sum(1 for v in qq[::max(1, len(qq) // 8)] if min(math.dist(v, w) for w in s[2]) < 1.0) >= 2:
            owner.setdefault(s[0], []).append(i)
seqs = sorted(owner)
for i in ids:
    mine = [s for s, ps in owner.items() if i in ps]
    print(f'#{i} {N.get(str(i))}: strokes {mine}')
    for s in mine:
        k = seqs.index(s)
        for t in seqs[max(0, k - K):k + K + 1]:
            print(f"   {t:6d} {'<--' if t == s else '   '} {[f'{p}:{N.get(str(p))}' for p in owner[t]]}")
