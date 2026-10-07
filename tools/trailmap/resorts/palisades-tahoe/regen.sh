#!/bin/bash
# Palisades Tahoe: rebuild the app data (src/data/resorts/palisades-tahoe/: one trail list, and per map panel in
# panels/<panel>/ its pieces, proposals, reviews and overlays) from the 2025-26 trail-map PDFs, the maps' reading
# (resort.py, panels/<panel>/resort.py, letters.json) and the naming decisions (panels/<panel>/decisions.py).
# Run from anywhere; working files go to $PALISADES_TAHOE_WORK (default work/palisades-tahoe, git-ignored).
#
#   tools/trailmap/resorts/palisades-tahoe/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/palisades-tahoe/regen.sh   # also rewrite public/maps/palisades-tahoe-*.jpg
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export PALISADES_TAHOE_WORK=${PALISADES_TAHOE_WORK:-$PWD/work/palisades-tahoe}; W=$PALISADES_TAHOE_WORK
mkdir -p "$W"

# 1. the three PDFs (palisadestahoe.com, its trail-maps page): the Palisades side, Alpine's front and back
B=https://www.palisadestahoe.com/-/media/palisades-tahoe/pdfs/trail-maps
[ -f "$W/palisades_main.pdf" ] || curl -sSfL -o "$W/palisades_main.pdf" "$B/palisadesmaintrailmap.pdf?rev=4a11b9e6cc8848bc8fa504fd1ff12139"
[ -f "$W/alpine_front.pdf" ] || curl -sSfL -o "$W/alpine_front.pdf" "$B/alpine-front-side-trail.pdf?rev=d16a1e2f47a24af8991e4924d5f4f7d2"
[ -f "$W/alpine_back.pdf" ] || curl -sSfL -o "$W/alpine_back.pdf" "$B/alpine-back-side-trail.pdf?rev=605e0041d6af471eb74b96978e3b8b46"

# 2. per panel: the map image (the page rendered), line pieces, names and symbols
python3 $T/resorts/palisades-tahoe/prepare.py
if [ -n "$IMAGES" ]; then
  for p in palisades alpine-front alpine-back; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/palisades-tahoe-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py palisades-tahoe
