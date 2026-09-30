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

With --labels (labels.json from seed_roster.py) and --image, a trace with no
pieces and no points (a reader found no cut to follow: a glade painted as
trees, a park drawn as an area) becomes a "no-line" review with a marker at
the trail's first label instead (Jay Peak, whose map draws no lines).
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
    ap.add_argument('--labels', help='labels.json from seed_roster.py: empty traces become label markers')
    ap.add_argument('--image', help='the map image (with --labels), for its size')
    a = ap.parse_args()
    labels = json.load(open(a.labels)) if a.labels else {}
    if a.labels:
        from PIL import Image
        W, H = Image.open(a.image).size
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
            if not t.get('pieces') and not t.get('traced') and labels.get(t['id'], {}).get('positions'):
                x, y = labels[t['id']]['positions'][0]
                doc['reviews'][t['id']].update(status='no-line', labelAt=[round(100 * x / W, 2), round(100 * y / H, 2)])
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
