import sys
sys.path.insert(0,'.')
from crop import img
from PIL import Image, ImageDraw, ImageFont
pts = [l.split('|') for l in sys.argv[2].split(';')]
r = int(sys.argv[3]) if len(sys.argv)>3 else 30
z = 6
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
tiles=[]
for name,xy in pts:
    x,y=map(int,xy.split(','))
    c=img().crop((x-r,y-r,x+r,y+r)).resize((2*r*z,2*r*z),Image.LANCZOS)
    d=ImageDraw.Draw(c); d.rectangle((0,0,2*r*z,18),fill='white'); d.text((3,1),name,fill='black',font=font)
    tiles.append(c)
cols=4
w=2*r*z; rows=(len(tiles)+cols-1)//cols
o=Image.new('RGB',(cols*(w+6),rows*(w+6)),'white')
for i,t in enumerate(tiles): o.paste(t,((i%cols)*(w+6),(i//cols)*(w+6)))
o.save(sys.argv[1],quality=90)
