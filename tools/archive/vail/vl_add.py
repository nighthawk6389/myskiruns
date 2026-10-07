"""vl_add.py panel "comment" id=NAME ... id=-:note ... | x,y=NAME : record decisions (by the current piece ids, or
a point) as points on the pieces in vl_checked.py, under the panel, with a comment line."""
import json, sys
exec(open('vl_pt.py').read())
panel, comment = sys.argv[1], sys.argv[2]
lines = f'pieces_{panel}.json'
named, unnamed = [], []
for a in sys.argv[3:]:
    k, v = a.split('=', 1)
    q = tuple(int(float(t)) for t in k.split(',')) if ',' in k else pt(panel, int(k), lines)
    if v.startswith('-'):
        unnamed.append((q, v[2:] if v.startswith('-:') else 'unnamed connector'))
    else:
        named.append((q, v))
s = open('vl_checked.py').read()


def insert(s, block, entries):
    if not entries:
        return s
    head = f"{block} = {{" if False else None
    i = s.index(f"{block} = {{")
    j = s.index(f"'{panel}': [", i) + len(f"'{panel}': [") + 1
    text = ''.join(f"    # {comment}\n" if n == 0 and comment else '' for n in range(1)) if block == 'CHECKED' else ''
    text += ''.join(f"    (({x}, {y}), {nm!r}),\n" for (x, y), nm in entries)
    return s[:j] + text + s[j:]


s = insert(s, 'CHECKED', named)
s = insert(s, 'UNNAMED', unnamed)
open('vl_checked.py', 'w').write(s)
exec(s)
print('recorded', len(named), 'named,', len(unnamed), 'unnamed;', {p: len(v) for p, v in CHECKED.items()})
