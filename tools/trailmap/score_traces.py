"""Score trace readers (prompts/4-trace.md) against reviewed geometry.

    python3 tools/trailmap/score_traces.py --traces 'work/trace_*.json' \\
        --reviews work/export/reviews --polylines src/data/resorts/stowe/linePolylines.json \\
        --size 4325x2553

For each traced trail the reference is what the reviewer saved (selected
pieces + drawn points). Both lines are sampled every 10 px; recall = share
of the reference within TOL px of the trace, precision = share of the trace
within TOL px of the reference. A trail "passes" when both are >= 0.8.
"""
import argparse
import glob
import json
import math
import os

TOL = 25


def dense(pts, step=10):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + list(pts[-1:])


def dist_to(p, lines):
    best = math.inf
    for pts in lines:
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1e-9)))
            best = min(best, math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy))
        if len(pts) == 1:
            best = min(best, math.dist(p, pts[0]))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--traces', required=True)
    ap.add_argument('--reviews', required=True, help='dir of exported review docs')
    ap.add_argument('--polylines', required=True)
    ap.add_argument('--size', required=True)
    a = ap.parse_args()
    W, H = map(int, a.size.split('x'))
    pieces = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']]
              for p in json.load(open(a.polylines))['polylines']}

    def lines_of(ids, drawn):
        out = [pieces[i] for i in ids if i in pieces]
        if drawn and len(drawn) > 1:
            out.append([tuple(q) for q in drawn])
        return out

    passed = total = 0
    for f in sorted(glob.glob(a.traces)):
        doc = json.load(open(f))
        if not isinstance(doc, dict) or 'trails' not in doc:
            continue  # not a trace file
        for t in json.load(open(f))['trails']:
            path = os.path.join(a.reviews, t['id'] + '.json')
            if not os.path.exists(path):
                continue
            r = json.load(open(path))
            r = r.get('data', r)
            ref = lines_of(r.get('polylines') or [], r.get('drawn') or [])
            got = lines_of(t.get('pieces') or [], t.get('traced') or [])
            if not ref or not got:
                print(f"{t['id']:20s} {'no reference' if not ref else 'no trace'}")
                continue
            rs = [q for L in ref for q in dense(L)]
            gs = [q for L in got for q in dense(L)]
            recall = sum(dist_to(q, got) <= TOL for q in rs) / len(rs)
            precision = sum(dist_to(q, ref) <= TOL for q in gs) / len(gs)
            ok = recall >= 0.8 and precision >= 0.8
            passed += ok
            total += 1
            print(f"{t['id']:20s} recall {recall:4.0%}  precision {precision:4.0%}  "
                  f"{'PASS' if ok else 'miss'}  ({t.get('confidence')})")
    print(f'{passed}/{total} traced trails match the review (recall and precision >= 80%, {TOL} px)')


if __name__ == '__main__':
    main()
