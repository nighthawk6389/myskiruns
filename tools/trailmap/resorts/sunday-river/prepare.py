"""Sunday River: the line pieces, printed names and symbols from the trail-map PDF, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/sunday-river/prepare.py      # regen.sh runs it

The page holds the main map and three insets (North Peak backside, Merrill Hill frontside, the South Ridge base
lodge), each drawn at its own scale: the main map's trail lines are 1 pt strokes, the North Peak inset's 0.49 pt,
Merrill Hill's 1.53 pt and the base lodge's 2.04 pt, and an inset's lines run on under its frame (clipped), so each
group of strokes is cut to its own frame here and the main map's are cut out of the insets. A few lines are
filled-and-stroked paths (White Heat): those count too (--filled).

Names are outlined glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets, is
in letters.json here), except a few set as text
(pdf_labels.py: UPPER and LOWER prefixes, Merrill Hill, the inset's smallest names). Word gaps are measured in
points, and each inset's letters are drawn at its own size, so the glyph labels are joined three times (one gap per
scale) and each label is taken from the run made for its region. Two names that run together in one glyph run
("EMERALD CITY* EUREKA*") are split at the snowmaking mark between them, and the mark (read as *) is dropped.

Writes, in $SUNDAY_RIVER_WORK (default work/sunday-river): pieces.json, printed.json, symbols.json.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('SUNDAY_RIVER_WORK', os.path.join(REPO, 'work/sunday-river')))
PDF = os.path.join(W, 'sundayriver.pdf')

# inset frames (inside their border strokes), PDF points
NORTH = (1418, 109, 1920, 386)
MERRILL = (1414, 403, 1870, 662)
BASE = (517, 744, 971, 960)
INSETS = (NORTH, MERRILL, BASE)
LEGEND = (1015, 680, 1920, 1080)  # the lifts and key boxes, partners' logos to their left
COLORS = ['green=0.05,0.69,0.3', 'blue=0,0.57,0.82', 'black=0,0,0', 'orange=0.98,0.67,0.3']
# (stroke widths, colours, the region the strokes belong to)
GROUPS = [((0.75, 1.1), COLORS, None), ((0.35, 0.5), COLORS[:3], NORTH), ((1.5, 1.56), COLORS[:2], MERRILL),
          ((2.0, 2.1), [COLORS[0], COLORS[3]], BASE)]


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def clip(pts, r, keep_inside):
    """The parts of a polyline inside (or outside) rectangle r, as polylines (Liang-Barsky per segment)."""
    out, cur = [], []
    for a, b in zip(pts, pts[1:]):
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for p, q in ((-dx, a[0] - r[0]), (dx, r[2] - a[0]), (-dy, a[1] - r[1]), (dy, r[3] - a[1])):
            if p == 0:
                if q < 0:
                    t0, t1 = 1.0, 0.0
            else:
                t = q / p
                if p < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
        at = lambda t: (a[0] + t * dx, a[1] + t * dy)  # noqa: E731
        spans = ([(t0, t1)] if t0 < t1 else []) if keep_inside else \
            ([(0.0, 1.0)] if t0 >= t1 else [(0.0, t0), (t1, 1.0)])
        for s0, s1 in spans:
            if s1 - s0 < 1e-9:
                continue
            p0, p1 = at(s0), at(s1)
            if cur and math.dist(cur[-1], p0) < 1e-6:
                cur.append(p1)
            else:
                if len(cur) > 1:
                    out.append(cur)
                cur = [p0, p1]
    if len(cur) > 1:
        out.append(cur)
    return out


def lines():
    x0, y0, x1, y1 = CLIP
    cw, ch = x1 - x0, y1 - y0
    pieces = []
    for k, ((wmin, wmax), cols, region) in enumerate(GROUPS):
        f = os.path.join(W, f'strokes_{k}.json')
        args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale',
                str(SCALE), '--min-width', str(wmin), '--max-width', str(wmax), '--min-length', '1', '--filled', '--out', f,
                '--max-icon', '20']  # the black rings of the lodges' icons (dining, shopping, tubing)
        for c in cols:
            args += ['--color', c]
        run(*args)
        for p in json.load(open(f))['polylines']:
            pts = [(x0 + cw * x / 100, y0 + ch * y / 100) for x, y in p['points']]  # back to PDF points
            parts = [pts]
            if region:
                parts = clip(pts, region, True)
            else:
                for r in INSETS + (LEGEND,):
                    parts = [q for part in parts for q in clip(part, r, False)]
            for q in parts:
                L = sum(math.dist(a, b) for a, b in zip(q, q[1:]))
                if L < 1.5:
                    continue
                pieces.append({'id': len(pieces), 'cls': p['cls'], 'lengthPx': round(L * SCALE),
                               'points': [[round(100 * (x - x0) / cw, 2), round(100 * (y - y0) / ch, 2)] for x, y in q]})
        os.remove(f)
    json.dump({'_source': 'PDF vector strokes (tools/trailmap/resorts/sunday-river/prepare.py)', 'polylines': pieces},
              open(os.path.join(W, 'pieces.json'), 'w'))
    print(len(pieces), 'pieces')


def region_of(c):
    return 'north' if inside(c, NORTH) else 'merrill' if inside(c, MERRILL) else 'base' if inside(c, BASE) else 'main'


def clips():
    """Each drawing's visible area: the intersection of the clip rectangles in force when it is painted (an
    inset's names run on under its frame, clipped there, and are invisible)."""
    import pymupdf
    out, stack = {}, []
    for d in pymupdf.open(PDF)[0].get_drawings(extended=True):
        lvl = d.get('level', 0)
        if d['type'] == 'group':
            continue
        while stack and stack[-1][0] >= lvl:
            stack.pop()
        if d['type'] == 'clip':
            stack.append((lvl, tuple(d['scissor'])))
            continue
        r = (-1e9, -1e9, 1e9, 1e9)
        for _l, s in stack:
            r = (max(r[0], s[0]), max(r[1], s[1]), min(r[2], s[2]), min(r[3], s[3]))
        out[d['seqno']] = r
    return out


# glyph fill colours of the names: the three trail colours, plus the slightly different greens of BEAR PAW and the
# North Peak inset's ROUNDABOUT and the dark grey of DOUBLE BLIND's diamonds; orange for freestyle runs
GLYPH_COLORS = ['green=0.05,0.69,0.3', 'green=0,0.66,0.31', 'green=0,0.65,0.32', 'blue=0,0.57,0.82', 'black=0,0,0',
                'black=0.14,0.12,0.12', 'orange=0.98,0.67,0.3']
LETTERS = os.path.join(HERE, 'letters.json')  # each glyph shape's letter, read on pdf_glyphs.py's contact sheets


def labels():
    G, L = os.path.join(W, 'glyphs.json'), LETTERS
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', G, '--exclude', ','.join(map(str, LEGEND)),
            '--exclude', '0,780,500,1080']
    for c in GLYPH_COLORS:
        args += ['--color', c]
    run(*args)
    visible = clips()
    runs = {}
    for region, space in (('main', 1.2), ('north', 0.55), ('merrill', 0.55), ('base', 2.0)):
        f = os.path.join(W, f'glyph_labels_{region}.json')
        run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', L, '--out', f, '--square',
            'blue', '--diamond', 'black', '--circle', 'green', '--space', str(space), '--double-dist', '1.7',
            '--sym-min', '1.2')
        runs[region] = json.load(open(f))
        os.remove(f)
    out = []
    for region, d in runs.items():
        for lab in d['labels']:
            if region_of(lab['c']) != region:
                continue
            v = visible.get(lab['seq'])
            if v and sum(inside(p, v) for p in lab['pts']) < 0.5 * len(lab['pts']):
                continue  # drawn outside its clip: hidden
            # split at a snowmaking mark followed by more text (two names in one run); drop the marks
            chars = [ch for ch in lab['text'] if ch != ' ']
            assert len(chars) == len(lab['pts']), lab['text']
            words, cur, k = [], [], 0
            for i, ch in enumerate(lab['text']):
                if ch == ' ':
                    cur.append((' ', None))
                    continue
                cur.append((ch, lab['pts'][k]))
                k += 1
                if ch == '*' and lab['text'][i + 1:].strip(' *'):
                    words.append(cur)
                    cur = []
            words.append(cur)
            for w in words:
                text = ''.join(ch for ch, _ in w).replace('*', '').strip()
                pts = [p for ch, p in w if p is not None and ch != '*']
                if text and pts:
                    out.append({'text': ' '.join(text.split()), 'font': 'glyph', 'size': lab['size'], 'seq': lab['seq'],
                                'color': lab['color'], 'pts': pts,
                                'c': [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]})
    named = {(0.05, 0.69, 0.3): 'green', (0.0, 0.57, 0.82): 'blue', (0.0, 0.0, 0.0): 'black',
             (0.98, 0.67, 0.3): 'orange', (0.14, 0.12, 0.12): 'black'}
    f = os.path.join(W, 'text_labels.json')
    run('python3', f'{T}/pdf_labels.py', PDF, '--out', f)
    for lab in json.load(open(f)):
        col = named.get(tuple(lab['color']))
        if not lab['font'].startswith('Futura-Condensed') or not col:
            continue
        out.append({'text': ' '.join(lab['text'].replace('ʼ', '’').split()), 'font': lab['font'], 'size': lab['size'],
                    'seq': lab['seq'], 'color': col, 'pts': lab['pts'], 'c': lab['c']})
    os.remove(f)
    json.dump(out, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    syms = [s for s in runs['main']['symbols'] if inside(s['c'], visible.get(s['seq'], (-1e9, -1e9, 1e9, 1e9)))]
    x0, y0 = CLIP[:2]
    json.dump([{'type': s['t'], 'src': [round((s['c'][0] - x0) * SCALE), round((s['c'][1] - y0) * SCALE)],
                'sizePt': 1.8 if region_of(s['c']) == 'north' else 3.4} for s in syms],
              open(os.path.join(W, 'symbols.json'), 'w'), indent=0)
    print(len(out), 'labels,', len(syms), 'symbols')


if __name__ == '__main__':
    lines()
    labels()
