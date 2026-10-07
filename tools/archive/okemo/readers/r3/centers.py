import json, math
G=json.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/r3/glyphs.json'))
L=[('SUNSET STRIP','green',(3253,752),(3355,722)),
('MOUNTAIN ROAD#1','green',(2751,861),(2868,920)),
('ROUNDHOUSE RUN','green',(2645,887),(2782,929)),
('COLEMAN BROOK','green',(2670,941),(2776,1020)),
('UPPER LIMELIGHT','black',(3304,952),(3392,856)),
('BLUE MOON','blue',(3062,996),(3152,1013)),
('MOUNTAIN ROAD#2','green',(2864,1087),(2957,1036)),
('GREEN LINK','green',(2665,1113),(2752,1101)),
('SIDEWINDER','blue',(2889,1216),(2966,1258)),
('LOWER LIMELIGHT','blue',(3369,1249),(3452,1352)),
('BOOMERANG','blue',(2799,1448),(2823,1545)),
("SCREAMIN' DEMON",'blue',(2621,1459),(2728,1555)),
('SIDEOUT','blue',(2937,1564),(2982,1510)),
('RISING STAR','green',(3255,1560),(3265,1485)),
('UPPER MOONSHADOW','blue',(3386,1534),(3460,1685)),
('PROMENADE','green',(3161,1627),(3257,1642)),
('JACK-A-LOPE','green',(3278,1776),(3382,1792)),
('DAYBREAK','green',(3041,1836),(3072,1912)),
('LINE DRIVE','blue',(3323,1946),(3372,2010)),
('TREE DANCER text','black',(2651,994),(2697,1012)),
]
def dseg(p,a,b):
    ax,ay=a;bx,by=b;px,py=p
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    t=max(-0.05,min(1.1,((px-ax)*dx+(py-ay)*dy)/L2))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
for n,c,a,b in L:
    tol=14 if 'TREE' in n else 9
    g=[q for q in G if (q['c']==c or (c=='black' and q['c']=='dark')) and dseg((q['x'],q['y']),a,b)<tol and math.hypot(q['x']-a[0],q['y']-a[1])>3]
    if not g: print(n,'none'); continue
    xs=[q['x'] for q in g]; ys=[q['y'] for q in g]
    far=max(g,key=lambda q:math.hypot(q['x']-a[0],q['y']-a[1]))
    print(f"{n:18s} n={len(g):2d} centre=({sum(xs)/len(xs):.0f},{sum(ys)/len(ys):.0f}) bbox=({min(xs):.0f},{min(ys):.0f})-({max(xs):.0f},{max(ys):.0f}) farthest=({far['x']:.0f},{far['y']:.0f})")
