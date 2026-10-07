"""regions.py PANEL OUTDIR STEPX STEPY OFFX OFFY ZOOM: reader packages: per region a pair image (plain | pieces with
id:name) of the core box plus a margin, and a text file listing the pieces it owns (midpoint inside the core) and
the names printed in it."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
from PIL import Image, ImageDraw
import pdf_resort as pr
panel, out = sys.argv[1], sys.argv[2]
sx, sy, ox, oy = map(int, sys.argv[3:7]); z = sys.argv[7]
W = f'/home/user/myskiruns/work/whistler-blackcomb/{panel}'
os.makedirs(out, exist_ok=True)
WW, HH = Image.open(f'{W}/map.png').size
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']
N = json.load(open(f'{W}/names.json'))
A = json.load(open(f'{W}/assign.json'))
r = pr.Resort(f'whistler-blackcomb/{panel}')
names = r.names(); r.symbols(names)
mid = {p['id']: pr.midpoint([(x * WW / 100, y * HH / 100) for x, y in p['points']]) for p in P}
M = 70
G = '/home/user/myskiruns/tools/trailmap/grid_crop.py'
regions = []
for y0 in range(-oy, HH, sy):
    for x0 in range(-ox, WW, sx):
        core = (max(0, x0), max(0, y0), min(WW, x0 + sx), min(HH, y0 + sy))
        own = [p for p in P if core[0] <= mid[p['id']][0] < core[2] and core[1] <= mid[p['id']][1] < core[3]]
        if not own: continue
        box = (max(0, core[0] - M), max(0, core[1] - M), min(WW, core[2] + M), min(HH, core[3] + M))
        tag = f'{panel}_{core[0]}_{core[1]}'
        T = tempfile.mkdtemp()
        b = ','.join(map(str, box))
        subprocess.run(['python3', G, '--image', f'{W}/map.png', '--box', b, '--zoom', z, '--out', f'{T}/a.png', '--grid', '100'], check=True, capture_output=True)
        subprocess.run(['python3', G, '--image', f'{W}/map.png', '--box', b, '--zoom', z, '--out', f'{T}/b.png', '--grid', '100', '--pieces', f'{W}/pieces_cut.json', '--names', f'{W}/names.json'], check=True, capture_output=True)
        a, bb = Image.open(f'{T}/a.png'), Image.open(f'{T}/b.png')
        zz = float(z)
        for im in (a, bb):  # the core box, dashed grey
            d = ImageDraw.Draw(im)
            d.rectangle([(core[0] - box[0]) * zz, (core[1] - box[1]) * zz, (core[2] - box[0]) * zz, (core[3] - box[1]) * zz], outline=(90, 90, 90), width=2)
        a.save(f'{out}/{tag}_plain.png'); bb.save(f'{out}/{tag}_pieces.png')
        lines = [f'Region {tag}: core box x {core[0]}-{core[2]}, y {core[1]}-{core[3]} (map px; grey rectangle on the images); images show x {box[0]}-{box[2]}, y {box[1]}-{box[3]} at zoom {z}.',
                 '', 'PIECES TO DECIDE (midpoint inside the core): id, colour class, current tag (? = undecided, NAME~ = stretch along a printed name), why the tool chose it, length px, end points (map px):']
        for p in own:
            pts = [(x * WW / 100, y * HH / 100) for x, y in p['points']]
            lines.append(f"  {p['id']} {p['cls']} tag={N.get(str(p['id']), '?')} why={A['why'].get(str(p['id']), '-')} len={p['lengthPx']} from ({pts[0][0]:.0f},{pts[0][1]:.0f}) to ({pts[-1][0]:.0f},{pts[-1][1]:.0f})")
        lines += ['', 'NAMES PRINTED IN THE IMAGE AREA (name, symbol, centre, first and last character, map px):']
        for n in names:
            if box[0] <= n['c'][0] <= box[2] and box[1] <= n['c'][1] <= box[3]:
                lines.append(f"  {n['name']} | {n.get('symbol') or 'no symbol found'} | centre ({n['c'][0]:.0f},{n['c'][1]:.0f}) | first ({n['pts'][0][0]:.0f},{n['pts'][0][1]:.0f}) last ({n['pts'][-1][0]:.0f},{n['pts'][-1][1]:.0f})")
        open(f'{out}/{tag}.txt', 'w').write('\n'.join(lines) + '\n')
        regions.append({'tag': tag, 'core': core, 'pieces': [p['id'] for p in own]})
json.dump(regions, open(f'{out}/regions.json', 'w'), indent=0)
print(len(regions), 'regions,', sum(len(x['pieces']) for x in regions), 'pieces')
