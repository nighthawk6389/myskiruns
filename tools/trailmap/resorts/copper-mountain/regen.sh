#!/bin/bash
# Copper Mountain: rebuild the app data (src/data/resorts/copper-mountain/) from the 2025-26 trail-map PDF, the glyph
# letter table (letters.json), the naming decisions settled on crops (decisions.py) and the trail list's header
# (header.txt), with the scripts in this folder (see README.md). Run from anywhere; working files go to
# $COPPER_MOUNTAIN_WORK (default work/copper-mountain, git-ignored).
#
#   tools/trailmap/resorts/copper-mountain/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/copper-mountain/regen.sh   # also rewrite public/maps/copper-mountain.jpg
#   FORCE=1 ...                                                # go on with a PDF that is not the recorded edition
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap; C=$T/resorts/copper-mountain; D=src/data/resorts/copper-mountain
export COPPER_MOUNTAIN_WORK=${COPPER_MOUNTAIN_WORK:-$PWD/work/copper-mountain}; W=$COPPER_MOUNTAIN_WORK
mkdir -p "$W"

# 1. the PDF: the 2025-26 main map as exported on 2025-11-06 ("FY26_Main Trail Map_WEB"), kept by skimap.org as map
#    36383 (plain curl works; the view URL redirects to the file). coppercolorado.com now links a re-export of
#    2025-12-17 that is not this file (README.md, "Source"). A copy placed in the work folder by hand is used as is.
SHA=a9a6134263c29bef51e495b9160467da2b2cf0d5b4fe447437b53c04e2cb49bc
if [ ! -f "$W/copper.pdf" ]; then
  curl -sSfL -A 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0' -o "$W/copper.pdf.part" https://skimap.org/skimaps/view/36383
  mv "$W/copper.pdf.part" "$W/copper.pdf"
fi
GOT=$(sha256sum "$W/copper.pdf" | cut -d' ' -f1)
if [ "$GOT" != "$SHA" ]; then
  echo "$W/copper.pdf is not the PDF this data was built from:" >&2
  echo "  SHA-256 $GOT, expected $SHA (2206732 bytes)." >&2
  if [ -z "$FORCE" ]; then
    echo "Another edition renumbers the PDF's drawings (lines.py's skips) and line pieces (decisions.py): see" >&2
    echo "README.md, \"A new season's map\". To go on anyway: FORCE=1 $0" >&2
    exit 1
  fi
  echo "FORCE=1: going on." >&2
fi

# 2. the map image (3911x2708): the PDF's vector layer rendered at 3 px/pt and matted over the embedded painting
#    (xref 258, 1817x1465 px) upscaled with Lanczos, over the map's clip. Its size sets the overlays' percent
#    coordinates, so it is made whenever it is missing.
if [ ! -f "$W/map.png" ] || [ -n "$IMAGES" ]; then
  python3 $T/matte_pdf_layer.py --pdf "$W/copper.pdf" --out "$W/map.png" --scale 3.0 --clip 0,150,1303.44,1052.54 \
    --xref 258 > "$W/matte.log"; cut -c1-120 "$W/matte.log"
fi
if [ -n "$IMAGES" ]; then
  python3 -c "
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
Image.open('$W/map.png').convert('RGB').save('public/maps/copper-mountain.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. the line pieces (centre lines of the outlined trail lines, plus the few plain strokes) -> linePolylines.json,
#    and the numbered tiles (aggregate_readings.py takes the image size from their index)
python3 $C/lines.py > "$W/lines.log"; tail -1 "$W/lines.log"
python3 $T/render_tiles.py --image "$W/map.png" --polylines $D/linePolylines.json --out "$W/tiles"

# 4. the names: glyph fills grouped by shape, each shape's letter (letters.json), joined into labels; the few names
#    set as real text; names set on several lines joined; the difficulty symbols attached
python3 $C/glyphs.py
python3 $C/cluster.py > "$W/cluster.log"; head -1 "$W/cluster.log"
python3 $C/labels.py > "$W/labels.log"; head -1 "$W/labels.log"
python3 $T/pdf_labels.py "$W/copper.pdf" --out "$W/text_raw.json" > /dev/null
python3 $C/names.py > "$W/names.log"; head -2 "$W/names.log"

# 5. each label -> its pieces (automatic match + decisions.py) -> one reading, stretches and markers
python3 $C/build.py > "$W/build.log"
python3 $C/reading.py | tail -3

# 6. the trail list with its header; the pieces' file notes; proposals, Claude's reviews and the overlays
python3 $T/seed_roster.py --readings "$W/tiles/result_copper.json" --areas 'copper-mountain=Copper Mountain=12441' \
  --trails $D/trails.ts --labels "$W/labels.json" > "$W/seed.log"; head -1 "$W/seed.log"
python3 - <<PY
f = '$D/trails.ts'
s = open(f).read()
old = s[s.index('// Seeded'):s.index('export const peaks')]
open(f, 'w').write(s.replace(old, open('$C/header.txt').read()))
PY
python3 - <<PY
import json
exec(open('$C/decisions.py').read())
d = json.load(open('$D/linePolylines.json'))
d['_unnamed'] = {str(k): v for k, v in sorted(UNNAMED.items())}
d['_source'] = ('Copper Mountain 2025-26 main map PDF: centre lines of the outlined trail lines (filled outlines thinned to a '
                 'skeleton and traced between junctions) plus the few drawn as plain strokes; percent of the 3911x2708 map image')
json.dump(d, open('$D/linePolylines.json', 'w'))
PY
python3 $T/aggregate_readings.py --tiles "$W/tiles" --readings "$W/tiles/result_*.json" --roster $D/trails.ts \
  --polylines $D/linePolylines.json --proposals $D/trailProposals.json --review-data "$W/review_data.json" \
  --labels "$W/labels.json" | tail -1
python3 $C/traces.py
rm -f "$W/recheck.json"
python3 $T/traces_to_reviews.py --replace-claude --traces "$W/trace_gaps.json" --reviews $D/trailReviews.json \
  --recheck "$W/recheck.json" --labels "$W/labels.json" --image "$W/map.png" | cut -c1-60
npm run -s trails:apply -- --resort copper-mountain
