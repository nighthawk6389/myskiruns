import sys, json
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
im=Image.open('../sugarbush_source.png').convert('RGB')
L=json.load(open(sys.argv[1]))
x0,y0,x1,y1=map(int,sys.argv[3:7]); z=float(sys.argv[7])
c=im.crop((x0,y0,x1,y1)).resize((int((x1-x0)*z),int((y1-y0)*z)),Image.LANCZOS)
d=ImageDraw.Draw(c); font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
for name,(x,y) in L.items():
    px,py=(x-x0)*z,(y-y0)*z
    if not(0<=px<c.width and 0<=py<c.height): continue
    d.line((px-8,py,px+8,py),fill=(255,0,0),width=3); d.line((px,py-8,px,py+8),fill=(255,0,0),width=3)
    d.text((px+6,py+4),name,fill=(200,0,0),font=font)
c.save(sys.argv[2]); print(c.size)
