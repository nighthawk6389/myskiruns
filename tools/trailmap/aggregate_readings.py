"""Merge the naming readers' reports into per-trail proposals.

    python3 tools/trailmap/aggregate_readings.py \\
        --tiles work/tiles --readings 'work/readings/result_*.json' \\
        --roster src/data/resorts/killington/trails.ts --polylines src/data/resorts/killington/linePolylines.json \\
        --proposals src/data/resorts/killington/trailProposals.json --review-data work/review/data.json

Each reading file (written by a reader, see prompts/1-name-lines.md) has
  {"lines":[{id, mapName, rosterId, color, confidence, note}],
   "missed":[{mapName, rosterId, color, tile, labelPx, linePx, note}]}

Every line piece gets votes weighted by confidence (high 3, medium 2, low 1);
the winning name owns the piece. Pieces voted NOT_A_TRAIL are flagged junk
(hidden on the review page). Names printed on the map but absent from the
roster become `new-<slug>` trails. `missed` reports become location hints so
the review page can zoom to a label whose line wasn't detected.

Proposal confidence per trail = weakest of its pieces' vote shares:
high (unanimous), medium (>= 60%), low; 'missed' = label seen but no piece.
"""
import argparse
import collections
import glob
import json
import re

WEIGHT = {'high': 3, 'medium': 2, 'low': 1}
ROSTER_RE = re.compile(
    r"\{ id:\s*'([^']+)',\s*name:\s*(['\"])(.*?)\2,[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'")


def slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tiles', required=True, help='dir with index.json from render_tiles.py')
    ap.add_argument('--readings', required=True, help='glob of reader result files')
    ap.add_argument('--roster', required=True, help='trails.ts')
    ap.add_argument('--polylines', required=True)
    ap.add_argument('--proposals', required=True, help='output: trailProposals.json')
    ap.add_argument('--review-data', required=True, help='output: data.json for the review page')
    a = ap.parse_args()

    index = json.load(open(f'{a.tiles}/index.json'))
    zoom, (W, H) = index['zoom'], index['imageSize']
    tiles = {t['tile']: t for t in index['tiles']}
    roster = [dict(id=i, name=n, difficulty=d, peak=p) for i, _q, n, d, p in ROSTER_RE.findall(open(a.roster).read())]
    roster_ids = {t['id'] for t in roster}
    # readers of a new map (prompts/0-new-map.md) give no rosterId: match the
    # printed name to a roster name instead
    by_name = {slug(t['name'].replace("'", '')): t['id'] for t in roster}
    def roster_id(rec):
        rid = rec.get('rosterId')
        return rid if rid in roster_ids else by_name.get(slug((rec.get('mapName') or '').replace("'", '').replace('’', '')))
    polys = json.load(open(a.polylines))['polylines']

    votes = collections.defaultdict(collections.Counter)
    info = collections.defaultdict(list)
    missed = []
    for f in sorted(glob.glob(a.readings)):
        r = json.load(open(f))
        for L in r.get('lines', []):
            name = (L.get('mapName') or '').strip().upper()
            if not name or name.startswith(('LIFT', 'NOT_A_TRAIL', 'UNKNOWN', 'SPLIT')):
                key = ('#' + (name.split(':')[0] or 'UNKNOWN'), None)
            else:
                key = (name, roster_id(L))
            votes[L['id']][key] += WEIGHT.get(L.get('confidence'), 1)
            info[L['id']].append(L)
        missed += r.get('missed', [])

    new = {}
    props = collections.defaultdict(lambda: {'polylines': [], 'share': [], 'mapName': None, 'notes': []})
    for pid, c in votes.items():
        (name, rid), w = c.most_common(1)[0]
        if name.startswith('#'):
            continue
        tid = rid or 'new-' + slug(name)
        if not rid:
            new.setdefault(tid, {'name': name.title(), 'colors': collections.Counter()})
            for L in info[pid]:
                new[tid]['colors'][L.get('color')] += 1
        p = props[tid]
        p['polylines'].append(pid)
        p['share'].append(w / sum(c.values()))
        p['mapName'] = name
        p['notes'] += [L['note'] for L in info[pid] if L.get('note')]

    hints = collections.defaultdict(list)
    for m in missed:
        rid = roster_id(m)
        tid = rid or 'new-' + slug(m.get('mapName'))
        if not rid:
            new.setdefault(tid, {'name': (m.get('mapName') or '?').title(), 'colors': collections.Counter()})
            new[tid]['colors'][m.get('color')] += 1
        if m.get('tile') in tiles and m.get('labelPx'):
            b = tiles[m['tile']]['box']
            to_src = lambda q: [round(b[0] + q[0] / zoom), round(b[1] + q[1] / zoom)]  # noqa: E731
            hints[tid] += [to_src(m['labelPx'])] + [to_src(q) for q in (m.get('linePx') or [])]
        if m.get('note'):
            props[tid]['notes'].append(m['note'])
        props[tid]['mapName'] = props[tid]['mapName'] or (m.get('mapName') or '').upper()

    def confidence(p):
        if not p['polylines']:
            return 'missed'
        low = min(p['share'])
        return 'high' if low >= 0.99 else 'medium' if low >= 0.6 else 'low'

    new_trails = [dict(id=k, name=v['name'], difficulty=(v['colors'].most_common(1) or [('blue', 0)])[0][0] or 'blue',
                       peak='new on map', isNew=True) for k, v in new.items()]
    trails, proposals = [], {}
    for t in roster + new_trails:
        e = {k: t[k] for k in ('id', 'name', 'difficulty', 'peak')}
        if t.get('isNew'):
            e['isNew'] = True
        p = props.get(t['id'])
        if p:
            prop = {'polylines': sorted(set(p['polylines'])), 'confidence': confidence(p), 'mapName': p['mapName'],
                    'note': ' | '.join(dict.fromkeys(p['notes']))[:300]}
            e['proposal'] = prop
            proposals[t['id']] = {k: v for k, v in prop.items() if v} | (
                {'newTrail': True, 'name': t['name'], 'difficulty': e['difficulty']} if t.get('isNew') else {})
        if hints.get(t['id']):
            e['hint'] = hints[t['id']]
        trails.append(e)

    junk = {int(k) for k, c in votes.items() if c.most_common(1)[0][0][0] == '#NOT_A_TRAIL'}
    review = {
        'imageSize': [W, H],
        'polylines': [{'id': p['id'], 'cls': p['cls'], **({'junk': True} if p['id'] in junk else {}),
                       'pts': [[round(x * W / 100, 1), round(y * H / 100, 1)] for x, y in p['points']]} for p in polys],
        'trails': trails,
    }
    json.dump(review, open(a.review_data, 'w'))
    json.dump({'_note': 'Per-trail line proposals from reading numbered map tiles. '
               'Reviews in trailReviews.json override these.', 'trails': proposals}, open(a.proposals, 'w'), indent=1)
    counts = collections.Counter(e.get('proposal', {}).get('confidence', 'none') for e in trails)
    print(f'{len(trails)} trails ({len(new)} new on map); proposals by confidence: {dict(counts)}; '
          f'{len(votes)} pieces voted, {len(junk)} not trails')


if __name__ == '__main__':
    main()
