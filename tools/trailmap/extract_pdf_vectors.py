"""Trail lines straight from a trail-map PDF whose lines are vector strokes
(Stowe's are: the painted background is one raster, and the trail lines,
labels and symbols are vectors on top).

    python3 tools/trailmap/extract_pdf_vectors.py map.pdf \
        --clip 0,0,1730,1021 --scale 2.5 \
        --color black=0.13,0.12,0.12 --color blue=0,0.61,0.86 --color green=0,0.65,0.31 \
        --max-width 1 --image public/maps/stowe.jpg \
        --out src/data/resorts/stowe/linePolylines.json

Writes the map image (the page rendered inside --clip) and one numbered
piece per continuous run of each stroked path in a trail colour, in percent
of the image - the same format as scripts/tracePolylines.mjs, so the rest of
the pipeline (tiles, readers, review, trails:apply) is unchanged. Curves are
flattened to points; pieces break where a path jumps (label gaps).

Requires: pip install pymupdf pillow
"""
import argparse
import io
import json
import math

import pymupdf
from PIL import Image


def bezier(p0, c1, c2, p3, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n
        m = 1 - t
        out.append((m**3 * p0.x + 3 * m * m * t * c1.x + 3 * m * t * t * c2.x + t**3 * p3.x,
                    m**3 * p0.y + 3 * m * m * t * c1.y + 3 * m * t * t * c2.y + t**3 * p3.y))
    return out


def simplify(pts, eps):
    """Douglas-Peucker (a closed loop, whose ends meet, is split at its point farthest from them)."""
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    norm = math.hypot(dx, dy)
    best, idx = 0, 0
    for i in range(1, len(pts) - 1):
        if norm < 1e-9:
            d = math.hypot(pts[i][0] - ax, pts[i][1] - ay)
        else:
            d = abs(dy * (pts[i][0] - ax) - dx * (pts[i][1] - ay)) / norm
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return simplify(pts[: idx + 1], eps)[:-1] + simplify(pts[idx:], eps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--clip', required=True, help='x0,y0,x1,y1 in PDF points: the map area')
    ap.add_argument('--scale', type=float, default=2.5, help='image px per PDF point')
    ap.add_argument('--color', action='append', required=True, help='class=r,g,b (0-1, 2 decimals)')
    ap.add_argument('--max-width', type=float, default=1.0, help='ignore thicker strokes (lifts)')
    ap.add_argument('--min-width', type=float, default=0.0,
                    help='ignore thinner strokes (with --append: pick up one odd width of a colour)')
    ap.add_argument('--min-length', type=float, default=4.0, help='drop pieces shorter than this (points)')
    ap.add_argument('--max-icon', type=float, default=10.0,
                    help='drop closed runs smaller than this (points): icons such as legend symbols')
    ap.add_argument('--filled', action='store_true',
                    help='also take filled paths whose outline is a trail colour (Sugarbush draws one line so)')
    ap.add_argument('--outlined', action='store_true',
                    help='instead take lines drawn as a thin filled outline in a trail colour (a stroke converted '
                         'to a fill: its first side, up to the end cap); use with --append and only the colours '
                         'no text is printed in (black glyphs are fills too) (Sugarbush: Snowball)')
    ap.add_argument('--solid', action='store_true',
                    help='skip dashed strokes (Whistler Blackcomb draws its access routes in the parks\' orange, dashed)')
    ap.add_argument('--exclude', action='append', default=[],
                    help='x0,y0,x1,y1 in PDF points: drop runs lying wholly inside (a legend or panel printed on the map)')
    ap.add_argument('--image', help='write the map image here (omit with --append)')
    ap.add_argument('--append', action='store_true',
                    help='add pieces for these colours to an existing --out, keeping its ids')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    x0, y0, x1, y1 = map(float, a.clip.split(','))
    excludes = [tuple(map(float, e.split(','))) for e in a.exclude]
    cw, ch = x1 - x0, y1 - y0
    classes = {}
    for spec in a.color:
        name, rgb = spec.split('=')
        classes[tuple(round(float(v), 2) for v in rgb.split(','))] = name

    page = pymupdf.open(a.pdf)[a.page]
    if a.image:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(a.scale, a.scale), clip=pymupdf.Rect(x0, y0, x1, y1))
        img = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
        img.save(a.image, quality=88, optimize=True, progressive=True)
        print(f'wrote {a.image} ({img.width}x{img.height})')

    pieces = []
    for d in page.get_drawings():
        width = d.get('width') or 0
        items = d['items']
        if a.outlined:
            if d['type'] != 'f' or not d.get('fill') or max(d['rect'].width, d['rect'].height) < a.min_length:
                continue
            cls = classes.get(tuple(round(v, 2) for v in d['fill']))
            side = []
            for it in items:
                if side and it[0] == 'l' and math.dist(it[1], it[2]) < 2:
                    break  # the end cap: the rest of the outline is the line's other side
                side.append(it)
            items = side
        else:
            kinds = ('s', 'fs') if a.filled else ('s',)
            if d['type'] not in kinds or not d.get('color') or not a.min_width <= width <= a.max_width:
                continue
            if a.solid and d.get('dashes') not in (None, '[] 0'):
                continue
            cls = classes.get(tuple(round(v, 2) for v in d['color']))
        if not cls:
            continue
        run = []
        for it in items:
            if it[0] == 'l':
                start, seg = it[1], [(it[2].x, it[2].y)]
            elif it[0] == 'c':
                start, seg = it[1], bezier(*it[1:5])
            else:
                continue
            if run and math.hypot(run[-1][0] - start.x, run[-1][1] - start.y) > 0.5:
                pieces.append((cls, run))
                run = []
            if not run:
                run = [(start.x, start.y)]
            run.extend(seg)
        if run:
            pieces.append((cls, run))

    doc = json.load(open(a.out)) if a.append else {'_source': 'PDF vector strokes (tools/trailmap/extract_pdf_vectors.py)'}
    out = doc.get('polylines', []) if a.append else []
    first_new = max((p['id'] for p in out), default=-1) + 1
    for cls, run in pieces:
        length = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(run, run[1:]))
        if length < a.min_length:
            continue
        xs, ys = [p[0] for p in run], [p[1] for p in run]
        if math.dist(run[0], run[-1]) < 0.5 and math.hypot(max(xs) - min(xs), max(ys) - min(ys)) < a.max_icon:
            continue  # a closed loop this small is an icon (Okemo's legend), not a trail
        if not any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in run):
            continue  # outside the map area (Winter Park's legend line icons)
        if any(all(e[0] <= x <= e[2] and e[1] <= y <= e[3] for x, y in run) for e in excludes):
            continue  # inside a legend or panel printed over the map (Breckenridge)
        pts = simplify(run, 0.25)
        out.append({
            'id': first_new + sum(1 for p in out if p['id'] >= first_new),
            'cls': cls,
            'lengthPx': round(length * a.scale),
            'points': [[round(100 * (x - x0) / cw, 2), round(100 * (y - y0) / ch, 2)] for x, y in pts],
        })
    doc['polylines'] = out
    with open(a.out, 'w') as f:
        json.dump(doc, f)
    from collections import Counter
    print(f'wrote {a.out}: {len(out)} pieces (new from id {first_new})', dict(Counter(p["cls"] for p in out)))


if __name__ == '__main__':
    main()
