"""Vail: the checked decisions -> per-panel inputs for the trail pipeline.

For each panel (front-side, back-bowls, blue-sky) writes:
  tiles/result_<panel>.json   one reading: every printed name (symbol + position) and every named piece
  tiles_<panel>/index.json    stub tile index (aggregate_readings wants the image size)
  linePolylines_<panel>.json  detected pieces (after CUTS) + the stretches traced along the painted line where
                              detection broke (TRACED), with the unnamed pieces' notes (_unnamed)
  labels_<panel>.json         seed_roster-style labels, this panel's positions only (markers go on their own panel)
  trace_<panel>.json          markers for names with no drawn line anywhere, on the panel where they are printed
"""
import collections, importlib.util, json, math, os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())   # NAMES, EXTRA
exec(open('vl_checked.py').read())    # CHECKED, UNNAMED, CUTS, TRACED
exec(open('vl_pt.py').read())         # SIZE, pts_of
exec(open('vl_lines.py').read().split('\ndef pca_dir')[0])  # masks()
REPO = '/home/user/myskiruns'
spec = importlib.util.spec_from_file_location('seed_roster', f'{REPO}/tools/trailmap/seed_roster.py')
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
PANELS = ('front-side', 'back-bowls', 'blue-sky')
SYM = {'circle': 'circle', 'square': 'square', 'diamond': 'diamond', 'double-diamond': 'double-diamond'}
# names the map prints in a case title() would get wrong
DISPLAY = {"CJ'S GLADE": "CJ's Glade", 'WFO': 'WFO', 'GS ALLEY': 'GS Alley'}
PARKS = {'GOLDEN PEAK TERRAIN PARK', "JAKE'S RIDE"}
# runs of the Back Bowls that the Blue Sky panel also shows at its edge: listed under Back Bowls
SHARED = {'SILK ROAD', 'POPPYFIELDS', 'SLEEPYTIME ROAD', 'MARMOT VALLEY'}
# not symbols (d_sheet.png): a lift line, a line end, a sign, the village's round bus/parking icons, the Blue Sky
# callout box, text
FALSE = {('front-side', 31), ('back-bowls', 15), ('front-side', 116), ('front-side', 162), ('front-side', 164),
         ('front-side', 165), ('front-side', 166), ('front-side', 167), ('back-bowls', 0), ('blue-sky', 15),
         ('front-side', 12)}


def tid(name):
    return sr.slug(sr.norm(name))


def label(panel, name, xy, symbol, kind=None):
    return {'mapName': name, 'printed': DISPLAY.get(name), 'symbol': symbol, 'glade': 'GLADE' in name,
            'park': name in PARKS, 'area': 'back-bowls' if name in SHARED else panel,
            'labelSrc': [round(xy[0]), round(xy[1])], 'confidence': 'certain', 'kind': kind}


labels, pieces, assign, unnamed = {}, {}, {}, {}
for panel in PANELS:
    W, H = SIZE[panel]
    out = []
    for s in json.load(open(f'syms_{panel}.json')):
        n = NAMES[panel].get(s['i'])
        if (panel, s['i']) in FALSE or not n or n == '?':
            continue
        out.append(label(panel, n, s['c'], SYM[s['t']]))
    # a symbol printed with no name on a named trail's line (where a run's rating changes, Vail prints the new
    # rating on the line): it counts toward that trail's difficulty too
    P0 = json.load(open(f'pieces_{panel}.json'))['polylines']
    A0 = json.load(open(f'assign_{panel}.json'))['assign']
    for s in json.load(open(f'syms_{panel}.json')):
        n = NAMES[panel].get(s['i'])
        if (panel, s['i']) in FALSE or (n and n != '?'):
            continue
        d, pid = min((min(seg_dist(s['c'], q[i], q[i + 1]) for i in range(len(q) - 1)), p['id'])
                     for p in P0 for q in [pts_of(panel, p)])
        if str(pid) in A0 and d <= max(1.6 * s['r'], 14):
            out.append(label(panel, A0[str(pid)][0], s['c'], SYM[s['t']], 'online'))
            print(f'  {panel} #{s["i"]} {s["t"]} (no name printed) on {A0[str(pid)][0]}')
    for e in EXTRA.get(panel, []):
        n, x, y, kind = (*e, None)[:4]
        # no symbol printed: a bowl is rated black (all of Vail's bowls are expert terrain); a family learning
        # area green; a park gets seed_roster's default (blue)
        sym = {'square': 'square', 'bowl': 'diamond', 'family': 'circle'}.get(kind)
        out.append(label(panel, n, (x, y), sym, kind))
    labels[panel] = out

    P = json.load(open(f'pieces_{panel}.json'))['polylines']
    A = json.load(open(f'assign_{panel}.json'))
    assign[panel] = {int(k): v[0] for k, v in A['assign'].items() if len(v) == 1}
    assert all(len(v) == 1 for v in A['assign'].values()), panel
    unnamed[panel] = {int(k): v for k, v in A['unnamed'].items()}
    assert not set(assign[panel]) & set(unnamed[panel])
    missing = [p['id'] for p in P if p['id'] not in assign[panel] and p['id'] not in unnamed[panel]]
    assert not missing, (panel, missing)
    # traced stretches: new pieces, coloured by the painted line under them
    M = masks(np.asarray(Image.open(f'{panel}.png').convert('RGB')))
    traced = []
    for n, pts in TRACED.get(panel, []):
        votes = collections.Counter()
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            for t in np.linspace(0, 1, 6):
                x, y = int(round(ax + t * (bx - ax))), int(round(ay + t * (by - ay)))
                for c, m in M.items():
                    votes[c] += int(m[max(0, y - 3):y + 4, max(0, x - 3):x + 4].any())
        cls = votes.most_common(1)[0][0]
        pid = len(P)
        L = round(sum(math.dist(a, b) for a, b in zip(pts, pts[1:])))
        P.append({'id': pid, 'cls': cls, 'lengthPx': L,
                  'points': [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in pts]})
        assign[panel][pid] = n
        traced.append(pid)
        print(f'  {panel} traced piece {pid}: {n} ({cls}, {L} px; votes {dict(votes)})')
    pieces[panel] = (P, traced)

# a name drawn nowhere gets a marker at its first label, on that label's panel
drawn = {n for panel in PANELS for n in assign[panel].values()}
os.makedirs('tiles', exist_ok=True)
for panel in PANELS:
    W, H = SIZE[panel]
    P, traced = pieces[panel]
    lines = [{'id': pid, 'mapName': n, 'color': P[pid]['cls'], 'confidence': 'certain',
              'note': 'traced along the painted line' if pid in traced else 'checked on a crop'}
             for pid, n in sorted(assign[panel].items())]
    json.dump({'labels': [{k: v for k, v in L.items() if k != 'kind' and v is not None} for L in labels[panel]],
               'lines': lines}, open(f'tiles/result_{panel}.json', 'w'), indent=1)
    os.makedirs(f'tiles_{panel}', exist_ok=True)
    json.dump({'zoom': 1, 'imageSize': [W, H], 'tiles': []}, open(f'tiles_{panel}/index.json', 'w'))
    src = {'front-side': 'front-side', 'back-bowls': 'back-bowls', 'blue-sky': 'blue-sky'}[panel]
    args = {'front-side': '--k 1 --text-max 36', 'back-bowls': '--k 1.75 --text-max 75', 'blue-sky': '--k 2.7 --text-max 80'}[panel]
    ncut = len(CUTS.get(panel, []))
    doc = {'_source': (f'Vail 2025-26 trail map, {panel} panel (scene7 image 20251001_VL_winter-{src}-trail_map_001, '
                       f'{W}x{H}): tools/trailmap/raster_lines.py {args} with the legend, inset frames and logos '
                       f'excluded; {ncut} piece(s) cut where one drawn line carries two trails (the second part '
                       f'appended); pieces {traced[0] if traced else "-"}+ (_traced) are stretches traced along the '
                       f'painted line where detection broke (label gaps, dashes far apart, slow-zone hatching); '
                       f'percent of the map image'),
           '_unnamed': {str(k): v for k, v in sorted(unnamed[panel].items())},
           '_traced': [str(k) for k in traced],
           'polylines': [{k: p[k] for k in ('id', 'cls', 'lengthPx', 'points')} for p in P]}
    json.dump(doc, open(f'linePolylines_{panel}.json', 'w'))
    by = collections.defaultdict(lambda: {'positions': [], 'symbols': collections.Counter()})
    for L in labels[panel]:
        e = by[tid(L['mapName'])]
        e['mapName'] = sr.norm(L['mapName'])
        e['positions'].append(L['labelSrc'])
        e['symbols'][L['symbol'] or 'none-visible'] += 1
    json.dump({k: {'mapName': v['mapName'], 'positions': v['positions'], 'symbols': dict(v['symbols']), 'labelled': True}
               for k, v in by.items()}, open(f'labels_{panel}.json', 'w'), indent=1)
    markers = []
    for L in labels[panel]:
        n = L['mapName']
        if n in drawn or any(tid(n) == m['id'] for m in markers):
            continue
        if any(n in {x['mapName'] for x in labels[q]} for q in PANELS[:PANELS.index(panel)]):
            continue  # already marked on an earlier panel
        if L['glade']:
            continue  # aggregate_readings marks a glade printed with no line itself
        markers.append({'id': tid(n), 'pieces': [], 'traced': [], 'confidence': 'high',
                        'note': {'bowl': 'A bowl named on the map with no line drawn: marker at its name',
                                 'park': 'A terrain park drawn as an area: marker at its name'}.get(
                            L['kind'], 'Named on the map with no line drawn (open slope or glade): marker at its symbol')})
    json.dump({'trails': markers}, open(f'trace_{panel}.json', 'w'), indent=1)
    print(panel, len(labels[panel]), 'labels,', len(lines), 'named pieces,', len(unnamed[panel]), 'unnamed,',
          len(traced), 'traced,', len(markers), 'markers:', ', '.join(m['id'] for m in markers))
