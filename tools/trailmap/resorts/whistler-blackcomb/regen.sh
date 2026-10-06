#!/bin/bash
# Whistler Blackcomb: rebuild the app data (src/data/resorts/whistler-blackcomb/: one trail list, and per map
# panel in panels/<panel>/ its pieces, proposals, reviews and overlays) from the 2025-26 trail-map PDF, the map's
# reading (resort.py, panels/<panel>/resort.py, letters.json) and the naming decisions (panels/<panel>/decisions.py).
# Run from anywhere; working files go to $WHISTLER_BLACKCOMB_WORK (default work/whistler-blackcomb, git-ignored).
#
#   tools/trailmap/resorts/whistler-blackcomb/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/whistler-blackcomb/regen.sh   # also rewrite public/maps/whistler-blackcomb-*.jpg
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export WHISTLER_BLACKCOMB_WORK=${WHISTLER_BLACKCOMB_WORK:-$PWD/work/whistler-blackcomb}; W=$WHISTLER_BLACKCOMB_WORK
mkdir -p "$W"

# 1. the PDF (whistlerblackcomb.com returns an error page to curl: fetch it from inside its trail-map page)
[ -f "$W/whistler.pdf" ] || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
  https://www.whistlerblackcomb.com/the-mountain/about-the-mountain/trail-maps.aspx \
  https://www.whistlerblackcomb.com/-/aemasset/sitecore/whistler-blackcomb/maps/winter-2025-2026/20251023_WB_winter-trail_map_001.pdf \
  "$W/whistler.pdf"

# 2. per panel: the map image (the vector layer over the upscaled painting), line pieces, names and symbols
python3 $T/resorts/whistler-blackcomb/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main symphony glacier; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/whistler-blackcomb-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py whistler-blackcomb
