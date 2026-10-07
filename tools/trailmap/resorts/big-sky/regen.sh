#!/bin/bash
# Big Sky: rebuild the app data (src/data/resorts/big-sky/: one trail list, and per map panel in panels/<panel>/
# its pieces, proposals, reviews and overlays) from the 2025-26 trail-map PDFs, the maps' reading (resort.py,
# report.json, panels/<panel>/resort.py) and the naming decisions (panels/<panel>/decisions.py).
# Run from anywhere; working files go to $BIG_SKY_WORK (default work/big-sky, git-ignored).
#
#   tools/trailmap/resorts/big-sky/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/big-sky/regen.sh   # also rewrite public/maps/big-sky-*.jpg
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export BIG_SKY_WORK=${BIG_SKY_WORK:-$PWD/work/big-sky}; W=$BIG_SKY_WORK
mkdir -p "$W"

# 1. the three PDFs (bigskyresort.com, its trail-maps page; files named by their SHA-1): the main map and its two
#    insets, the South Face and the Bowl
B=https://cdn.sanity.io/files/8ts88bij/big-sky
[ -f "$W/bigsky_main.pdf" ] || curl -sSfL -o "$W/bigsky_main.pdf" "$B/ddf76f88c4374aaef2f4249269e0eda706516f02.pdf"
[ -f "$W/bigsky_south-face.pdf" ] || curl -sSfL -o "$W/bigsky_south-face.pdf" "$B/cf39b98f33826917774e36d08618a0df4df12b7b.pdf"
[ -f "$W/bigsky_bowl.pdf" ] || curl -sSfL -o "$W/bigsky_bowl.pdf" "$B/6f495c2b95fb75491d486408a3276bd4d94ca342.pdf"

# 2. per panel: the map image (the page rendered over an upscaled painting), line pieces, names and symbols
python3 $T/resorts/big-sky/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main south-face bowl; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/big-sky-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py big-sky
