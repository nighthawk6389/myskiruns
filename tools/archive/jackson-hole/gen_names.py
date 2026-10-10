"""Jackson Hole: the reading notes (labels.txt: each name, its colour and label points; lines.txt: its line's waypoints,
'=' first for a line taken as read) as names.py's READING entries, printed: gen_names.py <folder with both>."""
import re, sys
S = sys.argv[1]
REN = {'Ashley Ridge (blue)': 'Ashley Ridge (Upper)', 'Ashley Ridge (black)': 'Ashley Ridge (Lower)',
       'Kemmerer': 'Kemmerer (Upper)', 'Kemmerer (blue)': 'Kemmerer (Lower)', 'Hanna?': 'Hanna (Lower)',
       'Upper Hanna': 'Hanna (Upper)', 'Teewino..?': 'Teewinot Gully', 'Werner?': 'Werner (Middle)',
       'Teewinot': 'Teewinot (Upper)', 'Lower Werner': 'Werner (Lower)', 'Upper Werner': 'Werner (Upper)',
       'Lower Teewinot': 'Teewinot (Lower)', 'Lower Sundance': 'Sundance (Lower)', 'Upper Sundance': 'Sundance (Upper)',
       "St. John's (2nd)?": "St. John's"}
PRINTED = {'Ashley Ridge (Upper)': 'ASHLEY RIDGE (blue)', 'Ashley Ridge (Lower)': 'ASHLEY RIDGE (black)',
           'Kemmerer (Upper)': 'KEMMERER (black)', 'Kemmerer (Lower)': 'KEMMERER (blue)', 'Hanna (Lower)': 'HANNA',
           'Hanna (Upper)': 'UPPER HANNA', 'Werner (Middle)': 'WERNER (the upper one)', 'Werner': 'WERNER (the lower one)',
           'Teewinot (Upper)': 'TEEWINOT', 'Werner (Lower)': 'LOWER WERNER', 'Werner (Upper)': 'UPPER WERNER',
           'Teewinot (Lower)': 'LOWER TEEWINOT', 'Sundance (Lower)': 'LOWER SUNDANCE', 'Sundance (Upper)': 'UPPER SUNDANCE',
           "Rawlin's Bowl": 'RAWLINS BOWL', "Eagle's Rest Cutoff": "EAGLE'S REST CUT OFF"}
LREN = {"St. John's (lower)": "St. John's"}
fix = {'Teewinot Gully': [(1970, 1268), (2035, 1197)], 'Werner (Middle)': [(2025, 1043), (2072, 987)]}
labels, order = {}, []
gros = 0
for line in open(f'{S}/labels.txt'):
    if '|' not in line or line.startswith('#'):
        continue
    p = [x.strip() for x in line.split('|')]
    n = REN.get(p[0], p[0])
    if n == 'Gros Ventre':
        n = 'Gros Ventre (Upper)' if gros == 0 else 'Gros Ventre (Lower)'; gros += 1
    pts = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', p[2])]
    pts = fix.get(n, pts)
    col = {'park pill': 'park', 'icon': 'park'}.get(p[1], p[1])
    if n not in labels:
        order.append(n)
    labels.setdefault(n, []).append((col, pts))
lines = {}
for line in open(f'{S}/lines.txt'):
    if '|' not in line or line.startswith('#'):
        continue
    n, pts = [x.strip() for x in line.split('|')[:2]]
    asread = n.startswith('=')
    n = LREN.get(n.lstrip('='), n.lstrip('='))
    ln = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', pts)]
    lines.setdefault(n, []).append((['as read'] if asread else []) + ln)
for n in order:
    col = labels[n][0][0]
    labs = [pts for _, pts in labels[n]]
    ls = lines.get(n, [])
    cm = f'  # printed {PRINTED[n]}' if n in PRINTED else ''
    print(f'    ({n!r}, {col!r}, {labs!r},{cm}')
    print(f'     {ls!r}),')
print('# MISSING LABELS', [n for n in lines if n not in labels], file=sys.stderr)
