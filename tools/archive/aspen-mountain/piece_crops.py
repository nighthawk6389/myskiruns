"""A crop of each given piece alone on the map (grid_crop.py, its box around the piece plus a margin, zoomed to about
900 px), to settle a piece's names and cuts. piece_crops.py <resort>/<panel> <out dir> id [id ...] (repo root)."""
import json
import os
import subprocess
import sys

from PIL import Image

rid, out, ids = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3:]]
W_DIR = f'work/{rid}'
W, H = Image.open(f'{W_DIR}/map.png').size
P = {p['id']: p for p in json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']}
os.makedirs(out, exist_ok=True)
for i in ids:
    pts = [(x * W / 100, y * H / 100) for x, y in P[i]['points']]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    m = 60
    box = (int(min(xs) - m), int(min(ys) - m), int(max(xs) + m), int(max(ys) + m))
    z = min(2.5, 900 / max(box[2] - box[0], box[3] - box[1]))
    one = os.path.join(out, f'p{i}.json')
    json.dump({'polylines': [P[i]]}, open(one, 'w'))
    grid = 50 if z >= 1 else 100
    subprocess.run(['python3', 'tools/trailmap/grid_crop.py', '--image', f'{W_DIR}/map.png', '--box', ','.join(map(str, box)),
                    '--zoom', f'{z:.2f}', '--grid', str(grid), '--fine', '0', '--pieces', one, '--names', f'{W_DIR}/names.json',
                    '--out', os.path.join(out, f'piece_{i}.png')], check=True)
