"""Build wb_truth/runs.json from the official 2025-26 terrain feed + the resort's GIS run layer.

Primary: whistlerblackcomb.com FR.TerrainStatusFeed captured 2026-01-22 (Common Crawl CC-MAIN-2026-04).
Secondary: runs in the resort's ArcGIS 'Ski Runs' layer (Ski_Runs_GDB/1) that the feed does not list.

Usage: python3 -I build_runs.py <out.json>
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb_common as C  # noqa: E402

FEED_SRC = ('whistlerblackcomb.com terrain & lift status feed (FR.TerrainStatusFeed), '
            'captured 2026-01-22 by Common Crawl CC-MAIN-2026-04')
GIS_SRC = ("Whistler Blackcomb's own ArcGIS 'Ski Runs' layer (services3.arcgis.com/XthfLqjm6BwtGUpE "
           "Ski_Runs_GDB/1, last edited 2026-08-06); not listed in the terrain feed")

LEARNING_MOUNTAIN = {
    'Adult Learning': 'Whistler',          # Adult Mini Carpet - Whistler - Olympic Zone
    'Base 2 Carpet': 'Blackcomb',          # Base 2 - Blackcomb
    'Blackcomb Base - Whistler Kids Only': 'Blackcomb',
    'CLC - Whistler Kids Only': 'Whistler',  # CLC Mini Carpet - Whistler
    'Creekside Base - Whistler Kids Only': 'Whistler',
    'Fantastic': 'Whistler',               # Fantastic Carpet - Whistler - Olympic Zone; GIS Whistler
    'Foxy Hollow': 'Whistler',             # GIS Whistler
    'Scampland - Whistler Kids Only': 'Whistler',  # Scampland Carpet - Whistler - CLC
    'Snowboard Carpet': 'Whistler',        # Snowboard Carpet - Whistler - Olympic Zone
    'Super Carpet': 'Whistler',            # Super Carpet - Whistler - Olympic Zone
}

# GIS run_name -> feed name(s) it is a spelling/segmentation variant of (same mountain).
ALIASES = {
    'Blackcomb': {
        'Base II Carpet': ['Base 2 Carpet'],
        'Big Easy - Lower': ['Big Easy'], 'Big Easy - Upper': ['Big Easy'],
        'Choker Park': ['Choker'],
        'Cruiser Bumps': ['Cruiser - Bumps'], 'Cruiser Grub': ['Cruiser - Grub'],
        'Diamond': ['Diamond Bowl'],
        'Glacier Drive': ['Glacier Drive - Lower'],
        'Green Line - Lower': ['Greenline - Lower'], 'Green Line - Mid': ['Greenline - Mid'],
        'Green Line - Upper': ['Greenline - Upper'],
        'Grub Stake': ['Grubstake'],
        'Honeycomb': ['Honeycomb - Lower', 'Honeycomb - Upper'],
        'Horseman Face': ['Horstman Face'],
        "Hugh's Heaven": ["Hugh's Heaven - Lower", "Hugh's Heaven - Upper"],
        'Jersey Cream': ['Jersey Cream - Lower', 'Jersey Cream - Upper'],
        'Lower Cloud 9': ['Cloud 9 - Lower'], 'Upper Cloud 9': ['Cloud 9 - Upper'],
        'Race Centre': ['Blackcomb Race Centre'],
        'Ridge Runner': ['Ridge Runner - Lower', 'Ridge Runner - Upper'],
        "Rock N' Roll - Lower": ['Rock & Roll - Lower'], "Rock N' Roll - Upper": ['Rock & Roll -Upper'],
        'Sapphire': ['Sapphire Bowl'],
        'Secret Basin': ['Secret Bassin'],
        'Slingshot - Connector': ['Slingshot Connector'],
        'Stoker - Upper': ['Stoker'], 'Stoker Bumps': ['Stoker - Bumps'],
        'Straight Shot': ['Straight Shot - Upper'],
        'The Blowhole': ['Blow Hole'],
        'The Outer Limits': ['Outer Limits'],
        'White Light': ['White Light - Upper'],
        "Xhiggy's Meadows": ["Xhiggy's Meadow"],
        'Zig Zag': ['Zig Zag - Lower', 'Zig Zag - Upper'],
    },
    'Whistler': {
        'Bear Cub': ['Bear Cub - Lower', 'Bear Cub - Upper'],
        'Burnt Stew Trail': ['Burnt Stew Trail - Lower', 'Burnt Stew Trail - Upper'],
        "Dusty's Decent": ["Dusty's Descent"],
        'Ego Bowl': ['Ego Bowl - Lower', 'Ego Bowl - Upper'],
        'Enchanted Forest': ['Enchanted Forest - Adventure Trail', 'Enchanted Forest - Lower Entrance',
                             'Enchanted Forest - Upper Entrance'],
        'Flute Bowl Main': ['Flute Bowl'],
        "Franz's Meadow": ["Franz's Meadows"],
        'G.S.': ['G.S. - Lower', 'GS - Upper'],
        'Gun Barrel - East': ['Gun Barrels'], 'Gun Barrel - West': ['Gun Barrels'],
        "Harvey's Harrow": ["Harvey's"],
        **{f'Horseshoe {i}': ['Harmony Horseshoes'] for i in range(1, 9)},
        'Litte Red - Lower': ['Little Red Run - Lower'], 'Little Red - Upper': ['Little Red Run - Upper'],
        "Lower McKonkey's": ["McConkey's - Lower"], "McConkey's - Upper": ["McKonkey's - Upper"],
        'Monday': ["Monday's"],
        "Robertson's Run": ["Robertson's"],
    },
}

# Notes for GIS-only entries that are probably a feed run under another name, or misspelt.
GIS_NOTES = {
    ('Whistler', 'C.C.'): "probably the feed's 'Closed Captions' (same spot, Big Red area)",
    ('Blackcomb', 'Kid Adventure'): "probably the feed's 'Animal Adventure Trail' (lower Blackcomb, by Yellow Brick Road)",
    ('Blackcomb', 'Lakeside Center'): "probably part of the feed's 'Lakeside Bowl'",
    ('Blackcomb', 'Access to Blackcomb Glacier'): "probably the feed's 'Entrance to Blackcomb Glacier'",
    ('Blackcomb', "Spanky's Ladder Traverse"): "probably the feed's 'Spankys Ladder'",
    ('Whistler', 'Norther Lights - Upper'): "sic: 'Northern Lights - Upper' (the feed lists only Northern Lights - Lower)",
    ('Whistler', 'Rapsody Road'): "sic: 'Rhapsody Road'",
    ('Whistler', 'Windorw Ridge - Upper'): "sic: 'Windrow Ridge - Upper'",
    ('Whistler', 'Tequilla Sunrise'): "sic: 'Tequila Sunrise'",
    ('Blackcomb', 'Ladies Fisrt'): "sic: 'Ladies First'",
    ('Blackcomb', 'Front Page Challenege'): "sic: 'Front Page Challenge'",
    ('Whistler', 'G.S Start'): "start of the feed's 'GS - Upper'",
    ('Whistler', 'Fantastic - Lower'): "lower part of the feed's 'Fantastic' (Learning Areas)",
    ('Blackcomb', 'Tube Park'): 'tube park, not a ski run',
}


def main():
    out_path = Path(sys.argv[1])
    _, feed = C.load_feed(C.FEED_2026)
    gis = C.load_gis_runs()
    polys = C.load_polys(C.GIS_POLY_NEW) + C.load_polys(C.GIS_POLY_OLD)

    # Feed entries, one per (name, area); a same-area duplicate is merged and noted.
    entries = {}
    for t in feed:
        mountain = C.AREA_MOUNTAIN.get(t['Area']) or LEARNING_MOUNTAIN[t['Name']]
        key = (t['Name'], t['Area'])
        if key in entries:
            entries[key]['feed_ids'].append(t['Id'])
            entries[key]['note'] = f"listed twice in the feed (ids {entries[key]['feed_ids'][0]}, {t['Id']})"
            continue
        entries[key] = {
            'name': t['Name'], 'mountain': mountain, 'area': t['Area'], 'difficulty': t['Difficulty'],
            'source': FEED_SRC, 'feed_ids': [t['Id']], 'gis_names': [], 'gis_difficulty': [],
            'gis_on_trail_map': [], 'note': None,
        }

    by_norm = collections.defaultdict(list)  # (mountain, norm name) -> feed entries
    for e in entries.values():
        by_norm[(e['mountain'], C.norm(e['name']))].append(e)

    # Attach GIS runs to feed entries (exact-normalised name, else alias); collect the rest.
    gis_only = collections.OrderedDict()
    mountain_conflicts = []
    for r in gis:
        m, n = r['mountain'], r['run_name']
        targets = by_norm.get((m, C.norm(n)))
        if not targets:
            other = 'Blackcomb' if m == 'Whistler' else 'Whistler'
            if by_norm.get((other, C.norm(n))):
                mountain_conflicts.append((n, m))
            alias = ALIASES.get(m, {}).get(n)
            if alias:
                targets = [e for a in alias for e in by_norm[(m, C.norm(a))]]
                assert targets, (m, n, alias)
        if targets:
            for e in targets:
                if n not in e['gis_names']:
                    e['gis_names'].append(n)
                if r['difficulty'] not in e['gis_difficulty']:
                    e['gis_difficulty'].append(r['difficulty'])
                if r['trailmap'] not in e['gis_on_trail_map']:
                    e['gis_on_trail_map'].append(r['trailmap'])
            continue
        g = gis_only.setdefault((m, n), {'diffs': [], 'trailmap': [], 'ids': []})
        if r['difficulty'] not in g['diffs']:
            g['diffs'].append(r['difficulty'])
        if r['trailmap'] not in g['trailmap']:
            g['trailmap'].append(r['trailmap'])
        g['ids'].append(r['id'])

    # epic_zone (the zone the Epic app uses) from the run polygons, for GIS-only runs.
    poly_zone = {}
    for p in polys:
        z = (p.get('epic_zone') or '').strip()
        if z and z != 'Not Seen By Public':
            poly_zone.setdefault((p['mountain'], C.norm(p['run'])), z)

    rows = []
    for e in entries.values():
        tm = [x for x in e['gis_on_trail_map'] if x]
        rows.append({
            'name': e['name'], 'mountain': e['mountain'], 'area': e['area'], 'difficulty': e['difficulty'],
            'source': e['source'],
            'gis_names': e['gis_names'] or None,
            'gis_difficulty': '/'.join(e['gis_difficulty']) or None,
            'gis_on_trail_map': '/'.join(tm) if tm else None,
            'note': e['note'],
        })
    for (m, n), g in gis_only.items():
        tm = [x for x in g['trailmap'] if x]
        area = poly_zone.get((m, C.norm(n)))
        notes = [x for x in (GIS_NOTES.get((m, n)),
                             'area = epic_zone of the GIS run polygon (Epic app zone wording)' if area else None) if x]
        rows.append({
            'name': n, 'mountain': m, 'area': area,
            'difficulty': '/'.join(g['diffs']), 'source': GIS_SRC,
            'gis_names': [n], 'gis_difficulty': '/'.join(g['diffs']),
            'gis_on_trail_map': '/'.join(tm) if tm else None,
            'note': '; '.join(notes) or None,
        })
    unused_notes = [k for k in GIS_NOTES if k not in gis_only]
    assert not unused_notes, unused_notes

    rows.sort(key=lambda r: (r['source'] != FEED_SRC, r['mountain'], r['area'] or '~', r['name'].lower()))
    out_path.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')

    # Summary for the report.
    feed_rows = [r for r in rows if r['source'] == FEED_SRC]
    gis_rows = [r for r in rows if r['source'] == GIS_SRC]
    print('rows', len(rows), 'feed', len(feed_rows), 'gis-only', len(gis_rows))
    print('feed per mountain', collections.Counter(r['mountain'] for r in feed_rows))
    print('feed per mountain x difficulty', sorted(collections.Counter((r['mountain'], r['difficulty']) for r in feed_rows).items()))
    print('feed per difficulty', collections.Counter(r['difficulty'] for r in feed_rows))
    print('feed rows with no GIS counterpart', sum(1 for r in feed_rows if not r['gis_names']))
    print('gis-only per mountain x on_trail_map', sorted(collections.Counter((r['mountain'], r['gis_on_trail_map']) for r in gis_rows).items(), key=str))
    print('gis-only per difficulty', collections.Counter(r['difficulty'] for r in gis_rows).most_common())
    print('gis-only with area', sum(1 for r in gis_rows if r['area']))
    print('mountain conflicts (GIS name only matches other mountain):', mountain_conflicts)
    xt = collections.Counter((r['difficulty'], r['gis_difficulty']) for r in feed_rows if r['gis_difficulty'])
    print('feed vs GIS difficulty:', sorted(xt.items(), key=lambda kv: -kv[1]))


if __name__ == '__main__':
    main()
