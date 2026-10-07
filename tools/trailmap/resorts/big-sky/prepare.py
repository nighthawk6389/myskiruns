"""Big Sky Resort: the map images, line pieces, printed names and symbols of its three panels, from the 2025-26
trail-map PDFs, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/big-sky/prepare.py      # regen.sh runs it

Panels (resort.py PANELS; each one's settings in panels/<panel>/resort.py, its files in work/.../<panel>/), one PDF
of one page each:
- main: the whole resort (bigsky_main.pdf).
- south-face: the South Face inset, Shedhorn, Dakota and the south side of Lone Peak (bigsky_south-face.pdf).
- bowl: the Bowl inset, Lone Peak above the Powder Seeker and the tram (bigsky_bowl.pdf).

- Images: each painting is about 1.4 px/pt, so it is swapped for a Lanczos upscale before the page is rendered
  (tools/trailmap/matte_pdf_layer.py --resample).
- Lines: strokes in the difficulty colours (and the terrain parks' orange) of the panel's widths; the main map draws
  its main green and blue routes wide, and the insets draw some lines twice at two widths: a piece that lies along a
  longer one of its colour is a copy of it and is dropped. A few lines are thin filled ribbons instead of strokes:
  their centre lines. Lines running on past an inset's frame are cut at it. The main map's real estate access trails (pink) are the village's beginner runs: read as
  green.
- Names: text (pdf_labels.py); dark names on a white halo, the halo a white copy of the text. A curved name is also
  drawn one letter at a time: pdf_resort.py joins the letters. The legend, logos and partners are left out.
- Symbols: fills. A green circle, a blue square (two side by side: advanced intermediate, a square too), a black
  diamond; two or three diamonds (expert terrain, and high exposure, also outlined in red) are a double diamond:
  drawn as one path, or one path each overlapping (a cluster of fills). Their kind is told by the width over the
  height.

Writes, per panel in $BIG_SKY_WORK/<panel> (default work/big-sky): map.png, pieces.json, printed.json (pdf_labels.py's
labels, PDF points), symbols.json ([{type, src, sizePt}], map px).
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
ROOT = os.path.abspath(os.environ.get('BIG_SKY_WORK', os.path.join(REPO, 'work/big-sky')))

GREEN, BLUE, BLACK, ORANGE = (0.22, 0.71, 0.29), (0.0, 0.58, 0.85), (0.14, 0.12, 0.13), (0.96, 0.51, 0.12)
PINK = (0.95, 0.52, 0.61)  # real estate access trails: the village's beginner runs (their green circles rate them)

SETUP = {
    'main': {
        'pdf': 'bigsky_main.pdf',
        'lines': {'green': [GREEN, PINK], 'blue': [BLUE, (0.11, 0.58, 0.82)], 'black': [BLACK], 'freestyle': [ORANGE]},
        'widths': (1.1, 5.0),
        # the logo, the legend with the partners' logos beside it, the Moonlight Basin sign at the bottom right
        'exclude': [(13, 13, 262, 262), (13, 950, 665, 1194), (2120, 1110, 2404, 1194)],
        'diamond': (5, 8.5),  # a diamond's height range, pt
    },
    'south-face': {
        'pdf': 'bigsky_south-face.pdf',
        'lines': {'blue': [(0.11, 0.58, 0.82), BLUE], 'black': [(0.0, 0.0, 0.0), BLACK]},
        'widths': (1.3, 2.5),
        'exclude': [(12, 12, 225, 232), (12, 1010, 510, 1204)],
        'diamond': (12, 20),
    },
    'bowl': {
        'pdf': 'bigsky_bowl.pdf',
        'lines': {'green': [GREEN], 'blue': [BLUE], 'black': [BLACK], 'freestyle': [ORANGE]},
        'widths': (1.0, 2.5),
        'exclude': [(12, 12, 182, 192), (620, 12, 1184, 212)],
        'diamond': (9, 14),
    },
}
CIRCLES = [GREEN, (0.23, 0.71, 0.29), (0.0, 0.63, 0.29)]
SQUARES = [BLUE, (0.11, 0.58, 0.82)]
DARK = [BLACK, (0.0, 0.0, 0.0)]


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def settings(panel):
    """The panel's resort.py (CLIP, SCALE)."""
    spec = importlib.util.spec_from_file_location(f'bs_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rgb(c):
    return ','.join(str(v) for v in c)


def col(c):
    return tuple(round(v, 2) for v in c or ())


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def image(R, W, pdf, page):
    out = os.path.join(W, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    painting = max(page.get_images(full=True), key=lambda im: im[2] * im[3])[0]
    run('python3', f'{T}/matte_pdf_layer.py', '--pdf', pdf, '--out', out, '--scale', str(R.SCALE), '--clip',
        ','.join(map(str, R.CLIP)), '--resample', str(painting))


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def outline(d):
    """A drawing's path as points (curves sampled), PDF points."""
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, b, c, e = it[1:5]
            pts += [((1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c.x + t ** 3 * e.x,
                     (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c.y + t ** 3 * e.y)
                    for t in [j / 12 for j in range(13)]]
    return pts


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


def ribbons(page, R, S):
    """Lines drawn as thin filled ribbons instead of strokes (some black ones outlined in white, some blue and pink
    ones over a white halo fill): (class, centre line) for each fill in a line colour at most 4 pt wide and at least
    15 pt long. The ribbon's outline is split at its two ends (its farthest-apart points) into two sides; the centre
    line runs midway from each point of one side to the nearest point of the other. A fill's colour matches a line
    colour within 0.01 (Oxbow's black fill is (0.137, 0.122, 0.125), its neighbours' strokes (0.137, 0.123, 0.126))."""
    classes = [(c, k) for k, cs in S['lines'].items() for c in cs]
    out = []
    for d in page.get_drawings():
        f = d.get('fill') if d['type'] in ('f', 'fs') else None
        k = next((k for c, k in classes if f and max(abs(a - b) for a, b in zip(f, c)) < 0.01), None)
        r = d['rect']
        if not k or max(r.width, r.height) < 15:
            continue
        mid = ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        if not inside(mid, R.CLIP) or any(inside(mid, e) for e in S['exclude']):
            continue
        o = dense(outline(d), 0.5)
        n = len(o)
        if n < 4:
            continue
        i, j = max(((i, j) for i in range(0, n, 2) for j in range(i + 1, n, 2)), key=lambda ij: math.dist(o[ij[0]], o[ij[1]]))
        a = o[i:j + 1]
        b = (o[j:] + o[:i + 1])[::-1]
        if len(a) < 2 or len(b) < 2:
            continue
        pairs = [(p, min(b, key=lambda q: math.dist(p, q))) for p in resample(a, 80)]
        if max(math.dist(p, q) for p, q in pairs) > 4:
            continue
        out.append((k, [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in pairs]))
    return out


def clip(pts):
    """A polyline in percent of the map cut to the map (0-100 both ways): the runs of it inside, each a list of
    points (Liang-Barsky on each segment)."""
    runs, run = [], []
    for a, b in zip(pts, pts[1:]):
        t0, t1, d = 0.0, 1.0, (b[0] - a[0], b[1] - a[1])
        for pq, qq in ((-d[0], a[0]), (d[0], 100 - a[0]), (-d[1], a[1]), (d[1], 100 - a[1])):
            if pq == 0:
                if qq < 0:
                    t0, t1 = 1.0, 0.0
                continue
            t = qq / pq
            if pq < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
        if t0 > t1:  # wholly outside
            if run:
                runs.append(run)
                run = []
            continue
        u = [round(a[0] + t0 * d[0], 2), round(a[1] + t0 * d[1], 2)]
        v = [round(a[0] + t1 * d[0], 2), round(a[1] + t1 * d[1], 2)]
        if run and (t0 > 0 or run[-1] != u):
            if t0 > 0:  # came back in: a new run
                runs.append(run)
                run = []
        if not run:
            run = [u]
        run.append(v)
        if t1 < 1:  # leaves here
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    if all(0 <= x <= 100 and 0 <= y <= 100 for x, y in pts):
        return [pts]
    return [r for r in runs if len(r) >= 2]


def lines(panel, R, S, W, pdf):
    f = os.path.join(W, 'pieces.json')
    lo, hi = S['widths']
    args = ['python3', f'{T}/extract_pdf_vectors.py', pdf, '--clip', ','.join(map(str, R.CLIP)), '--scale',
            str(R.SCALE), '--min-width', str(lo), '--max-width', str(hi), '--min-length', '1', '--out', f]
    for e in S['exclude']:
        args += ['--exclude', ','.join(map(str, e))]
    for cls, cols in S['lines'].items():
        args += [a for c in cols for a in ('--color', f'{cls}={rgb(c)}')]
    run(*args)
    doc = json.load(open(f))
    x0, y0, x1, y1 = R.CLIP
    # a few lines are drawn as thin filled ribbons, not strokes: their centre lines
    for k, c in ribbons(pymupdf.open(pdf)[0], R, S):
        doc['polylines'].append({'id': len(doc['polylines']), 'cls': k, 'lengthPx': round(length(c) * R.SCALE),
                                 'points': [[round(100 * (x - x0) / (x1 - x0), 2), round(100 * (y - y0) / (y1 - y0), 2)]
                                            for x, y in c]})
    pts = {p['id']: [(x0 + x * (x1 - x0) / 100, y0 + y * (y1 - y0) / 100) for x, y in p['points']]
           for p in doc['polylines']}
    # a piece lying along a longer piece of its colour (within 1 pt) is a copy of it: the same line drawn twice at
    # two widths, or a wide route's centre line
    P, copies = [], 0
    by_len = sorted(doc['polylines'], key=lambda p: -length(pts[p['id']]))
    kept = []
    for p in by_len:
        q = dense(pts[p['id']], 1.0)
        if any(o['cls'] == p['cls'] and all(min(seg_dist(v, a, b) for a, b in zip(pts[o['id']], pts[o['id']][1:]))
                                                < 1.0 for v in q) for o in kept):
            copies += 1
            continue
        kept.append(p)
    keep = {p['id'] for p in kept}
    clipped = 0  # pieces cut at the frame
    for p in doc['polylines']:  # in their extraction order, renumbered
        if p['id'] not in keep:
            continue
        # lines run on past an inset's frame: only the part on the map (a line leaving it and coming back, two)
        parts = clip(p['points'])
        if parts == [p['points']]:
            P.append({**p, 'id': len(P)})
            continue
        clipped += 1
        for q in parts:
            L = length([(x * (x1 - x0) / 100, y * (y1 - y0) / 100) for x, y in q])  # pt
            if L >= 1:
                P.append({**p, 'id': len(P), 'points': q, 'lengthPx': round(L * R.SCALE)})
    doc['polylines'] = P
    json.dump(doc, open(f, 'w'))
    print(f'  {panel}: {len(P)} pieces ({copies} copies of a line dropped, {clipped} cut at the frame)')


def labels(panel, R, S, W, pdf):
    f = os.path.join(W, 'text.json')
    run('python3', f'{T}/pdf_labels.py', pdf, '--out', f)
    L = [lab for lab in json.load(open(f)) if inside(lab['c'], R.CLIP)
         and not any(inside(lab['c'], e) for e in S['exclude'])]
    os.remove(f)
    json.dump(L, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {panel}: {len(L)} text objects')


def symbols(panel, R, S, W, page):
    """Symbol fills, clustered: overlapping diamonds are one symbol, and so are two squares side by side."""
    x0, y0 = R.CLIP[:2]
    lo, hi = S['diamond']
    dark, whole, squares, out = [], [], [], []
    for d in page.get_drawings():
        if d['type'] not in ('f', 'fs') or not d.get('fill'):
            continue
        r, c, kinds = d['rect'], col(d['fill']), ''.join(it[0] for it in d['items'])
        if max(r.width, r.height) > 3 * hi or not inside((r.x0, r.y0), R.CLIP) \
                or any(inside(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), e) for e in S['exclude']):
            continue
        if c in DARK and 'c' not in kinds and kinds.count('l') >= 4:
            # two or three diamonds drawn as one path (twice as wide as high, or more) are a symbol of their own
            (whole if r.width > 1.4 * r.height else dark).append(r)
        elif c in SQUARES and (kinds == 're' or kinds == 'llll') and abs(r.width - r.height) < 0.2 * r.width:
            squares.append(r)
        elif c in CIRCLES and kinds.count('c') == 4 and abs(r.width - r.height) < 0.2 * r.width \
                and lo * 0.6 <= r.height <= hi:
            out.append(('circle', r))

    def clusters(rects, gap):
        cl = []
        for r in rects:
            g = pymupdf.Rect(r.x0 - gap, r.y0 - gap, r.x1 + gap, r.y1 + gap)
            hit = [c for c in cl if any(g.intersects(q) for q in c)]
            new = [r] + [q for c in hit for q in c]
            cl = [c for c in cl if c not in hit] + [new]
        out = []
        for c in cl:
            u = pymupdf.Rect(c[0])
            for q in c:
                u |= q
            out.append(u)
        return out
    # diamonds drawn one path each, overlapping, are one symbol; a path of two or three is one already (the
    # Whitewater chutes' and Rock Creek's triple diamonds overlap each other's corners)
    for u in clusters(dark, 0.6) + whole:
        if not lo <= u.height <= hi:
            continue
        n = round((u.width / u.height - 1) / 0.55 + 1)
        if 1 <= n <= 3:
            out.append(('diamond' if n == 1 else 'double-diamond', u))
    for u in clusters(squares, 0.4 * min((q.width for q in squares), default=0)):
        if u.height <= hi:
            out.append(('square', u))
    syms = [{'type': t, 'src': [round(((u.x0 + u.x1) / 2 - x0) * R.SCALE, 2), round(((u.y0 + u.y1) / 2 - y0) * R.SCALE, 2)],
             'sizePt': round(max(u.width, u.height), 2)} for t, u in out]
    json.dump(syms, open(os.path.join(W, 'symbols.json'), 'w'), indent=0)
    tally = {}
    for s in syms:
        tally[s['type']] = tally.get(s['type'], 0) + 1
    print(f'  {panel}: {len(syms)} symbols {tally}')


if __name__ == '__main__':
    for panel, S in SETUP.items():
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        pdf = os.path.join(ROOT, S['pdf'])
        page = pymupdf.open(pdf)[0]
        image(R, W, pdf, page)
        lines(panel, R, S, W, pdf)
        labels(panel, R, S, W, pdf)
        symbols(panel, R, S, W, page)
