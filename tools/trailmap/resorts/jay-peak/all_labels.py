"""Every trail label as a list for the trace readers (prompts/4-trace.md): name | difficulty | label centres | kind.

    python3 tools/trailmap/resorts/jay-peak/all_labels.py work/jay-peak/labels.json \\
        src/data/resorts/jay-peak/trails.ts work/jay-peak/all_labels.txt

Reads seed_roster.py's labels.json and the trail list as seeded (regen.sh runs this before decisions.py
flags the trails found to have no cut); writes the text file that the legend in
tools/trailmap/runs/jay-peak-trace.json points the tracers at (work/jay-peak/all_labels.txt), so they can tell
whose cut is whose. Not needed for the app's data; it is there so the trace workflow can be re-run after
regen.sh. Was inline code (2026-09-30 11:56) that also wrote the workflow's args (now that runs file).
"""
import json
import re
import sys

L = json.load(open(sys.argv[1]))
T = {}
for m in re.finditer(r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)'(.*?)\}", open(sys.argv[2]).read()):
    T[m.group(1)] = {'name': m.group(2).strip('"\''), 'difficulty': m.group(3), 'glade': 'isGlade' in m.group(4),
                     'park': 'isTerrainPark' in m.group(4)}
with open(sys.argv[3], 'w') as f:
    f.write('Every trail label printed on the Jay Peak map: name | difficulty | label centre(s) in source px | kind\n')
    for tid, e in sorted(L.items(), key=lambda kv: kv[1]['positions'][0]):
        t = T[tid]
        kind = 'terrain park (orange pill)' if t['park'] else 'named glade' if t['glade'] else 'trail'
        if tid == 'sis-boom-bah':
            kind = 'only in the SIDE VIEW inset'
        f.write(f"{t['name']} | {t['difficulty']} | {e['positions']} | {kind}\n")
