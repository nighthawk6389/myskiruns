"""Difficulty symbols on a raster trail map (no vector PDF; Vail's three panels): solid squarish fills in a trail
colour (blue square, green circle, black diamond). A black pair of diamonds (two lobes with a waist between them, or
two single diamonds side by side) is a double diamond, and a pair holding white letters (two or more holes) is EX.

    python3 tools/trailmap/raster_symbols.py --image panel.png --out syms.json \\
        --size 19,30 --double-area 240,560 --exclude 45,1620,990,1980

--size is a single symbol's extent range in px on this map; --double-area the pixel area range of a double diamond
(drawn smaller than two singles). --exclude blanks legends. Writes [{i, t, c:[x,y], r}] sorted in rows of 200 px,
for naming each symbol on a contact sheet; check doubles on zoomed crops (a lift line's end or a sign can pass).

Requires: pip install pillow numpy opencv-python-headless
"""
import argparse
import collections
import json
import math

import cv2
import numpy as np
from PIL import Image

from raster_lines import masks

Image.MAX_IMAGE_PIXELS = None


def find(A, lo, hi, double_area, excludes):
    M = masks(A)
    for x0, y0, x1, y1 in excludes:
        for m in M.values():
            m[y0:y1, x0:x1] = False
    out = []
    for cls, t in (('blue', 'square'), ('green', 'circle'), ('black', 'diamond')):
        m = M[cls].astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
        for i in range(1, n):
            x, y, w, h, a = st[i]
            ext = max(w, h); asp = w / h; fill = a / (w * h)
            if lo <= ext <= hi and 0.75 <= asp <= 1.33 and fill >= 0.48:
                out.append({'t': t, 'c': [float(cen[i][0]), float(cen[i][1])], 'r': float(ext / 2)})
                continue
            if cls != 'black' or not (1.25 * lo <= ext <= 2.3 * hi):
                continue
            comp = (lab[y:y + h, x:x + w] == i).astype(np.uint8)
            cnts, hier = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts or not (double_area[0] <= a <= double_area[1]):
                continue
            holes = sum(1 for k in range(len(cnts)) if hier[0][k][3] >= 0 and cv2.contourArea(cnts[k]) > 2)
            # two lobes: along the principal axis the shape narrows to a waist between two wide parts
            ys, xs = np.nonzero(comp)
            xs = xs - xs.mean(); ys = ys - ys.mean()
            cxx, cyy, cxy = (xs * xs).mean(), (ys * ys).mean(), (xs * ys).mean()
            ang = 0.5 * math.atan2(2 * cxy, cxx - cyy)
            u = xs * math.cos(ang) + ys * math.sin(ang); v = -xs * math.sin(ang) + ys * math.cos(ang)
            bins = np.round(u).astype(int); bins -= bins.min()
            width = np.array([np.ptp(v[bins == b]) if np.any(bins == b) else 0 for b in range(bins.max() + 1)])
            L = len(width)
            if L < 8:
                continue
            mid = width[L // 3: 2 * L // 3 + 1]
            waist = mid.min(); left = width[:L // 2].max(); right = width[L // 2:].max()
            outer = max(cnts, key=cv2.contourArea)
            solidity = cv2.contourArea(outer) / (cv2.contourArea(cv2.convexHull(outer)) or 1)
            hole_area = sum(cv2.contourArea(cnts[k]) for k in range(len(cnts)) if hier[0][k][3] >= 0)
            if waist < 0.6 * min(left, right) and L > 1.4 * min(left, right) and solidity > 0.6:
                if holes == 0:
                    kind = 'double-diamond'
                elif holes >= 2 and hole_area < 0.35 * a:
                    kind = 'ex'  # white E and X inside (an icon frame has one big hole instead)
                else:
                    continue
                out.append({'t': kind, 'c': [float(cen[i][0]), float(cen[i][1])], 'r': float(ext / 2)})
    # two separate diamonds side by side also make a double diamond
    dia = [s for s in out if s['t'] == 'diamond']
    for a in range(len(dia)):
        for b in range(a + 1, len(dia)):
            if dia[a]['t'] != 'diamond' or dia[b]['t'] != 'diamond':
                continue
            if math.dist(dia[a]['c'], dia[b]['c']) < 2.2 * max(dia[a]['r'], dia[b]['r']):
                dia[a]['t'] = 'double-diamond'
                dia[a]['c'] = [(dia[a]['c'][0] + dia[b]['c'][0]) / 2, (dia[a]['c'][1] + dia[b]['c'][1]) / 2]
                dia[b]['t'] = None
    out = [s for s in out if s['t']]
    out.sort(key=lambda s: (s['c'][1] // 200, s['c'][0]))
    for i, s in enumerate(out):
        s['i'] = i
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--size', required=True, help='lo,hi: a single symbol extent range in px')
    ap.add_argument('--double-area', required=True, help='lo,hi: a double diamond area range in px')
    ap.add_argument('--exclude', action='append', default=[], help='x0,y0,x1,y1 to blank (legend)')
    a = ap.parse_args()
    lo, hi = (int(v) for v in a.size.split(','))
    da = tuple(int(v) for v in a.double_area.split(','))
    ex = [tuple(int(v) for v in e.split(',')) for e in a.exclude]
    out = find(np.asarray(Image.open(a.image).convert('RGB')), lo, hi, da, ex)
    json.dump(out, open(a.out, 'w'), indent=0)
    print(a.out, len(out), dict(collections.Counter(s['t'] for s in out)))


if __name__ == '__main__':
    main()
