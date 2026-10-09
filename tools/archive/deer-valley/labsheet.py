import json, sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
A=(1.3888948, 0.0000021, -27.5124, 0.0000022, 1.3888649, 573.8250)
nov=Image.open('work/deer-valley/src/nov4.png').convert('RGB')
oc=Image.open('work/deer-valley/src/oct_on_nov.png').convert('RGB')
d=json.load(open('work/deer-valley/printed.json'))
def px(p): return (A[0]*p[0]+A[1]*p[1]+A[2], A[3]*p[0]+A[4]*p[1]+A[5])
labs=sorted([l for l in d['labels'] if l.get('font')=='glyph'], key=lambda l:l['seq'])
if len(sys.argv)>2: order=[int(v) for v in open(sys.argv[2]).read().split()]; byseq={l['seq']:l for l in labs}; labs=[byseq[q] for q in order if q in byseq]
z=1.3; CW,CH=420,260
cells=[]
for i,l in enumerate(labs):
    P=[px(p) for p in l['pts']]
    xs=[p[0] for p in P]; ys=[p[1] for p in P]
    cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2
    w=max(max(xs)-min(xs)+30,60); h=max(max(ys)-min(ys)+30,40)
    w=min(w,CW/z/2*2); h=min(h,(CH-14)/z/2)
    b=(int(cx-w/2),int(cy-h/2),int(cx+w/2),int(cy+h/2))
    a=nov.crop(b).resize((int((b[2]-b[0])*z),int((b[3]-b[1])*z))); c=oc.crop(b).resize(a.size)
    t=Image.new('RGB',(CW,CH),'white'); t.paste(a,(0,14)); t.paste(c,(0,14+a.height+2))
    ImageDraw.Draw(t).text((2,1),f"{l['seq']} {l['text']}",fill='red')
    cells.append(t)
per=int(sys.argv[1]) if len(sys.argv)>1 else 40
cols=4
for s in range(0,len(cells),per):
    chunk=cells[s:s+per]; rows=(len(chunk)+cols-1)//cols
    o=Image.new('RGB',(cols*(CW+4),rows*(CH+4)),'gray')
    for k,t in enumerate(chunk): o.paste(t,((k%cols)*(CW+4),(k//cols)*(CH+4)))
    o.save(f'work/deer-valley/src/{sys.argv[3] if len(sys.argv)>3 else "labs"}_{s//per:02d}.png')
print(len(cells))
