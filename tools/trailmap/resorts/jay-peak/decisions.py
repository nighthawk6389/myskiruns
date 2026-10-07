"""Jay Peak: what the zoomed crops settled after the trace pass (hand-made), applied by regen.sh.

    python3 tools/trailmap/resorts/jay-peak/decisions.py traces tools/trailmap/resorts/jay-peak/readings work/jay-peak/traces
    python3 tools/trailmap/resorts/jay-peak/decisions.py trails src/data/resorts/jay-peak/trails.ts \\
        tools/trailmap/resorts/jay-peak/header.txt

`traces` copies the trace readers' outputs (readings/, laid out as the workflow wrote them) into one folder in
the order they came in, as NN_<dir>_<file>.json, so that traces_to_reviews.py, which reads one glob in sorted
order, adds the reviews in the order trailReviews.json holds them; and it makes sure the two traces rejected on
the crops are empty (REJECTED; in the session they were emptied in the readers' files themselves, which is how
they are archived, so on these readings this changes nothing).

`trails` flags as glades the trails whose label sits in painted trees with no cut to follow (NO_CUT) and puts
header.txt at the top of trails.ts. In the session these were hand edits of trails.ts made after
aggregate_readings.py had run (so trailProposals.json has markers only for the 11 named glades; these get
theirs from their empty traces), which is why regen.sh runs this after it.

Every decision is in checks/audit_log.json, one line per trail, from the crop that settled it.
"""
import glob
import json
import os
import shutil
import sys

# the trace files in the order they arrived (trailReviews.json keeps that order): Claude's markers for the
# parks and the inset-only name first, then the tracer groups of tools/trailmap/runs/jay-peak-trace.json as
# their runs finished (a session limit killed most of the first run; groups 3-8 were re-run as runs b-e)
TRACE_ORDER = [
    'trace/trace_markers.json',  # Claude: the 5 terrain parks and Sis Boom Bah: markers at their labels
    'trace/trace_0.json',        # group 0: Stateside's west side (Willard ... Heaven's Road)
    'trace/trace_1.json',        # group 1: Sweetheart ... Raccoon Run
    'trace/trace_2.json',        # group 2: Northway ... Lower Milk Run
    'trace_b/trace_0.json',      # group 6: along the tram (Vertigo ... Racer)
    'trace_c/trace_1.json',      # group 4: the Moons and the slow-zone lanes (Queen's Highway ... Buckaroo Bonzai)
    'trace_e/trace_0.json',      # group 8: the east side (Ullr's Dream ... André's Paradise)
    'trace_d/trace_1.json',      # group 7: the summit and the Flyer top (Face Chutes ... Staircase)
    'trace_d/trace_0.json',      # group 5: the Northway slope (Lift Line ... St. George's Prayer)
    'trace_c/trace_0.json',      # group 3: the base area (The Boulevard ... Taxi)
]

# low-confidence traces rejected on the crop: no points, so traces_to_reviews.py makes a marker at the label
REJECTED = {
    'tuckermans-chute': ('trace_d/trace_1.json', 'NO CUT (checked on a crop: no chute painted on the treed summit '
                         'face; marker at the label). Tracer: '),
    'deliverance': ('trace_d/trace_0.json', 'NO CUT (checked on a crop: the diamond sits in a lightly treed strip '
                    'beside the Lift Line cut; a parallel guess would overlap Lift Line; marker at the label). '
                    'Tracer: '),
}

# labels in painted trees with no cut (crops; Timbuktu, Valhalla, André's Paradise and Staircase were the
# tracers' own NO CUT calls, Deliverance the rejected trace above): glades, with a marker at the label.
# Tuckerman's Chute also gets a marker but stays a trail (a chute, not woods).
NO_CUT = ['timbuktu', 'valhalla', 'andres-paradise', 'staircase', 'deliverance']


def traces(readings: str, out: str) -> None:
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, '*.json')):
        os.remove(f)
    have = sorted(os.path.relpath(f, readings) for f in glob.glob(os.path.join(readings, 'trace*', '*.json')))
    assert sorted(TRACE_ORDER) == have, f'readings/ holds {have}, TRACE_ORDER lists {TRACE_ORDER}'
    for k, rel in enumerate(TRACE_ORDER):
        dst = os.path.join(out, f"{k:02d}_{rel.replace('/', '_')}")
        shutil.copyfile(os.path.join(readings, rel), dst)
        d = json.load(open(dst))
        changed = False
        for t in d['trails']:
            if t['id'] in REJECTED and REJECTED[t['id']][0] == rel and (t.get('traced') or t.get('pieces')):
                t['note'] = REJECTED[t['id']][1] + t.get('note', '')
                t['traced'], t['pieces'] = [], []
                changed = True
        if changed:
            json.dump(d, open(dst, 'w'), indent=1)
    print(f'{len(TRACE_ORDER)} trace files -> {out}')


def trails(path: str, header: str) -> None:
    s = open(path).read()
    for tid in NO_CUT:
        i = s.index(f"  {{ id: '{tid}', ")
        j = s.index(' },\n', i)
        assert 'isGlade' not in s[i:j], tid
        s = s[:j] + ', isGlade: true' + s[j:]
    s = s.replace(s[s.index('// Seeded'):s.index('export const peaks')], open(header).read())
    open(path, 'w').write(s)
    print(f'{path}: {len(NO_CUT)} trails with no cut flagged as glades; header from {header}')


if __name__ == '__main__':
    {'traces': traces, 'trails': trails}[sys.argv[1]](*sys.argv[2:])
