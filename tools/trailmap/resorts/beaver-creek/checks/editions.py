"""Beaver Creek: where the 2025-26 image (the map image) differs from the 2023 PDF it takes its lines, names and
symbols from (the playbook, Part 1, recipe D, step 2). Run after regen.sh (it reads work/beaver-creek/).

    python3 -I tools/trailmap/resorts/beaver-creek/checks/editions.py            # the differences, largest first
    python3 -I tools/trailmap/resorts/beaver-creek/checks/editions.py --sheet x,y,w,h ...   # crops of some

The page is rendered on the image's grid (resort.AFFINE's scale and offset), the two compared pixel by pixel (the
largest channel difference, blurred 1.5 px, over 60), the differences grown 15 px into regions; each region of 800
px or more is listed as x, y, w, h (map px). --sheet draws each region given, the 2025-26 image beside the 2023
page (work/beaver-creek/editions/sheet.png). Read them: the 2023 page and this season's image differ in the icons
of the base areas (lodge and restaurant signs moved), the partners' band, dashes drawn from another phase, and
Dakota Skiway, new at Arrowhead (traced in decisions.py).
"""
import argparse
import os
import sys

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../../..'))
sys.path.insert(0, os.path.dirname(HERE))
from resort import AFFINE  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('BEAVER_CREEK_WORK', os.path.join(REPO, 'work/beaver-creek')))


def render(size):
    s = (AFFINE[0] + AFFINE[4]) / 2
    page = pymupdf.open(os.path.join(W, 'beavercreek_2023.pdf'))[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(s, s))
    pdf = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    m = np.float32([[1, 0, AFFINE[2]], [0, 1, AFFINE[5]]])
    return cv2.warpAffine(pdf, m, size, borderValue=(128, 128, 128))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheet', nargs='*', help='x,y,w,h regions to draw side by side')
    a = ap.parse_args()
    img = np.asarray(Image.open(os.path.join(W, 'beavercreek_2025-26.png')).convert('RGB'))
    pdf = render((img.shape[1], img.shape[0]))
    if a.sheet:
        out = os.path.join(W, 'editions')
        os.makedirs(out, exist_ok=True)
        tiles = []
        for b in a.sheet:
            x, y, w, h = map(int, b.split(','))
            box = (x - 60, y - 60, x + w + 60, y + h + 60)
            t1, t2 = Image.fromarray(img).crop(box), Image.fromarray(pdf).crop(box)
            k = min(1.0, 700 / t1.width)
            if k < 1:
                t1, t2 = t1.resize((int(t1.width * k), int(t1.height * k))), t2.resize((int(t2.width * k), int(t2.height * k)))
            t = Image.new('RGB', (t1.width * 2 + 10, t1.height + 20), 'white')
            t.paste(t1, (0, 20)); t.paste(t2, (t1.width + 10, 20))
            ImageDraw.Draw(t).text((4, 4), f'{x},{y}  2025-26 | 2023', fill='red')
            tiles.append(t)
        sheet = Image.new('RGB', (max(t.width for t in tiles), sum(t.height + 6 for t in tiles)), 'grey')
        yy = 0
        for t in tiles:
            sheet.paste(t, (0, yy)); yy += t.height + 6
        sheet.save(os.path.join(out, 'sheet.png'))
        print('->', os.path.join(out, 'sheet.png'))
        return
    d = np.abs(img.astype(int) - pdf.astype(int)).max(axis=2).astype(np.uint8)
    m = (cv2.GaussianBlur(d, (0, 0), 1.5) > 60).astype(np.uint8)
    m = cv2.dilate(m, np.ones((15, 15), np.uint8))
    n, _lab, st, _c = cv2.connectedComponentsWithStats(m)
    regions = sorted(((int(st[i, 4]), tuple(int(v) for v in st[i, :4])) for i in range(1, n) if st[i, 4] > 800), reverse=True)
    print(len(regions), 'regions (area, x, y, w, h)')
    for area, (x, y, w, h) in regions:
        print(area, f'{x},{y},{w},{h}')


if __name__ == '__main__':
    main()
