"""Alta: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/alta/prepare.py      # regen.sh runs it

The 2025-26 trail map (alta.com's plan-your-trip page: Alta_Trailmap_2025_26.pdf, one Illustrator page, James
Niehues's painting at 300 dpi under a vector layer) draws its runs' lines as strokes in the three trail colours,
solid (1.97 pt), dashed (the traverses) or dotted (2.62 pt: the easier ways down); the controlled-access areas'
purple dash-dot outlines are no runs. Every name is outlined black glyphs on a white halo stroke, printed along its
run's line, the symbol (rounded diamonds, squares, circles) at its start; many expert runs (faces, chutes, bowls) are
a name and a diamond with no line.

- Image: the page rendered at resort.SCALE, the key bar along the bottom left out (resort.CLIP).
- Lines: the black, blue and green strokes 1.9 to 2.7 pt wide (tools/trailmap/extract_pdf_vectors.py).
- Names: the black glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets, is
  in letters.json here).
- Symbols: pdf_symbols.py --rounded (the fills' corners are rounded); those under 7 pt are icons' parts.

Writes, in $ALTA_WORK (default work/alta): map.png, pieces.json, glyphs.json, printed.json (labels, PDF points),
symbols.json (map px).
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

W = os.path.abspath(os.environ.get('ALTA_WORK', os.path.join(REPO, 'work/alta')))
PDF = os.path.join(W, 'alta_2025-26.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
COLOURS = {'black': (0.14, 0.12, 0.12), 'blue': (0.0, 0.61, 0.86), 'green': (0.0, 0.65, 0.32)}
DIAMOND = (0.14, 0.12, 0.13)  # the symbols' black, a shade off the lines' and letters'


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
    cols = [a for k, v in COLOURS.items() for a in ('--color', f'{k}={rgb(v)}')]
    print(' ', run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)),
                   '--scale', str(SCALE), *cols, '--min-width', '1.9', '--max-width', '2.7', '--min-length', '0.8',
                   *(['--image', img] if not os.path.exists(img) or os.environ.get('IMAGES') else []),
                   '--out', os.path.join(W, 'pieces.json')).strip().splitlines()[-1].replace(W + '/', ''))
    G = os.path.join(W, 'glyphs.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF, '--color', f'black={rgb(COLOURS["black"])}',
                   '--max-size', '12', '--out', G).strip().replace(W + '/', ''))
    f = os.path.join(W, 'printed.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                   '--out', f).strip().replace(W + '/', ''))
    d = json.load(open(f))
    for lab in d['labels']:
        lab['color'] = 'black'
    json.dump({'labels': [lab for lab in d['labels'] if CLIP[1] <= lab['c'][1] <= CLIP[3]], 'symbols': []},
              open(f, 'w'), indent=0)
    s = os.path.join(W, 'symbols.json')
    run('python3', '-I', f'{T}/pdf_symbols.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
        '--circle', rgb(COLOURS['green']), '--square', rgb(COLOURS['blue']), '--diamond', rgb(DIAMOND),
        '--max-size', '14', '--max-diamond', '12', '--max-square', '10', '--rounded', '--out', s)
    S = [x for x in json.load(open(s)) if x['sizePt'] >= 7]
    json.dump(S, open(s, 'w'), indent=0)
    by = {}
    for x in S:
        by[x['type']] = by.get(x['type'], 0) + 1
    print(f'  {len(S)} symbols {by}')


if __name__ == '__main__':
    main()
