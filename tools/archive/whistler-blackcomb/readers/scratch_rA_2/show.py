"""Render a zoomed crop with only chosen pieces drawn thin, side by side with the plain crop.
usage: show.py --box x0,y0,x1,y1 --zoom z --ids 1,2,3 --out out.png [--grid 50] [--width 2] [--stack]
"""
import argparse, json, colorsys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
MAP = '/home/user/myskiruns/work/whistler-blackcomb/main/map.png'
PC = '/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PAL = [(255,0,0),(0,0,255),(0,170,0),(255,0,255),(0,200,200),(255,140,0),(120,0,200),(0,0,0),(160,80,0),(255,255,0)]
ap = argparse.ArgumentParser()
ap.add_argument('--box', required=True); ap.add_argument('--zoom', type=float, default=3)
ap.add_argument('--ids', default=''); ap.add_argument('--out', required=True)
ap.add_argument('--grid', type=int, default=50); ap.add_argument('--width', type=int, default=2)
ap.add_argument('--stack', action='store_true', help='plain above overlay instead of side by side')
ap.add_argument('--noplain', action='store_true')
a = ap.parse_args()
img = Image.open(MAP).convert('RGB'); W, H = img.size
pcs = {p['id']: p for p in json.load(open(PC))['polylines']}
x0, y0, x1, y1 = map(int, a.box.split(',')); x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W, x1), min(H, y1)
z = a.zoom
base = img.crop((x0, y0, x1, y1)).resize((int((x1-x0)*z), int((y1-y0)*z)), Image.LANCZOS).convert('RGBA')
fs = ImageFont.truetype(BOLD, 11); f = ImageFont.truetype(BOLD, 13)
def grid(im):
    ov = Image.new('RGBA', im.size, (0,0,0,0)); d = ImageDraw.Draw(ov)
    if a.grid:
        for gx in range((x0//a.grid+1)*a.grid, x1, a.grid):
            X = (gx-x0)*z; d.line((X,0,X,im.height), fill=(255,0,255,70)); d.text((X+2,2), str(gx), fill=(200,0,200,255), font=fs, stroke_width=2, stroke_fill='white')
        for gy in range((y0//a.grid+1)*a.grid, y1, a.grid):
            Y = (gy-y0)*z; d.line((0,Y,im.width,Y), fill=(255,0,255,70)); d.text((2,Y+2), str(gy), fill=(200,0,200,255), font=fs, stroke_width=2, stroke_fill='white')
    return Image.alpha_composite(im, ov)
plain = grid(base)
ov = Image.new('RGBA', base.size, (0,0,0,0)); d = ImageDraw.Draw(ov)
tags = []
ids = [int(i) for i in a.ids.split(',') if i.strip()]
for k, i in enumerate(ids):
    p = pcs[i]; c = PAL[k % len(PAL)]
    pts = [((q[0]*W/100-x0)*z, (q[1]*H/100-y0)*z) for q in p['points']]
    if len(pts) > 1:
        d.line(pts, fill=c+(200,), width=a.width)
    for e in (pts[0], pts[-1]):
        d.ellipse((e[0]-5, e[1]-5, e[0]+5, e[1]+5), outline=c+(255,), width=2)
    ins = [q for q in pts if 0 <= q[0] < base.width and 0 <= q[1] < base.height]
    if ins:
        tags.append((ins[len(ins)//2], str(i), c))
for (x, y), t, c in tags:
    w = d.textlength(t, font=f)
    d.rectangle((x+3, y-8, x+w+7, y+8), fill=(255,255,255,220))
    d.text((x+5, y-8), t, fill=c+(255,) if c != (255,255,0) else (0,0,0,255), font=f)
over = grid(Image.alpha_composite(base, ov))
if a.noplain:
    out = over
elif a.stack:
    out = Image.new('RGBA', (base.width, base.height*2+6), (255,255,255,255)); out.paste(plain, (0,0)); out.paste(over, (0, base.height+6))
else:
    out = Image.new('RGBA', (base.width*2+6, base.height), (255,255,255,255)); out.paste(plain, (0,0)); out.paste(over, (base.width+6, 0))
out.convert('RGB').save(a.out); print(a.out, out.size)
