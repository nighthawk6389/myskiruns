"""Names of a panel with no line of their own: name, symbol, label start/end (first and last glyph, map px)."""
import sys, io, contextlib, json
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
drawn = {n for v in r.assign.values() for n in v}
rows = []
for n in r.names_:
    if n['name'] in drawn:
        continue
    a, b = n['pts'][0], n['pts'][-1]
    rows.append({'name': n['name'], 'sym': n.get('symbol'), 'a': [round(a[0]), round(a[1])], 'b': [round(b[0]), round(b[1])],
                 'c': [round(n['c'][0]), round(n['c'][1])], 's': [round(v) for v in n['sym']['c']] if n.get('sym') else None})
rows.sort(key=lambda x: (x['c'][0] // 600, x['c'][1]))
json.dump(rows, open(sys.argv[2], 'w'), indent=0)
for x in rows:
    print(f"{x['name']:24s} {str(x['sym']):15s} label {x['a']}->{x['b']} sym {x['s']}")
print(len(rows))
