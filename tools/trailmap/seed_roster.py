"""Build a new resort's trail list from what the readers saw printed on the
map (prompts/0-new-map.md), instead of from memory.

    python3 tools/trailmap/seed_roster.py --readings 'work/tiles/result_*.json' \\
        --areas 'mansfield=Mount Mansfield=4395,spruce-peak=Spruce Peak=3390' \\
        --trails src/data/resorts/stowe/trails.ts --labels work/labels.json

Per printed name (normalised): difficulty = majority of the reported symbols
(circle/square/diamond/double-diamond; a tie goes to the harder one), else
the majority colour of the line pieces named after it; glade = majority of
reports; park = any report on a park pill or a freestyle line; area = majority; label
position(s) = reports clustered within 200 source px (a name printed twice
far apart keeps both); display name = the reports' `printed` spelling if
given (a PDF's own text), else title case. Names that only appear on line
pieces are included too. Writes trails.ts (sorted by area, then name) and labels.json
({id: {name, positions, symbols, colors}}) for review hints and glade markers.
Everything here is a proposal: the human review decides.
"""
import argparse
import collections
import glob
import json
import math
import re
import unicodedata

SYMBOL = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'double-black'}
SKIP = ('LIFT', 'NOT_A_TRAIL', 'UNKNOWN', 'SPLIT')


def norm(name: str) -> str:
    n = (name or '').upper().replace('’', "'").replace('`', "'")
    n = re.sub(r'\s+', ' ', n).strip(' .')
    return n


def slug(s: str) -> str:
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))  # ANDRÉ -> andre
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace("'", '')).strip('-')


def title(n: str) -> str:
    words = []
    for w in n.split(' '):
        if re.fullmatch(r'(?:[A-Z]\.)+[A-Z]', w):  # initials (F.I.S.): norm() took the last dot
            words.append(w + '.')
            continue
        # keep S-53, T-LINE style tokens readable; lowercase after apostrophes
        parts = w.split('-')
        words.append('-'.join(p[:1] + p[1:].lower() for p in parts))
    return ' '.join(words)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--readings', required=True)
    ap.add_argument('--areas', required=True, help='id=Name=elevation,...  (first is the default)')
    ap.add_argument('--trails', required=True, help='output trails.ts')
    ap.add_argument('--labels', required=True, help='output labels.json')
    ap.add_argument('--glade-difficulty', default='black',
                    help='for glades printed with no symbol (the review can change it)')
    a = ap.parse_args()

    areas = [dict(zip(('id', 'name', 'elevation'), s.split('='))) for s in a.areas.split(',')]
    area_ids = [x['id'] for x in areas]

    info = collections.defaultdict(lambda: {'symbols': collections.Counter(), 'glade': collections.Counter(),
                                            'area': collections.Counter(), 'colors': collections.Counter(),
                                            'positions': [], 'printed': collections.Counter(),
                                            'park': collections.Counter()})
    for f in sorted(glob.glob(a.readings)):
        r = json.load(open(f))
        for lab in r.get('labels', []):
            n = norm(lab.get('mapName'))
            if not n:
                continue
            e = info[n]
            e['symbols'][lab.get('symbol') or 'none-visible'] += 1
            e['glade'][bool(lab.get('glade'))] += 1
            e['park'][bool(lab.get('park'))] += 1
            if lab.get('printed'):  # the name in the map's own case (a PDF's text), else title()
                e['printed'][lab['printed']] += 1
            if lab.get('area') in area_ids:
                e['area'][lab['area']] += 1
            if lab.get('labelSrc'):
                e['positions'].append(lab['labelSrc'])
        for line in r.get('lines', []):
            n = norm(line.get('mapName'))
            if not n or n.split(':')[0].strip() in SKIP:
                continue
            info[n]['colors'][line.get('color')] += 1

    trails, labels = [], {}
    for n, e in info.items():
        sym = sorted(((s, c) for s, c in e['symbols'].items() if s in SYMBOL),
                     key=lambda sc: (-sc[1], -list(SYMBOL).index(sc[0])))
        colors = [(c, k) for c, k in e['colors'].most_common() if c in ('green', 'blue', 'black')]
        glade = e['glade'][True] > e['glade'][False]
        park = (e['colors'].most_common(1)[0][0] == 'freestyle' if e['colors'] else False) or e['park'][True] > 0
        difficulty = (SYMBOL[sym[0][0]] if sym else colors[0][0] if colors
                      else a.glade_difficulty if glade else 'blue')
        clusters = []
        for p in e['positions']:
            for c in clusters:
                if math.dist(p, c['mean']) < 200:
                    c['pts'].append(p)
                    c['mean'] = [sum(q[i] for q in c['pts']) / len(c['pts']) for i in (0, 1)]
                    break
            else:
                clusters.append({'pts': [p], 'mean': list(p)})
        tid = slug(n)
        trails.append({
            'id': tid, 'name': e['printed'].most_common(1)[0][0] if e['printed'] else title(n), 'difficulty': difficulty,
            'peak': e['area'].most_common(1)[0][0] if e['area'] else area_ids[0],
            'glade': glade, 'park': park,
        })
        labels[tid] = {'mapName': n, 'positions': [[round(v) for v in c['mean']] for c in clusters],
                       'symbols': dict(e['symbols']), 'colors': dict(e['colors']),
                       'labelled': bool(e['positions'])}

    trails.sort(key=lambda t: (area_ids.index(t['peak']), t['name']))
    with open(a.trails, 'w') as f:
        f.write("import type { Trail, PeakData } from '../../../types';\n\n")
        f.write('// Seeded from the printed labels by tools/trailmap/seed_roster.py; names and\n')
        f.write('// difficulties are as printed on the 2025-26 map (symbols), glades from the\n')
        f.write('// glade icon. x/y/baseY/width are unused layout fields.\n')
        f.write('export const peaks: PeakData[] = [\n')
        for x in areas:
            f.write(f"  {{ id: '{x['id']}', name: '{x['name']}', elevation: {int(x['elevation'])}, x: 0, y: 0, baseY: 0, width: 0 }},\n")
        f.write('];\n\nexport const trails: Trail[] = [\n')
        for t in trails:
            name = f'"{t["name"]}"' if "'" in t['name'] else f"'{t['name']}'"
            extra = (', isGlade: true' if t['glade'] else '') + (', isTerrainPark: true' if t['park'] else '')
            f.write(f"  {{ id: '{t['id']}', name: {name}, difficulty: '{t['difficulty']}', peak: '{t['peak']}'{extra} }},\n")
        f.write('];\n')
    json.dump(labels, open(a.labels, 'w'), indent=1)
    by = collections.Counter((t['peak'], t['difficulty']) for t in trails)
    print(f'{len(trails)} trails ({sum(t["glade"] for t in trails)} glades):', dict(by))
    print('no label seen (names only from line pieces):', [t['id'] for t in trails if not labels[t['id']]['labelled']])
    print('no symbol read:', [t['id'] for t in trails if not any(s in SYMBOL for s in labels[t['id']]['symbols'])])


if __name__ == '__main__':
    main()
