import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
panel=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2].split(',')); step=int(sys.argv[3]) if len(sys.argv)>3 else 1
im=Image.open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/map.png').convert('RGB')
px=im.load()
def cls(c):
    r,g,b=c
    if r>200 and g<80 and b<80: return 'R'
    if r<60 and g>120 and b<110 and g>r+50: return 'G'
    if b>150 and r<90 and 100<g<200 and b>g+20: return 'B'   # trail blue
    if b>90 and r<60 and g<80: return 'N'  # navy
    if r<70 and g<70 and b<70: return 'K'
    if r>230 and g>230 and b>230: return ' '
    if r>200 and g>200 and b<120: return 'Y'
    if r>200 and 100<g<190 and b<80: return 'O'
    if r>100 and b>120 and g<90: return 'P'
    return '.'
print('     '+''.join(str((x//10)%10) if x%10==0 else ' ' for x in range(x0,x1,step)))
for y in range(y0,y1,step):
    print(f'{y:4d} '+''.join(cls(px[x,y]) for x in range(x0,x1,step)))
