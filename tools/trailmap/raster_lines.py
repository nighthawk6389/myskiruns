"""Trail lines from a raster trail map (no vector PDF; Vail's three panels): per colour class (green, blue, black),
a strict colour mask; text glyphs, icon bits and sign-box outlines dropped; dashed roads linked by growing their
marks (dashes and direction arrows) until consecutive ones merge; then a 1 px skeleton traced into pieces, joined
straight through junctions (a crossing yields two through pieces).

    python3 tools/trailmap/raster_lines.py --image panel.png --out lines.json \\
        --exclude 45,1620,990,1980 --k 1.75 --text-max 75 [--debug mask.png]

--exclude boxes blank legends, insets and logos. --k scales the mark sizes (a panel drawn with bigger symbols and
dashes: Vail's Back Bowls 1.75, Blue Sky 2.7); --text-max is the largest glyph (px) to treat as text. Yellow sign
boxes (WILDLIFE HABITAT) are found and blanked automatically. Writes {_source, polylines:[{id, cls, lengthPx,
points}]} in percent of the image, like extract_pdf_vectors.py. The colour masks are tuned to Vail's 2025-26
palette (--palette steamboat: Steamboat's 2026-27); check them on a new map (--debug draws what each class kept).

Requires: pip install pillow numpy opencv-python-headless scikit-image
"""
import argparse, collections, json, math
import numpy as np, cv2
from PIL import Image
from skimage.morphology import skeletonize

Image.MAX_IMAGE_PIXELS = None


def masks(A, palette='vail'):
    r, g, b = (A[..., i].astype(np.int16) for i in range(3))
    mx = A.max(2).astype(np.int16); mn = A.min(2).astype(np.int16)
    if palette == 'steamboat':  # Steamboat's 2026-27 map: a darker blue (53, 94, 153) and green (32, 145, 83)
        return {
            'blue': (b > 115) & (b - r > 60) & (b - g > 35) & (r < 110) & (g < 140),
            'green': (g > 110) & (g - r > 70) & (g - b > 30) & (r < 100),
            'black': (mx < 60) & (mx - mn < 25) & (g - r < 12),
        }
    return {
        'blue': (r < 40) & (g > 120) & (g < 185) & (b > 190) & (b - g > 40),
        'green': (r < 50) & (g > 130) & (g < 200) & (b < 120) & (g - b > 50) & (g - r > 100),
        'black': (mx < 70) & (mx - mn < 25) & (g - r < 12),
    }


def pca_dir(xs, ys):
    x = xs - xs.mean(); y = ys - ys.mean()
    cxx, cyy, cxy = (x * x).mean(), (y * y).mean(), (x * y).mean()
    tr, det = cxx + cyy, cxx * cyy - cxy * cxy
    l1 = tr / 2 + math.sqrt(max(0, tr * tr / 4 - det)); l2 = tr / 2 - math.sqrt(max(0, tr * tr / 4 - det))
    ang = 0.5 * math.atan2(2 * cxy, cxx - cyy)
    return (math.cos(ang), math.sin(ang)), math.sqrt(l1 / max(l2, 1e-6))


def clean(m, excludes, k=1.0, text_max=36, min_extent=26):
    """Line pixels of one colour class. Long components stay, except text (glyph-sized parts crowded by other
    glyphs) and sign-box outlines. Dashed roads are small marks standing alone on their white casing (dashes,
    direction arrows): grown by about half a gap so consecutive marks merge, and kept where the merged run is
    long and holds several marks. k scales the mark sizes (the back-bowls and blue-sky panels draw them bigger)."""
    m = m.copy()
    for x0, y0, x1, y1 in excludes:
        m[y0:y1, x0:x1] = False
    dash_max, dash_area, arrow_max = 16 * k, 90 * k * k, 36 * k
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    ext_all = np.maximum(st[:, 2], st[:, 3])
    aspect = st[:, 2] / np.maximum(st[:, 3], 1)
    # difficulty symbols (square, diamond, circle): squarish and solid; condensed letters are tall and narrow
    symbol = (st[:, 4] > 0.48 * st[:, 2] * st[:, 3]) & (aspect >= 0.75) & (aspect <= 1.33) & (ext_all >= 12) & (ext_all <= 40 * k)
    keep = np.zeros(n, bool)
    mark = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w, h, area = st[i]
        ext = max(w, h)
        if ext < 4 or area < 6:
            continue
        g = int(round(max(4, 4 * k)))
        win = lab[max(0, y - g):y + h + g, max(0, x - g):x + w + g]
        alone = not np.any((win != 0) & (win != i))  # (letters sit closer together than road dashes)
        fill = area / (w * h)
        if alone and ((ext <= dash_max and area <= dash_area) or (ext <= arrow_max and fill < 0.5)):
            mark[i] = True  # a dash, or a road's direction arrow (hollow triangle)
            continue
        if ext <= dash_max and area <= dash_area:
            continue  # glyph-sized and crowded: a letter
        if ext < text_max:
            g = int(round(max(5, 4 * k)))
            win = lab[max(0, y - g):y + h + g, max(0, x - g):x + w + g]
            nbs = [j for j in np.unique(win) if j not in (0, i) and not symbol[j]]
            ys, xs = np.nonzero(lab[y:y + h, x:x + w] == i)
            _, elong = pca_dir(xs.astype(float), ys.astype(float))
            # a letter of a word has another glyph-sized part close by; a short straight stretch of line beside a
            # symbol or a label is much thinner for its length than any letter (I, l are about 8:1)
            if elong < 11 and any(0.25 * ext <= ext_all[j] <= 4 * ext for j in nbs):
                continue
        squarish = 0.6 <= w / h <= 1.6
        if ext >= min_extent and not (ext < 40 * k and squarish and area > 0.45 * w * h):  # (a filled square: icon)
            if w > 20 and h > 12:  # a box outline (sign border): nearly all pixels on the bbox border
                ys, xs = np.nonzero(lab[y:y + h, x:x + w] == i)
                border = ((xs < 3) | (xs >= w - 3) | (ys < 3) | (ys >= h - 3)).mean()
                if border > 0.9:
                    continue
            keep[i] = True
    out = keep[lab]
    marks = mark[lab]
    r = int(round(7 * k))
    grown = cv2.dilate(marks.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    ng, labg, stg, _ = cv2.connectedComponentsWithStats(grown, connectivity=8)
    count = np.bincount(labg[marks & (labg > 0)], minlength=ng) if marks.any() else np.zeros(ng, int)
    # number of distinct marks per grown run
    members = {}
    for i in np.nonzero(mark)[0]:
        g = labg[int(round(cen[i][1])), int(round(cen[i][0]))]
        members[g] = members.get(g, 0) + 1
    good = np.zeros(ng, bool)
    for g in range(1, ng):
        if members.get(g, 0) >= 4 and max(stg[g, 2], stg[g, 3]) >= 70 * k:
            good[g] = True
    # the run's centre band: grown marks thinned back to about a line width
    band = good[labg] & (cv2.dilate(marks.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) | good[labg])
    out = out | band
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(out.astype(np.uint8), connectivity=8)
    big = np.zeros(n2, bool)
    big[1:] = np.maximum(st2[1:, 2], st2[1:, 3]) >= min_extent
    return big[lab2]


NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def graph(sk):
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
    while True:
        removed = False
        for q in [q for q, n in adj.items() if len(n) == 1]:
            if q not in adj or len(adj[q]) != 1:
                continue
            path = [q]; prev, cur = None, q
            while True:
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


def edges(adj):
    nodes = {q for q, n in adj.items() if len(n) != 2}
    used = set(); out = []
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
            out.append(path)
    covered = {q for e in out for q in e}
    for q in adj:  # loops with no node
        if q in covered or q in nodes:
            continue
        path = [q]; prev, cur = None, q
        while True:
            nxt = [t for t in adj[cur] if t != prev and t not in path[-2:]]
            if not nxt or nxt[0] == q:
                break
            prev, cur = cur, nxt[0]; path.append(cur)
        covered.update(path); out.append(path + [q])
    return out, nodes


def tangent(path, at_start, win=12):
    p = path if at_start else path[::-1]
    a = np.array(p[0], float); b = np.array(p[min(win, len(p) - 1)], float)
    v = b - a; L = np.linalg.norm(v) or 1
    return v / L  # pointing away from the node into the edge


def through_pieces(eds, nodes, contract=8):
    """Join edges through junctions by the straightest continuation (turn < ~35 deg)."""
    # junction clusters: nodes joined by edges shorter than `contract` act as one node
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    short = set()
    for k, e in enumerate(eds):
        if len(e) < contract and e[0] in nodes and e[-1] in nodes and e[0] != e[-1]:
            parent[find(e[0])] = find(e[-1]); short.add(k)
    ends = {}  # cluster -> [(edge index, at_start)]
    for k, e in enumerate(eds):
        if k in short:
            continue
        for at_start, q in ((True, e[0]), (False, e[-1])):
            if q in nodes:
                ends.setdefault(find(q), []).append((k, at_start))
    pair = {}
    for c, lst in ends.items():
        if len(lst) < 2:
            continue
        cands = []
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                (ki, si), (kj, sj) = lst[i], lst[j]
                if ki == kj:
                    continue
                d = float(np.dot(tangent(eds[ki], si), tangent(eds[kj], sj)))
                cands.append((d, i, j))
        taken = set()
        for d, i, j in sorted(cands):
            if d > -0.82:
                break
            if i in taken or j in taken:
                continue
            taken.add(i); taken.add(j)
            pair[lst[i]] = lst[j]; pair[lst[j]] = lst[i]
    seen = set(); pieces = []
    for k in range(len(eds)):
        if k in short or k in seen:
            continue
        # walk to one end of the chain
        cur, at_start = k, True
        visited = {k}
        while (cur, at_start) in pair:
            nk, ns = pair[(cur, at_start)]
            if nk in visited:
                break
            visited.add(nk); cur, at_start = nk, not ns
        # now walk forward from (cur, at_start)
        chain = []; c, s = cur, at_start; vis2 = set()
        while True:
            if c in vis2:
                break
            vis2.add(c); seen.add(c)
            e = eds[c] if s else eds[c][::-1]
            chain.extend(e if not chain else e[1:])
            nxt = pair.get((c, not s))
            if not nxt or nxt[0] in vis2:
                break
            c, s = nxt[0], nxt[1]
        pieces.append(chain)
    return pieces


def simplify(pts, eps):
    if len(pts) < 3:
        return pts
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


def sign_boxes(A, pad=8):
    """Yellow sign boxes (WILDLIFE HABITAT / NO ACCESS): their black borders and text are not trail lines."""
    r, g, b = (A[..., i].astype(np.int16) for i in range(3))
    yellow = (r > 235) & (g > 185) & (g < 230) & (b > 40) & (b < 110)
    n, lab, st, _ = cv2.connectedComponentsWithStats(yellow.astype(np.uint8), connectivity=8)
    return [(int(x - pad), int(y - pad), int(x + w + pad), int(y + h + pad)) for x, y, w, h, a in st[1:]
            if w > 60 and h > 25 and a > 0.5 * w * h]


def run(png, excludes, out, debug=None, min_len=30, text_max=36, k=1.0, source=None, palette='vail'):
    A = np.asarray(Image.open(png).convert('RGB'))
    H, W = A.shape[:2]
    boxes = sign_boxes(A, pad=int(round(6 * k)))
    excludes = list(excludes) + boxes
    res = []
    dbg = np.full((H, W, 3), 255, np.uint8) if debug else None
    for cls, m in masks(A, palette).items():
        cm = clean(m, excludes, k=k, text_max=text_max)
        sk = skeletonize(cm)
        adj = prune(graph(sk), 12)
        eds, nodes = edges(adj)
        for ch in through_pieces(eds, nodes):
            pts = [(x, y) for y, x in ch]
            L = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
            if L < min_len:
                continue
            res.append((cls, simplify(pts, 1.2), L))
        if debug is not None:
            dbg[cm] = {'blue': (120, 170, 255), 'green': (120, 220, 120), 'black': (150, 150, 150)}[cls]
    doc = {'_source': source or f'{png}: colour masks, linked dashes, skeleton pieces (tools/trailmap/raster_lines.py)',
           'polylines': [{'id': i, 'cls': c, 'lengthPx': round(L),
                          'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in pts]}
                         for i, (c, pts, L) in enumerate(res)]}
    json.dump(doc, open(out, 'w'))
    if debug is not None:
        Image.fromarray(dbg).save(debug)
    print(out, len(res), 'pieces', dict(collections.Counter(c for c, _, _ in res)), f'({len(boxes)} sign boxes blanked)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True, help='the map raster (lossless)')
    ap.add_argument('--out', required=True, help='output: line pieces json')
    ap.add_argument('--exclude', action='append', default=[], help='x0,y0,x1,y1 to blank (legend, inset, logo)')
    ap.add_argument('--k', type=float, default=1.0, help='scale of symbols and dashes relative to Vail Front Side')
    ap.add_argument('--text-max', type=int, default=36, help='largest glyph extent (px) to treat as text')
    ap.add_argument('--min-len', type=int, default=30, help='shortest piece kept (px)')
    ap.add_argument('--palette', default='vail', choices=['vail', 'steamboat'],
                    help="the colour masks: Vail's 2025-26 palette, or Steamboat's 2026-27")
    ap.add_argument('--debug', help='write the kept line pixels per class here')
    ap.add_argument('--source', help='text for the _source field')
    a = ap.parse_args()
    ex = [tuple(int(v) for v in e.split(',')) for e in a.exclude]
    run(a.image, ex, a.out, debug=a.debug, min_len=a.min_len, text_max=a.text_max, k=a.k, source=a.source,
        palette=a.palette)


if __name__ == '__main__':
    main()
