"""Snowbasin: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/snowbasin/prepare.py      # regen.sh runs it

The 2025-26 trail map (snowbasin.com's trail-maps page, "for Ikon, reduced": one InDesign page, James Niehues's
painting at about 2 px/pt under the vectors) draws its trail lines as 2.25 pt strokes in the three trail colours
(each drawn again at 1.13 pt over itself), the Olympic downhill courses as black lines in a yellow casing and the
"easier way down" as yellow dashes over a blue or green line. Names are text in the run's colour (AvenirNext Medium,
10.1 pt; a few at 7.9 or 9; the two-line bowl names Demi 13.5), printed along the run's line; the symbols (circle,
square, diamond, two diamonds) are fills set on the line, turned along it.

- Image: the page rendered at resort.SCALE with the painting swapped for a Lanczos upscale
  (tools/trailmap/matte_pdf_layer.py --resample); the legend (right of resort.CLIP) is left out.
- Lines: the 2.25 pt black, blue and green strokes (extract_pdf_vectors.py). One path is one piece: the map draws a
  run as one path and the runs that leave it as paths ending on it (where one path carries two runs, decisions.py
  cuts it). The area-access-gate icons, a black Π stroked at the trails' width, are dropped, and so is a piece drawn
  wholly over a longer one of its colour (Grizzly Finish's lower line and a stroke of Penny Lane's are drawn twice).
  Four blue lines are
  drawn as a filled outline instead (a stroke converted to a fill: the lines under the Blue Grouse and Orson's
  pills, Coyote Bowl's lower part, Sweet Revenge's top): each becomes a piece along its centreline (the two sides of
  the outline, from cap to cap, averaged), marked outlined. Every other fill in a trail colour (symbols, icons, the
  slow zone) is far wider than a stroke.
- Names: the trail-name text (pdf_labels.py), each with its colour as a class (green, blue, black): the colour of
  its last-drawn copy, the one on top (some names are drawn twice or more, in two colours: Beaver Slide green, then
  blue). The ﬂ ligature is written out (Wildflower).
- Symbols: pdf_symbols.py (fills in the three trail colours; two diamonds side by side are a double diamond).

Writes, in $SNOWBASIN_WORK (default work/snowbasin): map.png, pieces.json, printed.json, symbols.json.
"""
import json
import math
import os
import subprocess
import sys
import unicodedata

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('SNOWBASIN_WORK', os.path.join(REPO, 'work/snowbasin')))
PDF = os.path.join(ROOT, 'snowbasin_2025-26.pdf')
PAINTING = 73  # the painting's image xref
COLOURS = {'black': (0.0, 0.0, 0.0), 'blue': (0.0, 0.45, 0.74), 'green': (0.05, 0.69, 0.3)}
NAME_FONTS = ('AvenirNextLTPro-Medium', 'AvenirNextLTPro-Demi')  # the lifts' names are red, the lodges' AzoSans


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def col(c):
    return tuple(round(v, 2) for v in c or ())


def colour_class(c):
    """A text colour's trail class, or None (red lifts, white lodge names). Fro Zone is printed in 0.01 grey."""
    return next((k for k, v in COLOURS.items() if max(abs(a - b) for a, b in zip(col(c), v)) <= 0.011), None)


def image(R):
    out = os.path.join(ROOT, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    run('python3', '-I', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', out, '--scale', str(R.SCALE), '--clip',
        ','.join(map(str, R.CLIP)), '--resample', str(PAINTING))


def gate(p, W, H, scale):
    """An area-access-gate icon: a Π of three straight strokes, square to the page."""
    q = [(x * W / 100 / scale, y * H / 100 / scale) for x, y in p['points']]
    return (p['cls'] == 'black' and len(q) == 4 and abs(q[0][0] - q[1][0]) < 0.2 and abs(q[2][0] - q[3][0]) < 0.2
            and abs(q[1][1] - q[2][1]) < 0.2 and 5 < q[2][0] - q[1][0] < 10 and 7 < q[0][1] - q[1][1] < 12)


def flatten(d):
    """A fill's outline as points (pt): its lines and curves, in order."""
    pts = []
    for it in d['items']:
        a = it[1]
        if not pts:
            pts.append((a.x, a.y))
        if it[0] == 'l':
            pts.append((it[2].x, it[2].y))
        else:
            c1, c2, b = it[2], it[3], it[4]
            for k in range(1, 13):
                t, m = k / 12, 1 - k / 12
                pts.append((m**3 * a.x + 3 * m * m * t * c1.x + 3 * m * t * t * c2.x + t**3 * b.x,
                            m**3 * a.y + 3 * m * m * t * c1.y + 3 * m * t * t * c2.y + t**3 * b.y))
    return pts


def resample(pts, n):
    run = [0]
    for a, b in zip(pts, pts[1:]):
        run.append(run[-1] + math.dist(a, b))
    out, j = [], 0
    for k in range(n):
        s = run[-1] * k / (n - 1)
        while j < len(run) - 2 and run[j + 1] < s:
            j += 1
        f = (s - run[j]) / ((run[j + 1] - run[j]) or 1)
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])))
    return out


def centreline(d):
    """The centreline of a stroke drawn as a filled outline, and the outline's widest span across it (pt): the
    outline split at its two farthest-apart points (the caps), the two sides resampled and averaged."""
    ring = resample(flatten(d) + [flatten(d)[0]], 400)[:-1]
    n = len(ring)
    i, j = max(((i, j) for i in range(n) for j in range(i + 1, n)), key=lambda ij: math.dist(ring[ij[0]], ring[ij[1]]))
    a, b = resample(ring[i:j + 1], 60), resample((ring[j:] + ring[:i + 1])[::-1], 60)
    return [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(a, b)], max(
        math.dist(p, q) for p, q in zip(a[5:-5], b[5:-5]))


def outlined(R):
    """Pieces for the trail lines drawn as filled outlines (blue or green fills, longer than a symbol, no wider than
    a stroke and its caps)."""
    out = []
    for d in pymupdf.open(PDF)[0].get_drawings():
        k = next((k for k, v in COLOURS.items() if d['type'] == 'f' and col(d.get('fill')) == v), None)
        if k not in ('blue', 'green') or max(d['rect'].width, d['rect'].height) <= 14 or not all(
                it[0] in 'lc' for it in d['items']):
            continue
        pts, width = centreline(d)
        if width <= 4:
            out.append((k, pts))
    return out


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def drawn_over(p, q, W, H):
    """Every point of piece p lies within 1.5 px of the longer piece q, of p's colour (p is q drawn again)."""
    if p['cls'] != q['cls'] or p['lengthPx'] >= q['lengthPx']:
        return False
    qs = [(x * W / 100, y * H / 100) for x, y in q['points']]
    return all(min(seg_dist((x * W / 100, y * H / 100), a, b) for a, b in zip(qs, qs[1:])) <= 1.5
               for x, y in p['points'])


def lines(R):
    out = os.path.join(ROOT, 'pieces.json')
    run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, R.CLIP)),
        '--scale', str(R.SCALE), *[a for k, v in COLOURS.items() for a in ('--color', f'{k}={",".join(map(str, v))}')],
        '--min-width', '2.2', '--max-width', '2.4', '--min-length', '0.8', '--out', out)
    d = json.load(open(out))
    W, H = (R.CLIP[2] - R.CLIP[0]) * R.SCALE, (R.CLIP[3] - R.CLIP[1]) * R.SCALE
    gates = [p for p in d['polylines'] if gate(p, W, H, R.SCALE)]
    d['polylines'] = [p for p in d['polylines'] if p not in gates]
    twice = [p for p in d['polylines'] if any(drawn_over(p, q, W, H) for q in d['polylines'] if q is not p)]
    d['polylines'] = [p for p in d['polylines'] if p not in twice]
    for k, pts in outlined(R):
        d['polylines'].append({'id': len(d['polylines']), 'cls': k, 'outlined': True,
                               'lengthPx': round(sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) * R.SCALE),
                               'points': [[round(100 * (x - R.CLIP[0]) * R.SCALE / W, 2),
                                           round(100 * (y - R.CLIP[1]) * R.SCALE / H, 2)] for x, y in pts]})
    for i, p in enumerate(d['polylines']):  # ids in order again (pdf_resort.py indexes pieces by id)
        p['id'] = i
    json.dump(d, open(out, 'w'))
    by = {}
    for p in d['polylines']:
        by[p['cls']] = by.get(p['cls'], 0) + 1
    print(f'  wrote pieces.json: {len(d["polylines"])} pieces {by} ({len(gates)} gate icons and {len(twice)} lines '
          f'drawn twice left out, {sum(1 for p in d["polylines"] if p.get("outlined"))} lines drawn as outlines)')


def labels(R):
    f = os.path.join(ROOT, 'text.json')
    run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--out', f)
    L = []
    for lab in json.load(open(f)):
        k = colour_class(lab['color'])
        x, y = lab['c']
        if lab['font'] not in NAME_FONTS or not k or not 7.5 < lab['size'] < 14 or not (
                R.CLIP[0] <= x <= R.CLIP[2] and R.CLIP[1] <= y <= R.CLIP[3]):
            continue
        L.append({**lab, 'text': unicodedata.normalize('NFKC', lab['text']), 'color': k})
    # a name drawn in several copies (a halo pass, a second colour): every copy takes the colour of the last drawn
    for lab in L:
        same = [o for o in L if o['text'].replace(' ', '') == lab['text'].replace(' ', '')
                and math.dist(o['c'], lab['c']) < 1]
        lab['color'] = max(same, key=lambda o: o['seq'])['color']
    json.dump(L, open(os.path.join(ROOT, 'printed.json'), 'w'), indent=0)
    os.remove(f)
    tally = {}
    for lab in L:
        tally[lab['color']] = tally.get(lab['color'], 0) + 1
    print(f'  {len(L)} name labels (copies included) {tally}')


def symbols(R):
    run('python3', '-I', f'{T}/pdf_symbols.py', PDF, '--clip', ','.join(map(str, R.CLIP)), '--scale', str(R.SCALE),
        '--circle', ','.join(map(str, COLOURS['green'])), '--square', ','.join(map(str, COLOURS['blue'])),
        '--diamond', ','.join(map(str, COLOURS['black'])), '--max-size', '14', '--max-diamond', '9',
        '--out', os.path.join(ROOT, 'symbols.json'))
    S = json.load(open(os.path.join(ROOT, 'symbols.json')))
    by = {}
    for s in S:
        by[s['type']] = by.get(s['type'], 0) + 1
    print(f'  {len(S)} symbols {by}')


def main():
    sys.path.insert(0, HERE)
    import resort as R
    image(R)
    lines(R)
    labels(R)
    symbols(R)


if __name__ == '__main__':
    main()
