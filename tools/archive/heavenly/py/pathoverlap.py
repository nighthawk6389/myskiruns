"""Final overlays (trailPaths.json) lying along another trail's overlay for 40+ px (within 4 px): a route the apply
step added along another trail's line, or two trails sharing a line."""
import json, math, sys
W, H = int(sys.argv[2]), int(sys.argv[3])
T = json.load(open(sys.argv[1]))['trails']
def dense(s, step=2):
    out = []
    for a, b in zip(s, s[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [tuple(s[-1])]
def segd(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))
P = {k: [[(x * W / 100, y * H / 100) for x, y in s] for s in v['segments']] for k, v in T.items()}
for a, sa in P.items():
    for b, sb in P.items():
        if a >= b:
            continue
        for s in sa:
            run = best = 0; at = None
            for q in dense(s):
                if any(segd(q, u, v) < 4 for t in sb for u, v in zip(t, t[1:])):
                    run += 1
                    if run > best: best, at = run, q
                else:
                    run = 0
            if best * 2 >= 40:
                print(f'{a} along {b}: {best * 2} px, ending near ({at[0]:.0f},{at[1]:.0f})')
