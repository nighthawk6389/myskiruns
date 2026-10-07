"""Palisades Tahoe: the map images, line pieces, printed names and symbols of its three panels, from the 2025-26
trail-map PDFs, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/palisades-tahoe/prepare.py      # regen.sh runs it

Panels (resort.py PANELS; each one's settings in panels/<panel>/resort.py, its files in work/.../<panel>/), one PDF
of one page each:
- palisades: the Palisades side (palisadesmaintrailmap.pdf).
- alpine-front: Alpine's front side (alpine-front-side-trail.pdf).
- alpine-back: Alpine's back side, Sherwood and the back of Scott Peak (alpine-back-side-trail.pdf).

- Images: each painting is about 4 px/pt, so the page is rendered as it is, at the panel's scale.
- Lines: strokes in the difficulty colours (Palisades 1.26 pt; Alpine's front 1.11 pt, its black runs 1 pt pure black;
  its back 1 pt). A stroke drawn twice gives one piece; one drawn under a later stroke of another colour along its
  whole length is hidden and gives none.
- Names: black outlined glyphs on a white halo (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its
  contact sheets, is in letters.json here; the three maps share one font, condensed, its word gaps (pt) per map in
  'space'). A few glyphs are drawn out of turn (--reorder), and d and p are one shape turned over (--turned-hole).
- Symbols: green circles, blue squares, black diamonds and double diamonds before the name (fills; on the main map
  the squares are rectangles, on Alpine's every symbol has rounded corners, a double diamond is one notched outline).

Writes, per panel in $PALISADES_TAHOE_WORK/<panel> (default work/palisades-tahoe): map.png, pieces.json,
glyphs.json, printed.json ({labels, symbols}, PDF points).
"""
import importlib.util
import json
import math
import os
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('PALISADES_TAHOE_WORK', os.path.join(REPO, 'work/palisades-tahoe')))
LETTERS = os.path.join(HERE, 'letters.json')

GREEN, BLUE, BLACK, PURE_BLACK = (0, 0.65, 0.32), (0, 0.61, 0.86), (0.14, 0.12, 0.13), (0, 0, 0)

SETUP = {
    'palisades': {
        'pdf': 'palisades_main.pdf', 'exclude': [], 'space': 1.8,
        'lines': {'green': [GREEN], 'blue': [BLUE], 'black': [BLACK]},
        'widths': [(1.2, 1.3)],
    },
    'alpine-front': {
        'pdf': 'alpine_front.pdf', 'exclude': [], 'space': 0.9,
        'lines': {'green': [GREEN], 'blue': [BLUE], 'black': [PURE_BLACK]},
        'widths': [(0.95, 1.15)],
    },
    'alpine-back': {
        'pdf': 'alpine_back.pdf', 'exclude': [], 'space': 0.9,
        'lines': {'blue': [BLUE], 'black': [BLACK]},
        'widths': [(0.95, 1.05)],
    },
}
GLYPHS = {'black': BLACK, 'blue': BLUE, 'green': GREEN}  # names and diamonds; squares; circles


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def settings(panel):
    """The panel's resort.py (CLIP, SCALE)."""
    spec = importlib.util.spec_from_file_location(f'pt_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def rgb(c):
    return ','.join(str(v) for v in c)


def outside(clip, page):
    """Rectangles covering the page outside clip: --exclude them to keep only the panel's fills."""
    x0, y0, x1, y1 = clip
    w, h = page.rect.width, page.rect.height
    return [(0, 0, w, y0), (0, y1, w, h), (0, 0, x0, h), (x1, 0, w, h)]


def image(R, W, page):
    out = os.path.join(W, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    page.get_pixmap(matrix=pymupdf.Matrix(R.SCALE, R.SCALE), clip=pymupdf.Rect(*R.CLIP)).save(out)


def lines(panel, R, S, W, pdf):
    f = os.path.join(W, 'pieces.json')
    excl = [a for e in S['exclude'] for a in ('--exclude', ','.join(map(str, e)))]
    for k, (lo, hi) in enumerate(S['widths']):
        args = ['python3', f'{T}/extract_pdf_vectors.py', pdf, '--clip', ','.join(map(str, R.CLIP)), '--scale',
                str(R.SCALE), '--min-width', str(lo), '--max-width', str(hi), '--min-length', '1', '--out', f, *excl,
                *(['--append'] if k else [])]
        for cls, cols in S['lines'].items():
            args += [a for c in cols for a in ('--color', f'{cls}={rgb(c)}')]
        run(*args)
    doc = json.load(open(f))
    # a stroke drawn under a later stroke of another trail colour along its whole length is hidden (a blue line left
    # under the Saddle's black one): no piece
    x0, y0, x1, y1 = R.CLIP
    strokes = trail_strokes(pymupdf.open(pdf)[0], S['lines'])
    P, hidden, twice, seen = [], 0, 0, set()
    for p in doc['polylines']:
        key = (p['cls'], json.dumps(p['points']))
        if key in seen:  # a stroke drawn twice (the back side's are): one piece
            twice += 1
            continue
        seen.add(key)
        pts = dense([(x0 + x * (x1 - x0) / 100, y0 + y * (y1 - y0) / 100) for x, y in p['points']], 1.0)
        own = [s for s in strokes if s[1] == p['cls'] and all(near(q, s[2]) for q in pts)]
        if own and any(s[1] != p['cls'] and s[0] > max(o[0] for o in own) and all(near(q, s[2]) for q in pts)
                       for s in strokes):
            hidden += 1
            continue
        P.append({**p, 'id': len(P)})
    doc['polylines'] = P
    json.dump(doc, open(f, 'w'))
    print(f'  {panel}: {len(P)} pieces ({hidden} hidden under another colour, {twice} drawn twice)')


def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def near(q, pts, d=0.8):
    return any(abs(q[0] - x) < d and abs(q[1] - y) < d and math.dist(q, (x, y)) < d for x, y in pts)


def trail_strokes(page, classes):
    """The page's strokes in the trail colours: (drawing order, class, points every half point), in PDF points."""
    cls = {tuple(round(v, 2) for v in c): k for k, cols in classes.items() for c in cols}
    out = []
    for d in page.get_drawings():
        k = cls.get(tuple(round(v, 2) for v in (d.get('color') or ()))) if d['type'] in ('s', 'fs') else None
        if not k:
            continue
        pts = []
        for it in d['items']:
            if it[0] == 'l':
                pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == 'c':
                a, b, c, e = it[1:5]
                pts += [((1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c.x + t ** 3 * e.x,
                         (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c.y + t ** 3 * e.y)
                        for t in [j / 12 for j in range(13)]]
        if len(pts) > 1:
            out.append((d['seqno'], k, dense(pts, 0.5)))
    return out


def labels(panel, R, S, W, pdf, page):
    G = os.path.join(W, 'glyphs.json')
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', pdf, '--out', G, '--max-size', '14']  # (double diamonds)
    for cls, c in GLYPHS.items():
        args += ['--color', f'{cls}={rgb(c)}']
    for e in S['exclude'] + outside(R.CLIP, page):
        args += ['--exclude', ','.join(map(str, e))]
    run(*args)
    if not os.path.exists(LETTERS):
        return
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', panel, run('python3', f'{T}/pdf_glyphs.py', 'labels', pdf, '--glyphs', G, '--letters', LETTERS,
                          '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green',
                          '--rounded', '--rect-squares', '--even', '1.8', '--turned-hole', 'dp', '--reorder',
                          '--space', str(S['space'])).strip().replace('\n', '\n  '))
    d = json.load(open(f))
    os.remove(f)
    labs = [{**lab, 'font': 'glyph'} for lab in d['labels'] if inside(lab['c'], R.CLIP)]
    syms = [s for s in d['symbols'] if inside(s['c'], R.CLIP)]
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {panel}: {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    for panel, S in SETUP.items():
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        pdf = os.path.join(ROOT, S['pdf'])
        page = pymupdf.open(pdf)[0]
        image(R, W, page)
        lines(panel, R, S, W, pdf)
        labels(panel, R, S, W, pdf, page)
