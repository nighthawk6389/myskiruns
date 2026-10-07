"""List fills of a colour with their subpaths (a subpath starts at a move: an item whose start is not the previous end)."""
import sys, math, collections, pymupdf
pdf, col = sys.argv[1], tuple(float(v) for v in sys.argv[2].split(','))
doc = pymupdf.open(pdf); pg = doc[0]

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

def bbox(items):
    P = [q for it in items for q in pts_of(it)]
    xs = [q.x for q in P]; ys = [q.y for q in P]
    return min(xs), min(ys), max(xs), max(ys)

for d in pg.get_drawings():
    f = d.get('fill')
    if d['type'] != 'f' or not f or max(abs(a - b) for a, b in zip(f, col)) > 0.01:
        continue
    sp = subpaths(d)
    r = d['rect']
    sizes = collections.Counter()
    for s in sp:
        x0, y0, x1, y1 = bbox(s)
        sizes[(round(max(x1 - x0, y1 - y0)), len(s))] += 1
    print(d['seqno'], [round(v) for v in (r.x0, r.y0, r.x1, r.y1)], 'items', len(d['items']), 'subpaths', len(sp), 'eo', d.get('even_odd'), dict(sizes.most_common(4)))
