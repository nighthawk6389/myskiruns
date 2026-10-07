import sys, math
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
im=Image.open('/home/user/myskiruns/work/whistler-blackcomb/main/map.png').convert('RGB')
pts=[tuple(map(float,s.split(','))) for s in sys.argv[1:]]
out=[]
for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
    L=math.hypot(x1-x0,y1-y0); n=max(1,int(L/1.5))
    for i in range(n):
        t=i/n; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
        r,g,b=im.getpixel((round(x),round(y)))
        # classify
        if r>200 and g>200 and b>200: k='W'
        elif g>120 and r<100 and b<120: k='G'
        elif r>180 and g<90 and b<90: k='R'
        elif r>200 and g>180 and b<120: k='Y'
        elif b>150 and r<100: k='B'
        elif r<70 and g<70 and b<70: k='K'
        else: k='.'
        out.append(f'{round(x)},{round(y)}:{k}')
print(' '.join(out))
