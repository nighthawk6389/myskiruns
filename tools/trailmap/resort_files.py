"""Where a resort's files live: the Python twin of scripts/lib/resort.mjs, for the tools that take
`--resort <id>` and, for a map drawn in several panels, `--panel <id>`.

    from resort_files import resort_files, trail_info
    f = resort_files('vail', 'back-bowls')   # f['paths'], f['trails'], f['map'], f['work'], ...
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))


def panels_of(rid):
    """The resort's map panels (their folders under src/data/resorts/<id>/panels/), or [None] for one map."""
    d = os.path.join(ROOT, 'src/data/resorts', rid, 'panels')
    return sorted(os.listdir(d)) if os.path.isdir(d) else [None]


def resort_files(rid, panel=None):
    """Absolute paths of a resort's (or one of its panels') data files, its map image in public/maps/, and its
    working folder (work/<id>[/<panel>], git-ignored, where a regen.sh leaves the full-size map.png)."""
    if not re.fullmatch(r'[a-z0-9-]+', rid or '') or (panel and not re.fullmatch(r'[a-z0-9-]+', panel)):
        raise SystemExit(f'bad resort/panel id: {rid} {panel}')
    d = os.path.join(ROOT, 'src/data/resorts', rid)
    if not os.path.isdir(d):
        raise SystemExit(f'no resort {rid} in src/data/resorts/')
    pd = os.path.join(d, 'panels', panel) if panel else d
    if panel and not os.path.isdir(pd):
        raise SystemExit(f'{rid} has no panel {panel} (panels: {", ".join(p for p in panels_of(rid) if p)})')
    work = os.path.join(ROOT, 'work', rid, *([panel] if panel else []))
    return {
        'id': rid, 'panel': panel, 'dir': d,
        'trails': os.path.join(d, 'trails.ts'),
        'polylines': os.path.join(pd, 'linePolylines.json'),
        'proposals': os.path.join(pd, 'trailProposals.json'),
        'reviews': os.path.join(pd, 'trailReviews.json'),
        'paths': os.path.join(pd, 'trailPaths.json'),
        'map': os.path.join(ROOT, 'public/maps', f'{rid}-{panel}.jpg' if panel else f'{rid}.jpg'),
        'work': work,
        'tools': os.path.join(ROOT, 'tools/trailmap/resorts', rid),
    }


def trail_info(trails_ts):
    """{trail id: (name, difficulty, peak)} from a trails.ts."""
    out = {}
    for m in re.finditer(r"id: '([^']+)', name: (['\"])(.*?)\2, difficulty: '([^']+)'(?:, peak: '([^']+)')?",
                         open(trails_ts).read()):
        out[m.group(1)] = (m.group(3).replace("\\'", "'"), m.group(4), m.group(5))
    return out
