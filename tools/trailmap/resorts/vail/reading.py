"""Vail: the readings (names.py) and named pieces (build.py) -> per-panel inputs for the trail pipeline
(seed_roster.py, aggregate_readings.py, traces_to_reviews.py; regen.sh runs them).

For each panel writes, in $VAIL_WORK:
  tiles/result_<panel>.json   one reading: every printed name (symbol + position) and every named piece
  tiles_<panel>/index.json    stub tile index (aggregate_readings wants the image size)
  linePolylines_<panel>.json  the pieces (after CUTS) plus the TRACED stretches as new pieces (each coloured by
                              the painted line under it), with the not-a-trail pieces' notes (_unnamed)
  labels_<panel>.json         seed_roster-style labels with this panel's positions only (markers go on their panel)
  trace_<panel>.json          markers for names drawn nowhere, on the panel where they are printed
  named_syms_<panel>.json     every trail symbol with its name ([{name, t, c, r}]: symbol_audit.py --symbols)
"""
import collections
import importlib.util
import json
import math
import os

import numpy as np
from PIL import Image

from common import PANELS, REPO, SIZE, load, pts_of, seg_dist, symbol_names, work
from decisions import CUTS, TRACED
from names import DISPLAY, EXTRA, PARKS, SHARED
from raster_lines import masks

Image.MAX_IMAGE_PIXELS = None
spec = importlib.util.spec_from_file_location('seed_roster', f'{REPO}/tools/trailmap/seed_roster.py')
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
SYM = {'circle': 'circle', 'square': 'square', 'diamond': 'diamond', 'double-diamond': 'double-diamond'}


def tid(name):
    return sr.slug(sr.norm(name))


def label(panel, name, xy, symbol, kind=None):
    return {'mapName': name, 'printed': DISPLAY.get(name), 'symbol': symbol, 'glade': 'GLADE' in name,
            'park': name in PARKS, 'area': 'back-bowls' if name in SHARED else panel,
            'labelSrc': [round(xy[0]), round(xy[1])], 'confidence': 'certain', 'kind': kind}


labels, pieces, assign, unnamed = {}, {}, {}, {}
for panel in PANELS:
    W, H = SIZE[panel]
    syms = load(f'syms_{panel}.json')
    read = symbol_names(panel, syms)
    out, named_syms = [], []
    for s in syms:
        n, kind = read.get(s['i'], (None, None))
        if not n or n == '?':
            continue
        out.append(label(panel, n, s['c'], SYM[kind]))
        named_syms.append({'name': n, 't': kind, 'c': s['c'], 'r': s['r']})
    # a symbol printed with no name on a named trail's line (where a run's rating changes, Vail prints the new
    # rating on the line): it counts toward that trail's difficulty too
    P0 = load(f'pieces_{panel}.json')['polylines']
    A0 = load(f'assign_{panel}.json')['assign']
    for s in syms:
        n, kind = read.get(s['i'], (None, None))
        if n != '?':
            continue
        d, pid = min((min(seg_dist(s['c'], q[i], q[i + 1]) for i in range(len(q) - 1)), p['id'])
                     for p in P0 for q in [pts_of(panel, p)])
        if str(pid) in A0 and d <= max(1.6 * s['r'], 14):
            out.append(label(panel, A0[str(pid)][0], s['c'], SYM[kind], 'online'))
            named_syms.append({'name': A0[str(pid)][0], 't': kind, 'c': s['c'], 'r': s['r'], 'online': True})
            print(f'  {panel} {kind} at {[round(v) for v in s["c"]]} (no name printed) on {A0[str(pid)][0]}')
    for e in EXTRA.get(panel, []):
        n, x, y, kind = (*e, None)[:4]
        # no symbol printed: a bowl is rated black (all of Vail's bowls are expert terrain); a family learning
        # area green; a park gets seed_roster's default (blue)
        sym = {'square': 'square', 'bowl': 'diamond', 'family': 'circle'}.get(kind)
        out.append(label(panel, n, (x, y), sym, kind))
    labels[panel] = out
    json.dump(named_syms, open(work(f'named_syms_{panel}.json'), 'w'), indent=0)

    P = load(f'pieces_{panel}.json')['polylines']
    A = load(f'assign_{panel}.json')
    assign[panel] = {int(k): v[0] for k, v in A['assign'].items() if len(v) == 1}
    assert all(len(v) == 1 for v in A['assign'].values()), panel
    unnamed[panel] = {int(k): v for k, v in A['unnamed'].items()}
    assert not set(assign[panel]) & set(unnamed[panel])
    missing = [p['id'] for p in P if p['id'] not in assign[panel] and p['id'] not in unnamed[panel]]
    assert not missing, (panel, 'pieces with no decision (build.py lists them; add.py records one):', missing)
    # traced stretches: new pieces, coloured by the painted line under them
    M = masks(np.asarray(Image.open(work(f'{panel}.png')).convert('RGB')))
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
    pieces[panel] = (P, traced)

# a name drawn nowhere gets a marker at its first label, on that label's panel
drawn = {n for panel in PANELS for n in assign[panel].values()}
os.makedirs(work('tiles'), exist_ok=True)
for panel in PANELS:
    W, H = SIZE[panel]
    P, traced = pieces[panel]
    lines = [{'id': pid, 'mapName': n, 'color': P[pid]['cls'], 'confidence': 'certain',
              'note': 'traced along the painted line' if pid in traced else 'checked on a crop'}
             for pid, n in sorted(assign[panel].items())]
    json.dump({'labels': [{k: v for k, v in L.items() if k != 'kind' and v is not None} for L in labels[panel]],
               'lines': lines}, open(work(f'tiles/result_{panel}.json'), 'w'), indent=1)
    os.makedirs(work(f'tiles_{panel}'), exist_ok=True)
    json.dump({'zoom': 1, 'imageSize': [W, H], 'tiles': []}, open(work(f'tiles_{panel}/index.json'), 'w'))
    args = {'front-side': '--k 1 --text-max 36', 'back-bowls': '--k 1.75 --text-max 75', 'blue-sky': '--k 2.7 --text-max 80'}[panel]
    ncut = len(CUTS.get(panel, []))
    doc = {'_source': (f'Vail 2025-26 trail map, {panel} panel (scene7 image 20251001_VL_winter-{panel}-trail_map_001, '
                       f'{W}x{H}): tools/trailmap/raster_lines.py {args} with the legend, inset frames and logos '
                       f'excluded; {ncut} piece(s) cut where one drawn line carries two trails (the second part '
                       f'appended); pieces {traced[0] if traced else "-"}+ (_traced) are stretches traced along the '
                       f'painted line where detection broke (label gaps, dashes far apart, slow-zone hatching); '
                       f'percent of the map image'),
           '_unnamed': {str(k): v for k, v in sorted(unnamed[panel].items())},
           '_traced': [str(k) for k in traced],
           'polylines': [{k: p[k] for k in ('id', 'cls', 'lengthPx', 'points')} for p in P]}
    json.dump(doc, open(work(f'linePolylines_{panel}.json'), 'w'))
    by = collections.defaultdict(lambda: {'positions': [], 'symbols': collections.Counter()})
    for L in labels[panel]:
        e = by[tid(L['mapName'])]
        e['mapName'] = sr.norm(L['mapName'])
        e['positions'].append(L['labelSrc'])
        e['symbols'][L['symbol'] or 'none-visible'] += 1
    json.dump({k: {'mapName': v['mapName'], 'positions': v['positions'], 'symbols': dict(v['symbols']), 'labelled': True}
               for k, v in by.items()}, open(work(f'labels_{panel}.json'), 'w'), indent=1)
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
    json.dump({'trails': markers}, open(work(f'trace_{panel}.json'), 'w'), indent=1)
    print(panel, len(labels[panel]), 'labels,', len(lines), 'named pieces,', len(unnamed[panel]), 'not trails,',
          len(traced), 'traced,', len(markers), 'markers:', ', '.join(m['id'] for m in markers))
