# usage: c2.py name x0,y0,x1,y1 [zoom] [ids...]   -> SCRATCH/name.png: plain on top, pieces below (only ids if given)
import json, subprocess, sys, os
from PIL import Image
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rA_0'
M = '/home/user/myskiruns/work/whistler-blackcomb/main'
name, box = sys.argv[1], sys.argv[2]
zoom = sys.argv[3] if len(sys.argv) > 3 else '3'
ids = [int(a) for a in sys.argv[4:]]
pieces = M + '/pieces_cut.json'
if ids:
    d = json.load(open(pieces))
    d['polylines'] = [p for p in d['polylines'] if p['id'] in ids]
    pieces = S + '/_flt.json'
    json.dump(d, open(pieces, 'w'))
G = ['python3', '/home/user/myskiruns/tools/trailmap/grid_crop.py', '--image', M + '/map.png', '--box', box, '--zoom', zoom, '--grid', '50']
subprocess.run(G + ['--out', S + '/_a.png'], check=True, capture_output=True)
subprocess.run(G + ['--out', S + '/_b.png', '--pieces', pieces, '--names', M + '/names.json'], check=True, capture_output=True)
a, b = Image.open(S + '/_a.png'), Image.open(S + '/_b.png')
if a.width >= a.height * 1.3:
    out = Image.new('RGB', (a.width, a.height * 2 + 6), 'black'); out.paste(a, (0, 0)); out.paste(b, (0, a.height + 6))
else:
    out = Image.new('RGB', (a.width * 2 + 6, a.height), 'black'); out.paste(a, (0, 0)); out.paste(b, (a.width + 6, 0))
out.save(S + '/' + name + '.png'); print(S + '/' + name + '.png', out.size)
