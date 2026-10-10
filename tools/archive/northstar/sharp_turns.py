"""Where Northstar's pieces turn sharply (a centre line traced from one trail's line into another's at a junction
of the artwork's united outline: a V at the summit or at a meeting of two lines): candidate CUTS to check on crops.

    python3 tools/archive/northstar/sharp_turns.py [work/northstar] [max angle, degrees: 70]   (after a build)

Prints, per piece, each point where the directions 20 px before and after it meet at an angle under the limit.
"""
import json
import math
import sys

from PIL import Image

W_DIR = sys.argv[1] if len(sys.argv) > 1 else 'work/northstar'
LIM = float(sys.argv[2]) if len(sys.argv) > 2 else 70
W, H = Image.open(f'{W_DIR}/map.png').size
N = json.load(open(f'{W_DIR}/names.json'))


def resample(pts, step=2.0):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        n = max(1, int(L / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out


for p in json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']:
    pts = resample([(x * W / 100, y * H / 100) for x, y in p['points']])
    k = 10  # 20 px
    found = []
    for i in range(k, len(pts) - k):
        a, c, b = pts[i - k], pts[i], pts[i + k]
        v1, v2 = (a[0] - c[0], a[1] - c[1]), (b[0] - c[0], b[1] - c[1])
        n = math.hypot(*v1) * math.hypot(*v2)
        if not n:
            continue
        ang = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / n))))
        if ang < LIM:
            if found and i - found[-1][0] < 2 * k:
                if ang < found[-1][2]:
                    found[-1] = (i, c, ang)
            else:
                found.append((i, c, ang))
    if found:
        print(p['id'], N.get(str(p['id']), ''), [((round(c[0]), round(c[1])), round(ang)) for _i, c, ang in found])
