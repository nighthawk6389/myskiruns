import json, io, sys, colorsys, hashlib
import pymupdf
from PIL import Image, ImageDraw, ImageFont
BASE='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
x0,y0,x1,y1=map(float,sys.argv[1:5]); S=float(sys.argv[5]); out=sys.argv[6]
page=pymupdf.open(BASE+'okemo.pdf')[1]
pix=page.get_pixmap(matrix=pymupdf.Matrix(3*S,3*S),clip=pymupdf.Rect(x0/3,y0/3,x1/3,y1/3))
im=Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGBA')
im=Image.blend(im,Image.new('RGBA',im.size,(255,255,255,255)),0.45)
res=json.load(open(BASE+'tiles/result_0.json'))
polys={p['id']:p for p in json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']}
W,H=4374,2739
d=ImageDraw.Draw(im); font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
for l in res['lines']:
    h=int(hashlib.md5(l['mapName'].encode()).hexdigest()[:6],16)/0xffffff
    r,g,b=[int(255*v) for v in colorsys.hsv_to_rgb(h,0.9,0.85)]
    q=[((x*W/100-x0)*S,(y*H/100-y0)*S) for x,y in polys[l['id']]['points']]
    d.line(q,fill=(r,g,b,255),width=4)
    m=q[len(q)//2]
    t=f"{l['id']}:{l['mapName']}"
    d.text((m[0]+4,m[1]-7),t,fill=(r,g,b,255),font=font,stroke_width=2,stroke_fill=(255,255,255,255))
im.convert('RGB').save(out,quality=90); print(out,im.size)
