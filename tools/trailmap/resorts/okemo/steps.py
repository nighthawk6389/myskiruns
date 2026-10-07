"""Okemo's hand-made pipeline steps: each applies one group of decisions.py at its place in regen.sh.

    python3 tools/trailmap/resorts/okemo/steps.py <step> [--data DIR] [--work DIR] [--before FILE]

  trails   src/data/resorts/okemo/trails.ts (as seed_roster.py wrote it): TRAILS_TS, the by-hand changes
  unnamed  linePolylines.json: UNNAMED as `_unnamed` (aggregate_readings.py gives those pieces no trail)
  split    linePolylines.json: SPLITS cut by tools/trailmap/split_pieces.py, whose names it writes as the
           reading $OKEMO_WORK/readings/result_splits.json
  trace    $OKEMO_WORK/traces/trace_*.json (copies of readings/trace_*.json): TRACE_FIXES, a trace that used
           part of a piece now lists the split's new piece
  reviews  trailReviews.json and $OKEMO_WORK/recheck.json, after traces_to_reviews.py: Claude's markers
           (MARKERS), lines (LINES) and recheck notes (RECHECK), for trails no person has decided; with
           --before (trailReviews.json as it was before this rebuild), an unchanged decision keeps its time
  hints    $OKEMO_WORK/review/data.json (the review page's data): each trail with no proposal gets its
           printed label positions (labels.json) as a hint, so the page zooms to it
  person   check that a person's reviews (no "by": "claude") are the same as in --before

These were one-off scratch edits when Okemo was built (2026-09-30: the trail list and _unnamed at 08:03 UTC,
the split and the trace fix at 08:48, the reviews at 08:49, the hints at 08:49); the code here does what they
did, with checks added so a changed input stops the rebuild instead of being edited wrongly.
Reads and writes only the files named above (and the map's size from $OKEMO_WORK/okemo_source.png); --data
defaults to src/data/resorts/okemo, --work to $OKEMO_WORK (default work/okemo). Run from the repo root
(regen.sh does).
"""
import argparse
import datetime
import glob
import json
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions as D  # noqa: E402


def trails(a):
    p = f'{a.data}/trails.ts'
    s = open(p).read()
    for old, new in D.TRAILS_TS:
        if s.count(new) == 1:
            continue  # already applied
        if s.count(old) != 1:
            sys.exit(f'trails.ts: expected one {old!r} (did seed_roster.py change its output?)')
        s = s.replace(old, new)
    open(p, 'w').write(s)


def unnamed(a):
    p = f'{a.data}/linePolylines.json'
    d = json.load(open(p))
    d['_unnamed'] = D.UNNAMED
    json.dump(d, open(p, 'w'))


def split(a):
    W, H = Image.open(f'{a.work}/okemo_source.png').size
    cmd = [sys.executable, 'tools/trailmap/split_pieces.py', '--polylines', f'{a.data}/linePolylines.json',
           '--image-size', f'{W}x{H}', '--reading', f'{a.work}/readings/result_splits.json']
    for s in D.SPLITS:
        cmd += ['--split', s]
    subprocess.run(cmd, check=True)


def trace(a):
    new_ids = json.load(open(f'{a.data}/linePolylines.json')).get('_splits', {})
    for f in sorted(glob.glob(f'{a.work}/traces/trace_*.json')):
        d = json.load(open(f))
        changed = False
        for t in d['trails']:
            fix = D.TRACE_FIXES.get(t['id'])
            if not fix or str(fix[0]) not in (t.get('partial') or {}):
                continue
            piece, note = fix
            new_id = new_ids[str(piece)]
            t['pieces'] = [new_id if p == piece else p for p in t['pieces']]
            t['partial'] = {}
            t['note'] = note.format(new=new_id) + t.get('note', '')
            changed = True
        if changed:
            json.dump(d, open(f, 'w'), indent=1)


def reviews(a):
    path = f'{a.data}/trailReviews.json'
    doc = json.load(open(path))
    before = json.load(open(a.before))['reviews'] if a.before and os.path.exists(a.before) else {}
    rpath = f'{a.work}/recheck.json'
    rec = json.load(open(rpath)) if os.path.exists(rpath) else {}
    W, H = Image.open(f'{a.work}/okemo_source.png').size
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def person(tid):  # a person's decision outranks Claude's
        r = doc['reviews'].get(tid)
        return r is not None and r.get('by') != 'claude'

    doc['_note'] = D.REVIEWS_NOTE
    for tid, (x, y, what) in D.MARKERS.items():
        if person(tid):
            continue
        doc['reviews'][tid] = {'status': 'no-line', 'polylines': [], 'drawn': [], 'mapDifficulty': None,
                               'note': D.MARKER_NOTE.format(what=what), 'at': now, 'by': 'claude',
                               'labelAt': [round(100 * x / W, 2), round(100 * y / H, 2)]}
        rec[tid] = D.MARKER_RECHECK.format(what=what)
    for tid, (pieces, note) in D.LINES.items():
        if person(tid):
            continue
        doc['reviews'][tid] = {'status': 'confirmed', 'polylines': pieces, 'drawn': [], 'mapDifficulty': None,
                               'note': note, 'at': now, 'by': 'claude'}
    for tid, why in D.RECHECK.items():
        if not person(tid):
            rec[tid] = why.format(prior=rec.get(tid, '')[:120])
    for k, v in doc['reviews'].items():  # unchanged decisions keep their timestamp
        o = before.get(k)
        if v.get('by') == 'claude' and o and o.get('by') == 'claude' and {**o, 'at': None} == {**v, 'at': None}:
            v['at'] = o['at']
    json.dump(doc, open(path, 'w'), indent=1)
    json.dump(rec, open(rpath, 'w'), indent=1)
    mine = sorted(k for k, v in doc['reviews'].items() if v.get('by') == 'claude')
    print(f"{len(doc['reviews'])} reviews ({len(doc['reviews']) - len(mine)} by a person); "
          f"{len(rec)} flagged for recheck")


def hints(a):
    f = f'{a.work}/review/data.json'
    d = json.load(open(f))
    labels = json.load(open(f'{a.work}/labels.json'))
    for t in d['trails']:
        p = t.get('proposal') or {}
        if not p.get('polylines') and not p.get('drawn') and not t.get('hint') and labels.get(t['id']):
            t['hint'] = labels[t['id']]['positions']
    json.dump(d, open(f, 'w'))


def person(a):
    if not a.before or not os.path.exists(a.before):
        return
    def theirs(p):
        return {k: v for k, v in json.load(open(p))['reviews'].items() if v.get('by') != 'claude'}
    old, new = theirs(a.before), theirs(f'{a.data}/trailReviews.json')
    if old != new:
        bad = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        sys.exit(f"a person's reviews changed in the rebuild: {', '.join(bad)} (restore trailReviews.json from git)")
    print(f"{len(new)} reviews by a person, unchanged")


def main():
    steps = {f.__name__: f for f in (trails, unnamed, split, trace, reviews, hints, person)}
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('step', choices=list(steps))
    ap.add_argument('--data', default='src/data/resorts/okemo')
    ap.add_argument('--work', default=os.environ.get('OKEMO_WORK', 'work/okemo'))
    ap.add_argument('--before', help='trailReviews.json as it was before this rebuild')
    a = ap.parse_args()
    steps[a.step](a)


if __name__ == '__main__':
    main()
