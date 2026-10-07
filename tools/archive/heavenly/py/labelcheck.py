"""For each 2022 label (and symbol) of a panel: does the 2024 image still print it there? Draw the label's glyph
outlines (glyphs.json, PDF pt) at the image's scale and count how much of them is dark ink in the 2024 image."""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
panel = sys.argv[1]
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap/resorts/heavenly')
import importlib.util
spec = importlib.util.spec_from_file_location('t', '/home/user/myskiruns/tools/trailmap/resorts/heavenly/resort.py')
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
A, box = T.AFFINE[panel], T.BOX[panel]
def px(p):
    return (A[0] * p[0] + A[1] * p[1] + A[2] - box[0], A[3] * p[0] + A[4] * p[1] + A[5] - box[1])
W = '/home/user/myskiruns/work/heavenly'
G = json.load(open(f'{W}/glyphs.json'))['glyphs']
P = json.load(open(f'{W}/{panel}/printed.json'))
im = np.asarray(Image.open(f'{W}/{panel}/map.png').convert('RGB')).astype(int)
dark = (im.max(axis=2) < 110)
INK = {'black': dark, 'blue': (im[..., 2] > 120) & (im[..., 0] < 90), 'green': (im[..., 1] > 110) & (im[..., 0] < 90) & (im[..., 2] < 150)}
def score(glyphs, ink=None):
    mask = Image.new('1', (im.shape[1], im.shape[0]), 0)
    d = ImageDraw.Draw(mask)
    for g in glyphs:
        pts = [px(q) for q in g['pts']]
        if len(pts) > 2:
            d.polygon(pts, fill=1)
    m = np.asarray(mask)
    n = m.sum()
    return ((dark if ink is None else ink) & m).sum() / n if n else None
bycentre = {}
for g in G:
    bycentre.setdefault((round(g['c'][0], 1), round(g['c'][1], 1)), []).append(g)
rows = []
for lab in P['labels']:
    gl = [g for q in lab['pts'] for g in bycentre.get((round(q[0], 1), round(q[1], 1)), [])]
    s = score(gl)
    c = px(lab['c'])
    rows.append((s if s is not None else -1, lab['text'], round(c[0]), round(c[1]), lab['seq']))
for s in P['symbols']:
    g = [g for g in G if g['seq'] == s['seq']]
    sc = score(g, INK.get(s.get('color')))
    c = px(s['c'])
    rows.append((sc if sc is not None else -1, 'SYMBOL ' + s['t'] + ' ' + s.get('color', ''), round(c[0]), round(c[1]), s['seq']))
for r in sorted(rows):
    print(f'{r[0]:.2f}  {r[1]:32s} ({r[2]},{r[3]}) seq {r[4]}')
