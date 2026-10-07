"""pair.py PANEL x0,y0,x1,y1 zoom out.png [--names]: plain crop | crop with pieces (id:name) side by side."""
import subprocess, sys, tempfile, os
from PIL import Image
panel, box, z, out = sys.argv[1:5]
W = f'/home/user/myskiruns/work/whistler-blackcomb/{panel}'
T = tempfile.mkdtemp()
G = '/home/user/myskiruns/tools/trailmap/grid_crop.py'
subprocess.run(['python3', G, '--image', f'{W}/map.png', '--box', box, '--zoom', z, '--out', f'{T}/a.png', '--grid', '50'], check=True, capture_output=True)
subprocess.run(['python3', G, '--image', f'{W}/map.png', '--box', box, '--zoom', z, '--out', f'{T}/b.png', '--grid', '50',
                '--pieces', f'{W}/pieces_cut.json', '--names', f'{W}/names.json'], check=True, capture_output=True)
a, b = Image.open(f'{T}/a.png'), Image.open(f'{T}/b.png')
im = Image.new('RGB', (a.width + b.width + 10, a.height), 'white'); im.paste(a, (0, 0)); im.paste(b, (a.width + 10, 0)); im.save(out)
print(out, im.size)
