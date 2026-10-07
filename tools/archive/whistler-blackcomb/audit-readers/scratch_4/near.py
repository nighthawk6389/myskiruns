import json, sys
# usage: near.py PANEL x0 y0 x1 y1  (map px)
panel = sys.argv[1]
x0, y0, x1, y1 = map(float, sys.argv[2:6])
p = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/%s/printed.json' % panel))
# find scale: compare with trails_info
info = json.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/sheets/trails_info.json'))[panel]
import re
sc = None
for tid, t in info.items():
    for lab in t.get('labels_printed_here', []):
        for L in p['labels']:
            if L['text'] == lab['printed']:
                s = lab['at'][0] / L['c'][0] if L['c'][0] else None
                if s and abs(lab['at'][1] - L['c'][1] * s) < 30:
                    sc = s; break
        if sc: break
    if sc: break
print('scale', sc)
for L in p['labels']:
    x, y = L['c'][0] * sc, L['c'][1] * sc
    if x0 <= x <= x1 and y0 <= y <= y1:
        print('%-30s %-6s (%d,%d)' % (L['text'], L['color'], x, y))
