"""Buttermilk: the map image, line pieces and printed names with their ratings, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/buttermilk/prepare.py      # regen.sh runs it

The 2025-26 trail map (aspensnowmass.com: one Illustrator page, "layered", drawn like Snowmass's, see
../snowmass/prepare.py) draws its trail lines as vectors over a 100 dpi painting and prints every name as text,
white on a pill in the run's colour, set on the run's own line. It has no expert terrain.

- Image: the page rendered at resort.SCALE with its two paintings (the mountain and the sky behind it) swapped for a
  Lanczos upscale (tools/trailmap/matte_pdf_layer.py --resample).
- Lines: the blue (in two blues), black and green 1.12 pt strokes (extract_pdf_vectors.py, solid only: the uphill
  routes, orange dashes over black ones, are dashed), and the "least difficult way down", green dots (a dashed
  1.5 pt stroke): Homestead Road's line, from the top to the base. The legend and the logo are left out. One path is one piece: the map draws a run as one path, the runs
  that leave it as paths ending on it (where one path carries two runs, decisions.py cuts it).
- Names: the page's white Semibold text (pdf_labels.py; the lifts', lodges' and parking notices' names are Bold) on
  a pill: the pill's colour, sampled around each letter on a render of the page, is the run's (green, blue, black;
  the lifts' red pills are left out). resort.COLOR_SYMBOL turns the colour into the symbol; the map prints no other
  symbol by a name.

Writes, in $BUTTERMILK_WORK (default work/buttermilk): map.png, pieces.json, printed.json ({labels, symbols: []}:
pdf_labels.py's labels, PDF points, each with its pill's colour).
"""
import json
import os
import subprocess
import sys

import numpy as np
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('BUTTERMILK_WORK', os.path.join(REPO, 'work/buttermilk')))
PDF = os.path.join(ROOT, 'buttermilk_2025-26.pdf')
PAINTINGS = (85, 86)  # the two paintings' image xrefs (both 100 dpi)
LEGEND = (938, 533, 1143, 741)  # pt: the legend, bottom right
LOGO = (918, 0, 1143, 80)  # pt: the Buttermilk logo, top right
EXCLUDE = [LEGEND, LOGO]
# the pills' colours, as rendered (RGB 0-255): a pixel takes the nearest
PILLS = {'blue': (0, 163, 227), 'green': (0, 173, 77), 'black': (36, 31, 31), 'red': (230, 41, 36),
         'purple': (99, 64, 153)}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def in_map(R, p):
    return inside(p, R.CLIP) and not any(inside(p, e) for e in EXCLUDE)


def col(c):
    return tuple(round(v, 2) for v in c or ())


def image(R):
    out = os.path.join(ROOT, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    run('python3', '-I', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', out, '--scale', str(R.SCALE), '--clip',
        ','.join(map(str, R.CLIP)), *[a for x in PAINTINGS for a in ('--resample', str(x))])


def lines(R):
    """The trail strokes, one pieces.json."""
    ex = [a for e in EXCLUDE for a in ('--exclude', ','.join(map(str, e)))]
    out = os.path.join(ROOT, 'pieces.json')
    run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, R.CLIP)),
        '--scale', str(R.SCALE), '--color', 'blue=0,0.64,0.89', '--color', 'blue2=0,0.68,0.94',
        '--color', 'black=0.14,0.12,0.12', '--color', 'green=0,0.68,0.3', '--min-width', '1.05', '--max-width', '1.2',
        '--solid', *ex, '--out', out)
    # Homestead Road is drawn as the "least difficult way down": green dots (a dashed 1.5 pt stroke) from the top to
    # the base, its own line where no other runs along it
    dots = os.path.join(ROOT, 'dots.json')
    run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, R.CLIP)),
        '--scale', str(R.SCALE), '--color', 'green=0,0.68,0.3', '--min-width', '1.4', '--max-width', '1.6', *ex,
        '--out', dots)
    d = json.load(open(out))
    for p in d['polylines']:
        p['cls'] = 'blue' if p['cls'] == 'blue2' else p['cls']
    for p in json.load(open(dots))['polylines']:
        d['polylines'].append({**p, 'id': len(d['polylines']), 'dotted': True})
    os.remove(dots)
    json.dump(d, open(out, 'w'))
    by = {}
    for p in d['polylines']:
        by[p['cls']] = by.get(p['cls'], 0) + 1
    print(f'  wrote pieces.json: {len(d["polylines"])} pieces {by}')


def page_render(page, z):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)


def pill(img, z, lab):
    """The colour class of the pill a label is printed on: the most common class of the coloured pixels round its
    letters (within a third of the type size of each letter's centre; the white letters left out)."""
    pal = np.array(list(PILLS.values()))
    votes = {}
    r = max(1, int(lab['size'] * z / 3))
    for x, y in lab['pts']:
        cx, cy = int(x * z), int(y * z)
        win = img[max(0, cy - r):cy + r + 1, max(0, cx - r):cx + r + 1].reshape(-1, 3)
        win = win[win.min(axis=1) < 200]  # not the white letters
        if not len(win):
            continue
        d = np.linalg.norm(win[:, None, :] - pal[None, :, :], axis=2)
        k = d.argmin(axis=1)
        for i in k[d[np.arange(len(k)), k] < 60]:
            name = list(PILLS)[i]
            votes[name] = votes.get(name, 0) + 1
    return max(votes, key=votes.get) if votes else None


def labels(R, L, img, z):
    out, tally = [], {}
    for lab in L:
        if not in_map(R, lab['c']) or col(lab['color']) != (1.0, 1.0, 1.0) or 'Semibold' not in lab['font']:
            continue
        k = pill(img, z, lab)
        if k not in ('green', 'blue', 'black'):
            continue  # a lift (red) or no pill
        out.append({**lab, 'color': k})
        tally[k] = tally.get(k, 0) + 1
    json.dump({'labels': out, 'symbols': []}, open(os.path.join(ROOT, 'printed.json'), 'w'), indent=0)
    print(f'  {len(out)} names {tally}')


def main():
    sys.path.insert(0, HERE)
    import resort as R
    doc = pymupdf.open(PDF)
    f = os.path.join(ROOT, 'text.json')
    if not os.path.exists(f):
        run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--out', f)
    L = json.load(open(f))
    z = 6  # px per pt of the render the pills are sampled on
    image(R)
    lines(R)
    labels(R, L, page_render(doc[0], z), z)


if __name__ == '__main__':
    main()
