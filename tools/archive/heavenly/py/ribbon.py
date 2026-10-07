"""Subpaths of a fill and their centre lines (PDF points)."""
import math

def pts_of(it):
    if it[0] == 'l': return [it[1], it[2]]
    if it[0] == 'c': return [it[1], it[2], it[3], it[4]]
    if it[0] == 're': r = it[1]; return [r.tl, r.tr, r.br, r.bl]
    if it[0] == 'qu': q = it[1]; return [q.ul, q.ur, q.lr, q.ll]

def subpaths(d):
    out, cur, last = [], [], None
    for it in d['items']:
        p = pts_of(it)
        if it[0] in ('re', 'qu'):
            if cur: out.append(cur); cur = []
            out.append([it]); last = None; continue
        if last is not None and abs(p[0].x - last.x) + abs(p[0].y - last.y) > 1e-3:
            out.append(cur); cur = []
        cur.append(it); last = p[-1]
    if cur: out.append(cur)
    return out

def outline(items, n=12):
    pts = []
    for it in items:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, b, c, e = it[1:5]
            pts += [((1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c.x + t ** 3 * e.x,
                     (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c.y + t ** 3 * e.y)
                    for t in [j / n for j in range(n + 1)]]
        elif it[0] in ('re', 'qu'):
            pts += [(p.x, p.y) for p in pts_of(it)]
    return pts

def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    return out + [tuple(pts[-1])] if pts else out

def resample(pts, n):
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    out, j = [], 0
    for k in range(n):
        t = cum[-1] * k / (n - 1)
        while j < len(cum) - 2 and cum[j + 1] < t:
            j += 1
        u = (t - cum[j]) / ((cum[j + 1] - cum[j]) or 1)
        out.append((pts[j][0] + u * (pts[j + 1][0] - pts[j][0]), pts[j][1] + u * (pts[j + 1][1] - pts[j][1])))
    return out

def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))

def centre(items, step=0.25):
    """(centre line, width): the outline split at its two farthest-apart points into two sides, each point of one
    side paired with the nearest point of the other."""
    o = dense(outline(items), step)
    if o and math.dist(o[0], o[-1]) < 1e-6:
        o = o[:-1]
    n = len(o)
    if n < 4:
        return None, None
    stride = max(1, n // 400)
    i, j = max(((i, j) for i in range(0, n, stride) for j in range(i + 1, n, stride)), key=lambda ij: math.dist(o[ij[0]], o[ij[1]]))
    a = o[i:j + 1]
    b = (o[j:] + o[:i + 1])[::-1]
    if len(a) < 2 or len(b) < 2:
        return None, None
    m = max(8, int(length(a) / 0.5))
    pairs = [(p, min(b, key=lambda q: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)) for p in resample(a, m)]
    ws = sorted(math.dist(p, q) for p, q in pairs)
    return [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in pairs], ws[len(ws) // 2]
