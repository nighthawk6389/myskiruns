"""Rebuild the review page's data.json after the roster or reviews changed,
and flag trails for the reviewer to re-check.

    python3 tools/trailmap/refresh_review_data.py \\
        --review-data work/review/data.json --roster src/data/resorts/killington/trails.ts \\
        --reviews src/data/resorts/killington/trailReviews.json --page-ids work/review/page_ids.txt \\
        --recheck recheck.json

--recheck is {"trail-id": "why the reviewer should look again"}; those trails
open pre-filled with the current geometry from trailReviews.json and show as
"please recheck" until saved again. Trails removed from the roster disappear
from the page; renamed / re-rated trails show their new name and difficulty.

The page keeps its database ids forever: trails first seen as map-only names
are `new-<slug>` on the page even after they join the roster under a clean id
(new-racer-s-edge -> racers-edge). --page-ids lists the page's existing ids
(one per line, e.g. from a reviews export) so those keep matching.
"""
import argparse
import datetime
import json
import re

ROSTER_RE = re.compile(
    r"\{ id:\s*'([^']+)',\s*name:\s*(['\"])(.*?)\2,[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'")


def page_to_roster(pid: str) -> str:
    return re.sub(r'-s(-|$)', r's\1', pid[4:]) if pid.startswith('new-') else pid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--review-data', required=True)
    ap.add_argument('--roster', required=True)
    ap.add_argument('--reviews', required=True)
    ap.add_argument('--page-ids', help='file with the page database ids, one per line')
    ap.add_argument('--recheck', help='JSON {trailId: why}')
    a = ap.parse_args()

    data = json.load(open(a.review_data))
    old = {t['id']: t for t in data['trails']}
    roster = [dict(id=i, name=n, difficulty=d, peak=p) for i, _q, n, d, p in ROSTER_RE.findall(open(a.roster).read())]
    reviews = json.load(open(a.reviews))['reviews']
    page_ids = [l.strip() for l in open(a.page_ids)] if a.page_ids else list(old)
    back = {page_to_roster(pid): pid for pid in page_ids if pid}
    recheck = json.load(open(a.recheck)) if a.recheck else {}
    since = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    trails = []
    for t in roster:
        pid = back.get(t['id'], t['id'])
        e = {'id': pid, 'name': t['name'], 'difficulty': t['difficulty'], 'peak': t['peak']}
        if pid.startswith('new-'):
            e['isNew'] = True
        for k in ('proposal', 'hint', 'recheck'):
            if old.get(pid, {}).get(k):
                e[k] = old[pid][k]
        if t['id'] in recheck:
            r = reviews.get(t['id'], {})
            e['recheck'] = {'since': since, 'why': recheck[t['id']]}
            e['proposal'] = {'polylines': r.get('polylines', []), 'drawn': r.get('drawn', []),
                             'confidence': 'claude', 'mapName': t['name'].upper()}
        trails.append(e)
    data['trails'] = trails
    json.dump(data, open(a.review_data, 'w'))
    print(f'{len(trails)} trails; {len(recheck)} flagged for recheck')


if __name__ == '__main__':
    main()
