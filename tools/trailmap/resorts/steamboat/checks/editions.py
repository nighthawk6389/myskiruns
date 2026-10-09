"""Where Steamboat's 2026-27 trail map differs from the 2025-26 one (the same artwork): the 2025-26 image (skimap.org
36311, 10156 px wide) warped onto the 2026-27 image (the resort's, 2400 px) by AFFINE_2526 (register_pages.py), both
blurred, and the clusters of strong colour difference listed, largest first, each with a pair of crops (2026-27
left, 2025-26 right) to read.

    python3 tools/trailmap/resorts/steamboat/checks/editions.py [--out work/steamboat/editions] [--top 40]

Reads $STEAMBOAT_WORK (default work/steamboat): steamboat_2026-27.jpg (regen.sh downloads it) and skimap/36311.bin
(the README has the command).
"""
import argparse
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../../..'))
sys.path.insert(0, os.path.join(HERE, '..'))
W = os.path.abspath(os.environ.get('STEAMBOAT_WORK', os.path.join(REPO, 'work/steamboat')))

# the 2025-26 image (px) on the 2026-27 image (px): x = a u + b v + c, y = d u + e v + f (register_pages.py --ref on the
# 2025-26 image halved, --ref-scale 2: 2882 inliers, median residual 0.29 px)
AFFINE_2526 = (0.2337306, -0.0000059, 16.0090, -0.0000019, 0.2333268, 29.2298)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(W, 'editions'))
    ap.add_argument('--top', type=int, default=40)
    ap.add_argument('--thresh', type=int, default=90, help='colour difference (0-255) that counts as a change')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    new = Image.open(os.path.join(W, 'steamboat_2026-27.jpg')).convert('RGB')
    old = Image.open(os.path.join(W, 'skimap/36311.bin')).convert('RGB')
    w, h = new.size
    A = np.array([[AFFINE_2526[0], AFFINE_2526[1], AFFINE_2526[2]], [AFFINE_2526[3], AFFINE_2526[4], AFFINE_2526[5]]])
    oldw = cv2.warpAffine(np.asarray(old), A, (w, h), flags=cv2.INTER_AREA, borderValue=(128, 128, 128))
    Image.fromarray(oldw).save(os.path.join(a.out, 'old_on_new.png'))
    na = np.asarray(new.filter(ImageFilter.GaussianBlur(1.5)), np.float32)
    oa = np.asarray(Image.fromarray(oldw).filter(ImageFilter.GaussianBlur(1.5)), np.float32)
    d = np.abs(na - oa).max(axis=2)
    Image.fromarray(np.clip(d * 2, 0, 255).astype(np.uint8)).save(os.path.join(a.out, 'diff.png'))
    m = cv2.dilate((d >= a.thresh).astype(np.uint8), np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    rows = sorted(((int(st[i][4]), *map(int, st[i][:4])) for i in range(1, n) if st[i][4] >= 60), reverse=True)
    print(len(rows), 'clusters; percentiles of the difference', np.percentile(d, [50, 90, 99, 99.9]).round(1))
    for k, (area, x, y, bw, bh) in enumerate(rows[:a.top]):
        pad = 30
        box = (max(0, x - pad), max(0, y - pad), min(w, x + bw + pad), min(h, y + bh + pad))
        z = 3
        l = new.crop(box).resize(((box[2] - box[0]) * z, (box[3] - box[1]) * z), Image.LANCZOS)
        r = Image.fromarray(oldw).crop(box).resize(l.size, Image.LANCZOS)
        pair = Image.new('RGB', (l.width * 2 + 6, l.height), (255, 0, 255))
        pair.paste(l, (0, 0))
        pair.paste(r, (l.width + 6, 0))
        pair.save(os.path.join(a.out, f'c{k:02d}_{x}_{y}.png'))
        print(f'c{k:02d}: area {area}, box {x},{y},{x + bw},{y + bh}')


if __name__ == '__main__':
    main()
