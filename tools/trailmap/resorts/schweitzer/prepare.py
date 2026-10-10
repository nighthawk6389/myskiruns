"""Schweitzer: each panel's map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/schweitzer/prepare.py      # regen.sh runs it

The resort publishes its 2025-26 trail maps as images only (schweitzer.com's maps page; James Niehues's paintings):
Schweitzer Bowl at 3300x2550 (letter size at 300 dpi), Outback Bowl at 1920x1484 only; skimap.org's map 30575 is
the 2024-25 Outback Bowl at 3300x2550, the same artwork (checked against the 2025-26 image: no name, line or symbol
differs; tools/archive/schweitzer/editions.py), and is used for its resolution. The runs are painted slopes: a name
printed along each, its symbol by it, and no line, but for the cat tracks (navy lines). The resort's interactive maps
(resorts-interactive.com maps 1826, the front, and 1827, Outback Bowl) draw the same paintings, with each name's
letters (white fills) and symbol in a group named after the run (the trail report's names, the upper and lower
parts of a run apart), and the front's cat tracks as lines (tools/trailmap/vicomap.py parse --detail).

- Images: the prints, as they are (the panel's resort.CLIP is the whole image, 1 px per unit).
- Labels: per group, its letters in drawing order, split where they jump (another printing of the name), moved onto
  a smooth curve through them (a name set in two sizes zigzags), on the print by the panel's VICOMAP_AFFINE (registered on the interactive map's painting: register_pages.py --ref); and
  names.py's labels, for the groups with no letters (most of Outback Bowl's black runs) and the names in no group
  (the parks), each from its first letter to its last (and the points between it gives). Each label's colour is its
  group's rating (resort.COLOR_SYMBOL: the rating when no symbol is printed by it).
- Symbols: per group, its fills shaped like one (a square or a diamond: four sides; a circle: curves), coloured
  blue, black or green; two black ones side by side are a double diamond. The Outback map's groups have no black
  ones: names.py's, read on crops, and those of the front its groups lack.
- Lines: the cat tracks, the front's from the interactive map's lines and the others from names.py's waypoints,
  each routed along the print's own navy line (route(): the cheapest path through its pixels between points along
  it, each moved onto the line first), carrying its trail's name (resort.GROUPED).

Writes, per panel in $SCHWEITZER_WORK/<panel> (default work/schweitzer): map.png, pieces.json, printed.json
({labels, symbols}, map px).
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
from resort import REPORT  # noqa: E402
from vicomap import dense_pts  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.abspath(os.environ.get('SCHWEITZER_WORK', os.path.join(REPO, 'work/schweitzer')))
SOURCES = {'schweitzer-bowl': ('schweitzer-bowl_2025-26.jpg', 'vicomap-1826'),
           'outback-bowl': ('outback-bowl_2024-25.webp', 'vicomap-1827')}
NAVY = (44, 49, 146)  # the cat tracks' line colour on the prints
SYMBOL = {'#0071bc': 'blue', '#0071bb': 'blue', '#231f20': 'black', '#00a650': 'green'}
WHITE = ('#fff', '#ffffff')
RATING = {'Green': 'green', 'Blue': 'blue', 'Black': 'black', 'DoubleBlack': 'double-black'}  # the report's
OFF = 40.0  # route(): cost per px off the navy line


def panel_resort(panel):
    spec = importlib.util.spec_from_file_location(f'schweitzer_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
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


def symbol_shape(f):
    """A difficulty symbol's fill: one outline of four straight sides (a square, a diamond) or of curves only (a
    circle), about as wide as tall, 20 to 70 units; else None (a letter, a park's pill)."""
    w, h = f['box'][2] - f['box'][0], f['box'][3] - f['box'][1]
    if f['parts'] != 1 or min(w, h) < 0.6 * max(w, h) or not 20 <= max(w, h) <= 70:
        return False
    body = f['cmds'].strip('MZmz')
    return body in ('llll', 'lll') or (set(body) == {'c'} and 4 <= len(body) <= 8)


def inside(a, b, pad=0.5):
    return a[0] >= b[0] - pad and a[1] >= b[1] - pad and a[2] <= b[2] + pad and a[3] <= b[3] + pad


def split_parts(fills):
    """A fill of a few outlines (two diamonds drawn as one path) as one fill per outline."""
    out = []
    for q in fills:
        cmds = [c for c in q['cmds'].replace('m', 'M').split('M') if c]
        if (SYMBOL.get(q['fill']) and q.get('part_boxes') and len(cmds) == len(q['part_boxes'])
                and all(c.strip('Zz') == 'llll' for c in cmds)):  # each outline four-sided: symbols, not letters
            out += [{**q, 'box': bx, 'parts': 1, 'cmds': 'M' + c} for bx, c in zip(q['part_boxes'], cmds)]
        else:
            out.append(q)
    return out


def smooth(pts):
    """A label's letter centres moved onto a smooth curve through them (a parabola along the text's main axis): a
    name set in two sizes (DOWN THE HATCH's small THE, raised) would zigzag."""
    if len(pts) < 4:
        return pts
    a = np.array(pts, float)
    m = a.mean(axis=0)
    u = np.linalg.svd(a - m)[2][0]  # the main axis
    v = np.array([-u[1], u[0]])
    s, t = (a - m) @ u, (a - m) @ v
    c = np.polyfit(s, t, 2 if len(pts) >= 6 else 1)
    return [tuple(m + si * u + np.polyval(c, si) * v) for si in s]


def labels(panel, V, R):
    a, b, c, d, e, f = R.VICOMAP_AFFINE

    def tf(p):
        return (a * p[0] + b * p[1] + c, d * p[0] + e * p[1] + f)
    labs, syms = [], []
    renamed = {k: v[0] for k, v in names.GROUP_NAMES.get(panel, {}).items()}
    no_symbol = names.NO_SYMBOL.get(panel, {})
    for g, t in enumerate(V['trails']):
        t = {**t, 'name': renamed.get(t['name'], t['name']), 'fills': split_parts(t['fills'])}
        if not t['name']:
            continue
        shapes = [q for q in t['fills'] if SYMBOL.get(q['fill']) and symbol_shape(q)]
        groups = []  # a double diamond's two
        for q in shapes:
            for grp in groups:
                size = max(q['box'][2] - q['box'][0], q['box'][3] - q['box'][1])
                if SYMBOL[q['fill']] == SYMBOL[grp[0]['fill']] == 'black' and any(
                        math.dist(centre(o['box']), centre(q['box'])) < 1.6 * size for o in grp):
                    grp.append(q)
                    break
            else:
                groups.append([q])
        for grp in groups if t['name'] not in no_symbol else ():
            cls = SYMBOL[grp[0]['fill']]
            kind = {'green': 'circle', 'blue': 'square'}.get(cls) or ('double-diamond' if len(grp) > 1 else 'diamond')
            xs = [q['box'][i] for q in grp for i in (0, 2)]
            ys = [q['box'][i] for q in grp for i in (1, 3)]
            p = tf(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2))
            syms.append({'t': kind, 'c': [round(p[0], 1), round(p[1], 1)], 'group': t['name']})
        # its letters: coloured fills that are no symbol (the glades' brown, The Great Divide's grey), else the white
        # ones that are no symbol's or pill's halo
        others = [q for q in t['fills'] if q not in shapes]
        letters = [q for q in others if q['fill'] not in WHITE]
        if not letters or len(letters) < 3:
            letters = [q for q in others if q['fill'] in WHITE
                       and not any(inside(o['box'], q['box']) for o in t['fills'] if o is not q and o['fill'] not in WHITE)]
        runs, run = [], []
        for q in letters:  # drawing order is reading order; a jump starts another printing of the name
            hgt = max(q['box'][3] - q['box'][1], q['box'][2] - q['box'][0])
            if run and math.dist(centre(run[-1]['box']), centre(q['box'])) > 2.5 * hgt:
                runs.append(run)
                run = []
            run.append(q)
        if run:
            runs.append(run)
        for r in runs:
            if len(r) < 2:
                continue
            pts = smooth([tf(centre(q['box'])) for q in r])
            labs.append({'seq': 100 * g + len(labs) % 100, 'text': t['name'], 'color': t['rating'],
                         'pts': [[round(x, 1), round(y, 1)] for x, y in pts],
                         'c': [round(sum(p[0] for p in pts) / len(pts), 1), round(sum(p[1] for p in pts) / len(pts), 1)]})
    # names.py: the labels and symbols the groups lack, each label's letters spread from its first to its last
    # (about one per 18 px), its colour the report's rating (a park's: none)
    rating = {n: RATING.get(r) for n, _a, r in REPORT}
    for k, (name, first, last) in enumerate(names.LABELS.get(panel, [])):
        n = max(4, round(math.dist(first, last) / 18))
        pts = [(first[0] + (last[0] - first[0]) * i / (n - 1), first[1] + (last[1] - first[1]) * i / (n - 1))
               for i in range(n)]
        labs.append({'seq': 10000 + k, 'text': name, 'color': rating.get(name),
                     'pts': [[round(x, 1), round(y, 1)] for x, y in pts],
                     'c': [round(sum(p[0] for p in pts) / len(pts), 1), round(sum(p[1] for p in pts) / len(pts), 1)]})
    for kind, (x, y), group in names.SYMBOLS.get(panel, []):
        syms.append({'t': kind, 'c': [x, y], 'group': group})
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(ROOT, panel, 'printed.json'), 'w'), indent=0)
    by = {}
    for s in syms:
        by[s['t']] = by.get(s['t'], 0) + 1
    print(f'  {panel}: {len(labs)} labels, {len(syms)} symbols {by}')


def navy_mask(png):
    A = np.asarray(Image.open(png).convert('RGB')).astype(float)
    return np.linalg.norm(A - np.array(NAVY), axis=2) < 30  # (looser takes in the trees' dark blue shadows)


def snap(mask, q, r=25):
    """The nearest navy pixel within r px of q (a waypoint read a little off its line: the navy lines are the
    cat tracks only, far apart), else q."""
    x, y = int(round(q[0])), int(round(q[1]))
    x0, y0 = max(0, x - r), max(0, y - r)
    ys, xs = np.nonzero(mask[y0:y + r + 1, x0:x + r + 1])
    if not len(xs):
        return (x, y)
    i = int(np.argmin((xs + x0 - x) ** 2 + (ys + y0 - y) ** 2))
    return (int(xs[i] + x0), int(ys[i] + y0))


def route(mask, waypoints):
    """The cheapest path along the navy line through the waypoints (each moved onto the line first): cost 1 on the
    line's pixels, OFF elsewhere, so it crosses only the gaps where a label or a symbol is printed on the line."""
    import cv2
    from skimage.graph import MCP_Geometric
    cost = np.full(mask.shape, OFF)
    cost[cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)] = 1.0
    H, W = mask.shape
    pts = [snap(mask, q) for q in waypoints]
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        m = int(max(60, 0.5 * math.dist((x0, y0), (x1, y1))))
        bx0, by0 = max(0, min(x0, x1) - m), max(0, min(y0, y1) - m)
        bx1, by1 = min(W, max(x0, x1) + m), min(H, max(y0, y1) + m)
        mcp = MCP_Geometric(cost[by0:by1, bx0:bx1])
        mcp.find_costs([(y0 - by0, x0 - bx0)], [(y1 - by0, x1 - bx0)])
        seg = straight_gaps([(x + bx0, y + by0) for y, x in mcp.traceback((y1 - by0, x1 - bx0))], mask)
        path += seg if not path else seg[1:]
    return rdp(path, 1.5)


def straight_gaps(path, mask):
    """Each run of a path between two waypoints off the line (a gap where a label or symbol is printed on it) as a
    straight segment between the line pixels either side: on a pixel grid many off-line paths cost the same (a
    45-degree stretch and a level one as much as the straight line), and the router picks any."""
    on = [bool(mask[y, x]) for x, y in path]
    on[0] = on[-1] = True  # (the waypoints: a gap's waypoints in it, a label's letters, are kept)
    out, i = [], 0
    while i < len(path):
        if on[i]:
            out.append(path[i])
            i += 1
            continue
        j = i
        while j < len(path) and not on[j]:
            j += 1
        i = j  # path[i - 1 .. j]: drop the points between (a straight segment from the last on-line point to path[j])
    return out


def rdp(pts, tol):
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    n = math.hypot(bx - ax, by - ay) or 1e-9
    d = [abs((by - ay) * (x - ax) - (bx - ax) * (y - ay)) / n for x, y in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] <= tol:
        return [pts[0], pts[-1]]
    return rdp(pts[:i + 2], tol)[:-1] + rdp(pts[i + 1:], tol)


def lines(panel, V, R, png):
    a, b, c, d, e, f = R.VICOMAP_AFFINE
    mask = navy_mask(png)
    H, W = mask.shape
    raw = []  # (name, waypoints in map px)
    for t in V['trails']:
        for pl in t['lines']:
            pts = [(a * q[0] + b * q[1] + c, d * q[0] + e * q[1] + f) for q in pl]
            raw.append((t['name'], dense_pts(pts, 40.0)))  # its line as waypoints every 40 px
    for name, way in names.LINES.get(panel, []):
        raw.append((name, way))
    out = []
    for name, way in raw:
        if sum(math.dist(p, q) for p, q in zip(way, way[1:])) < 10:
            continue
        pts = route(mask, way)
        out.append({'id': len(out), 'cls': 'blue', 'name': name,
                    'lengthPx': round(sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))),
                    'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in pts]})
    json.dump({'_source': f'Schweitzer {panel}: the cat tracks routed on the print\'s navy lines (prepare.py)',
               'polylines': out}, open(os.path.join(ROOT, panel, 'pieces.json'), 'w'))
    print(f'  {panel}: {len(out)} cat-track pieces')


def main():
    for panel in SOURCES:
        os.makedirs(os.path.join(ROOT, panel), exist_ok=True)
        R = panel_resort(panel)
        png = image(panel)
        V = parse(panel)
        labels(panel, V, R)
        lines(panel, V, R, png)


if __name__ == '__main__':
    main()
