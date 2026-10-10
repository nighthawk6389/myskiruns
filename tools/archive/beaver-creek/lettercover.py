import json, sys, importlib.util
spec = importlib.util.spec_from_file_location('pg', 'tools/trailmap/pdf_glyphs.py'); pg = importlib.util.module_from_spec(spec); spec.loader.exec_module(pg)
g = json.load(open(sys.argv[1]))
for f in sys.argv[2:]:
    table = [t for t in json.load(open(f)) if 'size' in t and 'kinds' in t]
    n = sum(1 for x in g['glyphs'] ); hit = sum(1 for x in g['glyphs'] if pg.letter(table, x))
    print(f, hit, '/', n)
