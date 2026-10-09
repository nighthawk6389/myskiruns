"""Lines the interactive map may not draw: the image's pixels in a run's blue or green (within --dist of the colour
the print uses) farther than --near px from every line piece, every name's letters and every symbol, in blobs of
--min px or more, listed with their box (map px) to be looked at on a crop. Black runs are left out: the painting's
trees and shadows are as dark.

    python3 tools/trailmap/resorts/steamboat/checks/missed.py [--out work/steamboat/missed.png]

Reads work/steamboat (map.png, pieces.json, printed.json; $STEAMBOAT_WORK overrides): run it after prepare.py.
"""
import argparse
import json
import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../../..'))
W = os.path.abspath(os.environ.get('STEAMBOAT_WORK', os.path.join(REPO, 'work/steamboat')))
INK = {'blue': (45, 98, 165), 'green': (55, 150, 90)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dist', type=float, default=45)
    ap.add_argument('--near', type=int, default=6)
    ap.add_argument('--min', type=int, default=25)
    ap.add_argument('--out', default=os.path.join(W, 'missed.png'))
    a = ap.parse_args()
    img = np.asarray(Image.open(os.path.join(W, 'map.png')).convert('RGB')).astype(float)
    h, w = img.shape[:2]
    cover = np.zeros((h, w), np.uint8)
    for p in json.load(open(os.path.join(W, 'pieces.json')))['polylines']:
        pts = np.array([[x * w / 100, y * h / 100] for x, y in p['points']], np.int32)
        cv2.polylines(cover, [pts], False, 255, 2 * a.near + 1)
    pr = json.load(open(os.path.join(W, 'printed.json')))
    for l in pr['labels']:
        for x, y in l['pts']:
            cv2.circle(cover, (round(x), round(y)), 9, 255, -1)
    for s in pr['symbols']:
        cv2.circle(cover, (round(s['c'][0]), round(s['c'][1])), 10, 255, -1)
    show = Image.open(os.path.join(W, 'map.png')).convert('RGB')
    found = []
    for name, ink in INK.items():
        m = (np.linalg.norm(img - np.array(ink), axis=2) < a.dist) & (cover == 0)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = st[i]
            if area >= a.min and max(bw, bh) >= 12:
                found.append((int(area), name, int(x), int(y), int(x + bw), int(y + bh)))
    found.sort(reverse=True)
    from PIL import ImageDraw
    d = ImageDraw.Draw(show)
    for area, name, x0, y0, x1, y1 in found:
        print(f'{name:5s} {area:5d} px  box {x0},{y0},{x1},{y1}')
        d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=(255, 0, 255), width=2)
    show.save(a.out)
    print(len(found), 'blobs ->', a.out)


if __name__ == '__main__':
    main()
