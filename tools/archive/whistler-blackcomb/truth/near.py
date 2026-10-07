"""Print the nearest GIS runs to the middle of each named GIS run (for judging ambiguous aliases)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb_common as C  # noqa: E402

gis = C.load_gis_runs()


def pts(g):
    c = g['coordinates']
    if g['type'] == 'MultiLineString':
        c = [p for line in c for p in line]
    return c


def dist(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians(50)) * 111320, (a[1] - b[1]) * 111320)


for name in sys.argv[1:]:
    for r in [r for r in gis if r['run_name'] == name]:
        p = pts(r['geometry'])
        m = p[len(p) // 2]
        others = sorted((min(dist(m, q) for q in pts(o['geometry'])), o['run_name']) for o in gis if o is not r)
        print(f"{name} [{r['mountain']}, {r['difficulty']}, trailmap={r['trailmap']}, {r['length_m']} m] near:",
              ', '.join(f'{n} {round(d)}m' for d, n in others[:7]))
