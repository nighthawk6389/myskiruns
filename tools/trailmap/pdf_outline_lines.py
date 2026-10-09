"""Line pieces from a trail-map PDF whose trail lines are filled outlines (the artwork's strokes converted to fills:
Heavenly's 2022-23 PDF, Mt. Bachelor's 2025-26), read by their centre lines; recipe C in docs/trail-map-playbook.md.
The method is Heavenly's (tools/trailmap/resorts/heavenly/prepare.py, which keeps its own copy), as a tool.

    python3 tools/trailmap/pdf_outline_lines.py map.pdf --clip 355,0,1904,1080 --scale 3 \\
        --color blue=0.07,0.62,0.86 --color green=0.06,0.58,0.28 --color black=0.01,0.02,0.02 \\
        --max-width 1.3 --dark black --exclude 0,0,354,1080 --out work/<id>/pieces.json

Each fill in a --color is split into its outlines (subpaths). An outline is read by its centre line: split at its
two farthest-apart points into two sides, each point of one side paired with the nearest of the other; its width
is the median pair distance. Outlines wider than --max-width (squares, circles, diamonds, label boxes) are left out,
and so are arrowheads (two curved sides and a notch: items c l l c). A blue or green outline with more area than one
line of its length has (two lines drawn as one, an arrowhead merged into its line) is read by its skeleton instead,
one piece per branch, and so is one that reads wide but whose mean width (twice its area over its perimeter) is a
line's: lines meeting at a junction, drawn as one outline. A dashed line's dashes (each under --dash pt, one after
another in one fill, within 3.5 pt) are chained into one piece. A --dark colour's outlines are lines only if at least --dark-min pt long (the names'
letters are outlines of that colour too); any other line shorter than --min-length is a stray mark. A piece lying
along a longer piece of its colour (within 0.5 pt) is a copy and is dropped. Pieces are in drawing order, in
percent of the --clip area (the same format as extract_pdf_vectors.py, so pdf_resort.py reads them alike).
With --glyphs and --letters, the fills read as letters of the names are left out first (an I or a hyphen in a run's
colour is as thin as its line: Mt. Bachelor's names).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import raster_lines as RL  # noqa: E402


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
    """An outline's centre line and its median width (pt)."""
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


def thin(items):
    """An outline's mean width: twice its area over its perimeter (a line's width; half a square's side)."""
    o = outline(items)
    return 2 * area(o) / max(1e-9, length(o + o[:1]))


def skeleton(items, z=16):
    """A branched outline's skeleton, drawn at z px per pt, spurs under 2.5 pt pruned, joined straight through its
    junctions (raster_lines.py): one centre line per branch, in pt."""
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


def chained(segs, dash):
    """One fill's centre lines, in drawing order: a dashed line's dashes (each shorter than dash), one after another
    and each within 3.5 pt of the last, chained into one."""
    out = []
    for c in segs:
        L, prev = length(c), (out[-1] if out else None)
        if prev and L < dash and prev['last'] < dash:
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


def letter_fills(a):
    """The drawing orders of the fills that are letters of the names (--glyphs from pdf_glyphs.py collect, each shape
    read in --letters as a character other than *): a letter I or a hyphen is an outline as thin as a line."""
    if not a.glyphs:
        return set()
    from pdf_glyphs import letter
    table = json.load(open(a.letters))
    return {g['seq'] for g in json.load(open(a.glyphs))['glyphs'] if letter(table, g) not in (None, '*')}


def line_outlines(page, a, colours, excludes, clip):
    """Every line: (class, drawing order, centre line in pt, its length)."""
    lines = []
    letters = letter_fills(a)
    for d in page.get_drawings():
        if d['seqno'] in letters:
            continue
        f = d.get('fill') if d['type'] == 'f' else None
        k = next((k for k, c in colours.items() if f and max(abs(x - y) for x, y in zip(f, c)) < 0.01), None)
        r = d['rect']
        if k is None or any(e[0] <= r.x0 and r.x1 <= e[2] and e[1] <= r.y0 and r.y1 <= e[3] for e in excludes):
            continue
        if not (clip[0] <= (r.x0 + r.x1) / 2 <= clip[2] and clip[1] <= (r.y0 + r.y1) / 2 <= clip[3]):
            continue
        segs = []
        for sp in subpaths(d):
            if ''.join(it[0] for it in sp) == 'cllc':
                continue  # an arrowhead (two curved sides, a notch at the back)
            c, w = centre(sp)
            if c and w <= a.max_width and length(c) >= max(1.5, 2.5 * w):
                if k not in a.dark and length(c) >= a.dash and area(outline(sp)) > 1.15 * length(c) * w:
                    segs += [b for b in skeleton(sp) if length(b) >= 1.5]  # more outline than one line has: branched
                else:
                    segs.append(c)
            elif c and thin(sp) <= a.max_width:
                # lines meeting at a junction, drawn as one outline: the farthest-apart points split it across two
                # branches, so its centre line reads wide; its mean width (twice its area over its perimeter) is a
                # line's
                segs += [b for b in skeleton(sp) if length(b) >= 1.5]
        for ch in chained(segs, a.dash):
            L = length(ch['pts'])
            if (k in a.dark and L < a.dark_min) or (len(ch['parts']) == 1 and L < a.min_length):
                continue  # a letter, a lone dash or an arrowhead
            lines.append((k, d['seqno'], ch['pts'], L))
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('pdf')
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--clip', required=True, help='x0,y0,x1,y1 in PDF points: the map area')
    ap.add_argument('--scale', type=float, required=True, help='map px per PDF point')
    ap.add_argument('--color', action='append', required=True, help='class=r,g,b (0-1)')
    ap.add_argument('--max-width', type=float, default=1.3, help='pt: wider outlines are symbols, boxes, areas')
    ap.add_argument('--min-length', type=float, default=3.0, help='pt: a shorter single outline is a stray mark')
    ap.add_argument('--dark', action='append', default=[],
                    help="a class whose outlines are lines only if long (the names' letters are that colour too)")
    ap.add_argument('--dark-min', type=float, default=25.0, help='pt: the shortest line of a --dark class')
    ap.add_argument('--dash', type=float, default=5.0, help='pt: an outline shorter than this may be a dash')
    ap.add_argument('--exclude', action='append', default=[],
                    help='x0,y0,x1,y1 pt: drop fills lying wholly inside (a legend, a panel)')
    ap.add_argument('--glyphs', help="pdf_glyphs.py collect's glyphs.json: with --letters, its letters are no lines")
    ap.add_argument('--letters', help='the letters file the glyph shapes were read into')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    clip = [float(v) for v in a.clip.split(',')]
    colours = {}
    for c in a.color:
        k, v = c.split('=')
        colours[k] = tuple(float(x) for x in v.split(','))
    excludes = [[float(v) for v in e.split(',')] for e in a.exclude]
    page = pymupdf.open(a.pdf)[a.page]
    L = line_outlines(page, a, colours, excludes, clip)
    kept, copies = [], 0
    for cls, seq, pts, n in sorted(L, key=lambda l: -l[3]):
        q = dense(pts, 1.0)
        if any(o[0] == cls and all(line_dist(v, o[2]) < 0.5 for v in q) for o in kept):
            copies += 1
            continue
        kept.append((cls, seq, pts, n))
    kept.sort(key=lambda l: (l[1], l[2][0]))  # in drawing order
    W, H = (clip[2] - clip[0]) * a.scale, (clip[3] - clip[1]) * a.scale
    P = []
    for cls, seq, pts, n in kept:
        px = simplify([((x - clip[0]) * a.scale, (y - clip[1]) * a.scale) for x, y in pts], 0.3)
        P.append({'id': len(P), 'cls': cls, 'lengthPx': round(length(px)),
                  'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in px]})
    json.dump({'_source': f'outlined lines of {os.path.basename(a.pdf)} (tools/trailmap/pdf_outline_lines.py)',
               'polylines': P}, open(a.out, 'w'))
    by = {}
    for p in P:
        by[p['cls']] = by.get(p['cls'], 0) + 1
    print(f'wrote {a.out}: {len(P)} pieces {by} ({copies} copies dropped)')


if __name__ == '__main__':
    main()
