# vector render of PDF page 2 for a SOURCE-px box, zoom S relative to source px
import sys, json, io
import pymupdf
from PIL import Image, ImageDraw, ImageFont
BASE='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
x0,y0,x1,y1=map(float,sys.argv[1:5]); S=float(sys.argv[5]); out=sys.argv[6]
sel=sys.argv[7] if len(sys.argv)>7 else 'none'
page=pymupdf.open(BASE+'okemo.pdf')[1]
pix=page.get_pixmap(matrix=pymupdf.Matrix(3*S,3*S),clip=pymupdf.Rect(x0/3,y0/3,x1/3,y1/3))
crop=Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGBA')
W,H=4374,2739
if sel!='none':
    polys=json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']
    ids=None if sel=='all' else set(int(v) for v in sel.split(','))
    ov=Image.new('RGBA',crop.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
    for p in polys:
        if ids is not None and p['id'] not in ids: continue
        q=[((x*W/100-x0)*S,(y*H/100-y0)*S) for x,y in p['points']]
        if not any(-50<=a<crop.width+50 and -50<=b<crop.height+50 for a,b in q): continue
        d.line(q,fill=(255,0,255,140),width=1)
        for e in (q[0],q[-1]):
            d.ellipse((e[0]-3,e[1]-3,e[0]+3,e[1]+3),fill=(255,0,255,230))
        ins=[pt for pt in q if 0<=pt[0]<crop.width and 0<=pt[1]<crop.height]
        if ins:
            mx,my=ins[len(ins)//2]
            t=str(p['id']); tw=d.textlength(t,font=font)
            d.rectangle((mx-tw/2-2,my-18,mx+tw/2+2,my-2),fill=(255,255,0,200),outline=(0,0,0,255))
            d.text((mx-tw/2,my-18),t,fill=(0,0,0,255),font=font)
    crop=Image.alpha_composite(crop,ov)
crop.convert('RGB').save(out,quality=92)
print(out,crop.size)
