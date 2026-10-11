"""Stevens Pass: the map images, line pieces, printed names and symbols of its two panels, from the trail map PDF, for
tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/stevens-pass/prepare.py      # regen.sh runs it

The winter trail map (stevenspass.com's trail-maps page: 20241115_SV_winter-trail_map_001.pdf, two pages; the map is
the second) holds two paintings side by side, each a 100 dpi image under one vector layer: the Front Side on the left,
Mill Valley (the back side) on the right, drawn at a larger scale. Each is a panel here (resort.py PANELS; each one's
settings in panels/<panel>/resort.py, its files in work/stevens-pass/<panel>/). Runs' lines are strokes 1.1 to 1.4 pt
wide in the three trail colours (dashed: the roads and cat tracks), a yellow stroke beside the ones lit at night (left
out); lifts are red. Every name is outlined black glyphs on a white halo, printed along its run's line (some beside
it); symbols (squares, diamonds, two diamonds apart for double black, circles) by the name.

- Images: the page rendered at each panel's SCALE over its CLIP.
- Lines: tools/trailmap/extract_pdf_vectors.py, the blue, black and green strokes 1.0 to 1.5 pt wide.
- Names and symbols: tools/trailmap/pdf_glyphs.py (each shape's letter, read once on its contact sheets, is in
  letters.json here: a font of its own); the "LIFT UPGRADE" box on the Front Side and the page's lower half (the
  legend and the text) left out.

Writes, per panel in $STEVENS_PASS_WORK/<panel> (default work/stevens-pass): map.png, pieces.json, printed.json
(labels and symbols, PDF points); and glyphs.json and glyph_labels.json (the whole page) in the folder itself.
"""
import importlib.util
import json
import os
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('STEVENS_PASS_WORK', os.path.join(REPO, 'work/stevens-pass')))
PDF = os.path.join(ROOT, 'sv_2024-25.pdf')
PAGE = 1
LETTERS = os.path.join(HERE, 'letters.json')
sys.path.insert(0, HERE)
from resort import PANELS  # noqa: E402

BLACK, BLUE, GREEN = (0.0, 0.0, 0.0), (0.0, 0.4, 0.66), (0.34, 0.68, 0.28)
LOWER = (0, 700, 2016, 1296)  # the page's lower half: legend, lift table, text (PDF points)
UPGRADE = (13, 520, 216, 700)  # the Front Side's "LIFT UPGRADE" box


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def settings(panel):
    """The panel's resort.py (CLIP, SCALE)."""
    spec = importlib.util.spec_from_file_location(f'sv_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def main():
    G, L = os.path.join(ROOT, 'glyphs.json'), os.path.join(ROOT, 'glyph_labels.json')
    excl = [a for e in (LOWER, UPGRADE) for a in ('--exclude', ','.join(map(str, e)))]
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF, '--page', str(PAGE), '--out', G,
                   '--color', f'black={rgb(BLACK)}', '--color', f'blue={rgb(BLUE)}', '--color', f'green={rgb(GREEN)}',
                   '--max-size', '17', *excl).strip().replace(ROOT + '/', ''))
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                   '--out', L, '--square', 'blue', '--diamond', 'black', '--circle', 'green', '--turned', 'WM',
                   '--rounded', '--double-dist', '1.6').strip().splitlines()[0].replace(ROOT + '/', ''))
    d = json.load(open(L))
    page = pymupdf.open(PDF)[PAGE]
    for panel, _title in PANELS:
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        img = os.path.join(W, 'map.png')
        if not os.path.exists(img) or os.environ.get('IMAGES'):
            page.get_pixmap(clip=pymupdf.Rect(*R.CLIP), matrix=pymupdf.Matrix(R.SCALE, R.SCALE), alpha=False).save(img)
        cols = [a for k, v in (('black', BLACK), ('blue', BLUE), ('green', GREEN)) for a in ('--color', f'{k}={rgb(v)}')]
        out = run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--page', str(PAGE),
                  '--clip', ','.join(map(str, R.CLIP)), '--scale', str(R.SCALE), *cols, '--min-width', '1.0',
                  '--max-width', '1.5', '--min-length', '1', *excl, '--out', os.path.join(W, 'pieces.json'))
        print(f'  {panel}:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
        labs = [{**lab, 'font': 'glyph', 'color': 'black'} for lab in d['labels'] if inside(lab['c'], R.CLIP)]
        syms = [s for s in d['symbols'] if inside(s['c'], R.CLIP)]
        json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
        print(f'  {panel}: {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    main()
