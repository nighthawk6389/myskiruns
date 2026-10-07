from PIL import Image, ImageDraw, ImageFont
im = Image.open('../okemo_source.png').convert('RGB')
items = [
 ('BIG BANG', 3765, 771), ('BLACK HOLE', 3696, 853), ('SUPERNOVA', 3465, 1267), ('ROLLING THUNDER', 3492, 1168),
 ('VORTEX', 3519, 820), ('UPPER LIMELIGHT', 3304, 952), ('WHITE LIGHTNING', 3515, 1047), ('ECLIPSE', 3829, 1104),
 ('QUANTUM LEAP', 3786, 1252), ('TUCKERED OUT', 3918, 743), ('LOWER LIMELIGHT', 3369, 1249), ('UPPER MOONSHADOW', 3386, 1534),
 ('LINE DRIVE', 3323, 1946), ('LOWER MOONSHADOW', 3421, 2020), ('SUNSET STRIP', 3253, 752), ('RISING STAR', 3255, 1560),
 ('JACK-A-LOPE', 3278, 1776), ('SOUTHERN CROSSING', 3514, 1832), ('EXPRESSO', 3984, 1684), ('FAST TRACK', 4019, 1877),
 ('INN BOUND', 3937, 2060), ('BRIGHT STAR BASIN', 3935, 2160), ('SPUR LINE', 4039, 1724), ('TREE TAP', 3930, 2095),
]
R, S = 26, 7
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
cols = 6
cw, ch = 2 * R * S, 2 * R * S + 24
sheet = Image.new('RGB', (cols * cw, ((len(items) + cols - 1) // cols) * ch), 'white')
d = ImageDraw.Draw(sheet)
for k, (n, x, y) in enumerate(items):
    c = im.crop((x - R, y - R, x + R, y + R)).resize((2 * R * S, 2 * R * S), Image.NEAREST)
    ox, oy = (k % cols) * cw, (k // cols) * ch
    sheet.paste(c, (ox, oy + 24))
    d.text((ox + 4, oy + 2), n, fill='black', font=font)
    d.rectangle((ox, oy + 24, ox + cw - 1, oy + ch - 1), outline='red')
sheet.save('symsheet.png')
print(sheet.size)
