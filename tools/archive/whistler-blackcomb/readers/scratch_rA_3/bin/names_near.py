# list printed names (from all region txt files) whose centre/first/last lies within R of a point or box
import re, sys, glob, math
D = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/rA'
seen = {}
for f in glob.glob(D + '/*.txt'):
    for line in open(f):
        m = re.match(r'\s+(.+?) \| (.+?) \| centre \((\d+),(\d+)\) \| first \((\d+),(\d+)\) last \((\d+),(\d+)\)', line)
        if m:
            k = (m.group(1), m.group(3), m.group(4))
            seen[k] = (m.group(1), m.group(2), *map(int, m.groups()[2:]))
x0, y0, x1, y1 = map(int, sys.argv[1].split(','))
for v in sorted(seen.values(), key=lambda v: (v[3], v[2])):
    name, sym, cx, cy, fx, fy, lx, ly = v
    if any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in ((cx, cy), (fx, fy), (lx, ly))):
        print(f'{name} | {sym} | centre ({cx},{cy}) first ({fx},{fy}) last ({lx},{ly})')
