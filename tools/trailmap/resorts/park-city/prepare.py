"""Park City Mountain: the map image, line pieces, printed names and symbols from the 2025-26 trail-map PDF, for
tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/park-city/prepare.py      # regen.sh runs it

One page: the Park City side on the left, Canyons on the right, and the High Meadow Park inset (a kids' area at
Canyons, drawn larger) at the top right; the lift table, partners and rental advert below the map are left out.

- Image: the paintings (the map's, and the inset's, clipped to its frame) are about 1 px/pt, so each is swapped for
  a Lanczos upscale before the page is rendered (tools/trailmap/matte_pdf_layer.py --resample).
- Lines: 1.14 pt strokes in green, blue, black (two near-blacks) and the terrain parks' orange; the inset's are
  1.54 and 1.57 pt and run on under its frame, so they are cut to it. An easier way down is its run's line drawn
  dashed: it counts too. Where lines cross, the map redraws a short bit of line over the crossing's white halo,
  and some dashed lines' first dash is drawn apart: such bits (under 4 pt, by a longer line of their colour) are
  dropped.
- Names: outlined glyphs in the run's colour (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its
  contact sheets, is in letters.json here), the symbol before the name; the parks' names are in orange. 6 and 9
  are one shape turned over: the half its hole is in decides (--turned-hole). A few small names are text.
- Symbols: green circles, blue squares, black diamonds; two diamonds side by side are a double diamond.

Writes, in $PARK_CITY_WORK (default work/park-city): map.png, pieces.json, glyphs.json, printed.json ({labels,
symbols}, PDF points).
"""
import json
import math
import os
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('PARK_CITY_WORK', os.path.join(REPO, 'work/park-city')))
PDF = os.path.join(W, 'parkcity.pdf')
LETTERS = os.path.join(HERE, 'letters.json')

GREEN, BLUE, BLACK, BLACK2, ORANGE = (0, 0.62, 0.34), (0, 0.55, 0.77), (0.01, 0.02, 0.02), (0, 0, 0), (0.98, 0.67, 0.3)
LINES = {'green': [GREEN], 'blue': [BLUE], 'black': [BLACK, BLACK2], 'freestyle': [ORANGE]}
INSET = (1383.3, 30.3, 1667.4, 209.2)  # the High Meadow Park inset's frame (inside its 1.4 pt border), PDF points
# on the map, wholly inside: the legend, and the closed-terrain notice
EXCLUDE = [(83, 794, 632, 866), (1470, 748, 1688, 858)]


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def paintings(page):
    """The two largest images: the map's painting and the inset's."""
    ims = sorted(page.get_images(full=True), key=lambda im: -im[2] * im[3])
    return [im[0] for im in ims[:2]]


def image(page):
    if not os.path.exists(os.path.join(W, 'map.png')) or os.environ.get('IMAGES'):
        run('python3', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', os.path.join(W, 'map.png'), '--scale',
            str(SCALE), '--clip', ','.join(map(str, CLIP)),
            *[a for x in paintings(page) for a in ('--resample', str(x))])


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def clip_to(pts, r, keep_inside):
    """The parts of a polyline inside (or outside) rectangle r (Liang-Barsky per segment)."""
    out, cur = [], []
    for a, b in zip(pts, pts[1:]):
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for p, q in ((-dx, a[0] - r[0]), (dx, r[2] - a[0]), (-dy, a[1] - r[1]), (dy, r[3] - a[1])):
            if p == 0:
                if q < 0:
                    t0, t1 = 1.0, 0.0
            elif p < 0:
                t0 = max(t0, q / p)
            else:
                t1 = min(t1, q / p)
        spans = ([(t0, t1)] if t0 < t1 else []) if keep_inside else \
            ([(0.0, 1.0)] if t0 >= t1 else [(0.0, t0), (t1, 1.0)])
        for s0, s1 in spans:
            if s1 - s0 < 1e-9:
                continue
            p0, p1 = (a[0] + s0 * dx, a[1] + s0 * dy), (a[0] + s1 * dx, a[1] + s1 * dy)
            if cur and math.dist(cur[-1], p0) < 1e-6:
                cur.append(p1)
            else:
                if len(cur) > 1:
                    out.append(cur)
                cur = [p0, p1]
    if len(cur) > 1:
        out.append(cur)
    return out


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def lines():
    f = os.path.join(W, 'pieces.json')
    x0, y0, x1, y1 = CLIP
    cw, ch = x1 - x0, y1 - y0
    runs, seen = [], set()  # (cls, points in PDF points)
    # (stroke widths, the region the strokes belong to: the map outside the inset, or the inset)
    for k, ((lo, hi), keep_inside) in enumerate((((1.0, 1.2), False), ((1.5, 1.6), True))):
        tmp = os.path.join(W, f'strokes_{k}.json')
        args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale',
                str(SCALE), '--min-width', str(lo), '--max-width', str(hi), '--min-length', '1', '--out', tmp]
        for e in EXCLUDE:
            args += ['--exclude', ','.join(map(str, e))]
        for cls, cols in LINES.items():
            args += [a for c in cols for a in ('--color', f'{cls}={rgb(c)}')]
        run(*args)
        for p in json.load(open(tmp))['polylines']:
            key = (p['cls'], json.dumps(p['points']))
            if key in seen:
                continue  # a stroke drawn twice
            seen.add(key)
            pts = [(x0 + cw * x / 100, y0 + ch * y / 100) for x, y in p['points']]  # back to PDF points
            runs += [(p['cls'], q) for q in clip_to(pts, INSET, keep_inside) if length(q) >= 1.0]
        os.remove(tmp)
    # bits of line under 4 pt by a longer line of their colour (within 3.5 pt): a patch the map draws over a
    # crossing's white halo, or the first dash of a dashed line drawn apart: not pieces of their own
    patches = set()
    for i, (cls, q) in enumerate(runs):
        if length(q) > 4:
            continue
        for j, (c2, q2) in enumerate(runs):
            if j != i and c2 == cls and length(q2) > length(q) and j not in patches and all(
                    min(seg_dist(v, a, b) for a, b in zip(q2, q2[1:])) < 3.5 for v in q):
                patches.add(i)
                break
    P = []
    for i, (cls, q) in enumerate(runs):
        if i in patches:
            continue
        P.append({'id': len(P), 'cls': cls, 'lengthPx': round(length(q) * SCALE),
                  'points': [[round(100 * (x - x0) / cw, 2), round(100 * (y - y0) / ch, 2)] for x, y in q]})
    json.dump({'_source': 'PDF vector strokes (tools/trailmap/resorts/park-city/prepare.py)', 'polylines': P},
              open(f, 'w'))
    print(f'  {len(P)} pieces ({len(patches)} patches over a line dropped)')


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def text_labels():
    """Names set as text (Trade Gothic, 6.1 pt: Mimi's Way, Tombstone Alley, the parks' Pick Axe and Halfpipe), one
    copy each (one is drawn twice). The inset's larger text names are hidden under their glyph copies: left out."""
    f = os.path.join(W, 'text_p0.json')
    run('python3', f'{T}/pdf_labels.py', PDF, '--page', '0', '--out', f)
    cols = {tuple(round(v, 2) for v in c): k for k, c in (('green', GREEN), ('blue', BLUE), ('black', BLACK),
                                                          ('orange', ORANGE))}
    out = []
    for lab in json.load(open(f)):
        col = cols.get(tuple(round(v, 2) for v in lab['color']))
        if not col or not lab['font'].startswith('TradeGothicLT-BoldCond') or lab['size'] > 8 or not inside(lab['c'], CLIP):
            continue
        if any(o['text'] == lab['text'] and math.dist(o['c'], lab['c']) < 1.0 for o in out):
            continue
        out.append({'text': ' '.join(lab['text'].replace("'", '’').split()), 'font': lab['font'], 'size': lab['size'],
                    'seq': lab['seq'], 'color': col, 'pts': lab['pts'], 'c': lab['c']})
    os.remove(f)
    return out


def labels():
    G = os.path.join(W, 'glyphs.json')
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', G, '--exclude', f'0,{CLIP[3]},2000,2000']
    for e in EXCLUDE:
        args += ['--exclude', ','.join(map(str, e))]
    for cls, cols in (('black', [BLACK, BLACK2]), ('blue', [BLUE]), ('green', [GREEN]), ('orange', [ORANGE])):
        args += [a for c in cols for a in ('--color', f'{cls}={rgb(c)}')]
    run(*args)
    # word gaps in points: the inset's letters are drawn larger, so its labels come from a run with a wider gap
    labs, syms = [], []
    for region, space in (('main', 1.0), ('inset', 1.5)):
        f = os.path.join(W, f'glyph_labels_{region}.json')
        print(' ', region, run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                               '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green', '--space',
                               str(space), '--double-dist', '1.5', '--turned-hole', '69').strip()
              .replace('\n', '\n  '))
        d = json.load(open(f))
        os.remove(f)
        mine = (lambda c: inside(c, INSET)) if region == 'inset' else (lambda c: not inside(c, INSET) and inside(c, CLIP))
        labs += [{**lab, 'font': 'glyph'} for lab in d['labels'] if mine(lab['c'])]
        syms += [s for s in d['symbols'] if mine(s['c'])]
    labs += text_labels()
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    page = pymupdf.open(PDF)[0]
    image(page)
    lines()
    labels()
