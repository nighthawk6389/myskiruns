"""Mt. Hood Meadows: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/mt-hood-meadows/prepare.py      # regen.sh runs it

- Image: the 2025-26 PDF's page 2 (the map; page 1 is its back) rendered at resort.SCALE, from the left text
  column's edge (resort.CLIP). The painting is all vectors (some 226,000 drawings, no image), so it takes a while.
- Lines: its 0.69 pt strokes in the runs' green, blue and black (the 2.78 pt green dots are uphill routes, the
  2.78 pt black dots the area's boundary; lifts are maroon dashes; the legend left out).
- Names: outlined glyphs in the map's near-black (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on
  its contact sheets, is in letters.json here: Beaver Creek's, the same font, and the shapes this map adds; one
  name's glyphs, Memorial Bowl's, a shade darker), and the one name set as text (Dallas Bowl, pdf_labels.py); each
  run's symbol is printed on its line by the name: green circles, blue squares, black diamonds with rounded corners
  (two overlapping in one fill: a double diamond).

Writes, in $MT_HOOD_MEADOWS_WORK (default work/mt-hood-meadows): map.png, pieces.json, glyphs.json, printed.json
({labels, symbols}, PDF points).
"""
import json
import os
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('MT_HOOD_MEADOWS_WORK', os.path.join(REPO, 'work/mt-hood-meadows')))
PDF = os.path.join(W, 'hood_2025-26.pdf')
PAGE = 1
LETTERS = os.path.join(HERE, 'letters.json')

GREEN, BLUE, DARK = (0, 0.65, 0.32), (0, 0.61, 0.86), (0.14, 0.12, 0.13)
DARKER = (0, 0.09, 0.06)  # one name's glyphs (Memorial Bowl's) are a shade darker than the others'
LINES = {'green': GREEN, 'blue': BLUE, 'black': DARK}
LEGEND = (1150, 900, 1440, 1224)  # PDF points: the map key's box


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
        page = pymupdf.open(PDF)[PAGE]
        page.get_pixmap(clip=pymupdf.Rect(*CLIP), matrix=pymupdf.Matrix(SCALE, SCALE), alpha=False).save(out)


def lines():
    args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--page', str(PAGE), '--clip', ','.join(map(str, CLIP)),
            '--scale', str(SCALE), '--min-width', '0.6', '--max-width', '0.8', '--min-length', '1',
            '--exclude', ','.join(map(str, LEGEND)), '--out', os.path.join(W, 'pieces.json')]
    for cls, c in LINES.items():
        args += ['--color', f'{cls}={rgb(c)}']
    print(' ', run(*args).strip().replace(W + '/', ''))


def glyphs():
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--page', str(PAGE), '--out',
            os.path.join(W, 'glyphs.json'), '--max-size', '12', '--exclude', ','.join(map(str, LEGEND)),
            '--exclude', f'0,0,{CLIP[0]},{CLIP[3]}']
    for cls, c in (('black', DARK), ('black', DARKER), ('blue', BLUE), ('green', GREEN)):
        args += ['--color', f'{cls}={rgb(c)}']
    print(' ', run(*args).strip())


def labels():
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', os.path.join(W, 'glyphs.json'),
                   '--letters', LETTERS, '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green',
                   '--turned', 'nu', '--turned-hole', '69', '--rounded', '--overlapped-doubles'
                   ).strip().replace('\n', '\n  '))
    d = json.load(open(f))
    x0, y0, x1, y1 = CLIP
    labs = [{**lab, 'font': 'glyph'} for lab in d['labels'] if x0 <= lab['c'][0] <= x1 and y0 <= lab['c'][1] <= y1]
    f = os.path.join(W, 'text_labels.json')
    run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--page', str(PAGE), '--out', f)
    for lab in json.load(open(f)):  # the one name set as text (Dallas Bowl's, in the names' near-black)
        if lab['font'].startswith('FuturaPTCond-Medium') and x0 <= lab['c'][0] <= x1 and y0 <= lab['c'][1] <= y1:
            labs.append({'text': ' '.join(lab['text'].split()), 'font': lab['font'], 'size': lab['size'],
                         'seq': lab['seq'], 'color': 'black', 'pts': lab['pts'], 'c': lab['c']})
    os.remove(f)
    syms = [s for s in d['symbols'] if x0 <= s['c'][0] <= x1 and y0 <= s['c'][1] <= y1]
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    lines()
    glyphs()
    if os.path.exists(LETTERS):
        labels()
