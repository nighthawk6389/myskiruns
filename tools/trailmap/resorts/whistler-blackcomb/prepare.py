"""Whistler Blackcomb: the map images, line pieces, printed names and symbols of its three panels, from the
2025-26 trail-map PDF (the "Mountain Atlas"), for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/whistler-blackcomb/prepare.py      # regen.sh runs it

Panels (resort.py PANELS; each one's settings in panels/<panel>/resort.py, its files in work/.../<panel>/):
- main: the PDF's second page, both mountains, above the info bands; its legend, the stats box and the fold-up
  note sit on the map (left out of the lines and names).
- symphony: the first page's Symphony Amphitheatre inset (Symphony Bowl is drawn only there).
- glacier: the first page's Blackcomb Glacier inset (the glacier's bowls and runs are drawn only there).
The first page's 7th Heaven inset repeats the main map's 7th Heaven from another side: left out.

- Images: each panel's painting is about 2 px/pt, so the map image is the vector layer matted over a smooth upscale
  of it (tools/trailmap/matte_pdf_layer.py).
- Lines: strokes in the difficulty colours (main map 1.07 pt, some 1.6 pt; insets 0.77 and 0.6 pt), a few runs in a
  second green or a near-black navy, family-area runs in purple. The legend's GLADED TRAIL is a black line under
  white dashes: the main map draws it as a 1.6 pt black stroke under a 1.07 pt white dashed one, and those pieces are
  marked "glade" (resort.py GLADE_LINES). EASIEST WAY DOWN is the same in green. Strokes drawn twice are kept once.
  The terrain parks' lines are solid orange strokes (0.88 to 1.07 pt, class freestyle); the same orange dashed is
  an access route, at 1.6 pt the boundary, at 0.85 pt hatching: left out.
- Names: outlined glyphs in the run's colour (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its
  contact sheets, is in letters.json here) and names set as text (Interstate, Trade Gothic, DIN), some also drawn
  one object per letter; a name set twice in two colours shows the later copy, so only that one is kept, and a
  label drawn over by a later one with other text is dropped (Big Bang under Sylvain). Terrain parks are
  near-black glyphs on orange halos.
- Symbols: green circles, blue squares, black diamonds and double diamonds before the name (fills; a double diamond
  is one notched eight-sided outline, or one with rounded corners; some insets' squares are rectangles).

Writes, per panel in $WHISTLER_BLACKCOMB_WORK/<panel> (default work/whistler-blackcomb): map.png, pieces.json,
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
ROOT = os.path.abspath(os.environ.get('WHISTLER_BLACKCOMB_WORK', os.path.join(REPO, 'work/whistler-blackcomb')))
PDF = os.path.join(ROOT, 'whistler.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
PAGE_W, PAGE_H = 1728, 1215

GREEN, GREEN2, BLUE = (0, 0.65, 0.32), (0, 0.63, 0.34), (0, 0.58, 0.85)
BLACK, NAVY_BLACK, PURPLE = (0.14, 0.12, 0.13), (0, 0, 0.08), (0.64, 0.14, 0.56)
ORANGE = (0.97, 0.58, 0.12)  # the terrain parks' lines
WHITE_DASHES = [(1.0, 1.0, 1.0), (0.96, 0.98, 1.0)]  # the dashes over glades and the easiest way down
TEXT_FONTS = ('Interstate-Bold', 'InterstateCondensed-Bold', 'TradeGothicLTStd-Bold', 'DIN2014-Bold')
TEXT_COLORS = {GREEN: 'green', GREEN2: 'green', BLUE: 'blue', BLACK: 'black', PURPLE: 'purple'}

SETUP = {
    'main': {
        'page': 1, 'xref': 197,
        # the legend, the stats box and the fold-up note printed over the map
        'exclude': [(0, 571, 290, 845), (289, 664, 406, 845), (1441, 805, 1728, 845)],
        'lines': {'green': [GREEN, GREEN2], 'blue': [BLUE], 'black': [BLACK, NAVY_BLACK], 'purple': [PURPLE]},
        'widths': [(1.0, 1.15), (1.5, 2.2)],
        'solid': {'freestyle': ([ORANGE], (0.87, 1.15))},  # (one pass each, dashed strokes left out)
        'glyphs': {'black': BLACK, 'blue': BLUE, 'green': GREEN, 'park': NAVY_BLACK, 'purple': PURPLE},
    },
    'symphony': {
        'page': 0, 'xref': 577, 'exclude': [],
        'lines': {'green': [GREEN], 'blue': [BLUE], 'black': [BLACK]},
        'widths': [(0.7, 0.85)],
        'glyphs': {'black': BLACK, 'blue': BLUE, 'green': GREEN},
    },
    'glacier': {
        'page': 0, 'xref': 580, 'exclude': [],
        'lines': {'black': [BLACK]},
        'widths': [(0.55, 0.65)],
        'glyphs': {'black': BLACK},
    },
}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def settings(panel):
    """The panel's resort.py (CLIP, SCALE)."""
    spec = importlib.util.spec_from_file_location(f'wb_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def rgb(c):
    return ','.join(str(v) for v in c)


def outside(clip):
    """Rectangles covering the page outside clip: --exclude them to keep only the panel's fills."""
    x0, y0, x1, y1 = clip
    return [(0, 0, PAGE_W, y0), (0, y1, PAGE_W, PAGE_H), (0, 0, x0, PAGE_H), (x1, 0, PAGE_W, PAGE_H)]


def image(panel, R, S, W):
    if not os.path.exists(os.path.join(W, 'map.png')) or os.environ.get('IMAGES'):
        run('python3', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', os.path.join(W, 'map.png'), '--scale',
            str(R.SCALE), '--clip', ','.join(map(str, R.CLIP)), '--page', str(S['page']), '--xref', str(S['xref']))


def dashes(page):
    """The white dashed strokes (over glades and the easiest way down), as point lists in PDF points."""
    out = []
    for d in page.get_drawings():
        if d['type'] != 's' or not d.get('color') or tuple(round(v, 2) for v in d['color']) not in WHITE_DASHES:
            continue
        if d.get('dashes') in (None, '[] 0') or round(d.get('width') or 0, 2) != 1.07:
            continue
        pts = []
        for it in d['items']:
            if it[0] == 'l':
                pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == 'c':
                a, b, c, e = it[1:5]
                pts += [((1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c.x + t ** 3 * e.x,
                         (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c.y + t ** 3 * e.y)
                        for t in [k / 16 for k in range(17)]]
        out.append(pts)
    return out


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) or 1e-9


def inside_runs(pts):
    """The parts of a polyline (percent of the panel) inside the panel, cut at its edges (Liang-Barsky)."""
    runs, run = [], []
    for a, b in zip(pts, pts[1:]):
        t0, t1, d = 0.0, 1.0, (b[0] - a[0], b[1] - a[1])
        for p, q in ((-d[0], a[0]), (d[0], 100 - a[0]), (-d[1], a[1]), (d[1], 100 - a[1])):
            if p == 0:
                if q < 0:
                    t0, t1 = 1.0, 0.0
            elif p < 0:
                t0 = max(t0, q / p)
            else:
                t1 = min(t1, q / p)
        if t0 > t1:
            if run:
                runs.append(run)
                run = []
            continue
        c0 = [round(a[0] + t0 * d[0], 2), round(a[1] + t0 * d[1], 2)]
        c1 = [round(a[0] + t1 * d[0], 2), round(a[1] + t1 * d[1], 2)]
        if not run:
            run = [c0]
        run.append(c1)
        if t1 < 1.0:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    return [r for r in runs if len(r) > 1 and length(r) > 0.05]


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def lines(panel, R, S, W, page):
    f = os.path.join(W, 'pieces.json')
    excl = [a for e in S['exclude'] for a in ('--exclude', ','.join(map(str, e)))]
    for k, (lo, hi) in enumerate(S['widths']):
        args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--page', str(S['page']), '--clip',
                ','.join(map(str, R.CLIP)), '--scale', str(R.SCALE), '--min-width', str(lo), '--max-width', str(hi),
                '--min-length', '1', '--out', f, *excl, *(['--append'] if k else [])]
        for cls, cols in S['lines'].items():
            args += [a for c in cols for a in ('--color', f'{cls}={rgb(c)}')]
        run(*args)
    for cls, (cols, (lo, hi)) in S.get('solid', {}).items():
        run('python3', f'{T}/extract_pdf_vectors.py', PDF, '--page', str(S['page']), '--clip', ','.join(map(str, R.CLIP)),
            '--scale', str(R.SCALE), '--min-width', str(lo), '--max-width', str(hi), '--min-length', '1', '--solid',
            '--out', f, *excl, '--append', *[a for c in cols for a in ('--color', f'{cls}={rgb(c)}')])
    doc = json.load(open(f))
    x0, y0, x1, y1 = R.CLIP
    # a stroke drawn twice (the easiest way down is, in places) gives the same piece twice: keep the first; a stroke
    # running on under an inset's frame: only its part inside the panel
    seen, P = set(), []
    for p in doc['polylines']:
        key = (p['cls'], json.dumps(p['points']))
        if key in seen:
            continue
        seen.add(key)
        for part in inside_runs(p['points']):
            P.append({**p, 'points': part, 'lengthPx': round(p['lengthPx'] * length(part) / length(p['points'])),
                      'id': len(P)})
    # glades: black pieces under the white dashes
    D = dashes(page)
    for p in P:
        if p['cls'] != 'black':
            continue
        pts = [(x0 + x * (x1 - x0) / 100, y0 + y * (y1 - y0) / 100) for x, y in p['points']]
        near = sum(1 for q in pts if any(seg_dist(q, a, b) < 0.6 for d in D for a, b in zip(d, d[1:])))
        if near >= 0.6 * len(pts):
            p['glade'] = True
    doc['polylines'] = P
    json.dump(doc, open(f, 'w'))
    print(f'  {panel}: {len(P)} pieces ({sum(1 for p in P if p.get("glade"))} glade lines)')


def text_labels(panel, R, S, page_no):
    """Names set as text, in the trail colours; of copies of one name at one place the last drawn (it shows)."""
    f = os.path.join(ROOT, f'text_p{page_no}.json')
    if not os.path.exists(f):
        run('python3', f'{T}/pdf_labels.py', PDF, '--page', str(page_no), '--out', f)
    out = []
    for lab in json.load(open(f)):
        col = TEXT_COLORS.get(tuple(round(v, 2) for v in lab['color']))
        if not col or lab['font'] not in TEXT_FONTS or not inside(lab['c'], R.CLIP):
            continue
        if any(inside(lab['c'], e) for e in S['exclude']):
            continue
        out.append({'text': ' '.join(lab['text'].split()), 'font': lab['font'], 'size': lab['size'],
                    'seq': lab['seq'], 'color': col, 'pts': lab['pts'], 'c': lab['c']})
    keep = []
    for lab in sorted(out, key=lambda l: -l['seq']):
        if not any(k['text'] == lab['text'] and math.dist(k['c'], lab['c']) < 1.0 for k in keep):
            keep.append(lab)
    return sorted(keep, key=lambda l: l['seq'])


def odd_symbols(G):
    """Symbols pdf_glyphs.py's test (straight, even sides) misses: a double diamond drawn with rounded corners (one
    outline of lines and curves; Spanky's Ladder's, on the main map) and blue squares drawn as rectangles (the
    Symphony inset's)."""
    out = []
    for g in G:
        w, h = g['rect'][2] - g['rect'][0], g['rect'][3] - g['rect'][1]
        if g['col'] == 'black' and g['kinds'] == 'cllcclclccllclclclc':
            out.append({'t': 'double-diamond', 'c': g['c'], 'color': 'black', 'seq': g['seq']})
        elif g['col'] == 'blue' and g['kinds'] == 'l' and min(w, h) > 2.2 and max(w, h) < 1.2 * min(w, h):
            out.append({'t': 'square', 'c': g['c'], 'color': 'blue', 'seq': g['seq']})
    return out


def hidden(labs):
    """Labels drawn under another, later one at the same place with other text (last season's name or a misspelt
    copy: Big Bang under Sylvain, Glaceir Road under Glacier Road): mostly the same glyph positions both ways."""
    out = []
    for a in labs:
        for b in labs:
            if b['seq'] <= a['seq'] or b['text'].replace(' ', '') == a['text'].replace(' ', ''):
                continue
            n = sorted((len(a['pts']), len(b['pts'])))
            if n[0] < 3 or n[0] < 0.75 * n[1]:
                continue  # a name's part, also printed whole, is not a replaced label
            share = [sum(1 for p in x['pts'] if any(math.dist(p, q) < 1.5 for q in y['pts'])) for x, y in ((a, b), (b, a))]
            if share[0] >= 0.5 * len(a['pts']) and share[1] >= 0.5 * len(b['pts']):
                out.append(a)
                break
    return out


def labels(panel, R, S, W):
    G = os.path.join(W, 'glyphs.json')
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--page', str(S['page']), '--out', G]
    for cls, c in S['glyphs'].items():
        args += ['--color', f'{cls}={rgb(c)}']
    for e in S['exclude'] + outside(R.CLIP):
        args += ['--exclude', ','.join(map(str, e))]
    run(*args)
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', panel, run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                          '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green', '--space', '1.5',
                          '--even', '1.6', '--sym-min', '2.2').strip().replace('\n', '\n  '))
    d = json.load(open(f))
    labs = [{**lab, 'font': 'glyph'} for lab in d['labels'] if inside(lab['c'], R.CLIP)]
    labs += text_labels(panel, R, S, S['page'])
    under = hidden(labs)
    labs = [lab for lab in labs if lab not in under]
    if under:
        print(f'  {panel}: drawn over by a later label:', ', '.join(lab['text'] for lab in under))
    syms = list(d['symbols'])
    for s in odd_symbols(json.load(open(G))['glyphs']):  # (some drawn twice: Horstman Face's)
        if not any(t['t'] == s['t'] and math.dist(t['c'], s['c']) < 1.0 for t in syms):
            syms.append(s)
    syms = [s for s in syms if inside(s['c'], R.CLIP)]
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {panel}: {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    doc = pymupdf.open(PDF)
    for panel, S in SETUP.items():
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        image(panel, R, S, W)
        lines(panel, R, S, W, doc[S['page']])
        labels(panel, R, S, W)
