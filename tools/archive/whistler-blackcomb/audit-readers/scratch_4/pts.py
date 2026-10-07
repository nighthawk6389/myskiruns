import json, sys
panel = sys.argv[1]
d = json.load(open('/home/user/myskiruns/src/data/resorts/whistler-blackcomb/panels/%s/trailPaths.json' % panel))['trails']
from PIL import Image
W, H = Image.open('/home/user/myskiruns/work/whistler-blackcomb/%s/map.png' % panel).size
for tid in sys.argv[2:]:
    t = d.get(tid)
    if t is None:
        print(tid, 'NONE'); continue
    print(tid, {k: v for k, v in t.items() if k != 'segments'})
    for s in t.get('segments', []):
        print('  seg:', ' '.join('(%d,%d)' % (p[0] * W / 100, p[1] * H / 100) for p in s))
