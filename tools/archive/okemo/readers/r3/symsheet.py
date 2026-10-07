from PIL import Image, ImageDraw, ImageFont
B='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
img=Image.open(B+'okemo_source.png').convert('RGB')
items=[('SUNSET STRIP',3253,752),('MOUNTAIN ROAD 1',2751,861),('ROUNDHOUSE RUN',2645,887),('COLEMAN BROOK',2670,941),
('UPPER LIMELIGHT',3304,952),('BLUE MOON',3062,996),('TREE DANCER',2676,1030),('MOUNTAIN ROAD 2',2864,1087),('GREEN LINK',2665,1113),
('SIDEWINDER',2889,1216),('LOWER LIMELIGHT',3369,1249),('BOOMERANG',2799,1448),('SCREAMIN DEMON',2621,1459),('UPPER MOONSHADOW',3386,1534),
('RISING STAR',3255,1560),('SIDEOUT',2937,1564),('PROMENADE',3161,1627),('JACK-A-LOPE',3278,1776),('DAYBREAK',3041,1836),('LINE DRIVE',3323,1946),('?? 3421,2020',3421,2020)]
S=8; r=22
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
cells=[]
for n,x,y in items:
    c=img.crop((x-r,y-r,x+r,y+r)).resize((2*r*S,2*r*S),Image.NEAREST)
    cell=Image.new('RGB',(2*r*S,2*r*S+24),'white'); cell.paste(c,(0,24))
    ImageDraw.Draw(cell).text((4,2),n,fill='black',font=font); cells.append(cell)
cols=4; w,h=cells[0].size
rows=(len(cells)+cols-1)//cols
sheet=Image.new('RGB',(cols*w,rows*h),'white')
for i,c in enumerate(cells): sheet.paste(c,((i%cols)*w,(i//cols)*h))
sheet.save(B+'r3/symsheet.png'); print(sheet.size)
