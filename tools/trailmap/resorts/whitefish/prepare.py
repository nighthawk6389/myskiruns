"""Whitefish Mountain Resort: each panel's map image and line pieces, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/whitefish/prepare.py      # regen.sh runs it

The resort publishes its trail maps as web JPEGs only (skiwhitefish.com's trail-maps page: the 2025-26 front side,
1600x913, and the 2024-25 North Side and Hellroaring Basin insets, 1219x900; James Niehues's paintings), with no
PDF and no interactive map. Their thin trail lines are blurred into the painting by the JPEG, and many are drawn in
a casing (the "easiest route down" yellow, the runs lit for night skiing purple), so the colour masks of
raster_lines.py find only part of them. The lines are read instead: names.py holds each name as printed with its
label's position and symbol, and its run's line as rough points read on zoomed grid crops.

- Images: each JPEG upscaled 2x (Lanczos), the grid names.py's points are read on (map.png in each panel's folder).
- Pieces: each line of names.py routed along its painted line between its waypoints (tools/trailmap/route_trace.py:
  the cheapest path over a cost grid low on the run's colour, by raster_lines.py's whitefish masks, and on the
  yellow and purple casings of the blue and green runs, high elsewhere, so it crosses only short gaps: a label in
  the line, a symbol), one piece per line, carrying its trail's name (resort.GROUPED: pdf_resort.py names the piece
  by it).
- Names: names.py's labels, as resort.EXTRA (pdf_resort.py: names printed some other way, with their symbol);
  printed.json is empty.

Writes, per panel in $WHITEFISH_WORK/<panel> (default work/whitefish): map.png, pieces.json, printed.json.
"""
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/trailmap'))
from route_trace import Router  # noqa: E402

ROOT = os.path.abspath(os.environ.get('WHITEFISH_WORK', os.path.join(REPO, 'work/whitefish')))
SOURCES = {'front-side': 'W2526_FrontSide_Web.jpg', 'north-side': 'W2425_NorthSide.jpg',
           'hellroaring': 'W2425_OtherSides.jpg'}
UPSCALE = 2
CLS = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black', 'park': 'blue'}


def image(panel):
    out = os.path.join(ROOT, panel, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        im = Image.open(os.path.join(ROOT, SOURCES[panel])).convert('RGB')
        im.resize((im.width * UPSCALE, im.height * UPSCALE), Image.LANCZOS).save(out)
    return out


def pieces(panel, reading, png):
    R = Router(png, 'whitefish')
    H, W = R.A.shape[:2]
    out = []
    for name, _at, symbol, lines, *rest in reading:
        cls = rest[0] if rest else CLS[symbol]
        for line in lines:
            pts = R.route(cls, line, casing=cls != 'black')
            out.append({'id': len(out), 'cls': cls, 'name': name,
                        'lengthPx': round(sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))),
                        'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in pts]})
    json.dump({'_source': f'Whitefish {panel}: names.py lines snapped onto the painted lines (prepare.py)',
               'polylines': out}, open(os.path.join(ROOT, panel, 'pieces.json'), 'w'))
    json.dump({'labels': [], 'symbols': []}, open(os.path.join(ROOT, panel, 'printed.json'), 'w'))
    by = {}
    for p in out:
        by[p['cls']] = by.get(p['cls'], 0) + 1
    print(f'  {panel}: {len(reading)} names, {len(out)} lines {by}')


def main():
    sys.path.insert(0, HERE)
    import names
    for panel in SOURCES:
        os.makedirs(os.path.join(ROOT, panel), exist_ok=True)
        if panel in names.READING:
            pieces(panel, names.READING[panel], image(panel))


if __name__ == '__main__':
    main()
