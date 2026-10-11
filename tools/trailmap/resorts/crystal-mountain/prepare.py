"""Crystal Mountain: each panel's map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/crystal-mountain/prepare.py      # regen.sh runs it

The main panel, from the 2025-26 trail map PDF:
- Image: its page (VistaMap's painting is vector art) rendered at the panel's SCALE inside its CLIP (the painting
  above the partners' band).
- Lines: the runs' 1.5 pt strokes in the legend's green, blue and black (tools/trailmap/extract_pdf_vectors.py), the
  legend's box left out.
- Names: the PDF's text (tools/trailmap/pdf_labels.py; resort.is_name keeps the names' style).
- Symbols: the fills with rounded corners in the three colours (tools/trailmap/pdf_symbols.py --rounded: a double
  diamond is one fill half again as wide as tall).

The Northway panel, from the inset image (a WebP): upscaled 2x (Lanczos), each run's line routed along its black
stroke between the points read on crops (names.py; tools/trailmap/route_trace.py's black ink), one piece per line
carrying its name (the panel's GROUPED).

Writes, per panel in $CRYSTAL_MOUNTAIN_WORK/<panel> (default work/crystal-mountain/<panel>): map.png, pieces.json,
printed.json (PDF points); symbols.json (map px) for the main panel.
"""
import importlib.util
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
ROOT = os.path.abspath(os.environ.get('CRYSTAL_MOUNTAIN_WORK', os.path.join(REPO, 'work/crystal-mountain')))
PDF = os.path.join(ROOT, 'crystal_2025-26.pdf')
NORTHWAY = os.path.join(ROOT, 'northway_2425.webp')
W = os.path.join(ROOT, 'main')
UPSCALE = 2


def settings(panel):
    spec = importlib.util.spec_from_file_location(f'cm_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R = settings('main')
LINES = {'green': (0.0, 0.65, 0.32), 'blue': (0.0, 0.61, 0.86), 'black': (0.14, 0.12, 0.12)}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def box(b):
    return ','.join(str(v) for v in b)


def image():
    out = os.path.join(W, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        page = pymupdf.open(PDF)[0]
        page.get_pixmap(matrix=pymupdf.Matrix(R.SCALE, R.SCALE), clip=pymupdf.Rect(*R.CLIP)).save(out)


def lines():
    args = ['python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', box(R.CLIP), '--scale', str(R.SCALE),
            '--min-width', '1.4', '--max-width', '1.6', '--min-length', '1', '--out', os.path.join(W, 'pieces.json')]
    for cls, c in LINES.items():
        args += ['--color', f'{cls}={",".join(map(str, c))}']
    for b in R.LEGEND:
        args += ['--exclude', box(b)]
    print('  main:', run(*args).strip().splitlines()[-1].replace(ROOT + '/', ''))


def names():
    run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--out', os.path.join(W, 'printed.json'))


def symbols():
    args = ['python3', '-I', f'{T}/pdf_symbols.py', PDF, '--clip', box(R.CLIP), '--scale', str(R.SCALE),
            '--circle', '0.0,0.65,0.32', '--square', '0.0,0.61,0.86', '--diamond', '0.14,0.12,0.12', '--rounded',
            '--max-diamond', '14', '--max-square', '14', '--max-size', '15', '--out', os.path.join(W, 'symbols.json')]
    for b in R.LEGEND:
        args += ['--exclude', box(b)]
    print('  main:', run(*args).strip().splitlines()[-1].replace(ROOT + '/', ''))


def northway():
    """The inset's map (2x upscale) and its lines routed along the painted ones (names.py)."""
    sys.path.insert(0, T)
    from route_trace import Router
    sys.path.insert(0, HERE)
    import names
    out_dir = os.path.join(ROOT, 'northway')
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, 'map.png')
    if not os.path.exists(png) or os.environ.get('IMAGES'):
        im = Image.open(NORTHWAY).convert('RGB')
        im.resize((im.width * UPSCALE, im.height * UPSCALE), Image.LANCZOS).save(png)
    router = Router(png, 'vail')
    H, Wd = router.A.shape[:2]
    cls_of = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black'}
    out = []
    for name, _at, symbol, lines_read in names.READING['northway']:
        for line in lines_read:
            # every run's line is drawn black here; each point read (a little off its line on the crops) moved onto
            # the nearest black ink within 30 px first, so the route has no spur out to it and back
            pts = router.route('black', [router.snap('black', q, r=30) for q in line])
            out.append({'id': len(out), 'cls': cls_of[symbol], 'name': name,
                        'lengthPx': round(sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))),
                        'points': [[round(100 * x / Wd, 3), round(100 * y / H, 3)] for x, y in pts]})
    json.dump({'_source': 'Crystal Mountain northway: names.py lines routed along the painted ones (prepare.py)',
               'polylines': out}, open(os.path.join(out_dir, 'pieces.json'), 'w'))
    json.dump({'labels': [], 'symbols': []}, open(os.path.join(out_dir, 'printed.json'), 'w'))
    print(f'  northway: {len(names.READING["northway"])} names, {len(out)} lines')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    lines()
    names()
    symbols()
    northway()
