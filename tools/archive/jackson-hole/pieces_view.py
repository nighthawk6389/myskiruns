"""Draw pieces.json (percent) on the faded map, coloured by class, in tiles: jh_pieces_view.py <map> <pieces> <out prefix> [tile w h]"""
import json, sys
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert('RGB')
W, H = im.size
fade = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.55)
d = ImageDraw.Draw(fade)
col = {'blue': (0, 70, 255), 'green': (0, 170, 0), 'black': (255, 0, 0)}
for p in json.load(open(sys.argv[2]))['polylines']:
    pts = [(x * W / 100, y * H / 100) for x, y in p['points']]
    d.line(pts, fill=col.get(p['cls'], (255, 0, 255)), width=3)
    d.ellipse((pts[0][0] - 3, pts[0][1] - 3, pts[0][0] + 3, pts[0][1] + 3), fill=(255, 0, 255))
    d.ellipse((pts[-1][0] - 3, pts[-1][1] - 3, pts[-1][0] + 3, pts[-1][1] + 3), fill=(255, 0, 255))
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 1000; th = int(sys.argv[5]) if len(sys.argv) > 5 else 700
k = 0
for y in range(280, H - 300, th):
    for x in range(0, W, tw):
        fade.crop((x, y, x + tw, y + th)).save(f'{sys.argv[3]}_{k}_{x}_{y}.png'); k += 1
