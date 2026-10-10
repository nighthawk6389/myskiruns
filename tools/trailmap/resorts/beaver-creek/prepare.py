"""Beaver Creek: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/beaver-creek/prepare.py      # regen.sh runs it

- Image: the 2025-26 image's map (resort.BOX), as it is (4.28 px per PDF point).
- Lines: the 2023 PDF's 0.66 pt strokes in green, blue and black (solid: runs; dashed: roads and catwalks; West
  Fall Road's dashes are in the squares' blue), and its 0.71 pt dotted green and blue strokes (homeowner skiways);
  lifts are maroon, the boundary orange, closures red hatching; the legend left out; on the image's grid
  (resort.CLIP and SCALE come from the registration). Two glades are drawn as a brown line, the legend's Gladed
  Zone (Three Tree Gully, Jack Rabbit Alley): pieces too, after the strokes'. One green drawing holds a skiway's dots as filled shapes, not
  a dotted stroke (Creekside Skiway's and the skiway above it): dots() chains them into pieces, after the strokes'.
- Names: outlined glyphs in the map's near-black (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on
  its contact sheets, is in letters.json here); each run's symbol is printed on its line by the name: green circles,
  blue squares, black diamonds (two: expert; two holding E and X: extreme terrain).

Writes, in $BEAVER_CREEK_WORK (default work/beaver-creek): map.png, pieces.json, glyphs.json, printed.json ({labels,
symbols}, PDF points).
"""
import json
import math
import os
import subprocess
import sys

import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import BOX, CLIP, SCALE  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('BEAVER_CREEK_WORK', os.path.join(REPO, 'work/beaver-creek')))
PDF = os.path.join(W, 'beavercreek_2023.pdf')
IMG = os.path.join(W, 'beavercreek_2025-26.png')
LETTERS = os.path.join(HERE, 'letters.json')

GREEN, BLUE, DARK = (0, 0.65, 0.32), (0, 0.62, 0.88), (0.14, 0.12, 0.13)
SQUARE = (0, 0.61, 0.86)  # the blue squares' fill (a shade off the blue lines')
GLADED = (0.68, 0.36, 0.06)  # the gladed zones' brown lines
LINES = {'green': GREEN, 'blue': BLUE, 'black': DARK}
LEGEND = (18, 750, 397, 911)  # PDF points: the map key's box


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


def lines():
    args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
            '--min-width', '0.6', '--max-width', '0.75', '--min-length', '1', '--exclude', ','.join(map(str, LEGEND)),
            '--out', os.path.join(W, 'pieces.json')]
    for cls, c in LINES.items():
        args += ['--color', f'{cls}={rgb(c)}']
    args += ['--color', f'blue={rgb(SQUARE)}']  # West Fall Road's dashes are drawn in the squares' blue
    print(' ', run(*args).strip().replace(W + '/', ''))
    # the gladed zones' brown lines (the legend's Gladed Zone: Three Tree Gully's and Jack Rabbit Alley's), after
    args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
            '--min-width', '0.6', '--max-width', '1.0', '--min-length', '1', '--exclude', ','.join(map(str, LEGEND)),
            '--color', f'black={rgb(GLADED)}', '--append', '--out', os.path.join(W, 'pieces.json')]
    print(' ', run(*args).strip().replace(W + '/', ''))


def dots():
    """Skiways drawn as filled dots (one fill of many tiny closed shapes, in the trail colours): each dot's centre,
    chained in drawing order into a piece wherever the next dot is within 4 pt; appended to pieces.json."""
    f = os.path.join(W, 'pieces.json')
    d = json.load(open(f))
    x0, y0, x1, y1 = CLIP
    cw, ch = x1 - x0, y1 - y0
    colours = {tuple(round(v, 2) for v in c): cls for cls, c in LINES.items()}
    added = 0
    for dr in pymupdf.open(PDF)[0].get_drawings():
        cls = colours.get(tuple(round(v, 2) for v in dr['fill'])) if dr.get('fill') and not dr.get('color') else None
        if not cls or len(dr['items']) < 40:
            continue
        shapes, cur, last = [], [], None  # the closed shapes: a new one wherever an item doesn't start at the last end
        for it in dr['items']:
            a, b = it[1], it[-1]
            if last is not None and math.dist((a.x, a.y), last) > 0.01:
                shapes.append(cur)
                cur = []
            cur += [(a.x, a.y), (b.x, b.y)]
            last = (b.x, b.y)
        shapes.append(cur)
        if max(max(p[0] for p in sh) - min(p[0] for p in sh) for sh in shapes) > 1.5:
            continue  # not dots
        centres = [(sum(p[0] for p in sh) / len(sh), sum(p[1] for p in sh) / len(sh)) for sh in shapes]
        runs, run = [], [centres[0]]
        for c in centres[1:]:
            if math.dist(c, run[-1]) > 4:
                runs.append(run)
                run = []
            run.append(c)
        runs.append(run)
        for run in runs:
            if len(run) < 3:
                continue
            length = sum(math.dist(a, b) for a, b in zip(run, run[1:]))
            d['polylines'].append({'id': len(d['polylines']), 'cls': cls, 'lengthPx': round(length * SCALE),
                                   'points': [[round(100 * (x - x0) / cw, 2), round(100 * (y - y0) / ch, 2)]
                                              for x, y in run]})
            added += 1
    json.dump(d, open(f, 'w'))
    print(f'  {added} pieces of dots appended to pieces.json')


def glyphs():
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', os.path.join(W, 'glyphs.json'),
            '--exclude', ','.join(map(str, LEGEND))]
    for cls, c in (('black', DARK), ('blue', SQUARE), ('green', GREEN)):
        args += ['--color', f'{cls}={rgb(c)}']
    print(' ', run(*args).strip())


def labels():
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', os.path.join(W, 'glyphs.json'),
                   '--letters', LETTERS, '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green',
                   '--turned', 'nu', '--turned-hole', '69', '--rect-squares').strip().replace('\n', '\n  '))
    d = json.load(open(f))
    x0, y0, x1, y1 = CLIP
    labs = [{**lab, 'font': 'glyph'} for lab in d['labels'] if x0 <= lab['c'][0] <= x1 and y0 <= lab['c'][1] <= y1]
    syms = [s for s in d['symbols'] if x0 <= s['c'][0] <= x1 and y0 <= s['c'][1] <= y1]
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    lines()
    dots()
    glyphs()
    if os.path.exists(LETTERS):
        labels()
