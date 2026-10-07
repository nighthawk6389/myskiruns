"""Copper Mountain: the trail lines are filled outlines (strokes converted to fills), and the top-bowl lines are
clip outlines filled with a fading image. Centre lines: rasterise each outline, thin it to a 1 px skeleton
(Zhang-Suen), and trace the skeleton into pieces split at junctions.

    python3 tools/trailmap/resorts/copper-mountain/lines.py      # regen.sh runs it (was cu_lines.py)

Reads the PDF ($COPPER_MOUNTAIN_WORK/copper.pdf). Writes src/data/resorts/copper-mountain/linePolylines.json
(the numbered pieces, in percent of the map image: its clip CLIP at 3 px/pt; regen.sh then adds _unnamed and the
final _source) and piece_src.json in the working folder (each piece's PDF drawing: "fill <seqno>", "clip [box]"
or "stroke <seqno>").
- Fills in the trail colours (COL) at least 10.5 pt long are line outlines (smaller ones are glyphs: glyphs.py);
  the logo, the SEE INSET boxes, the slash between a bowl's two symbols, the closed-area sign, the Green Acres
  and Easy Rider zones, the highway 91 shields, the I-70 arrows and the snow-maze icon are left out (SKIP_SEQ,
  SKIP_KINDS, LOGO: drawing numbers of this edition of the PDF).
- Each outline is rasterised at R = 6 px/pt (XOR of its subpaths, so holes stay holes), thinned, built into a pixel
  graph without the diagonal steps a 4-neighbour path already joins (else every staircase forks), spurs under
  2.5 pt pruned, polylines traced between forks and simplified (0.25 pt).
- The Tucker Mountain (Three Bears) lines are clip paths filled with a fading image: of each pair of clips (line,
  halo) the one with fewer items is the line.
- A few lines are plain strokes (See & Ski / EZ Road, West Village Traverse, Lyman Lane, Timber Road, West Ten
  Mile, Pine Cone Alley): their runs are taken as they are (dashed ones are uphill routes: left out; 4945 is the
  Log Chute kids' zone outline: a marker at its label instead).
- Boulderado's line runs on under the COPPER MOUNTAIN peak label: cut at the label's box (BOXES).
"""
import json, math
import os
import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from common import DATA, PDF, work

p = pymupdf.open(PDF)[0]
COL = {(0.14, 0.12, 0.13): 'black', (0.04, 0.52, 0.78): 'blue', (0.0, 0.52, 0.78): 'blue', (0.0, 0.65, 0.3): 'green',
       (0.0, 0.65, 0.31): 'green', (0.0, 0.65, 0.32): 'green', (0.0, 0.0, 0.0): 'black'}
LOGO = (75, 160, 450, 290)
SKIP_KINDS = {'lclclclc'}  # rounded boxes (SEE INSET)
SKIP_SEQ = {15, 192, 452, 5309, 5513, 5568, 5584, 5866}  # closed-area sign; Green Acres and Easy Rider zones;
# highway 91 shields, I-70 arrows, the snow-maze icon
R = 6.0  # raster px per PDF pt
CLIP = (0, 150, 1303.44, 1052.54)  # the map image's area (PDF pt)


def bez(a, b, c, e, n=10):
    return [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y)
            for t in [i / n for i in range(1, n + 1)]]


def polys(items):
    out, cur, last = [], [], None
    for it in items:
        if it[0] in ('re', 'qu'):
            continue
        s = it[1]
        if last is not None and math.dist((s.x, s.y), last) > 0.01:
            out.append(cur); cur = []
        if not cur:
            cur.append((s.x, s.y))
        cur += bez(*it[1:5]) if it[0] == 'c' else [(it[2].x, it[2].y)]
        last = (it[-1].x, it[-1].y)
    if cur:
        out.append(cur)
    return out


def thin(img):
    """Zhang-Suen thinning of a 0/1 uint8 array."""
    img = np.pad(img, 1).astype(np.uint8)
    while True:
        changed = False
        for step in (0, 1):
            P = img
            n = [np.roll(np.roll(P, dy, 0), dx, 1) for dy, dx in ((1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1))]
            # neighbours p2..p9 clockwise from north: north is the pixel above -> roll by +1 in y gives the pixel above
            p2, p3, p4, p5, p6, p7, p8, p9 = n
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.uint8) for i in range(8))
            if step == 0:
                c = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                c = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            m = (P == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if m.any():
                img = P.copy(); img[m] = 0; changed = True
        if not changed:
            return img[1:-1, 1:-1]


NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def graph(sk):
    """Skeleton pixels as a graph: 8-neighbours, minus a diagonal step wherever a 4-neighbour path joins the
    two pixels already (so staircase pixels have degree 2 and only real forks have 3+)."""
    ys, xs = np.nonzero(sk)
    on = set(zip(ys.tolist(), xs.tolist()))
    adj = {q: set() for q in on}
    for q in on:
        for dy, dx in NB:
            r = (q[0] + dy, q[1] + dx)
            if r not in on:
                continue
            if dy and dx and ((q[0] + dy, q[1]) in on or (q[0], q[1] + dx) in on):
                continue
            adj[q].add(r)
    return adj


def prune(adj, minlen):
    """Repeatedly drop end branches shorter than minlen px that hang off a fork."""
    while True:
        removed = False
        for q in [q for q, n in adj.items() if len(n) == 1]:
            if q not in adj or len(adj[q]) != 1:
                continue
            path = [q]; prev, cur = None, q
            while len(adj[cur]) == 2 or cur == q:
                nxt = [r for r in adj[cur] if r != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                if len(adj[cur]) != 2:
                    break
                path.append(cur)
            if len(adj.get(cur, ())) >= 3 and len(path) < minlen:
                for r in path:
                    for t in adj.pop(r):
                        if t in adj:
                            adj[t].discard(r)
                removed = True
        if not removed:
            return adj


def trace(adj):
    """Polylines between nodes (ends and forks); loops with no node come out whole."""
    nodes = {q for q, n in adj.items() if len(n) != 2}
    used = set(); lines = []
    for n in nodes:
        for r in adj[n]:
            if (n, r) in used:
                continue
            path = [n, r]; prev, cur = n, r
            while cur not in nodes:
                nxt = [t for t in adj[cur] if t != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]; path.append(cur)
            used.add((n, r)); used.add((path[-1], path[-2]))
            lines.append(path)
    rest = {q for q in adj if q not in nodes and not any(q in ln for ln in lines[:0])}
    covered = {q for ln in lines for q in ln}
    for q in adj:
        if q in covered or q in nodes:
            continue
        path = [q]; prev, cur = None, q
        while True:
            nxt = [t for t in adj[cur] if t != prev and t not in path[-2:]]
            if not nxt or nxt[0] == q:
                break
            prev, cur = cur, nxt[0]; path.append(cur)
        covered.update(path); lines.append(path + [q])
    return lines


def simplify(pts, eps):
    if len(pts) < 3:
        return pts
    if math.dist(pts[0], pts[-1]) < 1e-6:  # a closed loop: cut it at its farthest point first
        k = max(range(len(pts)), key=lambda i: math.dist(pts[0], pts[i]))
        return simplify(pts[:k + 1], eps)[:-1] + simplify(pts[k:], eps)
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay; nrm = math.hypot(dx, dy) or 1e-9
    best, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * (pts[i][0] - ax) - dx * (pts[i][1] - ay)) / nrm
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return simplify(pts[:idx + 1], eps)[:-1] + simplify(pts[idx:], eps)


shapes = []  # (class, [polygons], source)
for d in p.get_drawings():
    if d['type'] not in ('f', 'fs') or not d.get('fill'):
        continue
    cls = COL.get(tuple(round(v, 2) for v in d['fill']))
    r = d['rect']
    if not cls or max(r.width, r.height) < 10.5 or d['seqno'] in SKIP_SEQ:
        continue
    kinds = ''.join(it[0] for it in d['items'])
    if kinds in SKIP_KINDS or (kinds == 'cclcclc' and max(r.width, r.height) < 14):
        continue  # SEE INSET boxes; the slash between a bowl's two symbols
    if r.x0 >= LOGO[0] and r.y0 >= LOGO[1] and r.x1 <= LOGO[2] and r.y1 <= LOGO[3]:
        continue  # the resort logo
    shapes.append((cls, polys(d['items']), f"fill {d['seqno']}"))
# top-bowl lines: of each clip pair (line, halo) the one with fewer items is the line
clips = [d for d in p.get_drawings(extended=True) if d.get('type') == 'clip' and d.get('items')
         and ''.join(it[0] for it in d['items']) != 're' and d['scissor'][1] < 240 and d['scissor'][3] < 340]
pairs = {}
for d in clips:
    sc = pymupdf.Rect(d['scissor'])
    if sc.width > 150 or (abs(sc.x0 - 499.1) < 1 and abs(sc.y0 - 207.5) < 1):
        continue  # the bowl's area clip; the Three Bears lift
    key = next((k for k in pairs if abs(k[0] - sc.x0) < 2 and abs(k[1] - sc.y0) < 2 and abs(k[2] - sc.x1) < 2), None)
    pairs.setdefault(key or (sc.x0, sc.y0, sc.x1, sc.y1), []).append(d)
for k, ds in pairs.items():
    d = min(ds, key=lambda d: len(d['items']))
    shapes.append(('black', polys(d['items']), f"clip {[round(v) for v in k]}"))
print(len(shapes), 'outlines')
# a few lines are plain strokes (See & Ski / EZ Road, West Village Traverse, Lyman Lane, Timber Road, West Ten Mile,
# Pine Cone Alley): take their runs as centre lines directly. Dashed ones are uphill routes.
strokes = []
for d in p.get_drawings():
    if d['type'] != 's' or not d.get('color') or (d.get('width') or 0) < 1.0 or d.get('dashes') not in (None, '[] 0'):
        continue
    cls = COL.get(tuple(round(v, 2) for v in d['color']))
    r = d['rect']
    if not cls or max(r.width, r.height) < 8 or d['seqno'] == 4945:
        continue  # 4945: the Log Chute kids' zone outline (a marker at its label instead)
    for pl in polys(d['items']):
        strokes.append((cls, pl, f"stroke {d['seqno']}"))
print(len(strokes), 'stroke runs')

pieces = []
for cls, pls, src in shapes:
    pls = [pl for pl in pls if len(pl) >= 3]
    if not pls:
        continue  # a fill made only of rectangles (sign boxes)
    xs = [x for pl in pls for x, y in pl]; ys = [y for pl in pls for x, y in pl]
    ox, oy = min(xs) - 2, min(ys) - 2
    w, h = int((max(xs) - ox + 2) * R) + 1, int((max(ys) - oy + 2) * R) + 1
    mask = Image.new('1', (w, h), 0)
    for pl in pls:
        m = Image.new('1', (w, h), 0)
        ImageDraw.Draw(m).polygon([((x - ox) * R, (y - oy) * R) for x, y in pl], fill=1)
        mask = Image.frombytes('1', (w, h), bytes(a ^ b for a, b in zip(mask.tobytes(), m.tobytes())))
    sk = thin(np.array(mask, dtype=np.uint8))
    adj = prune(graph(sk), 2.5 * R)  # spurs under 2.5 pt are thinning artefacts at caps and corners
    for ln in trace(adj):
        pts = [(x / R + ox, y / R + oy) for y, x in ln]
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        if length < 3:
            continue
        pieces.append({'cls': cls, 'src': src, 'pt': simplify(pts, 0.25), 'len': length})
for cls, pl, src in strokes:
    length = sum(math.dist(a, b) for a, b in zip(pl, pl[1:]))
    if length >= 3:
        pieces.append({'cls': cls, 'src': src, 'pt': simplify(pl, 0.25), 'len': length})
BOXES = [(362.9, 284.6, 446.3, 310.6)]  # the COPPER MOUNTAIN peak label, printed over Boulderado's lower end


def outside_end(pts, box):
    """Cut off the part of a polyline that runs on into a label box at either end."""
    inside = lambda q: box[0] <= q[0] <= box[2] and box[1] <= q[1] <= box[3]  # noqa: E731
    for _ in (0, 1):
        if inside(pts[-1]):
            k = max(i for i, q in enumerate(pts) if not inside(q))
            a, b = pts[k], pts[k + 1]
            lo, hi = 0.0, 1.0
            for _ in range(30):  # bisect for the box edge
                m = (lo + hi) / 2
                lo, hi = (m, hi) if not inside((a[0] + m * (b[0] - a[0]), a[1] + m * (b[1] - a[1]))) else (lo, m)
            pts = pts[:k + 1] + [(a[0] + lo * (b[0] - a[0]), a[1] + lo * (b[1] - a[1]))]
        pts = pts[::-1]
    return pts


for q in pieces:
    for box in BOXES:
        if any(box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in q['pt']):
            q['pt'] = outside_end(q['pt'], box)
            q['len'] = sum(math.dist(a, b) for a, b in zip(q['pt'], q['pt'][1:]))
print(len(pieces), 'pieces')
x0, y0, x1, y1 = CLIP; S = 3.0
out = []
for i, q in enumerate(pieces):
    out.append({'id': i, 'cls': q['cls'], 'lengthPx': round(q['len'] * S),
                'points': [[round(100 * (x - x0) / (x1 - x0), 2), round(100 * (y - y0) / (y1 - y0), 2)] for x, y in q['pt']]})
json.dump({'_source': 'Copper Mountain 2025-26 PDF: centre lines of the outlined trail lines (lines.py)', 'polylines': out},
          open(os.path.join(DATA, 'linePolylines.json'), 'w'))
json.dump([{'id': i, 'src': q['src']} for i, q in enumerate(pieces)], open(work('piece_src.json'), 'w'))
import collections
print(collections.Counter(q['cls'] for q in pieces))
