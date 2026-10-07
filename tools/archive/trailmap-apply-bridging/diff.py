"""diff.py: per changed resort, the trails whose paths differ between the old bridge rule and the new one, and the
end points the old rule added (the bridged-to point and the end it extended), in map px."""
import json, os, sys
from PIL import Image
S = os.path.dirname(os.path.abspath(__file__))
R = '/home/user/myskiruns'
Image.MAX_IMAGE_PIXELS = None
out = []
for f in sorted(os.listdir(f'{S}/old')):
    n = f[:-5]
    old = json.load(open(f'{S}/old/{f}'))['trails']; new = json.load(open(f'{S}/new/{f}'))['trails']
    img = f'{R}/public/maps/{n}.jpg'
    W, H = Image.open(img).size
    px = lambda q: (round(q[0] * W / 100), round(q[1] * H / 100))
    for t in sorted(set(old) | set(new)):
        a, b = old.get(t, {}).get('segments', []), new.get(t, {}).get('segments', [])
        if a == b:
            continue
        A = {tuple(map(tuple, s)) for s in a}; B = {tuple(map(tuple, s)) for s in b}
        gone = [s for s in A if s not in B]; came = [s for s in B if s not in A]
        for s in gone:
            # the new segment that is this one minus an end point
            for c in came:
                if s[1:] == c or s[:-1] == c:
                    end = s[0] if s[1:] == c else s[-1]
                    nxt = s[1] if s[1:] == c else s[-2]
                    out.append((n, t, px(end), px(nxt)))
                    break
            else:
                out.append((n, t, 'other change', len(s), [len(c) for c in came]))
for o in out:
    print(*o)
json.dump(out, open(f'{S}/diff.json', 'w'))
