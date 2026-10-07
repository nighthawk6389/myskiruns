import json, colorsys, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
im=Image.open('../sugarbush_source.png').convert('RGB')
W,H=im.size
polys={p['id']:p for p in json.load(open('/home/user/myskiruns/src/data/resorts/sugarbush/linePolylines.json'))['polylines']}
r=json.load(open('../tiles/result_2.json'))
x0,y0,x1,y1=map(int,sys.argv[2:6]); z=float(sys.argv[6])
c=im.crop((x0,y0,x1,y1)).resize((int((x1-x0)*z),int((y1-y0)*z)),Image.LANCZOS)
c=Image.blend(c,Image.new('RGB',c.size,(255,255,255)),0.35)
d=ImageDraw.Draw(c); font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',12)
names=sorted({l['mapName'] for l in r['lines']})
for k,l in enumerate(r['lines']):
    h=(names.index(l['mapName'])*0.618)%1
    col=tuple(int(255*v) for v in colorsys.hsv_to_rgb(h,1,0.85))
    q=[((x*W/100-x0)*z,(y*H/100-y0)*z) for x,y in polys[l['id']]['points']]
    d.line(q,fill=col,width=4)
    ins=[pt for pt in q if 0<=pt[0]<c.width and 0<=pt[1]<c.height]
    if ins:
        mx,my=ins[len(ins)//2]
        t=f"{l['id']}:{l['mapName']}"
        d.rectangle((mx+3,my-7,mx+7+d.textlength(t,font=font),my+8),fill=(255,255,255))
        d.text((mx+5,my-7),t,fill=col,font=font)
c.save(sys.argv[1]); print(c.size)
