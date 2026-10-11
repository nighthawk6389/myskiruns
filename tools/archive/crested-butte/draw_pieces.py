"""Crested Butte: each line piece drawn over the faded map in its class's colour, the whole map at half size or a
crop with each piece's id: the first look at what pdf_outline_lines.py read (letters, the boundary's dashes and the
fences' left as lines; the black runs' dashes not yet linked).

    python3 tools/archive/crested-butte/draw_pieces.py work/crested-butte/main/map.png \
        work/crested-butte/main/pieces.json out.png [x0,y0,x1,y1]
"""
import json, sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
img, pieces, out = sys.argv[1:4]
crop = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
im=Image.open(img).convert('RGB'); W,H=im.size
im=Image.blend(im, Image.new('RGB',im.size,'white'), 0.6); d=ImageDraw.Draw(im)
col={'black':(255,0,255),'blue':(0,0,255),'green':(0,160,0),'park':(255,120,0)}
for p in json.load(open(pieces))['polylines']:
    d.line([(x*W/100,y*H/100) for x,y in p['points']], fill=col.get(p['cls'],(255,0,0)), width=5)
    if crop:
        x,y=p['points'][len(p['points'])//2]; d.text((x*W/100+4,y*H/100), str(p['id']), fill=(200,0,0))
if crop: im=im.crop(crop)
else: im=im.resize((W//2,H//2))
im.save(out)
