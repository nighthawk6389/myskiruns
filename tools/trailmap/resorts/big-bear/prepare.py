"""Big Bear Mountain Resort: each panel's map image, line pieces, printed names and symbols, for
tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/big-bear/prepare.py      # regen.sh runs it

The resort publishes its 2025-26 trail maps as images only (Snow Summit 2500x1859, Bear Mountain 2500x1770, Snow
Valley 1965x2400: James Niehues's paintings), and an interactive map of each (resorts-interactive.com maps 1818, 1808,
1825) whose SVG draws the same painting with, per run, a group named after it holding its symbols' fills and a line
(tools/trailmap/vicomap.py parse --detail): the symbols land on the prints' own, but the lines are an older drawing,
and the names' letters aren't in the groups.

- Images: the prints, as they are (each panel's resort.CLIP is the whole image, 1 px per unit). Snow Valley's
  interactive map is its painting and an inset of the summit drawn bigger; only the painting is registered (its
  summit is the print's too) and the inset's copies of lines and symbols are left out.
- Symbols: per group, its fills shaped like one at the panel's symbol size (SIZE): four straight sides about as wide
  as tall a square (blue), a ring of twelve straight sides (or four, filled black) taller than wide a diamond, two
  diamonds side by side a double diamond, four curves a circle (green); a symbol drawn as a fill and its white ring
  is one. Each is placed by the panel's VICOMAP_AFFINE (register_pages.py --ref on the interactive map's painting).
  names.py adds the symbols of the runs with no group.
- Labels: one per printed symbol, at it (the name is printed by its symbol), carrying its group's name; names.py's
  for the names in no group (at the label's middle).
- Lines: Snow Summit's from its print (colour masks per class, MASKS; text, symbols and icons left out; skeleton
  pieces through junctions: tools/trailmap/raster_lines.py's clean() and tracing), named by pdf_resort.py from the
  symbol at each run's top (decisions.py settles the rest). Bear Mountain's and Snow Valley's prints draw no lines:
  the interactive map's line of each group, as it is, carrying its group's name (resort.GROUPED), the way Mammoth's
  are (and, in pdf_resort.py, the stretch along the printed name where a run has no group or a stub of a line:
  each panel's LABEL_LINE).

Writes, per panel in $BIG_BEAR_WORK/<panel> (default work/big-bear): map.png, pieces.json, printed.json ({labels,
symbols}, map px).
"""
import importlib.util
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
sys.path.insert(0, T)
import names  # noqa: E402
from vicomap import dense_pts  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.abspath(os.environ.get('BIG_BEAR_WORK', os.path.join(REPO, 'work/big-bear')))
# per panel: the print, its interactive map, how its lines are drawn ('print': detected on it; 'vicomap': the
# interactive map's), the symbols' size range in SVG units (the larger side), the SVG's x beyond which its inset
# lies (None: no inset), and whether the groups' symbols are the print's (Snow Valley's interactive map is an older
# edition: its names and symbols are read on the print instead, names.py)
SOURCES = {'snow-summit': ('snow-summit_2025-26.webp', 'vicomap-1818', 'print', (28, 66), None, True),
           'bear-mountain': ('bear-mountain_2025-26.jpg', 'vicomap-1808', 'vicomap', (18, 40), None, True),
           'snow-valley': ('snow-valley_2025-26.png', 'vicomap-1825', 'vicomap', (50, 95), 3083, False)}
LINE_CLS = {'blue': 'blue', 'green': 'green', 'black': 'black', 'double-black': 'black'}


def panel_resort(panel):
    spec = importlib.util.spec_from_file_location(f'big_bear_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    return R


def image(panel):
    out = os.path.join(ROOT, panel, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        Image.open(os.path.join(ROOT, SOURCES[panel][0])).convert('RGB').save(out)
    return out


def parse(panel):
    d = os.path.join(ROOT, SOURCES[panel][1])
    p = subprocess.run(['python3', '-I', os.path.join(T, 'vicomap.py'), 'parse', d, '--detail'],
                       capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stdout + p.stderr)
    print(f'  {panel}:', p.stdout.splitlines()[0])
    return json.load(open(os.path.join(d, 'trails.json')))


def centre(b):
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def symbol_kind(f, size):
    """A group's fill as a symbol: 'square', 'diamond', 'circle', or None (a letter, a park's pill, a big halo)."""
    w, h = f['box'][2] - f['box'][0], f['box'][3] - f['box'][1]
    if not size[0] <= max(w, h) <= size[1]:
        return None
    first = f['cmds'].replace('m', 'M').split('M')[1].strip('Zz')
    if first == 'llll' and 0.8 <= w / h <= 1.25:
        return 'square'
    if (first == 'llllllllllll' or (first == 'llll' and f['fill'] == '#231f20')) and 1.2 <= h / w <= 1.9:
        return 'diamond'
    if set(first) <= {'c', 'l'} and first.count('c') >= 4 and first.count('l') <= 1 and 0.85 <= w / h <= 1.18:
        return 'circle'
    return None


def symbols(panel, V, R):
    """[(kind, (x, y) map px, group name)]: each group's printed symbols."""
    a, b, c, d, e, f = R.VICOMAP_AFFINE
    size, inset = SOURCES[panel][3], SOURCES[panel][4]
    out = []
    for t in V['trails']:
        found = []  # (kind, centre in SVG units, width)
        for q in t['fills']:
            k = symbol_kind(q, size)
            cq = centre(q['box'])
            if not k or (inset and cq[0] > inset):
                continue
            if any(math.dist(cq, o[1]) < 6 for o in found):
                continue  # a symbol's fill and its white ring
            found.append((k, cq, q['box'][2] - q['box'][0]))
        used = set()
        for i, (k, cq, w) in enumerate(found):
            if i in used:
                continue
            kind = k
            if k == 'diamond':  # two diamonds side by side: a double diamond
                j = next((j for j, (k2, c2, _w) in enumerate(found) if j != i and j not in used and k2 == 'diamond'
                          and abs(c2[1] - cq[1]) < 0.3 * w and abs(c2[0] - cq[0]) < 1.6 * w), None)
                if j is not None:
                    used.add(j)
                    cq = ((cq[0] + found[j][1][0]) / 2, cq[1])
                    kind = 'double-diamond'
            used.add(i)
            out.append((kind, (a * cq[0] + b * cq[1] + c, d * cq[0] + e * cq[1] + f), t['name']))
    return out


def printed(panel, V, R):
    syms = symbols(panel, V, R) if SOURCES[panel][5] else []
    syms += [(k, xy, n) for k, xy, n in names.SYMBOLS.get(panel, [])]
    read = {e[0] for e in names.LABELS.get(panel, [])}
    labs = []
    for g, (_k, (x, y), name) in enumerate(syms):
        if name not in read:  # a label at the symbol (the name is printed by it)
            labs.append({'seq': g, 'text': name, 'color': None, 'pts': [[round(x, 1), round(y, 1)]],
                         'c': [round(x, 1), round(y, 1)]})
    # names.py's labels, each from its first letter to its last (about one point per 18 px)
    for k, (name, first, last) in enumerate(names.LABELS.get(panel, [])):
        n = max(4, round(math.dist(first, last) / 18))
        pts = [(first[0] + (last[0] - first[0]) * i / (n - 1), first[1] + (last[1] - first[1]) * i / (n - 1))
               for i in range(n)]
        labs.append({'seq': 10000 + k, 'text': name, 'color': None,
                     'pts': [[round(x, 1), round(y, 1)] for x, y in pts],
                     'c': [round(sum(p[0] for p in pts) / len(pts), 1), round(sum(p[1] for p in pts) / len(pts), 1)]})
    out = {'labels': labs, 'symbols': [{'t': k, 'c': [round(x, 1), round(y, 1)], 'group': n} for k, (x, y), n in syms]}
    json.dump(out, open(os.path.join(ROOT, panel, 'printed.json'), 'w'), indent=0)
    by = {}
    for k, _xy, _n in syms:
        by[k] = by.get(k, 0) + 1
    print(f'  {panel}: {len(labs)} labels, {len(syms)} symbols {by}')


def masks(png):
    """Snow Summit's line colours: blue (about 0, 160, 225), green (about 20, 145, 70), black; the lifts are red."""
    A = np.asarray(Image.open(png).convert('RGB')).astype(np.int16)
    r, g, b = A[..., 0], A[..., 1], A[..., 2]
    mx, mn = A.max(2), A.min(2)
    return {'blue': (b > 150) & (b - r > 90) & (b - g > 25) & (r < 110),
            'green': (g > 90) & (g - r > 45) & (g - b > 15) & (r < 110),
            'black': (mx < 70) & (mx - mn < 30)}


def lines_only(cm, black_runs):
    """The black mask less the painting's trees (dark strokes too): a run's line is one long thin component (its
    two farthest points 60 px or more apart, under 7 px wide on average, its skeleton no more than three times as
    long as that: a tree crown's is tangled) near an interactive-map black run's line (within NEAR px: they lie up
    to 25 px off the print's)."""
    import collections
    import cv2
    from scipy.spatial import cKDTree
    from skimage.morphology import skeletonize
    n, lab, st, _ = cv2.connectedComponentsWithStats(cm.astype(np.uint8), connectivity=8)
    sk = skeletonize(cm)
    pts = collections.defaultdict(list)
    for y, x in zip(*np.nonzero(sk)):
        pts[lab[y, x]].append((x, y))
    tree = cKDTree(black_runs)
    keep = np.zeros(n, bool)
    for i, p in pts.items():
        if i == 0:
            continue
        p = np.array(p, float)
        a = p[np.linalg.norm(p - p.mean(0), axis=1).argmax()]
        b = p[np.linalg.norm(p - a, axis=1).argmax()]
        span = np.linalg.norm(a - b)
        if span < 60 or st[i, 4] / span > 7 or len(p) > 3 * span or np.median(tree.query(p)[0]) > NEAR:
            continue
        keep[i] = True
    return keep[lab]


NEAR = 50


def print_lines(panel, png, R, V):
    """The print's own lines: raster_lines.py's clean() (text, symbols, icons out) and skeleton pieces; black only
    where lines_only() keeps it."""
    import collections
    from skimage.morphology import skeletonize
    import raster_lines as rl
    M = masks(png)
    H, W = M['blue'].shape
    a, b, c, d, e, f = R.VICOMAP_AFFINE
    black_runs = [(a * q[0] + b * q[1] + c, d * q[0] + e * q[1] + f) for t in V['trails']
                  if LINE_CLS.get(t['rating']) == 'black' for pl in t['lines'] for q in dense_pts(pl, 4.0)]
    res = []
    for cls, m in M.items():
        cm = rl.clean(m, getattr(R, 'EXCLUDE', []), k=1.0, text_max=R.TEXT_MAX)
        if cls == 'black':
            cm = lines_only(cm, black_runs)
        adj = rl.prune(rl.graph(skeletonize(cm)), 12)
        eds, nodes = rl.edges(adj)
        for ch in rl.through_pieces(eds, nodes):
            pts = [(x, y) for y, x in ch]
            L = sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
            if L >= R.MIN_LEN:
                res.append((cls, rl.simplify(pts, 1.2), L))
    out = [{'id': i, 'cls': c, 'lengthPx': round(L),
            'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in pts]} for i, (c, pts, L) in enumerate(res)]
    print(f'  {panel}: {len(out)} pieces from the print {dict(collections.Counter(p["cls"] for p in out))}')
    return out


def vicomap_lines(panel, V, R, png):
    """The interactive map's line of each group, as it is (the print draws none), and names.py's."""
    a, b, c, d, e, f = R.VICOMAP_AFFINE
    inset = SOURCES[panel][4]
    H, W = np.asarray(Image.open(png)).shape[:2]
    raw = []
    for t in V['trails']:
        for pl in t['lines']:
            if inset and min(q[0] for q in pl) > inset:
                continue  # the summit inset's copy
            raw.append((t['name'], LINE_CLS.get(t['rating'], 'blue'), [(a * q[0] + b * q[1] + c, d * q[0] + e * q[1] + f) for q in pl]))
    raw += [(n, cls, list(pts)) for n, cls, pts in names.LINES.get(panel, [])]
    out = []
    for name, cls, pts in raw:
        if sum(math.dist(p, q) for p, q in zip(pts, pts[1:])) < 6:
            continue
        import raster_lines as rl
        pts = rl.simplify(dense_pts(pts, 1.0), 1.0)
        out.append({'id': len(out), 'cls': cls, 'name': name,
                    'lengthPx': round(sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))),
                    'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in pts]})
    print(f'  {panel}: {len(out)} lines from the interactive map')
    return out


def main():
    for panel, (_img, _v, mode, _s, _i, _g) in SOURCES.items():
        os.makedirs(os.path.join(ROOT, panel), exist_ok=True)
        R = panel_resort(panel)
        png = image(panel)
        V = parse(panel)
        printed(panel, V, R)
        P = print_lines(panel, png, R, V) if mode == 'print' else vicomap_lines(panel, V, R, png)
        json.dump({'_source': R.SOURCE, 'polylines': P}, open(os.path.join(ROOT, panel, 'pieces.json'), 'w'))


if __name__ == '__main__':
    main()
