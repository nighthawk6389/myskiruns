"""letters_fit.py <glyphs.json>: how many of a new map's glyphs each resort's letters.json already reads (a font met before?)."""
import glob, json, sys
sys.path.insert(0, 'tools/trailmap')
import pdf_glyphs as P
g = json.load(open(sys.argv[1]))
for f in sorted(glob.glob('tools/trailmap/resorts/*/letters.json') + glob.glob('tools/trailmap/resorts/*/panels/*/letters.json')):
    t = json.load(open(f))
    hit = sum(1 for x in g['glyphs'] if P.letter(t, x))
    print(f'{hit:5d}/{len(g["glyphs"])} {f}')
