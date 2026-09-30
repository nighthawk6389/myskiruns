"""Split line pieces that run through a junction into a differently named
trail (readers report these as "SPLIT: A / B").

    python3 tools/trailmap/split_pieces.py --polylines src/data/resorts/stowe/linePolylines.json \\
        --image-size 4325x2553 --split '1@1755,585=RIDGE VIEW/LOWER RIDGEVIEW' ... \\
        --reading work/tiles/result_splits.json

Each --split is "<id>@<x>,<y>=<name A>/<name B>" in source px: the piece is
cut at its point nearest (x,y); the part with the smaller mean y (higher on
the mountain) keeps the id and gets name A, the other part becomes a new
piece and gets name B ("-" = leave unnamed). Pieces are rewritten in place
(new ids appended); the names are written as a reading with confidence
"certain" that aggregate_readings.py merges with the readers' (their SPLIT
votes on these pieces are dropped). Re-running on already split
pieces is a no-op for ids that were split before (recorded in _splits).
"""
import argparse
import json
import math


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--polylines', required=True)
    ap.add_argument('--image-size', required=True)
    ap.add_argument('--split', action='append', default=[])
    ap.add_argument('--reading', required=True)
    a = ap.parse_args()
    W, H = map(int, a.image_size.split('x'))
    doc = json.load(open(a.polylines))
    polys = {p['id']: p for p in doc['polylines']}
    done = doc.setdefault('_splits', {})
    lines = []
    for spec in a.split:
        head, names = spec.split('=')
        pid, at = head.split('@')
        pid = int(pid)
        x, y = (float(v) for v in at.split(','))
        name_a, name_b = names.split('/')
        if str(pid) in done:
            new_id = done[str(pid)]
        else:
            p = polys[pid]
            pts = [[q[0] * W / 100, q[1] * H / 100] for q in p['points']]
            # nearest point on the polyline (insert it if it falls mid-segment)
            best = (math.inf, 0, None)
            for i in range(1, len(pts)):
                (ax, ay), (bx, by) = pts[i - 1], pts[i]
                dx, dy = bx - ax, by - ay
                t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / ((dx * dx + dy * dy) or 1e-9)))
                q = [ax + t * dx, ay + t * dy]
                d = math.dist(q, (x, y))
                if d < best[0]:
                    best = (d, i, q)
            _, i, q = best
            first, second = pts[:i] + [q], [q] + pts[i:]
            if sum(v[1] for v in first) / len(first) > sum(v[1] for v in second) / len(second):
                first, second = second, first
            pct = lambda s: [[round(100 * u / W, 2), round(100 * v / H, 2)] for u, v in s]  # noqa: E731
            length = lambda s: round(sum(math.dist(s[k - 1], s[k]) for k in range(1, len(s))))  # noqa: E731
            new_id = max(polys) + 1
            p['points'], p['lengthPx'] = pct(first), length(first)
            polys[new_id] = {'id': new_id, 'cls': p['cls'], 'lengthPx': length(second), 'points': pct(second)}
            done[str(pid)] = new_id
            print(f'split {pid} at ({x:.0f},{y:.0f}), {best[0]:.0f}px off the line -> {pid} + {new_id}')
        for i_, n in ((pid, name_a), (new_id, name_b)):
            if n != '-':
                lines.append({'id': i_, 'mapName': n, 'color': polys[i_]['cls'], 'confidence': 'certain',
                              'note': f'split of piece {pid}'})
    doc['polylines'] = [polys[k] for k in sorted(polys)]
    json.dump(doc, open(a.polylines, 'w'))
    json.dump({'lines': lines, 'labels': []}, open(a.reading, 'w'), indent=1)


if __name__ == '__main__':
    main()
