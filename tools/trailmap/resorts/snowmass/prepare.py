"""Snowmass: the map images, line pieces, printed names and their ratings, of its two panels, for
tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/snowmass/prepare.py      # regen.sh runs it

The 2025-26 trail map (aspensnowmass.com: one Illustrator page, "layered") draws its trail lines as vectors over a
100 dpi painting and prints every name as text, white on a pill in the run's colour, set on the run's own line.

Panels (resort.py PANELS; each one's settings in panels/<panel>/resort.py, its files in work/.../<panel>/):
- main: the whole mountain (the page, its Hanging Valley inset and legend left out of the reading).
- hanging-valley: the inset at the top, Hanging Valley drawn larger, with names the main map leaves out.

- Images: the page rendered at resort.SCALE with the two paintings (the main one and the inset's) swapped for a
  Lanczos upscale (tools/trailmap/matte_pdf_layer.py --resample).
- Lines: the blue, black and green strokes (extract_pdf_vectors.py, the panel's widths; a few black lines are pure
  black; the inset's dashed ridge line is no run), and the expert runs, a black line in a yellow casing drawn as
  filled outlines, by the casing's centre line (pdf_outline_lines.py; the inset's casings are in two yellows); a few
  casings are a thin yellow stroke over a black one instead: that stroke. Where a black stroke runs along a casing,
  it is the expert line's centre drawn again, and left out. The legend and the inset are left out of the main
  panel's lines. One path is one piece: the map draws a run as one path, the runs that leave it as paths ending on
  it (where one path carries two runs, decisions.py cuts it).
- Names: the page's white text (pdf_labels.py) on a pill: the pill's colour, sampled around each letter on a
  render of the page, is the run's (green, blue, black; red and purple pills are lifts, left out). Two names drawn
  as one text object on two pills (resort.SPLIT) are split first. A black run is expert (double black) where its
  own line (the piece most of its letters lie on) is a yellow-cased one or an EX mark (white E and X on two black
  diamonds, as text or as shapes: extreme terrain) is by a letter of it (the double diamonds are printed along the
  cased lines, often far from the names: the casing tells those); a name printed in parts (resort.JOIN) is expert
  if a part is. resort.COLOR_SYMBOL turns the colour into the symbol; the map prints no other symbol by a name.
  The lodges', areas' and notices' callouts (white bold type on a black box, smaller than the lifts' names) are
  left out.

Writes, per panel in $SNOWMASS_WORK/<panel> (default work/snowmass): map.png, pieces.json, printed.json ({labels,
symbols: []}: pdf_labels.py's labels, PDF points, each with its pill's colour).
"""
import importlib.util
import json
import math
import os
import subprocess
import sys

import numpy as np
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('SNOWMASS_WORK', os.path.join(REPO, 'work/snowmass')))
PDF = os.path.join(ROOT, 'snowmass_2025-26.pdf')
PAINTINGS = (115, 116)  # the main painting's and the inset's image xrefs (both 100 dpi)
INSET = (362, 0, 555, 129)  # pt: the Hanging Valley inset
LEGEND = (1225, 0, 1368, 232)  # pt: the legend, top right
LOGO = (0, 0, 166, 57)  # pt: the Snowmass logo, top left

SETUP = {
    'main': {'strokes': ('--min-width', '1.05', '--max-width', '1.2'), 'diamond': (4.5, 8.5),
             'exclude': [INSET, LEGEND, LOGO]},
    # (the inset's thin dashed black line along the ridge above High Pass is no run: --solid)
    'hanging-valley': {'strokes': ('--min-width', '0.6', '--max-width', '1.3', '--solid'), 'diamond': (2.0, 4.0),
                       'exclude': []},
}
DARK = [(0.14, 0.12, 0.12), (0.14, 0.12, 0.13)]
# the pills' colours, as rendered (RGB 0-255): a pixel takes the nearest
PILLS = {'blue': (0, 163, 227), 'green': (0, 173, 77), 'black': (36, 31, 31), 'red': (230, 41, 36),
         'purple': (99, 64, 153)}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def settings(panel):
    """The panel's resort.py (CLIP, SCALE)."""
    spec = importlib.util.spec_from_file_location(f'sm_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def in_panel(panel, R, p):
    return inside(p, R.CLIP) and not any(inside(p, e) for e in SETUP[panel]['exclude'])


def col(c):
    return tuple(round(v, 2) for v in c or ())


def image(R, W):
    out = os.path.join(W, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    run('python3', '-I', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', out, '--scale', str(R.SCALE), '--clip',
        ','.join(map(str, R.CLIP)), *[a for x in PAINTINGS for a in ('--resample', str(x))])


def lines(panel, R, W):
    """The strokes and the expert runs' casings, one pieces.json (ids in that order)."""
    clip = ','.join(map(str, R.CLIP))
    ex = [a for e in SETUP[panel]['exclude'] for a in ('--exclude', ','.join(map(str, e)))]
    s, o = os.path.join(W, 'strokes.json'), os.path.join(W, 'casings.json')
    run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', clip, '--scale', str(R.SCALE),
        '--color', 'blue=0,0.64,0.89', '--color', 'black=0.14,0.12,0.12', '--color', 'black=0.14,0.12,0.13',
        '--color', 'black=0,0,0', '--color', 'green=0,0.68,0.3', *SETUP[panel]['strokes'], *ex, '--out', s)
    # (a few black lines are pure black: Cabin, Camp 3, the foot of Garrett Gulch, the inset's West I & II)
    # (each class its own name: two --color of one name would keep the last)
    run('python3', '-I', f'{T}/pdf_outline_lines.py', PDF, '--clip', clip, '--scale', str(R.SCALE),
        '--color', 'black=1.0,0.9,0.0', '--color', 'black2=0.97,0.86,0.0', '--max-width', '3', *ex, '--out', o)
    # a few cased lines are a thin yellow stroke over a wide black one instead (AMF's and Gowdy's, the Cirque's exit,
    # the inset's West I & II): the yellow stroke
    y = os.path.join(W, 'thin_casings.json')
    run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', clip, '--scale', str(R.SCALE),
        '--color', 'black=1.0,0.9,0.0', '--min-width', '0.4', '--max-width', '0.8', *ex, '--out', y)
    w, h = (R.CLIP[2] - R.CLIP[0]) * R.SCALE, (R.CLIP[3] - R.CLIP[1]) * R.SCALE
    raw = []
    for f, expert in ((s, False), (o, True), (y, True)):
        for p in json.load(open(f))['polylines']:
            raw.append(('black' if p['cls'] == 'black2' else p['cls'], expert,
                        [(x * w / 100, y * h / 100) for x, y in p['points']]))
        os.remove(f)
    # an expert line's black centre is drawn as a stroke too in places (the inset's): the stroke along a casing is
    # its copy (and so is a casing along a longer one)
    def copy(i, r):
        return any(c[1] and j != i and (not r[1] or (length(c[2]), j) > (length(r[2]), i))
                   and all(near(q, c[2], 0.6 * R.SCALE) for q in dense(r[2], R.SCALE)) for j, c in enumerate(raw))
    raw = [r for i, r in enumerate(raw) if not copy(i, r)]
    P = []
    for cls, expert, pts in raw:
        P.append({'id': len(P), 'cls': cls, 'lengthPx': round(length(pts)),
                  'points': [[round(100 * x / w, 3), round(100 * y / h, 3)] for x, y in pts],
                  **({'expert': True} if expert else {})})
    json.dump({'_source': f'Snowmass 2025-26 trail map PDF: strokes and expert casings, '
                          f'tools/trailmap/resorts/snowmass/prepare.py; percent of the map image', 'polylines': P},
              open(os.path.join(W, 'pieces.json'), 'w'))
    by = {}
    for p in P:
        k = p['cls'] + ('/expert' if p.get('expert') else '')
        by[k] = by.get(k, 0) + 1
    print(f'  {panel}: wrote pieces.json: {len(P)} pieces {by}')
    return P


def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def near(q, pts, tol):
    return min(seg(q, a, b) for a, b in zip(pts, pts[1:])) < tol


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def page_render(page, z):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)


def pill(img, z, lab):
    """The colour class of the pill a label is printed on: the most common class of the coloured pixels round its
    letters (within a third of the type size of each letter's centre; the white letters left out)."""
    pal = np.array(list(PILLS.values()))
    votes = {}
    r = max(1, int(lab['size'] * z / 3))
    for x, y in lab['pts']:
        cx, cy = int(x * z), int(y * z)
        win = img[max(0, cy - r):cy + r + 1, max(0, cx - r):cx + r + 1].reshape(-1, 3)
        win = win[win.min(axis=1) < 200]  # not the white letters
        if not len(win):
            continue
        d = np.linalg.norm(win[:, None, :] - pal[None, :, :], axis=2)
        k = d.argmin(axis=1)
        for i in k[d[np.arange(len(k)), k] < 60]:
            name = list(PILLS)[i]
            votes[name] = votes.get(name, 0) + 1
    return max(votes, key=votes.get) if votes else None


def ex_marks(page, lo, hi):
    """The EX marks drawn as shapes: a dark four-sided fill (lo-hi pt) with a white letter (a fill of ten or more
    straight sides: E or X) inside; the centre of each."""
    ds, letters = [], []
    for d in page.get_drawings():
        if d['type'] not in ('f', 'fs') or not d.get('fill'):
            continue
        kinds, r = ''.join(it[0] for it in d['items']), d['rect']
        if col(d['fill']) in DARK and kinds == 'llll' and lo <= max(r.width, r.height) <= hi:
            ds.append(r)
        elif (col(d['fill']) == (1.0, 1.0, 1.0) and set(kinds) == {'l'} and len(kinds) >= 10
              and max(r.width, r.height) < hi):
            letters.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
    return [((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2) for r in ds if any(r.contains(pymupdf.Point(*q)) for q in letters)]


def labels(panel, R, W, L, img, z, page, P):
    x0, y0 = R.CLIP[:2]
    w, h = (R.CLIP[2] - x0) * R.SCALE, (R.CLIP[3] - y0) * R.SCALE
    pieces = [([(x * w / 100 / R.SCALE + x0, y * h / 100 / R.SCALE + y0) for x, y in p['points']], p.get('expert'))
              for p in P]
    # the EX marks (extreme terrain); the double diamonds are printed along the expert runs' cased lines, some far
    # from the names, so the casing tells those
    marks = [tuple(lab['c']) for lab in L if lab['text'].replace(' ', '') == 'EX' and in_panel(panel, R, lab['c'])]
    marks += [q for q in ex_marks(page, *SETUP[panel]['diamond']) if in_panel(panel, R, q)]
    reach = 2.5 * (5 if panel == 'main' else 2.6)  # pt from a name's letter to its mark: two and a half letters

    def own_line_cased(lab):
        """Is the name's own line (the piece most of its letters lie on, within 0.6 of the type size) a casing?"""
        tol = 0.6 * lab['size']
        best = max(((sum(1 for q in lab['pts'] if min(seg(q, a, b) for a, b in zip(c, c[1:])) < tol), bool(e))
                    for c, e in pieces), default=(0, False))
        return best[0] >= max(2, 0.4 * len(lab['pts'])) and best[1]
    def split(lab):
        """resort.SPLIT: two names drawn as one text object, each on its own pill (UTE CHUTE's blue, FAST DRAW's
        black): the parts, by their letters (one point per letter), before the pills are read."""
        parts = R.SPLIT.get(lab['text'])
        if not parts:
            return [lab]
        n = [len(t.replace(' ', '')) for t in parts]
        assert sum(n) == len(lab['pts']), ('SPLIT: the parts are not the label', lab['text'], parts)
        out = []
        for k, t in enumerate(parts):
            pts = lab['pts'][sum(n[:k]):sum(n[:k + 1])]
            out.append({**lab, 'text': t, 'pts': pts,
                        'c': [sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)]})
        return out
    out, tally = [], {}
    for lab in [part for lab in L for part in split(lab)]:
        if not in_panel(panel, R, lab['c']) or col(lab['color']) != (1.0, 1.0, 1.0):
            continue
        if lab['text'].replace(' ', '') == 'EX' or not ('Semibold' in lab['font'] or lab['size'] >= 6):
            continue  # (the lodges', areas' and notices' callouts are bold, smaller than the lifts' names)
        k = pill(img, z, lab)
        if k not in ('green', 'blue', 'black'):
            continue  # a lift (red, purple) or no pill (a lodge's or area's name)
        if k == 'black' and (own_line_cased(lab) or any(math.dist(m, q) < reach for m in marks for q in lab['pts'])):
            k = 'expert'
        out.append({**lab, 'color': k})
    # a name printed in parts (resort.JOIN) is expert if any part is (its symbol or casing may be by either line)
    for parts in R.JOIN:
        for first in [lab for lab in out if lab['text'] == parts[0]]:
            chain = [first]
            for part in parts[1:]:
                gap = lambda lab: min(math.dist(p, q) for p in chain[-1]['pts'] for q in lab['pts'])  # noqa: E731
                nxt = min((lab for lab in out if lab['text'] == part and lab not in chain), key=gap, default=None)
                if nxt is None or gap(nxt) > R.JOIN_GAP:
                    break
                chain.append(nxt)
            if len(chain) == len(parts) and any(lab['color'] == 'expert' for lab in chain) \
                    and all(lab['color'] in ('black', 'expert') for lab in chain):
                for lab in chain:
                    lab['color'] = 'expert'
    for lab in out:
        tally[lab['color']] = tally.get(lab['color'], 0) + 1
    json.dump({'labels': out, 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {panel}: {len(out)} names {tally}; {len(marks)} EX marks')


def seg(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def main():
    sys.path.insert(0, HERE)
    import resort as top
    doc = pymupdf.open(PDF)
    f = os.path.join(ROOT, 'text.json')
    if not os.path.exists(f):
        run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--out', f)
    L = json.load(open(f))
    z = 6  # px per pt of the render the pills are sampled on
    img = page_render(doc[0], z)
    for panel, _name in top.PANELS:
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        image(R, W)
        P = lines(panel, R, W)
        labels(panel, R, W, L, img, z, doc[0], P)


if __name__ == '__main__':
    main()
