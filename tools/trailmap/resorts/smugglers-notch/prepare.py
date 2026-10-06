"""Smugglers' Notch: the map image, line pieces, printed names and symbols from the trail-map PDF on smuggs.com,
for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/smugglers-notch/prepare.py      # regen.sh runs it

- Image: the painting is only 2356x1596 px for 1695x1147 pt, so the map image is the vector layer matted over a
  smooth upscale of it (tools/trailmap/matte_pdf_layer.py), clipped to the map left of the key panel.
- Lines: 3.44 pt green, blue and black strokes.
- Names: white outlined glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets,
  is in letters.json here; two names are white text) on label boxes in the run's colour. n and u are one shape
  turned over here, and so are ! and i (--turned). A label box sits on its line, or off it with a thin leader line
  from the box to the line or to a hollow circle (a glade): such a name becomes a name at the leader's far end, once
  per leader.
- Each name's colour is its label box's (green, blue, black): the map rates runs by colour, and its experts' terrain
  by chains of black diamonds on the line (two: double black; three, The Black Hole: triple, the app's double).
- Terrain parks: 7.46 pt orange lines (class freestyle), named in orange boxes in black (glyphs, or text for the
  Burton Treehouse Riglet Park); a box joined to its line by a leader names the line at the leader's end.

Writes, in $SMUGGLERS_NOTCH_WORK (default work/smugglers-notch): map.png, pieces.json, printed.json, symbols.json
(each diamond chain: a double-diamond symbol at its middle, with its diamonds).
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

W = os.path.abspath(os.environ.get('SMUGGLERS_NOTCH_WORK', os.path.join(REPO, 'work/smugglers-notch')))
PDF = os.path.join(W, 'smuggs.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
KEY = (1695, 0, 2346, 1147)  # the key panel, PDF points
APP = (1346, 696, 1627, 1106)  # the phone-app picture over the map's lower right
COLORS = {'green': (0.0, 0.65, 0.32), 'blue': (0.0, 0.68, 0.94), 'black': (0.0, 0.0, 0.0)}
PARK_LINE = (0.99, 0.72, 0.2)  # the terrain parks' 7.46 pt orange lines
PARK_BOX = (0.97, 0.58, 0.3)  # their names' boxes (black text)
LEADER_WIDTHS = (0.99, 1.17, 1.46)


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def inside(p, r, pad=0.0):
    return r[0] - pad <= p[0] <= r[2] + pad and r[1] - pad <= p[1] <= r[3] + pad


def px(p):
    return [round((p[0] - CLIP[0]) * SCALE), round((p[1] - CLIP[1]) * SCALE)]


def image():
    if not os.path.exists(os.path.join(W, 'map.png')) or os.environ.get('IMAGES'):
        run('python3', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', os.path.join(W, 'map.png'), '--scale',
            str(SCALE), '--clip', ','.join(map(str, CLIP)), '--xref', '259')


def lines():
    args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
            '--min-width', '3.3', '--max-width', '7.5', '--min-length', '1', '--exclude', ','.join(map(str, APP)),
            '--out', os.path.join(W, 'pieces.json')]
    for name, rgb in {**COLORS, 'freestyle': PARK_LINE}.items():
        args += ['--color', f'{name}={",".join(map(str, rgb))}']
    run(*args)


def subpaths(items):
    subs, cur, last = [], [], None
    for it in items:
        s = it[1]
        if last is not None and math.dist((s.x, s.y), last) > 0.01:
            subs.append(cur)
            cur = []
        cur.append(it)
        last = (it[-1].x, it[-1].y)
    if cur:
        subs.append(cur)
    return subs


def leaders(page):
    """The thin black leader segments [(a, b)] and hollow circles [(centre, radius)], in PDF points."""
    segs, circles = [], []
    for d in page.get_drawings():
        if d['type'] not in ('s', 'fs') or not d.get('color') or tuple(round(v, 2) for v in d['color']) != (0, 0, 0):
            continue
        if round(d.get('width') or 0, 2) not in LEADER_WIDTHS:
            continue
        if d['type'] == 'fs' and ''.join(it[0] for it in d['items']) != 'l':
            continue  # an icon's outline; a leader drawn filled-and-stroked is one straight segment
        for sp in subpaths(d['items']):
            a, b = sp[0][1], sp[-1][-1]
            if math.dist((a.x, a.y), (b.x, b.y)) < 0.05 and all(it[0] == 'c' for it in sp):
                xs = [q.x for it in sp for q in it[1:]]
                ys = [q.y for it in sp for q in it[1:]]
                circles.append((((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2), (max(xs) - min(xs)) / 2))
            else:
                segs.append(((a.x, a.y), (b.x, b.y)))
    return segs, circles


def pills(page):
    """Filled label boxes in a run colour, or a park's: [(outline, colour)], the outline a polygon in PDF points."""
    out = []
    for d in page.get_drawings():
        if d['type'] not in ('f', 'fs') or not d.get('fill'):
            continue
        col = next((k for k, v in {**COLORS, 'park': PARK_BOX}.items()
                    if tuple(round(c, 2) for c in d['fill']) == v), None)
        r = d['rect']
        if col and 'c' in ''.join(it[0] for it in d['items']) and 8 < max(r.width, r.height) < 200:
            pts = []
            for it in d['items']:
                if it[0] == 'c':
                    a, b, c, e = it[1:5]
                    pts += [((1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c.x + t ** 3 * e.x,
                             (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c.y + t ** 3 * e.y)
                            for t in (0.25, 0.5, 0.75, 1)]
                elif it[0] == 'l':
                    pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            out.append((pts, col))
    return out


def in_box(p, poly, pad=0.0):
    """Point p inside the box outline, or within pad of its edge."""
    edges = list(zip(poly, poly[1:] + poly[:1]))
    inside_ = False
    for (x0, y0), (x1, y1) in edges:
        if (y0 > p[1]) != (y1 > p[1]) and p[0] < x0 + (p[1] - y0) * (x1 - x0) / (y1 - y0):
            inside_ = not inside_
    return inside_ or min(seg_dist(p, a, b) for a, b in edges) <= pad


def area(poly):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))) / 2


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def labels():
    G = os.path.join(W, 'glyphs.json')
    run('python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', G, '--color', 'white=1,1,1', '--color',
        'black=0,0,0', '--exclude', ','.join(map(str, KEY)), '--exclude', ','.join(map(str, APP)))
    f = os.path.join(W, 'glyph_labels.json')
    run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS, '--out', f,
        '--space', '1.3', '--turned', 'nu', '--turned', '!i')
    page = pymupdf.open(PDF)[0]
    boxes = pills(page)
    segs, circles = leaders(page)
    park_boxes = [poly for poly, col in boxes if col == 'park']
    # white glyph names, and black ones in a park's box (the terrain parks' names)
    labs = [lab for lab in json.load(open(f))['labels'] if '*' not in lab['text']
            and (lab['color'] == 'white' or any(in_box(lab['c'], poly) for poly in park_boxes))]
    f2 = os.path.join(W, 'text_labels.json')  # a few names are set as text: Bud's Way, the Howie's of Howie's
    run('python3', f'{T}/pdf_labels.py', PDF, '--out', f2)  # Wanderer, the Burton Treehouse Riglet Park's box
    labs += [{**lab, 'text': ' '.join(lab['text'].split()), 'size': lab['size']} for lab in json.load(open(f2))
             if lab['font'].startswith('MyriadPro-Semibold') and tuple(lab['color']) == (1, 1, 1)
             or any(in_box(lab['c'], poly) for poly in park_boxes)]
    os.remove(f2)
    out, used = [], set()
    for lab in labs:
        c = lab['c']
        if not inside(c, CLIP):
            continue
        under = [(poly, col) for poly, col in boxes if in_box(c, poly)]
        if not under:
            print('  no label box under', lab['text'], [round(v) for v in c])
            continue
        box, col = min(under, key=lambda pc: area(pc[0]))
        ends = []  # the far ends of the leaders that leave this box
        for k, (a, b) in enumerate(segs):
            for near, far in ((a, b), (b, a)):
                if in_box(near, box, 1.0) and not in_box(far, box, 1.0):
                    ends.append((k, far))
        base = {'text': lab['text'], 'font': 'glyph', 'size': lab['size'], 'seq': lab['seq'], 'color': col}
        if not ends:
            out.append({**base, 'pts': lab['pts'], 'c': c})
            continue
        for k, far in ends:
            used.add(k)
            circle = min(circles, key=lambda cr: math.dist(cr[0], far) - cr[1], default=None)
            if circle and math.dist(circle[0], far) < circle[1] + 1.5:  # a glade: the name at its circle
                out.append({**base, 'pts': [list(circle[0])], 'c': list(circle[0]), 'glade': True})
            else:  # the leader ends on the run's line
                out.append({**base, 'pts': [list(far)], 'c': list(far), 'leader': True})
    for k, (a, b) in enumerate(segs):
        if k not in used:
            print('  leader with no label box:', [round(v) for v in a], [round(v) for v in b])
    json.dump(out, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(len(out), 'names', f'({sum(1 for o in out if o.get("leader"))} at leader ends, '
          f'{sum(1 for o in out if o.get("glade"))} at glade circles)')
    diamonds(page)


def diamonds(page):
    """Chains of black diamonds (experts): a symbol at each chain's middle."""
    ds = []
    for d in page.get_drawings():
        if d['type'] in ('f', 'fs') and d.get('fill') and tuple(round(v, 2) for v in d['fill']) == (0, 0, 0) \
                and ''.join(it[0] for it in d['items']) == 'llllllcl':
            r = d['rect']
            if inside(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), CLIP):
                ds.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, max(r.width, r.height)))
    chains = []
    for q in ds:
        for ch in chains:
            if any(math.dist(q[:2], o[:2]) < 1.2 * q[2] for o in ch):
                ch.append(q)
                break
        else:
            chains.append([q])
    syms = []
    for ch in chains:
        cx, cy = sum(q[0] for q in ch) / len(ch), sum(q[1] for q in ch) / len(ch)
        syms.append({'type': 'double-diamond', 'src': px((cx, cy)), 'sizePt': 6, 'diamonds': len(ch),
                     'pts': [px(q[:2]) for q in sorted(ch, key=lambda q: (q[1], q[0]))]})
    json.dump(syms, open(os.path.join(W, 'symbols.json'), 'w'), indent=0)
    print(len(syms), 'diamond chains:', sorted(s['diamonds'] for s in syms))


if __name__ == '__main__':
    image()
    lines()
    labels()
