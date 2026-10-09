"""symbols_vs_report.py (run from the repo root): each Mammoth panel's printed names whose symbol (as pdf_resort.py attaches
it) differs from the trail report's rating, and the symbols no name took. What it showed (Lupin's seven-curve circle,
Antin Alley's square of straight curves, the bowls' symbols above a level name, Starr Chutes' double diamond) is in
resorts/mammoth/prepare.py and the panels' resort.py."""
import json, sys
sys.path.insert(0,'tools/trailmap')
import importlib
pr=importlib.import_module('pdf_resort')
R=json.load(open('tools/trailmap/resorts/mammoth/report.json'))['trails']
rate={n:r for n,a,r in R}
want={'Green':'circle','Blue':'square','BlueBlack':'square','Black':'diamond','DoubleBlack':'double-diamond'}
for panel in ('main','back-side'):
    r=pr.Resort(f'mammoth/{panel}')
    names=r.names(); syms,loose=r.symbols(names)
    print('==',panel)
    for n in names:
        s=n.get('symbol'); exp=want.get(rate.get(n['name']))
        if s!=exp:
            print('  ', n['name'], 'printed', n['printed'], 'symbol', s, 'report', rate.get(n['name']), [round(v) for v in n['c']])
    for s in loose: print('   loose', s['t'], [round(v) for v in s['c']])
