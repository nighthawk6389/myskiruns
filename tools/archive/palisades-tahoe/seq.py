"""seq.py PANEL id[,id...] [--k 4]: each piece's PDF stroke (seqno) and the strokes drawn k before and after it, with
the pieces they gave and those pieces' names: one run's strokes are usually drawn one after another."""
import importlib.util, json, math, sys
import pymupdf
P_ = sys.argv[1]; ids = [int(v) for v in sys.argv[2].split(',')]
K = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 4
H = '/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe'
W = f'/home/user/myskiruns/work/palisades-tahoe/{P_}'
spec = importlib.util.spec_from_file_location('r', f'{H}/panels/{P_}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[P_]
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
x0c, y0c, x1c, y1c = R.CLIP
WW, HH = (x1c - x0c) * R.SCALE, (y1c - y0c) * R.SCALE
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']; N = json.load(open(f'{W}/names.json'))
TR = {(0.0, 0.65, 0.32): 'green', (0.0, 0.61, 0.86): 'blue', (0.14, 0.12, 0.13): 'black', (0.0, 0.0, 0.0): 'black'}
S = []
for d in page.get_drawings():
    c = tuple(round(v, 2) for v in (d.get('color') or ()))
    if d['type'] != 's' or c not in TR:
        continue
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, b, cc, e = it[1:5]
            pts += [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [j/8 for j in range(9)]]
    if pts:
        S.append((d['seqno'], TR[c], round(d.get('width') or 0, 2), d.get('dashes') not in (None, '[] 0'), pts))
pt = lambda q: (q[0] / R.SCALE + x0c, q[1] / R.SCALE + y0c)  # noqa: E731
pp = {p['id']: [pt((x * WW / 100, y * HH / 100)) for x, y in p['points']] for p in P}
def strokes_of(pid):
    q = pp[pid]; m = q[len(q) // 2]
    return [s for s in S if min(math.dist(m, v) for v in s[4]) < 0.8]
def pieces_of(stroke):
    out = []
    for pid, q in pp.items():
        m = q[len(q) // 2]
        if min(math.dist(m, v) for v in stroke[4]) < 0.8:
            out.append(f"{pid}:{N.get(str(pid), '?')}")
    return out
order = [s[0] for s in S]
for i in ids:
    mine = strokes_of(i)
    print(f'#{i} {N.get(str(i), "?")}: strokes {[(s[0], s[1], "dashed" if s[3] else "") for s in mine]}')
    for s in mine[:1]:
        k = order.index(s[0])
        for t in S[max(0, k - K): k + K + 1]:
            print(f'    {t[0]:5d} {t[1]:6s}{" dashed" if t[3] else "       "} {"<--" if t[0] == s[0] else "   "} {pieces_of(t)}')
