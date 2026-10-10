"""Route lines.txt's waypoints (route_trace.Router, jackson-hole palette) and draw them on the map with their names."""
import re, sys, json
sys.path.insert(0, 'tools/trailmap')
from route_trace import Router
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]
col = {}
for line in open(f'{S}/jh/read.txt'):
    if '|' in line and not line.startswith('#'):
        p = [x.strip() for x in line.split('|')]
        col[p[0]] = p[1]
R = Router('work/jackson-hole/map.png', 'jackson-hole')
im = Image.open('work/jackson-hole/map.png').convert('RGB')
fade = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.45)
d = ImageDraw.Draw(fade)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
out = {}
for line in open(f'{S}/jh/lines.txt'):
    if '|' not in line or line.startswith('#'):
        continue
    name, pts = [x.strip() for x in line.split('|')[:2]]
    wp = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', pts)]
    cls = col.get(name, 'black')
    cls = {'park pill': 'blue', 'icon': 'blue'}.get(cls, cls)
    path = R.route(cls, wp)
    out[name] = path
    c = {'blue': (0, 60, 255), 'black': (220, 0, 0), 'green': (0, 160, 0)}[cls]
    d.line([tuple(p) for p in path], fill=(255, 0, 255), width=4)
    d.line([tuple(p) for p in path], fill=c, width=2)
    for q in wp:
        d.ellipse((q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3), outline=(255, 120, 0), width=2)
    m = path[len(path) // 2]
    d.text((m[0] + 4, m[1]), name, fill=(120, 0, 120), font=f, stroke_width=2, stroke_fill='white')
json.dump(out, open(f'{S}/jh/routes.json', 'w'))
x0, y0, x1, y1 = map(int, sys.argv[2].split(','))
fade.crop((x0, y0, x1, y1)).save(sys.argv[3])
