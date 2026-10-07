from PIL import Image, ImageDraw, ImageFont
import sys
BASE='/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
src=Image.open(BASE+'okemo_source.png').convert('RGB')
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
items=[
('UPPER MTN ROAD',1998,486),('EASY RIDER',2158,594),('WHISTLER up',2052,597),('WHISPERING PINES',2303,623),
('SWEET SOLITUDE',2233,693),('WHISTLER low',2175,734),('TOMAHAWK blue',2116,736),('UPPER SAPPHIRE',2061,752),
('EVERGLADE',2419,770),('UPPER TIMBERLINE',2009,842),('MOUNTAIN ROAD',2751,861),('CUTTERS FOLLY',2068,865),
('ROUNDHOUSE RUN',2645,887),('EXPRESS LANE',2254,901),('COLEMAN BROOK',2670,941),('RT 103',2139,971),
('LOWER SAPPHIRE',2238,983),('EXHIBITION',2505,995),('HEAVENS GATE',2405,996),('TREE DANCER',2673,1030),
('LOWER TIMBERLINE',2169,1086),('GREEN LINK',2665,1113),('UPPER ARROW',2099,1140),('RIDGE RUNNER',2253,1143),
('SELS CHOICE',2072,1192),('DOUBLE DIPPER',2211,1228),('LOWER MTN ROAD',2389,1290),('SWITCHBACK',2296,1329),
('BROKEN ARROW',2141,1334),('THE SHADOWS',2377,1401),('THE PLUNGE',2475,1422),('SCREAMIN DEMON',2621,1459),
('BOOMERANG',2799,1448),('LOWER ARROW',2193,1538),('VILLAGE RUN',2515,1575),('HOMEWARD BOUND',2109,1777),
('SNOW TRACK',2233,1832),('LEDGEWOOD',2057,1936),('KETTLE BROOK',1937,1955),('TOMAHAWK park',2322,982),
]
R=22; Z=7
cell=2*R*Z
cols=6
rows=(len(items)+cols-1)//cols
sheet=Image.new('RGB',(cols*cell,rows*(cell+18)),'white')
d=ImageDraw.Draw(sheet)
for k,(n,x,y) in enumerate(items):
    c=src.crop((x-R,y-R,x+R,y+R)).resize((cell,cell),Image.NEAREST)
    cx,cy=(k%cols)*cell,(k//cols)*(cell+18)
    sheet.paste(c,(cx,cy+18))
    d.text((cx+3,cy+2),f'{n} ({x},{y})',fill=(200,0,0),font=f)
sheet.save('symsheet_r2.png')
print(sheet.size)
