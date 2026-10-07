"""Heavenly: the map images, line pieces, printed names and symbols of its two panels, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/heavenly/prepare.py      # regen.sh runs it

Sources (resort.py): the 2024-25 map as an image (scene7.png, 3652 x 4990 px) and the 2022-23 PDF of the same
artwork (heavenly_2022.pdf), whose page is registered on each of the image's two paintings (resort.AFFINE).

Panels (resort.py PANELS and BOX; each one's settings in panels/<panel>/resort.py, its files in work/.../<panel>/):
- main: the California and Nevada sides, the image down to the blue band under the painting.
- top-of-gondola: the Top of Gondola inset below it.

- Images: the panel's part of the image, as it is.
- Lines: the PDF draws every line as a filled outline (the artwork's strokes outlined): the trail routes in blue,
  green and dark (Ellie's, Rim Trail), solid or dashed (one outline per dash). Each outline narrower than the panel's
  lines (SETUP: the main map's are 0.83 pt wide, the inset's 2.7) is read by its centre line (split at its two ends,
  each point of one side paired with the nearest of the other); a dashed line's dashes, drawn one after another in one
  fill, are chained into one piece. Squares, circles and diamonds are wider, arrowheads have a shape of their own (two
  curved sides and a notched back), an outline shorter than the panel's shortest line is a mark (a stray dash), and a
  dark outline is a line only if it is long (the names' letters are dark outlines too; the inset has no dark line). A
  blue or green outline with more area than one line of its length has (two lines drawn as one, or an arrowhead merged
  into its line) is read by its skeleton instead, one piece per branch. A piece lying along a longer one of its colour
  is a copy of it and is dropped.
- Names: dark outlined glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets,
  is in letters.json here). M and W are one shape turned over (--turned WM), and O and zero match each other: a word
  with letters in it takes O, a number zero. Word gaps (pt) per panel: the inset's letters are larger.
- Symbols: blue squares, green circles (drawn with 16 curves), black diamonds; two diamonds one above the other
  (6 to 6.6 pt apart, a diamond 4.9 pt across) are a double diamond.
- What the 2024 image no longer prints where the 2022 page has it (resort.GONE, every changed area checked on the
  image) is left out, and so are the 2022 page's navigation box at its top right (gone from the 2024 map), its
  legend and a sponsor's logo.

Writes, per panel in $HEAVENLY_WORK/<panel> (default work/heavenly): map.png, pieces.json, printed.json ({labels,
symbols}, PDF points); and glyphs.json in $HEAVENLY_WORK.
"""
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('HEAVENLY_WORK', os.path.join(REPO, 'work/heavenly')))
LETTERS = os.path.join(HERE, 'letters.json')
sys.path.insert(0, T)
import raster_lines as RL  # noqa: E402
PDF = os.path.join(ROOT, 'heavenly_2022.pdf')
IMAGE = os.path.join(ROOT, 'scene7.png')

BLUE, GREEN, DARK = (0.0, 0.36, 0.67), (0.0, 0.61, 0.4), (0.14, 0.12, 0.13)
LINES = {'blue': BLUE, 'green': GREEN, 'black': DARK}
DARK_MIN = 25  # pt: a dark outline shorter than this is a letter, not a line
DASH = 5  # pt: an outline shorter than this is a dash (2.8 to 3.6 pt long)
# the 2022 page's navigation box (top right), legend (under the inset, and right of it) and Observation Deck box
# (a sponsor's logo outlined in the names' dark colour): not the map
EXCLUDE = [(820, 0, 1171, 252), (0, 1322, 1171, 1711), (760, 960, 1171, 1711), (655, 585, 725, 665)]
# per panel: the part of the page it shows (pt); its lines' widest outline and shortest solid line (pt: the inset
# draws its lines 2.7 pt wide, and its arrowheads, narrower than that, are short); the word gap of its names (pt);
# its line colours (the inset has no dark line: its dark outlines are letters)
SETUP = {'main': {'page': (0, 0, 1171, 958), 'width': 1.3, 'min': 3, 'space': 1.2,
                  'lines': ('blue', 'green', 'black')},
         'top-of-gondola': {'page': (0, 968, 761, 1323), 'width': 3.0, 'min': 18, 'space': 2.0,
                            'lines': ('blue', 'green')}}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def top():
    spec = importlib.util.spec_from_file_location('heavenly', os.path.join(HERE, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def to_px(A, box, p):
    """PDF points -> px of the panel's image."""
    a, b, c, d, e, f = A
    return (a * p[0] + b * p[1] + c - box[0], d * p[0] + e * p[1] + f - box[1])


def image(panel, box, W):
    out = os.path.join(W, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    Image.open(IMAGE).convert('RGB').crop(box).save(out)


# ---- lines ---------------------------------------------------------------------------------------------------
def pts_of(it):
    if it[0] == 'l':
        return [it[1], it[2]]
    if it[0] == 'c':
        return list(it[1:5])
    if it[0] == 're':
        r = it[1]
        return [r.tl, r.tr, r.br, r.bl]
    q = it[1]
    return [q.ul, q.ur, q.lr, q.ll]


def subpaths(d):
    """A fill's outlines: a new one starts where an item does not start at the last one's end."""
    out, cur, last = [], [], None
    for it in d['items']:
        p = pts_of(it)
        if it[0] in ('re', 'qu'):
            if cur:
                out.append(cur)
                cur = []
            out.append([it])
            last = None
            continue
        if last is not None and abs(p[0].x - last.x) + abs(p[0].y - last.y) > 1e-3:
            out.append(cur)
            cur = []
        cur.append(it)
        last = p[-1]
    if cur:
        out.append(cur)
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
        else:
            pts += [(p.x, p.y) for p in pts_of(it)]
    return pts


def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    return out + [tuple(pts[-1])] if pts else out


def resample(pts, n):
    """n points evenly spaced along a polyline."""
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


def centre(items):
    """An outline's centre line and its median width (pt): the outline split at its two farthest-apart points into
    two sides, each point of one side paired with the nearest point of the other."""
    o = dense(outline(items), 0.25)
    if len(o) > 1 and math.dist(o[0], o[-1]) < 1e-6:
        o = o[:-1]
    n = len(o)
    if n < 4:
        return None, None
    step = max(1, n // 400)
    i, j = max(((i, j) for i in range(0, n, step) for j in range(i + 1, n, step)),
               key=lambda ij: math.dist(o[ij[0]], o[ij[1]]))
    a, b = o[i:j + 1], (o[j:] + o[:i + 1])[::-1]
    if len(a) < 2 or len(b) < 2:
        return None, None
    pairs = [(p, min(b, key=lambda q: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2))
             for p in resample(a, max(8, int(length(a) / 0.5)))]
    ws = sorted(math.dist(p, q) for p, q in pairs)
    return [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in pairs], ws[len(ws) // 2]


def area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def skeleton(items, z=16):
    """A branched outline (two lines drawn as one fill, or an arrowhead merged into its line): its skeleton,
    drawn at z px per pt, spurs under 2.5 pt (an arrowhead's barbs) pruned, joined straight through its junctions
    (tools/trailmap/raster_lines.py): one centre line per branch, in pt."""
    o = outline(items, 16)
    x0, y0 = min(x for x, _ in o) - 1, min(y for _, y in o) - 1
    w, h = int((max(x for x, _ in o) - x0 + 1) * z) + 2, int((max(y for _, y in o) - y0 + 1) * z) + 2
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).polygon([((x - x0) * z, (y - y0) * z) for x, y in o], fill=255)
    eds, nodes = RL.edges(RL.prune(RL.graph(skeletonize(np.ascontiguousarray(np.asarray(im) > 0))), int(2.5 * z)))
    return [[(x0 + c / z, y0 + r / z) for r, c in p] for p in RL.through_pieces(eds, nodes) if len(p) > 1]


def simplify(pts, tol):
    """Ramer-Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    ds = [abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / n if n else math.dist(p, a) for p in pts[1:-1]]
    k = max(range(len(ds)), key=ds.__getitem__)
    if ds[k] <= tol:
        return [a, b]
    return simplify(pts[:k + 2], tol)[:-1] + simplify(pts[k + 1:], tol)


def line_dist(q, pts):
    best = float('inf')
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = dx * dx + dy * dy
        t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
        best = min(best, math.dist(q, (a[0] + t * dx, a[1] + t * dy)))
    return best


def chained(segs):
    """One fill's centre lines, in drawing order, as lines: a dashed line's dashes (each shorter than DASH), one after
    another and each within 3.5 pt of the last (blue dashes are 1.7 pt apart, green ones 2.6), chained into one."""
    out = []
    for c in segs:
        L, prev = length(c), (out[-1] if out else None)
        if prev and L < DASH and prev['last'] < DASH:
            p = prev['pts']
            if len(prev['parts']) == 1 and (min(math.dist(p[0], c[0]), math.dist(p[0], c[-1]))
                                             < min(math.dist(p[-1], c[0]), math.dist(p[-1], c[-1]))):
                p.reverse()  # the first dash runs the other way
            if math.dist(p[-1], c[-1]) < math.dist(p[-1], c[0]):
                c = c[::-1]
            if math.dist(p[-1], c[0]) < 3.5:
                p += c
                prev['parts'].append(L)
                prev['last'] = L
                continue
        out.append({'pts': list(c), 'parts': [L], 'last': L})
    return out


def line_outlines(page, S):
    """Every line on the panel's part of the page: (class, drawing order, centre line in pt, its length)."""
    lines = []
    for d in page.get_drawings():
        f = d.get('fill') if d['type'] == 'f' else None
        k = next((k for k, c in LINES.items() if f and max(abs(a - b) for a, b in zip(f, c)) < 0.01), None)
        r = d['rect']
        if k not in S['lines'] or any(e[0] <= r.x0 and r.x1 <= e[2] and e[1] <= r.y0 and r.y1 <= e[3] for e in EXCLUDE):
            continue
        if not inside(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), S['page']):
            continue
        segs = []
        for sp in subpaths(d):
            if ''.join(it[0] for it in sp) == 'cllc':
                continue  # an arrowhead (two curved sides, a notch at the back)
            c, w = centre(sp)
            if c and w <= S['width'] and length(c) >= max(1.5, 2.5 * w):
                if k != 'black' and length(c) >= DASH and area(outline(sp)) > 1.15 * length(c) * w:
                    segs += [b for b in skeleton(sp) if length(b) >= 1.5]  # more outline than one line has: branched
                else:
                    segs.append(c)
        for ch in chained(segs):
            L = length(ch['pts'])
            if (k == 'black' and L < DARK_MIN) or (len(ch['parts']) == 1 and L < S['min']):
                continue  # a letter, a lone dash or an arrowhead
            lines.append((k, d['seqno'], ch['pts'], L))
    return lines


def lines(panel, S, A, box, W, page):
    L = line_outlines(page, S)
    # a piece lying along a longer piece of its colour (within 0.5 pt) is a copy of it
    kept, copies = [], 0
    for cls, seq, pts, n in sorted(L, key=lambda l: -l[3]):
        q = dense(pts, 1.0)
        if any(o[0] == cls and all(line_dist(v, o[2]) < 0.5 for v in q) for o in kept):
            copies += 1
            continue
        kept.append((cls, seq, pts, n))
    kept.sort(key=lambda l: (l[1], l[2][0]))  # in drawing order
    w, h = box[2] - box[0], box[3] - box[1]
    P = []
    for cls, seq, pts, n in kept:
        px = simplify([to_px(A, box, p) for p in pts], 0.3)
        P.append({'id': len(P), 'cls': cls, 'lengthPx': round(length(px)),
                  'points': [[round(100 * x / w, 3), round(100 * y / h, 3)] for x, y in px]})
    json.dump({'_source': 'outlined lines of the 2022-23 PDF, registered on the 2024-25 image '
                          '(tools/trailmap/resorts/heavenly/prepare.py)', 'polylines': P},
              open(os.path.join(W, 'pieces.json'), 'w'))
    print(f'  {panel}: {len(P)} pieces ({copies} copies dropped)')


# ---- names and symbols ---------------------------------------------------------------------------------------
def word(w):
    """O and zero are one shape: a word with letters in it takes O, a number zero."""
    if re.search(r'[A-NP-Z]', w):
        return w.replace('0', 'O')
    if re.search(r'\d', w):
        return w.replace('O', '0')
    return w


def labels(panel, S, R, A, box, W):
    G = os.path.join(ROOT, 'glyphs.json')
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', panel, run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                          '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green',
                          '--circle-curves', '16', '--double-dist', '1.5', '--turned', 'WM', '--space', str(S['space'])
                          ).strip().replace('\n', '\n  '))
    d = json.load(open(f))
    os.remove(f)
    labs = [{**lab, 'text': ' '.join(word(w) for w in lab['text'].split(' ')), 'font': 'glyph'}
            for lab in d['labels'] if inside(lab['c'], S['page'])]
    syms = [s for s in d['symbols'] if inside(s['c'], S['page'])]
    # what the 2024 image no longer prints where the 2022 page has it (resort.GONE)
    gone = R.GONE.get(panel, {})
    labs = [lab for lab in labs if not any(t == lab['text'] and math.dist(to_px(A, box, lab['c']), q) < 20
                                           for t, q in gone.get('labels', ()))]
    syms = [s for s in syms if not any(math.dist(to_px(A, box, s['c']), q) < 10 for q in gone.get('symbols', ()))]
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {panel}: {len(labs)} labels, {len(syms)} symbols')


def glyphs():
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', os.path.join(ROOT, 'glyphs.json'),
            '--color', 'black=' + ','.join(map(str, DARK)), '--color', 'blue=' + ','.join(map(str, BLUE)),
            '--color', 'green=' + ','.join(map(str, GREEN))]
    for e in EXCLUDE:
        args += ['--exclude', ','.join(map(str, e))]
    print(' ', run(*args).strip())


if __name__ == '__main__':
    R = top()
    page = pymupdf.open(PDF)[0]
    glyphs()
    for panel, S in SETUP.items():
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        image(panel, R.BOX[panel], W)
        lines(panel, S, R.AFFINE[panel], R.BOX[panel], W, page)
        labels(panel, S, R, R.AFFINE[panel], R.BOX[panel], W)
