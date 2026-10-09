"""How well each line piece lies on the image's own line: the share of its points (every px along it) with a pixel
of its run's colour within --tol px (blue and green as the print draws them; black: any dark pixel, so the
painting's trees count too and a black piece's share is an upper bound; a blue piece's black too: an
advanced-intermediate run is drawn blue under black dashes). The interactive map is a second drawing of
the map, partly of an earlier season's: pieces under --share are listed, worst first, to be looked at on a crop.

    python3 tools/trailmap/resorts/steamboat/checks/ink.py [--share 0.8] [--names]

Reads work/steamboat (map.png, pieces.json or, with --cut, pieces_cut.json and names.json from pdf_resort.py build).
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../../..'))
W = os.path.abspath(os.environ.get('STEAMBOAT_WORK', os.path.join(REPO, 'work/steamboat')))
INK = {'blue': (45, 98, 165), 'green': (55, 150, 90)}


def dense(pts, step=1.0):
    out = []
    for u, v in zip(pts, pts[1:]):
        n = max(1, int(math.dist(u, v) / step))
        out += [(u[0] + (v[0] - u[0]) * k / n, u[1] + (v[1] - u[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tol', type=int, default=2)
    ap.add_argument('--share', type=float, default=0.8)
    ap.add_argument('--dist', type=float, default=50)
    ap.add_argument('--cut', action='store_true', help="pdf_resort.py's pieces_cut.json and names.json")
    a = ap.parse_args()
    img = np.asarray(Image.open(os.path.join(W, 'map.png')).convert('RGB')).astype(float)
    h, w = img.shape[:2]
    masks = {k: np.linalg.norm(img - np.array(c), axis=2) < a.dist for k, c in INK.items()}
    masks['black'] = img.max(axis=2) < 70
    masks['blue'] = masks['blue'] | masks['black']  # an advanced-intermediate run: blue under black dashes
    near = {k: ndimage.binary_dilation(m, iterations=a.tol) for k, m in masks.items()}
    P = json.load(open(os.path.join(W, 'pieces_cut.json' if a.cut else 'pieces.json')))['polylines']
    names = json.load(open(os.path.join(W, 'names.json'))) if a.cut else {}
    rows = []
    for p in P:
        pts = dense([(x * w / 100, y * h / 100) for x, y in p['points']])
        ok = [near[p['cls']][min(h - 1, max(0, round(y))), min(w - 1, max(0, round(x)))] for x, y in pts]
        share = sum(ok) / len(ok)
        rows.append((share, p['id'], p['cls'], p.get('name') or names.get(str(p['id']), ''), p['lengthPx'],
                     [round(v) for v in pts[len(pts) // 2]]))
    rows.sort()
    bad = [r for r in rows if r[0] < a.share]
    for share, pid, cls, nm, ln, mid in bad:
        print(f'{pid:4d} {cls:5s} {share:4.0%} {ln:5d} px  mid {mid[0]},{mid[1]}  {nm}')
    print(f'{len(bad)} of {len(rows)} pieces under {a.share:.0%}')


if __name__ == '__main__':
    main()
