"""Sun Valley: the map images, line pieces, printed names and symbols of its two panels (Bald Mountain, Dollar
Mountain), for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/sun-valley/prepare.py      # regen.sh runs it

This season's maps (sunvalley.com's trail-maps page: 2627_SV_Baldy_Map and 2627_SV_Dollar_Map) are images only (a
PDF holding one picture each). skimap.org keeps the 2023-24 exports of both artworks as vector PDFs (Bald: map
24666; Dollar: map 24667): trail lines as strokes, names as outlined glyphs, symbols as fills, the painting as an
image under them. Each export is registered on this season's image (resort.py per panel: AFFINE, from
tools/trailmap/register_pages.py), and everything on it is put on the image through that affine, so the panels'
settings are in map px (CLIP is the image, SCALE 1).

- Images: this season's pictures, as they are (tools/trailmap/extract_pdf_image.py).
- Lines: the exports' strokes in the runs' green, blue and black (Bald 1 pt, Dollar 0.75 pt; the navy strokes are
  the snowmaking icons' rings, the maroon dashes the lifts), and on Bald the 4 pt dotted green and blue of the
  least difficult way down (the legend's name), the only line drawn for the cat tracks it follows (Leigh Lane,
  Roundhouse Lane, Olympic Lane...),
  extracted on the page (tools/trailmap/extract_pdf_vectors.py) then moved onto the image; a piece's points off the
  image (the exports show more sky) are dropped, splitting it.
- Names and symbols: the near-black glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its
  contact sheets, is in letters.json here, one font for both maps), and the green circles, blue squares and black
  diamonds (two side by side: double black); each panel's legend, insets and logos left out (EXCLUDE, map px).

Writes, per panel in $SUN_VALLEY_WORK/<panel> (default work/sun-valley): map.png, pieces.json, printed.json (labels
and symbols, map px).
"""
import importlib.util
import json
import os
import subprocess
import sys

import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('SUN_VALLEY_WORK', os.path.join(REPO, 'work/sun-valley')))
LETTERS = os.path.join(HERE, 'letters.json')
sys.path.insert(0, HERE)
from resort import PANELS  # noqa: E402

GREEN, BLUE = (0.0, 0.65, 0.32), (0.0, 0.61, 0.86)


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def settings(panel):
    spec = importlib.util.spec_from_file_location(f'sv_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    for panel, _title in PANELS:
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        pdf, png = os.path.join(ROOT, R.EXPORT), os.path.join(ROOT, R.IMAGE)
        img = os.path.join(W, 'map.png')
        if not os.path.exists(img) or os.environ.get('IMAGES'):
            Image.open(png).convert('RGB').save(img)
        iw, ih = R.CLIP[2], R.CLIP[3]
        a, b, c, d, e, f = R.AFFINE

        def on_map(x, y):
            return a * x + b * y + c, d * x + e * y + f

        def outside(p):  # in a legend, inset or logo
            return any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for x0, y0, x1, y1 in R.EXCLUDE)
        page = pymupdf.open(pdf)[0].rect
        # the lines, on the page (percent of it), then on the image
        raw = os.path.join(W, 'pieces_page.json')
        polys = []
        # the runs' lines, then (where the panel says so) the least difficult way down's dots, which are the only line
        # the cat tracks it follows have
        for colours, width in (((('green', GREEN), ('blue', BLUE), ('black', R.DARK)), R.LINE_WIDTH),
                               ((('green', GREEN), ('blue', BLUE)), getattr(R, 'WAY_DOWN_WIDTH', None))):
            if not width:
                continue
            cols = [x for k, v in colours for x in ('--color', f'{k}={rgb(v)}')]
            run('python3', '-I', f'{T}/extract_pdf_vectors.py', pdf, '--clip', f'0,0,{page.width},{page.height}',
                '--scale', '1', *cols, '--min-width', str(width[0]), '--max-width', str(width[1]),
                '--min-length', '1', '--out', raw)
            polys += json.load(open(raw))['polylines']
        out = []
        for p in polys:
            runs, cur = [], []
            for u, v in p['points']:
                x, y = on_map(u * page.width / 100, v * page.height / 100)
                if 0 <= x <= iw and 0 <= y <= ih and not outside((x, y)):
                    cur.append((x, y))
                elif cur:
                    runs.append(cur)
                    cur = []
            runs.append(cur)
            for r in runs:
                length = sum(((r[k + 1][0] - r[k][0]) ** 2 + (r[k + 1][1] - r[k][1]) ** 2) ** 0.5
                             for k in range(len(r) - 1))
                if len(r) >= 2 and length >= 3:
                    out.append({'id': len(out), 'cls': p['cls'], 'lengthPx': round(length),
                                'points': [[round(100 * x / iw, 3), round(100 * y / ih, 3)] for x, y in r]})
        os.remove(raw)
        json.dump({'_source': R.SOURCE, 'polylines': out}, open(os.path.join(W, 'pieces.json'), 'w'))
        # the names and symbols, on the page (points), then on the image
        G, L = os.path.join(W, 'glyphs.json'), os.path.join(W, 'glyph_labels.json')
        run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', pdf, '--out', G, '--max-size', '12',
            *[x for k, v in (('black', R.DARK), ('black', R.DARK2), ('blue', BLUE), ('green', GREEN))
              for x in ('--color', f'{k}={rgb(v)}')])
        run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', pdf, '--glyphs', G, '--letters', LETTERS, '--out', L,
            '--square', 'blue', '--diamond', 'black', '--circle', 'green', '--rounded', *R.LABEL_ARGS)
        dd = json.load(open(L))
        labs, syms = [], []
        for lab in dd['labels']:
            c2 = on_map(*lab['c'])
            if 0 <= c2[0] <= iw and 0 <= c2[1] <= ih and not outside(c2):
                labs.append({**lab, 'font': 'glyph', 'color': 'black', 'c': [round(v, 2) for v in c2],
                             'size': round(lab['size'] * a, 1),
                             'pts': [[round(v, 2) for v in on_map(*q)] for q in lab['pts']]})
        for s in dd['symbols']:
            c2 = on_map(*s['c'])
            if 0 <= c2[0] <= iw and 0 <= c2[1] <= ih and not outside(c2):
                syms.append({**s, 'c': [round(v, 2) for v in c2]})
        json.dump({'labels': labs, 'symbols': syms}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
        print(f'  {panel}: {len(out)} pieces, {len(labs)} labels, {len(syms)} symbols')


if __name__ == '__main__':
    main()
