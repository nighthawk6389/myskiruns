import sys, numpy as np, cv2
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
nov=Image.open('work/deer-valley/src/nov4.png').convert('RGB')
oc=Image.open('work/deer-valley/src/oct_on_nov.png').convert('RGB')
boxes=[tuple(map(int,b.split(','))) for b in sys.argv[2:]]
tiles=[]
for x,y,w,h in boxes:
    pad=40; b=(x-pad,y-pad,x+w+pad,y+h+pad)
    a=nov.crop(b); c=oc.crop(b)
    z=2
    a=a.resize((a.width*z,a.height*z)); c=c.resize((c.width*z,c.height*z))
    t=Image.new('RGB',(a.width*2+10,a.height+16),'white'); t.paste(a,(0,16)); t.paste(c,(a.width+10,16))
    ImageDraw.Draw(t).text((2,2),f'{x},{y} nov | oct',fill='black'); tiles.append(t)
W=max(t.width for t in tiles); H=sum(t.height+6 for t in tiles)
out=Image.new('RGB',(W,H),'white'); yy=0
for t in tiles: out.paste(t,(0,yy)); yy+=t.height+6
out.save(sys.argv[1]); print(out.size)
