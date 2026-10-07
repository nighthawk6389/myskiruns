import sys, json
from PIL import Image, ImageDraw, ImageFont
BASE='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
SRC=Image.open(BASE+'r2/vector_only.png').convert('RGB')
W,H=SRC.size
PL=json.load(open('/home/user/myskiruns/src/data/resorts/okemo/linePolylines.json'))['polylines']
def crop(x0,y0,x1,y1,scale,out,overlay=False,grid=0):
    im=SRC.crop((x0,y0,x1,y1)).resize((int((x1-x0)*scale),int((y1-y0)*scale)),Image.LANCZOS)
    d=ImageDraw.Draw(im)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
    if overlay:
        for p in PL:
            pts=[((x*W/100-x0)*scale,(y*H/100-y0)*scale) for x,y in p['points']]
            if all(not(0<=a<=im.width and 0<=b<=im.height) for a,b in pts): continue
            d.line(pts,fill=(255,0,255),width=1)
            for a,b in (pts[0],pts[-1]):
                d.ellipse((a-2,b-2,a+2,b+2),fill=(255,0,255))
            m=pts[len(pts)//2]
            d.text((m[0]+4,m[1]-8),str(p['id']),fill=(255,200,0),font=f,stroke_width=2,stroke_fill=(0,0,0))
    if grid:
        g=grid
        for gx in range((x0//g+1)*g, x1, g):
            X=(gx-x0)*scale; d.line([(X,0),(X,6)],fill=(255,0,0),width=1); d.text((X+2,0),str(gx),fill=(255,0,0),font=f)
        for gy in range((y0//g+1)*g, y1, g):
            Y=(gy-y0)*scale; d.line([(0,Y),(6,Y)],fill=(255,0,0),width=1); d.text((0,Y+2),str(gy),fill=(255,0,0),font=f)
    im.save(out, quality=92)
    print(out, im.size)
if __name__=='__main__':
    a=sys.argv
    x0,y0,x1,y1=map(int,a[1:5]); sc=float(a[5]); out=a[6]
    ov = len(a)>7 and a[7]=='ov'
    grid = int(a[8]) if len(a)>8 else 0
    crop(x0,y0,x1,y1,sc,out,ov,grid)
