"""Deer Valley: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/deer-valley/prepare.py      # regen.sh runs it

- Image: the November image's trail area (resort.BOX), as it is (1.39 px per PDF point: the October PDF's painting
  is 0.62).
- Lines: the October PDF's 2.1 pt strokes in green, blue and black (each on a 4.1 pt white casing; lifts are red,
  the boundary orange dots, slow zones yellow hatching), the legend left out, on the image's grid (resort.CLIP and
  SCALE come from the registration).
- Names: outlined glyphs (one, Northern Light, is text), all in the map's near-black (tools/trailmap/pdf_glyphs.py; each shape's letter, read once
  on its contact sheets, is in letters.json here), with the run's symbol at one end: green circles, blue squares
  (two side by side: advanced intermediate), black diamonds (two: expert).

Writes, in $DEER_VALLEY_WORK (default work/deer-valley): map.png, pieces.json, glyphs.json, printed.json ({labels,
symbols}, PDF points).
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import BOX, CLIP, SCALE  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('DEER_VALLEY_WORK', os.path.join(REPO, 'work/deer-valley')))
PDF = os.path.join(W, 'deervalley_2025-10.pdf')
NOV = os.path.join(W, 'deervalley_2025-11.png')
LETTERS = os.path.join(HERE, 'letters.json')

GREEN, BLUE, DARK = (0, 0.68, 0.3), (0, 0.68, 0.94), (0.14, 0.12, 0.13)
LINES = {'green': GREEN, 'blue': BLUE, 'black': DARK}
LEGEND = (3238, 1295, 3663, 1851)  # PDF points: the legend's white box


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
        Image.open(NOV).convert('RGB').crop(BOX).save(out)


def lines():
    args = ['python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
            '--min-width', '1.6', '--max-width', '2.2', '--min-length', '1', '--exclude', ','.join(map(str, LEGEND)),
            '--out', os.path.join(W, 'pieces.json')]
    for cls, c in LINES.items():
        args += ['--color', f'{cls}={rgb(c)}']
    print(' ', run(*args).strip().replace(W + '/', ''))


def glyphs():
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', os.path.join(W, 'glyphs.json'),
            '--exclude', ','.join(map(str, LEGEND)), '--max-size', '19']
    for cls, c in (('black', DARK), ('blue', BLUE), ('green', GREEN)):
        args += ['--color', f'{cls}={rgb(c)}']
    print(' ', run(*args).strip())


def word(w):
    """l and I are one shape (a bar): inside a word with small letters it is l (BowI, GIade, DaIy)."""
    return w[:1] + w[1:].replace('I', 'l') if re.search('[a-z]', w) else w


def text_labels():
    """The one name set as text (Northern Light, MyriadPro-Bold, a letter at a time, drawn twice): its letters, which
    pdf_resort.py joins into one label."""
    f = os.path.join(W, 'text_p0.json')
    run('python3', f'{T}/pdf_labels.py', PDF, '--page', '0', '--out', f)
    out = [{**lab, 'color': 'black'} for lab in json.load(open(f)) if lab['font'] == 'MyriadPro-Bold']
    os.remove(f)
    return out


def labels():
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', os.path.join(W, 'glyphs.json'),
                   '--letters', LETTERS, '--out', f, '--square', 'blue', '--diamond', 'black', '--circle', 'green',
                   '--turned', 'nu', '--turned-hole', '69', '--join', '13', '--diamond-curves', '4', '--sym-min', '4', '--double-dist', '1.6').strip().replace('\n', '\n  '))
    d = json.load(open(f))
    x0, y0, x1, y1 = CLIP
    labs = [{**lab, 'text': ' '.join(word(w) for w in lab['text'].split(' ')), 'font': 'glyph'} for lab in d['labels'] if x0 <= lab['c'][0] <= x1 and y0 <= lab['c'][1] <= y1]
    syms = [s for s in d['symbols'] if x0 <= s['c'][0] <= x1 and y0 <= s['c'][1] <= y1]
    labs += text_labels()
    json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    lines()
    glyphs()
    if os.path.exists(LETTERS):
        labels()
