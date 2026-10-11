"""Telluride: each panel's map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/telluride/prepare.py      # regen.sh runs it

The 2024-25 trail map PDF (tellurideskiresort.com's mountain page, "DOWNLOAD MAP PDF": 2425_TSR_Trail-Map_layered-
trailmap.pdf, still the current one; one Illustrator page) is James Niehues's painting, embedded at only 100 dpi, under
a vector layer. Runs' lines are 1 pt strokes in the trail colours (black, blue, green) over 2 pt white casings; glades
are white hatching; lifts red. Every name is outlined glyphs in its run's colour on a white halo, printed in a gap of
the run's line, its symbols after it (rounded fills: circles, squares, diamonds; two of a kind for the advanced
beginner, advanced intermediate and expert runs; the extreme terrain's two outlined diamonds, white inside, read as
EX). Terrain parks are white names on orange pills (Hoot Brown) or orange names (Beginner Park).

- Image: the page at resort.SCALE with the painting upscaled (Lanczos) first, so it isn't blurred
  (tools/trailmap/matte_pdf_layer.py --resample).
- Lines: the 0.9 to 1.1 pt solid strokes in the three colours (tools/trailmap/extract_pdf_vectors.py), the legend
  left out.
- Parks: the orange freestyle strokes, 5 to 8 pt (Hoot Brown's under its white name, Ute Park's by its lift).
- Names and symbols: the glyphs in the four name colours (tools/trailmap/pdf_glyphs.py; each shape's letter, read
  once on its contact sheets, is in letters.json here); two diamonds up to 1.65 of their width apart are a double;
  the EX, double black.

The resort's two inset images of the hike-to terrain the map marks "See Reverse for Detail" (Revelation Bowl;
Palmyra Peak and Black Iron Bowl) are panels of their own, read on crops (names.py): each image upscaled 2x (Lanczos),
each name at its label with its symbol, each chute's black line (and See Forever's blue) routed along the painted one
between the points read (tools/trailmap/route_trace.py), one piece per line carrying its name (resort.GROUPED).

Writes, per panel in $TELLURIDE_WORK/<panel> (default work/telluride/<panel>): map.png, pieces.json, printed.json
({labels, symbols}, PDF points; empty for the insets); glyphs.json in $TELLURIDE_WORK.
"""
import importlib.util
import json
import math
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('TELLURIDE_WORK', os.path.join(REPO, 'work/telluride')))
PDF = os.path.join(ROOT, 'telluride_2024-25.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
PAINTING = 290  # the painting's image xref
COLOURS = {'black': (0.14, 0.12, 0.12), 'blue': (0.0, 0.68, 0.93), 'green': (0.0, 0.65, 0.32)}
ORANGE = (0.95, 0.45, 0.19)  # the parks' names
LEGEND = (0, 0, 160, 320)  # the key, top left (PDF points)
INSETS = {'revelation': 'revvy-23.24-1.png', 'black-iron-bowl': 'palmyra-23.24.png'}
UPSCALE = 2
CLS = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black'}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def settings(panel):
    spec = importlib.util.spec_from_file_location(f'tel_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inset(panel, reading):
    """An inset image's map (2x upscale) and its lines routed along the painted ones (names.py)."""
    sys.path.insert(0, T)
    from route_trace import Router
    W = os.path.join(ROOT, panel)
    os.makedirs(W, exist_ok=True)
    png = os.path.join(W, 'map.png')
    if not os.path.exists(png) or os.environ.get('IMAGES'):
        im = Image.open(os.path.join(ROOT, INSETS[panel])).convert('RGB')
        im.resize((im.width * UPSCALE, im.height * UPSCALE), Image.LANCZOS).save(png)
    R = Router(png, 'vail')
    H, Wd = R.A.shape[:2]
    out = []
    for name, _at, symbol, lines in reading:
        cls = 'blue' if symbol == 'square' else CLS[symbol]
        for line in lines:
            pts = R.route(cls, line)
            out.append({'id': len(out), 'cls': cls, 'name': name,
                        'lengthPx': round(sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))),
                        'points': [[round(100 * x / Wd, 3), round(100 * y / H, 3)] for x, y in pts]})
    json.dump({'_source': f'Telluride {panel}: names.py lines routed along the painted ones (prepare.py)',
               'polylines': out}, open(os.path.join(W, 'pieces.json'), 'w'))
    json.dump({'labels': [], 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'))
    print(f'  {panel}: {len(reading)} names, {len(out)} lines')


def main():
    sys.path.insert(0, HERE)
    import names
    R = settings('main')
    W = os.path.join(ROOT, 'main')
    os.makedirs(W, exist_ok=True)
    img = os.path.join(W, 'map.png')
    clip = ','.join(map(str, R.CLIP))
    if not os.path.exists(img) or os.environ.get('IMAGES'):
        run('python3', '-I', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', img, '--scale', str(R.SCALE), '--clip',
            clip, '--resample', str(PAINTING))
    cols = [a for k, v in COLOURS.items() for a in ('--color', f'{k}={rgb(v)}')]
    out = run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', clip, '--scale', str(R.SCALE), *cols,
              '--min-width', '0.9', '--max-width', '1.1', '--min-length', '0.8', '--solid', '--exclude',
              ','.join(map(str, LEGEND)), '--out', os.path.join(W, 'pieces.json'))
    print('  main:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
    # the terrain parks' freestyle terrain: orange strokes 5 to 8 pt wide (the Hoot Brown Terrain Park's, under its
    # white name on the stroke, and Ute Park's two either side of its lift)
    out = run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', clip, '--scale', str(R.SCALE),
              '--color', f'park={rgb(ORANGE)}', '--min-width', '4.5', '--max-width', '8.5', '--min-length', '0.8',
              '--append', '--out', os.path.join(W, 'pieces.json'))
    print('  main:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
    G = os.path.join(ROOT, 'glyphs.json')
    gcols = [a for k, v in {**COLOURS, 'orange': ORANGE}.items() for a in ('--color', f'{k}={rgb(v)}')]
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF, *gcols, '--exclude', ','.join(map(str, LEGEND)),
                   '--out', G).strip().replace(ROOT + '/', ''))
    f = os.path.join(W, 'printed.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS, '--out', f,
                   '--diamond', 'black', '--square', 'blue', '--circle', 'green', '--double-dist', '1.65')
          .strip().splitlines()[0].replace(ROOT + '/', ''))
    # the extreme terrain's EX (two outlined diamonds holding E and X): double black, as the app rates EX
    d = json.load(open(f))
    for sym in d['symbols']:
        if sym['t'] == 'ex':
            sym['t'] = 'double-diamond'
    json.dump(d, open(f, 'w'), indent=0)
    for panel in INSETS:
        inset(panel, names.READING[panel])


if __name__ == '__main__':
    main()
