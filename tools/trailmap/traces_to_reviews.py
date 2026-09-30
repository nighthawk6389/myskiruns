"""Pre-fill the review with trace readers' results (prompts/4-trace.md).

    python3 tools/trailmap/traces_to_reviews.py --traces 'work/trace_*.json' \\
        --reviews src/data/resorts/<id>/trailReviews.json --recheck work/recheck.json

Each traced trail becomes a "confirmed" review with the reader's pieces and
traced points (by: claude), unless a human decision already exists; it is
also added to the recheck file so the review page opens it pre-filled with
"please recheck". Then run refresh_review_data.py and trails:apply.
Reviews hold whole pieces: a trace that uses only part of a piece (its
`partial`) is warned about; cut that piece with split_pieces.py and put the
part's id in the trace first (Okemo: Turkey Shoot on piece 210).
"""
import argparse
import datetime
import glob
import json
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--traces', required=True)
    ap.add_argument('--reviews', required=True)
    ap.add_argument('--recheck', required=True, help='JSON {trailId: why}; created or extended')
    a = ap.parse_args()
    doc = json.load(open(a.reviews)) if os.path.exists(a.reviews) else {'reviews': {}}
    recheck = json.load(open(a.recheck)) if os.path.exists(a.recheck) else {}
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    added = []
    for f in sorted(glob.glob(a.traces)):
        d = json.load(open(f))
        if not isinstance(d, dict) or 'trails' not in d:
            continue
        for t in d['trails']:
            cur = doc['reviews'].get(t['id'])
            if cur and cur.get('by') != 'claude':
                continue  # a human decided already
            doc['reviews'][t['id']] = {
                'status': 'confirmed', 'polylines': t.get('pieces') or [], 'drawn': t.get('traced') or [],
                'mapDifficulty': None, 'note': (t.get('note') or '')[:300], 'at': now, 'by': 'claude',
            }
            recheck[t['id']] = f"Traced by a reader ({t.get('confidence')} confidence): {(t.get('note') or '')[:200]}"
            added.append(t['id'])
            if any(t.get('partial', {}).values()):
                # the review stores whole pieces: cut them first (split_pieces.py) and list the part's id
                print(f"warning: {t['id']} uses only part of piece(s) {', '.join(t['partial'])}: {t['partial']}")
    json.dump(doc, open(a.reviews, 'w'), indent=1)
    json.dump(recheck, open(a.recheck, 'w'), indent=1)
    print(f'{len(added)} traced trails pre-filled for recheck:', ', '.join(added))


if __name__ == '__main__':
    main()
