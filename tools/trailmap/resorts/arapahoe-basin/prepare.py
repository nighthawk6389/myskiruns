"""Arapahoe Basin: the map images, line pieces, printed names and symbols of its two panels, from the 2025-26 trail
map PDF, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/arapahoe-basin/prepare.py      # regen.sh runs it

The 2025-26 winter trail map (arapahoebasin.com's trail-maps page: "a basin map 2025.pdf", one page, VistaMap's
artwork) holds two paintings, each about 4.2 px/pt, under one vector layer: the Frontside & The Beavers below, Zuma
Bowl (Montezuma Bowl) in a frame at the top right. Each is a panel here (resort.py PANELS; each one's settings in
panels/<panel>/resort.py, its files in work/arapahoe-basin/<panel>/). Runs' lines are thin strokes in the three
trail colours (0.5 pt on the Frontside, 0.75 pt in Zuma; the Frontside's blue in two shades), drawn for the groomed
and the gladed runs and the traverses; the open faces, bowls and chutes are a name and a symbol with no line. The
hiking routes and the summer activities' outlines are thin black strokes too (settled in decisions.py). Every name is
outlined near-black glyphs on a white halo, printed along its run; symbols (rounded diamonds, squares, circles; the
EX double diamond one outline with white E and X) by the name.

- Images: the page rendered at each panel's SCALE over its CLIP (the paintings' own resolution: no matte needed).
- Lines: strokes 0.45 to 0.8 pt wide in black, blue (both shades) and green (tools/trailmap/extract_pdf_vectors.py),
  and the skiing traverses' 1.5 pt black dashes (Grand Portage, on a white casing).
- Names: the near-black glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets,
  is in letters.json here), each panel's those inside its CLIP.
- Symbols: tools/trailmap/pdf_symbols.py --rounded; fills under 3.5 pt are icons' parts; the legend and the Steep
  Gullies note left out.

Writes, per panel in $ARAPAHOE_BASIN_WORK/<panel> (default work/arapahoe-basin): map.png, pieces.json, printed.json
(labels, PDF points), symbols.json (map px); and glyphs.json and labels.json (the whole page) in the folder itself.
"""
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('ARAPAHOE_BASIN_WORK', os.path.join(REPO, 'work/arapahoe-basin')))
PDF = os.path.join(ROOT, 'abasin_2025-26.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
sys.path.insert(0, HERE)
from resort import PANELS  # noqa: E402

BLACK, BLACK2 = (0.14, 0.12, 0.13), (0.14, 0.12, 0.12)  # the lines' and symbols' black; the names' (both kinds)
BLUE, BLUE2, GREEN = (0.0, 0.61, 0.86), (0.16, 0.56, 0.76), (0.0, 0.65, 0.32)
LEGEND = (1090, 1072, 1296, 1294.58)  # the map key, bottom right (PDF points)
NOTE = (1040, 1028, 1122, 1062)  # the STEEP GULLIES note (its EX symbol is the note's)


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def settings(panel):
    """The panel's resort.py (CLIP, SCALE)."""
    spec = importlib.util.spec_from_file_location(f'ab_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def main():
    G, L = os.path.join(ROOT, 'glyphs.json'), os.path.join(ROOT, 'labels.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', G, '--color', f'black={rgb(BLACK2)}',
                   '--color', f'black={rgb(BLACK)}').strip().replace(ROOT + '/', ''))
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                   '--out', L).strip().splitlines()[0].replace(ROOT + '/', ''))
    labels = json.load(open(L))['labels']
    for panel, _title in PANELS:
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        img = os.path.join(W, 'map.png')
        clip = ','.join(map(str, R.CLIP))
        cols = [a for k, v in (('black', BLACK), ('blue', BLUE), ('blue', BLUE2), ('green', GREEN))
                for a in ('--color', f'{k}={rgb(v)}')]
        excl = [a for e in (LEGEND, NOTE) for a in ('--exclude', ','.join(map(str, e)))]
        out = run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', clip, '--scale', str(R.SCALE), *cols,
                  '--min-width', '0.45', '--max-width', '0.8', '--min-length', '0.8', *excl,
                  *(['--image', img] if not os.path.exists(img) or os.environ.get('IMAGES') else []),
                  '--out', os.path.join(W, 'pieces.json'))
        print(f'  {panel}:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
        # the skiing traverses (Grand Portage): 1.5 pt black dashes on a white casing
        out = run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', clip, '--scale', str(R.SCALE),
                  '--color', f'black={rgb(BLACK)}', '--min-width', '1.4', '--max-width', '1.6', '--min-length', '0.8',
                  *excl, '--append', '--out', os.path.join(W, 'pieces.json'))
        print(f'  {panel}:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
        labs = [{**lab, 'color': 'black'} for lab in labels
                if inside(lab['c'], R.CLIP) and not inside(lab['c'], LEGEND) and not inside(lab['c'], NOTE)]
        json.dump({'labels': labs, 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
        s = os.path.join(W, 'symbols.json')
        run('python3', '-I', f'{T}/pdf_symbols.py', PDF, '--clip', clip, '--scale', str(R.SCALE),
            '--circle', rgb(GREEN), '--square', rgb(BLUE), '--diamond', rgb(BLACK), '--max-size', '14',
            '--rounded', '--max-square', '8', '--max-diamond', '6.5', *excl, '--out', s)
        S = [x for x in json.load(open(s)) if x['sizePt'] >= 3.5]
        json.dump(S, open(s, 'w'), indent=0)
        by = {}
        for x in S:
            by[x['type']] = by.get(x['type'], 0) + 1
        print(f'  {panel}: {len(labs)} labels, {len(S)} symbols {by}')


if __name__ == '__main__':
    main()
