"""Brighton: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/brighton/prepare.py      # regen.sh runs it

The 2025-26 trail map (brightonresort.com's trail-maps page: one Illustrator page, James Niehues's painting at 312
dpi under a vector layer) draws every run's line as a 0.8 pt stroke in its rating's colour (green, blue, black; the
parks orange), each name printed along its line on a white halo, its symbol (circle, square, diamond, two diamonds)
on the line by it. The names are outlined glyphs in Eurostile Condensed Heavy, black or a near-black, except five set
as text in the near-black (Pine Martin, Thunder Road by My-O-My, Candyland, Pee-Wee, Golden Needle).

- Image: the page rendered at resort.SCALE (resort.CLIP: the whole page).
- Lines: the green, blue, black and orange 0.8 pt strokes (tools/trailmap/extract_pdf_vectors.py; two blues and two
  blacks, a stroke or two in each other shade).
- Names: the glyphs in the black and the near-black (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on
  its contact sheets, is in letters.json here; M and W are one shape turned over, so are i, l and I without their
  dots: resort.RENAME spells what that misreads), and the text names (tools/trailmap/pdf_labels.py).
- Symbols: tools/trailmap/pdf_symbols.py (green circles, blue squares, near-black diamonds; two side by side a double
  diamond).

Writes, in $BRIGHTON_WORK (default work/brighton): map.png, pieces.json, glyphs.json, printed.json (labels, PDF
points), symbols.json (map px).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('BRIGHTON_WORK', os.path.join(REPO, 'work/brighton')))
PDF = os.path.join(W, 'brighton_2025-26.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
# the runs' stroke colours (each class may hold a shade or two drawn for a stroke or two)
LINES = [('green', (0.0, 0.65, 0.43)), ('blue', (0.0, 0.36, 0.65)), ('blue', (0.0, 0.4, 0.7)),
         ('blue', (0.0, 0.44, 0.74)), ('black', (0.21, 0.21, 0.22)), ('black', (0.14, 0.12, 0.12)),
         ('orange', (0.94, 0.51, 0.19))]
GLYPHS = {'black': (0.0, 0.0, 0.0), 'dark': (0.14, 0.12, 0.12)}
SYMBOLS = {'circle': (0.0, 0.65, 0.43), 'square': (0.0, 0.4, 0.7), 'diamond': (0.14, 0.12, 0.12)}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def main():
    os.makedirs(W, exist_ok=True)
    img = os.path.join(W, 'map.png')
    cols = [a for k, v in LINES for a in ('--color', f'{k}={rgb(v)}')]
    print(' ', run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)),
                   '--scale', str(SCALE), *cols, '--min-width', '0.7', '--max-width', '0.9', '--min-length', '0.8',
                   *(['--image', img] if not os.path.exists(img) or os.environ.get('IMAGES') else []),
                   '--out', os.path.join(W, 'pieces.json')).strip().splitlines()[-1].replace(W + '/', ''))
    G = os.path.join(W, 'glyphs.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF,
                   *[a for k, v in GLYPHS.items() for a in ('--color', f'{k}={rgb(v)}')],
                   '--max-size', '12', '--out', G).strip().replace(W + '/', ''))
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                   '--turned', 'WM', '--out', f).strip().splitlines()[0].replace(W + '/', ''))
    labels = []
    for lab in json.load(open(f))['labels']:
        labels.append({**lab, 'font': 'glyph', 'color': 'black'})
    os.remove(f)
    f = os.path.join(W, 'text_labels.json')
    run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--out', f)
    for lab in json.load(open(f)):  # the names set as text (the lifts' are red, their halos white)
        if lab['font'].startswith('EurostileCon') and tuple(lab['color']) in GLYPHS.values():
            labels.append({'text': ' '.join(lab['text'].split()), 'font': lab['font'], 'size': lab['size'],
                           'seq': lab['seq'], 'color': 'black', 'pts': lab['pts'], 'c': lab['c']})
    os.remove(f)
    json.dump({'labels': labels, 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    s = os.path.join(W, 'symbols.json')
    run('python3', '-I', f'{T}/pdf_symbols.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
        *[a for k, v in SYMBOLS.items() for a in (f'--{k}', rgb(v))], '--max-size', '8', '--max-diamond', '6',
        '--out', s)
    S = json.load(open(s))
    by = {}
    for x in S:
        by[x['type']] = by.get(x['type'], 0) + 1
    print(f'  {len(labels)} labels, {len(S)} symbols {by}')


if __name__ == '__main__':
    main()
