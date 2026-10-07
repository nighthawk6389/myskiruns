#!/bin/bash
# reg.sh PANEL x0,y0,x1,y1 ZOOM OUT: current pieces image of a box + the info list (pieces whose midpoint is inside)
set -e
cd /home/user/myskiruns
P=$1; B=$2; Z=$3; O=$4
W=work/whistler-blackcomb/$P
python3 tools/trailmap/grid_crop.py --image $W/map.png --box $B --zoom $Z --out $O --grid 100 --pieces $W/pieces_cut.json --names $W/names.json > /dev/null
python3 - "$P" "$B" <<'PY'
import json, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
from PIL import Image
panel, b = sys.argv[1], tuple(map(float, sys.argv[2].split(',')))
W = f'/home/user/myskiruns/work/whistler-blackcomb/{panel}'
WW, HH = Image.open(f'{W}/map.png').size
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']
N = json.load(open(f'{W}/names.json')); A = json.load(open(f'{W}/assign.json'))
for p in P:
    pts = [(x * WW / 100, y * HH / 100) for x, y in p['points']]
    m = pr.midpoint(pts)
    if b[0] <= m[0] <= b[2] and b[1] <= m[1] <= b[3]:
        print(f"{p['id']:4d} {p['cls']:6s} {N.get(str(p['id']), '?'):26.26s} {A['why'].get(str(p['id']), ''):32.32s} L{p['lengthPx']:5d} ({pts[0][0]:.0f},{pts[0][1]:.0f})-({pts[-1][0]:.0f},{pts[-1][1]:.0f})")
r = pr.Resort(f'whistler-blackcomb/{panel}')
names = r.names(); r.symbols(names)
for n in names:
    if b[0] <= n['c'][0] <= b[2] and b[1] <= n['c'][1] <= b[3]:
        print('   NAME', n['name'], '|', n.get('symbol'), '|', [round(v) for v in n['c']], 'first', [round(v) for v in n['pts'][0]], 'last', [round(v) for v in n['pts'][-1]])
PY
