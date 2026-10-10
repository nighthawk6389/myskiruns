"""Snowbird: the reading notes (labels.txt: each name, its colour and label points, its symbol in the note; lines.txt:
its line's waypoints, '=' first for a line taken as read) as names.py's READING entries, printed:
gen_names.py <folder with both>. A label's rating is its colour, and 'expert' where the note says a double diamond is
printed by it; a name's rating is its first label's."""
import re
import sys

S = sys.argv[1]
SPELL = {'Fields Cut-Off': 'Fields Cutoff'}  # (the report's spelling)
PRINTED = {'Fields Cutoff': 'FIELDS CUT-OFF', 'Niagra': 'NIAGARA', 'Condo Bypass': 'CONDO BYPASS RD.',
           'Upper White Diamonds': 'WHITE DIAMONDS (black)', 'Lower White Diamonds': 'WHITE DIAMONDS (blue)'}
labels, order = {}, []
for f in ('labels.txt',):
    for line in open(f'{S}/{f}'):
        if '|' not in line or line.startswith('#'):
            continue
        p = [x.strip() for x in line.split('|')]
        n = SPELL.get(p[0], p[0])
        pts = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', p[2])]
        note = p[3] if len(p) > 3 else ''
        rating = 'expert' if p[1] == 'black' and 'double diamond' in note else p[1]
        if n not in labels:
            order.append(n)
        labels.setdefault(n, []).append((rating, pts))
lines = {}
for line in open(f'{S}/lines.txt'):
    if '|' not in line or line.startswith('#'):
        continue
    n, pts = [x.strip() for x in line.split('|')[:2]]
    asread = n.startswith('=')
    n = SPELL.get(n.lstrip('='), n.lstrip('='))
    ln = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', pts)]
    lines.setdefault(n, []).append((['as read'] if asread else []) + ln)
for n in order:
    rating = labels[n][0][0]
    labs = [pts for _, pts in labels[n]]
    cm = f'  # printed {PRINTED[n]}' if n in PRINTED else ''
    print(f'    ({n!r}, {rating!r}, {labs!r},{cm}')
    print(f'     {lines.get(n, [])!r}),')
print('# MISSING LABELS', [n for n in lines if n not in labels], file=sys.stderr)
