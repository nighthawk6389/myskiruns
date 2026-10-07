import sys; sys.path.insert(0,'.')
from crop import img
from PIL import Image, ImageDraw, ImageFont
L = {"BIRCH RUN":[2092,1408],"MORNING STAR":[2142,1426],"SUNRISE":[2103,1532],"VILLAGE RUN":[2215,1938],
"PANORAMA":[3073,879],"RIM RUN":[3156,962],"BLACK DIAMOND RUSH":[2997,1007],"F.I.S.":[3083,1013],
"UPPER LOOKIN' GOOD":[3162,1064],"LOOKIN' GOOD":[3164,1204],"ELBOW":[3231,1125],"LWR ELBOW":[3309,1278],
"BRAVO WOODS":[3285,1155],"BRAVO":[3305,1087],"EXTERMINATOR":[3367,1109],"BRAVINATOR WOODS":[3364,1154],
"EXTERMINATOR WOODS":[3468,1180],"WAY BACK":[3394,1226],"LOWER RIM RUN":[3046,1230],"ROB ROY":[3154,1254],
"LOWER F.I.S.a":[3060,1330],"LOWER F.I.S.b":[3082,1876],"SPIN OUT":[3121,1354],"SOUTH BOUND":[3155,1430],
"TUMBLER":[3290,1593],"TUMBLER WOODS":[3281,1637],"MOOSE RUN WOODS":[3150,1671],"THE CLIFFS":[3338,1528],
"HAMMERHEAD":[3380,1515],"ENCORE":[3404,1470],"ELLEN'S WOODS":[3372,2093]}
def draw(box, z, out, keys):
    x0,y0,x1,y1=box
    im=img().crop(box).resize((int((x1-x0)*z),int((y1-y0)*z)),Image.LANCZOS)
    d=ImageDraw.Draw(im); f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
    for k in keys:
        x,y=L[k]; px,py=(x-x0)*z,(y-y0)*z
        d.ellipse((px-6,py-6,px+6,py+6),outline=(0,200,0),width=3)
        d.text((px+8,py-6),k,fill=(0,120,255),font=f)
    im.save(out,quality=90)
draw((2940,850,3500,1460),1.6,'lab_ellen_top.jpg',[k for k,v in L.items() if 2940<=v[0]<=3500 and 850<=v[1]<=1460])
draw((2940,1300,3500,2150),1.2,'lab_ellen_low.jpg',[k for k,v in L.items() if 2940<=v[0]<=3500 and 1460<v[1]<=2150])
draw((1950,1330,2320,2000),1.4,'lab_nl.jpg',[k for k,v in L.items() if v[0]<2500])
