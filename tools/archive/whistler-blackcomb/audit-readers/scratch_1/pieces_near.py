import json, sys
panel = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2].split(','))
fn = sys.argv[3] if len(sys.argv) > 3 else 'pieces_cut.json'
sizes = {'main': (4320, 2103), 'symphony': (1704, 1022), 'glacier': (1114, 1008)}
W, H = sizes[panel]
d = json.load(open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/{fn}'))
P = d['polylines'] if isinstance(d, dict) else d
assign = {}
try:
    assign = json.load(open(f'/home/user/myskiruns/work/whistler-blackcomb/{panel}/assign.json'))
except Exception:
    pass
for p in P:
    pts = [(round(x * W / 100), round(y * H / 100)) for x, y in p['points']]
    if any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in pts):
        a = assign.get(str(p['id'])) if isinstance(assign, dict) else None
        print(p['id'], p.get('cls'), p.get('lengthPx'), 'glade' if p.get('glade') else '', a, pts if len(pts) < 40 else pts[:20] + ['...'] + pts[-5:])
