import sys, numpy as np, pymupdf
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS=None
A=(1.3888948, 0.0000021, -27.5124, 0.0000022, 1.3888649, 573.8250)
s=(A[0]+A[4])/2
x0,y0=-A[2]/A[0],-A[5]/A[4]
nov=Image.open('work/deer-valley/src/nov4.png').convert('RGB')
W,H=nov.size
pg=pymupdf.open('work/deer-valley/skimap/223_35124')[0]
clip=pymupdf.Rect(x0,y0,x0+W/s,y0+H/s) & pg.rect
pix=pg.get_pixmap(matrix=pymupdf.Matrix(s,s),clip=clip)
o=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
oct_=Image.new('RGB',(W,H),(128,128,128))
off=(round((clip.x0-x0)*s),round((clip.y0-y0)*s)); print(clip, off, o.size)
oct_.paste(o,off)
oct_.save('work/deer-valley/src/oct_on_nov.png')
a=np.asarray(nov.filter(ImageFilter.GaussianBlur(2)),np.float32); b=np.asarray(oct_.filter(ImageFilter.GaussianBlur(2)),np.float32)
d=np.abs(a-b).max(axis=2)
m=np.zeros((H,W),bool); m[off[1]:off[1]+o.size[1], off[0]:off[0]+o.size[0]]=True
d[~m]=0
Image.fromarray(np.clip(d*2,0,255).astype(np.uint8)).save('work/deer-valley/src/diff.png')
print(np.percentile(d[m],[50,90,99,99.9]))
