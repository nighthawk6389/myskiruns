"""Shared loading/normalisation for the Whistler Blackcomb ground-truth build."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'data'
FEED_2026 = ROOT / 'cc/feeds_CC-MAIN-2026-04_20260122155441/feed_04_FR_TerrainStatusFeed.json'
FEED_2025 = ROOT / 'cc/feeds_CC-MAIN-2025-13_20250319182559/feed_02_FR_TerrainStatusFeed.json'
GIS_RUNS = ROOT / 'arcgis/features/Ski_Runs_GDB_L1_p0.geojson'
GIS_POLY_NEW = ROOT / 'arcgis/features/Ski_Trail_Polygons_GDB_L1_p0.geojson'
GIS_POLY_OLD = ROOT / 'arcgis/features/Ski_Run_Polygon_L0_p0.geojson'

AREA_MOUNTAIN = {
    '7th Heaven': 'Blackcomb',
    'Crystal Ridge': 'Blackcomb',
    'Excalibur / Blackcomb Gondola - Lower': 'Blackcomb',
    'Excelerator / Catskinner / Blackcomb Gondola - Upper': 'Blackcomb',
    'Glacier / Showcase T-bar': 'Blackcomb',
    'Jersey Cream': 'Blackcomb',
    'Big Red / Garbanzo / Village Gondola - Upper': 'Whistler',
    'Creekside': 'Whistler',
    'Emerald / Garbanzo / Village Gondola - Upper': 'Whistler',
    'Fitzsimmons / Whistler Village Gondola - Lower': 'Whistler',
    'Harmony': 'Whistler',
    'Peak / T-bar': 'Whistler',
    'Symphony': 'Whistler',
}

MOUNTAIN_FIX = {'Blakcomb': 'Blackcomb', 'BLackcomb': 'Blackcomb', 'Whsitler': 'Whistler'}
DIFF_FIX = {'Adavnced': 'Advanced', 'Begginer': 'Beginner', 'EXxpert Gladed': 'Expert Gladed'}


def norm(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    s = s.lower().replace('&', ' and ')
    s = re.sub(r"[’'`.]", '', s)
    s = re.sub(r'\s*-\s*', ' - ', s)
    s = re.sub(r'[^a-z0-9 -]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def load_feed(path):
    d = json.loads(Path(path).read_text())
    out = []
    for a in d['GroomingAreas']:
        for t in a['Trails']:
            out.append(dict(t, Area=a['Name']))
    return d, out


def load_gis_runs():
    d = json.loads(GIS_RUNS.read_text())
    runs = []
    for f in d['features']:
        p = dict(f['properties'])
        p['mountain'] = MOUNTAIN_FIX.get(p['mountain'], p['mountain'])
        p['difficulty'] = DIFF_FIX.get(p['difficulty'], p['difficulty'])
        p['trailmap'] = (p.get('trailmap') or '').strip() or None
        p['run_name'] = p['run_name'].strip()
        p['geometry'] = f['geometry']
        runs.append(p)
    return runs


def load_polys(path, name_field='run'):
    d = json.loads(Path(path).read_text())
    return [dict(f['properties'], geometry=f['geometry']) for f in d['features']]
