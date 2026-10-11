"""Mount Snow: the map image, line pieces and printed names, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/mount-snow/prepare.py      # regen.sh runs it

- Image: the 2025-26 image's map (resort.BOX), as it is (2.08 px per point of this season's page).
- Lines: the 2023-24 PDF's 1.15 pt strokes in the runs' colours, green, blue and black, and orange (the freestyle
  terrain's lines: the parks', Roller Coaster's natural terrain), on the image's grid (resort.CLIP and SCALE come from
  the registration, resort.AFFINE), less those this season's inset covers; then the inset's own 0.61 pt green, blue
  and black strokes, put on the grid through resort.INSET_AFFINE.
- Names: the 2024-25 uphill map's text in the condensed Futura at 16 pt, each name printed twice: once in the run's
  colour (green, blue, orange for the parks) and once in black under it (a two-line name's black copy as two labels);
  a label whose characters all lie on a coloured label's, or on a longer one's, is a copy and dropped, so a black name
  is a black run's. Each character is put on the 2023-24 page's points through the image (resort.UPHILL_AFFINE, then
  resort.AFFINE inverted), as pdf_resort.py reads the labels in those.

Writes, in $MOUNT_SNOW_WORK (default work/mount-snow): map.png, pieces.json, printed.json ({labels, symbols}, 2023-24
PDF points).
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import AFFINE, BOX, CLIP, INSET, INSET_AFFINE, INSET_COVER, SCALE, UPHILL_AFFINE  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('MOUNT_SNOW_WORK', os.path.join(REPO, 'work/mount-snow')))
PDF = os.path.join(W, 'mountsnow_2023-24.pdf')
UPHILL = os.path.join(W, 'mountsnow_uphill_2024-25.pdf')
IMG = os.path.join(W, 'mountsnow_2025-26.png')
LINES = {'green': (0.0, 0.65, 0.32), 'blue': (0.0, 0.61, 0.86), 'black': (0.14, 0.12, 0.13), 'park': (0.98, 0.61, 0.14)}
NAME_COLOURS = {(0.0, 0.65, 0.32): 'green', (0.0, 0.61, 0.86): 'blue', (0.14, 0.12, 0.13): 'black',
                (0.98, 0.61, 0.14): 'orange'}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def image():
    out = os.path.join(W, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        Image.open(IMG).convert('RGB').crop(BOX).save(out)
    return out


def lines():
    f = os.path.join(W, 'pieces.json')
    args = ['python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip=' + ','.join(map(str, CLIP)), '--scale',
            str(SCALE), '--min-width', '1.0', '--max-width', '1.3', '--min-length', '1', '--exclude',
            ','.join(map(str, INSET_COVER)), '--out', f]
    for cls, c in LINES.items():
        args += ['--color', f'{cls}={rgb(c)}']
    print(' ', run(*args).strip().splitlines()[-1].replace(W + '/', ''))
    # the inset's strokes, on the inset's own grid (percent of its frame), then put on the map's
    g = os.path.join(W, 'inset_pieces.json')
    s = (INSET_AFFINE[0] + INSET_AFFINE[4]) / 2
    args = ['python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip=' + ','.join(map(str, INSET)), '--scale',
            str(s), '--min-width', '0.55', '--max-width', '0.7', '--min-length', '1', '--out', g]
    for cls in ('green', 'blue'):
        args += ['--color', f'{cls}={rgb(LINES[cls])}']
    args += ['--color', 'black=0.01,0.02,0.02']  # Bear Trap's line beside its lift
    run(*args)
    d, ins = json.load(open(f)), json.load(open(g))['polylines']
    x0, y0, x1, y1 = INSET
    mw, mh = BOX[2] - BOX[0], BOX[3] - BOX[1]
    for p in ins:
        pts = []
        for u, v in p['points']:  # percent of the inset frame -> its points -> image px -> map px
            x, y = x0 + u * (x1 - x0) / 100, y0 + v * (y1 - y0) / 100
            X = INSET_AFFINE[0] * x + INSET_AFFINE[1] * y + INSET_AFFINE[2] - BOX[0]
            Y = INSET_AFFINE[3] * x + INSET_AFFINE[4] * y + INSET_AFFINE[5] - BOX[1]
            pts.append([round(100 * X / mw, 3), round(100 * Y / mh, 3)])
        d['polylines'].append({'id': len(d['polylines']), 'cls': p['cls'], 'lengthPx': p['lengthPx'], 'points': pts})
    json.dump(d, open(f, 'w'))
    print(f'  {len(ins)} inset pieces appended')


def to_page(q):
    """An uphill-map point (pt) on the 2023-24 page (pt), through the image."""
    a = UPHILL_AFFINE
    X, Y = a[0] * q[0] + a[1] * q[1] + a[2], a[3] * q[0] + a[4] * q[1] + a[5]
    return [round((X - AFFINE[2]) / AFFINE[0], 2), round((Y - AFFINE[5]) / AFFINE[4], 2)]


def names():
    f = os.path.join(W, 'labels_raw.json')
    run('python3', '-I', f'{T}/pdf_labels.py', UPHILL, '--out', f)
    raw = [l for l in json.load(open(f)) if l['font'] == 'Futura-CondensedMedium' and abs(l['size'] - 16) < 0.1
           and tuple(l['color']) in NAME_COLOURS]
    for l in raw:
        l['color'] = NAME_COLOURS[tuple(l['color'])]

    def on(l, o):  # every character of l on one of o's
        return all(any(math.dist(p, q) < 1.0 for q in o['pts']) for p in l['pts'])

    def copy_of(l):  # a black copy under a coloured name, or a part of a longer label printed over it (the
        # black copies of SWITCH BACK, SECOND THOUGHTS and LITTLE STEEP are their two lines apart)
        return any(o is not l and ((l['color'] == 'black' and o['color'] != 'black') or len(o['pts']) > len(l['pts']))
                   and on(l, o) for o in raw)
    labels = [l for l in raw if not copy_of(l)]
    for l in labels:
        l['pts'] = [to_page(q) for q in l['pts']]
        l['c'] = to_page(l['c'])
    return labels


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    lines()
    labels = names()
    json.dump({'labels': labels, 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labels)} labels')
