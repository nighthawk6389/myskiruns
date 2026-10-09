"""Mt. Bachelor: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/mt-bachelor/prepare.py      # regen.sh runs it

One InDesign page: the legend and Ski Patrol panel on the left, the painting (300 dpi) with its vector layer on the
right (resort.CLIP).

- Image: the page's map area rendered at resort.SCALE (3 px per pt; the painting is 4.2).
- Lines: every trail line is a filled outline (the artwork's strokes outlined), 1.1 pt wide, in blue, green or black
  (tools/trailmap/pdf_outline_lines.py: centre lines; the names' letters, outlines in the same colours, are left out
  by their glyph shapes, and black outlines are lines only if 5 pt long or more: the shortest, Snapshot Bowl's stub
  to Northwest Crossover, is 6).
- Names: outlined capitals in the run's colour (blue, green, black; lodges, peaks and the parks' areas in a second
  near-black), on a white halo (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets,
  is in letters.json here; the Whitebark Pine logo's letters and the icons are read as *). Z is N turned a quarter
  (resort.RENAME), O and zero are one shape (a word with letters takes O).
- Symbols: green circles (drawn with any number of curves: --any-circles), blue squares (some as rectangles:
  --rect-squares), black diamonds, double diamonds.

Writes, in $MT_BACHELOR_WORK (default work/mt-bachelor): map.png, pieces.json, glyphs.json, printed.json ({labels,
symbols}, PDF points).
"""
import json
import os
import re
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('MT_BACHELOR_WORK', os.path.join(REPO, 'work/mt-bachelor')))
PDF = os.path.join(W, 'mtbachelor_2025-26.pdf')
LETTERS = os.path.join(HERE, 'letters.json')

BLUE, GREEN, BLACK, K14 = (0.07, 0.62, 0.86), (0.06, 0.58, 0.28), (0.01, 0.02, 0.02), (0.14, 0.12, 0.13)


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
        pix = pymupdf.open(PDF)[0].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), clip=pymupdf.Rect(*CLIP))
        pix.save(out)


def lines():
    print(' ', run('python3', f'{T}/pdf_outline_lines.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale',
                   str(SCALE), '--color', f'blue={rgb(BLUE)}', '--color', f'green={rgb(GREEN)}', '--color',
                   f'black={rgb(BLACK)}', '--dark', 'black', '--max-width', '1.3', '--dark-min', '5',
                   '--glyphs', os.path.join(W, 'glyphs.json'), '--letters', LETTERS,
                   '--out', os.path.join(W, 'pieces.json')).strip().replace(W + '/', ''))


def word(w):
    """O and zero are one shape: a word with letters in it takes O, a number zero."""
    if re.search(r'[A-NP-Z]', w):
        return w.replace('0', 'O')
    if re.search(r'\d', w):
        return w.replace('O', '0')
    return w


def glyphs():
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', os.path.join(W, 'glyphs.json'),
                   '--color', f'blue={rgb(BLUE)}', '--color', f'green={rgb(GREEN)}', '--color', f'black={rgb(BLACK)}',
                   '--color', f'k14={rgb(K14)}', '--exclude', f'0,0,{CLIP[0] - 1},{CLIP[3]}').strip()
          .replace(W + '/', ''))


def labels():
    G = os.path.join(W, 'glyphs.json')
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS, '--out', f,
                   '--square', 'blue', '--diamond', 'black', '--circle', 'green', '--join', '12', '--space', '1.0',
                   '--any-circles', '--rect-squares').strip().replace(W + '/', '').replace('\n', '\n  '))
    d = json.load(open(f))
    labs = [{**lab, 'text': ' '.join(word(w) for w in lab['text'].split(' ')), 'font': 'glyph'} for lab in d['labels']]
    json.dump({'labels': labs, 'symbols': d['symbols']}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labs)} labels, {len(d["symbols"])} symbols')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    glyphs()
    lines()
    labels()
