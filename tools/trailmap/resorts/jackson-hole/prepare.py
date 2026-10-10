"""Jackson Hole Mountain Resort: the map image, line pieces and printed names, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/jackson-hole/prepare.py      # regen.sh runs it

The resort publishes its 2025-26 trail map as one image (jacksonhole.com's winter trail map page: a 3000x1900 PNG,
James Niehues's painting), with no PDF and no interactive map. Each run is a thin line (one or two px) in its colour,
green, blue or black, solid or dashed, its name printed in a gap of it in the same colour (no symbols: the name's
colour is the rating). The names are solid and the colour masks find their letters; the lines blend into the snow and
the masks find only stretches of them (raster_lines.py traced them into 136 pieces, a third of the runs), so they are
read instead, as Whitefish's are: names.py holds each name's label and its run's line as points read on crops.

- Image: the PNG as it is (resort.CLIP is the whole image, 1 px per unit).
- Pieces: each line of names.py routed along its painted line between its points (tools/trailmap/route_trace.py with
  raster_lines.py's jackson-hole masks: the cheapest path over a grid low on the run's colour, high elsewhere, so it
  crosses only short gaps: its label's letters are in its colour too), one piece per line, carrying its trail's name
  (resort.GROUPED).
- Labels: names.py's, each moved onto its letters: the letter-sized parts of its colour's mask within LETTER_REACH px
  of the line through its points, in order along it (a name printed on two lines, or a park's, keeps its point).

Writes, in $JACKSON_HOLE_WORK (default work/jackson-hole): map.png, pieces.json, printed.json ({labels, symbols},
map px).
"""
import collections
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'tools/trailmap'))
import names  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('JACKSON_HOLE_WORK', os.path.join(REPO, 'work/jackson-hole')))
SOURCE = 'trailmap_2025-26.png'
CLS = {'green': 'green', 'blue': 'blue', 'black': 'black', 'park': 'blue'}
LETTER = (5, 22)  # px: a letter's height or width
LETTER_REACH = 12  # px: a letter's centre from the line through the label's points
LABEL_END = 10  # px: a line's point at one of its label's points


def image():
    out = os.path.join(W, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        Image.open(os.path.join(W, SOURCE)).convert('RGB').save(out)
    return out


def route(R, cls, line, ends):
    """The line routed along the painted one between its points, except across its own label (two points in a row
    at its label's points, its first and last letters or a bend, within LABEL_END px): straight there (a route
    through the letters zigzags)."""
    out = []
    i = 0
    while i < len(line) - 1:
        a, b = line[i], line[i + 1]
        at = [any(math.dist(q, e) <= LABEL_END for e in ends) for q in (a, b)]
        if all(at):
            seg = [list(a), list(b)]
            i += 1
        else:
            j = i + 1
            while j < len(line) - 1 and not (any(math.dist(line[j], e) <= LABEL_END for e in ends) and
                                             any(math.dist(line[j + 1], e) <= LABEL_END for e in ends)):
                j += 1
            seg = R.route(cls, line[i:j + 1])
            i = j
        out += seg if not out else seg[1:]
    return [[round(x), round(y)] for x, y in out]


def pieces(png):
    from route_trace import Router
    R = Router(png, 'jackson-hole')
    H, Wd = R.A.shape[:2]
    out = []
    for name, colour, labels, lines in names.READING:
        cls = CLS[colour]
        ends = [q for lab in labels if len(lab) >= 2 for q in lab]
        for line in lines:
            # a line given 'as read' is taken as it is, not routed (where the route would snap onto another
            # label's letters or the trees' shadows close by)
            pts = [list(q) for q in line[1:]] if line[0] == 'as read' else route(R, cls, line, ends)
            out.append({'id': len(out), 'cls': cls, 'name': name,
                        'lengthPx': round(sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))),
                        'points': [[round(100 * x / Wd, 3), round(100 * y / H, 3)] for x, y in pts]})
    json.dump({'_source': "Jackson Hole 2025-26: names.py's lines routed along the painted ones (prepare.py)",
               'polylines': out}, open(os.path.join(W, 'pieces.json'), 'w'))
    print(f'  {len(names.READING)} names, {len(out)} lines {dict(collections.Counter(p["cls"] for p in out))}')
    return R


def letters(R):
    """Per colour: the centres of its mask's letter-sized parts."""
    import cv2
    out = {}
    for cls, m in R.M.items():
        n, _lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        ext = np.maximum(st[:, 2], st[:, 3])
        ok = (ext >= LETTER[0]) & (ext <= LETTER[1]) & (st[:, 4] >= 10)
        ok[0] = False
        out[cls] = cen[ok]
    return out


def on_letters(pts, cen):
    """The label's letters: centres within LETTER_REACH of the polyline through pts, ordered along it."""
    found = []
    acc = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.dist((ax, ay), (bx, by)) or 1e-9
        ux, uy = (bx - ax) / L, (by - ay) / L
        t = (cen[:, 0] - ax) * ux + (cen[:, 1] - ay) * uy
        d = np.abs((cen[:, 0] - ax) * uy - (cen[:, 1] - ay) * ux)
        sel = (t >= -LETTER_REACH) & (t <= L + LETTER_REACH) & (d <= LETTER_REACH)
        found += [(acc + float(tt), (float(x), float(y))) for tt, (x, y) in zip(t[sel], cen[sel])]
        acc += L
    seen, out = set(), []
    for _t, c in sorted(found):
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def spread(pts, pitch=12):
    """Points along the polyline through pts, about pitch px apart."""
    out = [tuple(pts[0])]
    for a, b in zip(pts, pts[1:]):
        n = max(1, round(math.dist(a, b) / pitch))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]
    return out


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def printed(R):
    cen = letters(R)
    labs, moved = [], 0
    for k, (name, colour, labels, _lines) in enumerate(names.READING):
        for j, pts in enumerate(labels):
            got = on_letters(pts, cen[CLS[colour]]) if len(pts) >= 2 and colour != 'park' else []
            # kept only if they span the label as read (other marks in its colour nearby, the slow zones' green
            # hatching, would stretch it),
            # and only if they don't zigzag (letters of a label printed close beside it: the Alta Chutes')
            if (len(got) >= 2 and math.dist(got[0], pts[0]) <= LABEL_END * 3 and
                    math.dist(got[-1], pts[-1]) <= LABEL_END * 3 and
                    length(got) <= 1.25 * length(pts) + 2 * LABEL_END):
                pts, moved = got, moved + 1
            elif len(pts) >= 2:  # as read: one point per letter's width (pdf_resort.py pushes a stretch's ends out
                # by most of the spacing between its label's points)
                pts = spread(pts)
            pts = [[round(x, 1), round(y, 1)] for x, y in pts]
            labs.append({'seq': 100 * k + j, 'text': name, 'color': colour if colour != 'park' else None,
                         'pts': pts, 'c': [round(sum(p[0] for p in pts) / len(pts), 1),
                                           round(sum(p[1] for p in pts) / len(pts), 1)]})
    json.dump({'labels': labs, 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labs)} labels ({moved} moved onto their letters)')


def main():
    os.makedirs(W, exist_ok=True)
    png = image()
    R = pieces(png)
    printed(R)


if __name__ == '__main__':
    main()
