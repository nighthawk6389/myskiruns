"""overlaps.py RESORT/PANEL [--tol 3] [--min 25]: stretches of a named piece lying along another named piece of a
different name (within tol map px) for at least min px: two overlays on one drawn line."""
import contextlib, io, json, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
tol = float(sys.argv[sys.argv.index('--tol') + 1]) if '--tol' in sys.argv else 3
mn = float(sys.argv[sys.argv.index('--min') + 1]) if '--min' in sys.argv else 25
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
P = {p['id']: r.pts_of(p) for p in r.P}
A = r.assign
def dense(pts, step=2):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [pts[-1]]
for i in sorted(A):
    di = dense(P[i])
    for j in sorted(A):
        if j == i or A[j] == A[i]:
            continue
        xs = [q[0] for q in P[j]]; ys = [q[1] for q in P[j]]
        if min(q[0] for q in di) > max(xs) + tol or max(q[0] for q in di) < min(xs) - tol or min(q[1] for q in di) > max(ys) + tol or max(q[1] for q in di) < min(ys) - tol:
            continue
        near = [pr.line_dist(q, P[j]) < tol for q in di]
        run = best = 0; start = bstart = 0
        for k, v in enumerate(near):
            if v:
                if run == 0:
                    start = k
                run += 1
                if run > best:
                    best, bstart = run, start
            else:
                run = 0
        if best * 2 >= mn:
            a, b = di[bstart], di[bstart + best - 1]
            print(f'{i} {sorted(A[i])} runs along {j} {sorted(A[j])} for {best * 2} px: ({a[0]:.0f},{a[1]:.0f})..({b[0]:.0f},{b[1]:.0f})')
