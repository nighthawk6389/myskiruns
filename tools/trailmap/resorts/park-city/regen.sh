#!/bin/bash
# Park City Mountain: rebuild the app data (src/data/resorts/park-city/) from the trail-map PDF, the map's reading
# (resort.py, letters.json) and the naming decisions (decisions.py). Run from anywhere; working files go to
# $PARK_CITY_WORK (default work/park-city, git-ignored).
#
#   tools/trailmap/resorts/park-city/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/park-city/regen.sh   # also rewrite public/maps/park-city.jpg
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export PARK_CITY_WORK=${PARK_CITY_WORK:-$PWD/work/park-city}; W=$PARK_CITY_WORK
mkdir -p "$W"

# 1. the PDF (parkcitymountain.com returns an error page to curl: fetch it from inside its trail-map page)
[ -f "$W/parkcity.pdf" ] || PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs \
  https://www.parkcitymountain.com/the-mountain/about-the-mountain/trail-map.aspx \
  https://www.parkcitymountain.com/-/aemasset/sitecore/park-city/maps/20251114_PC_winter-trail_map_001.pdf \
  "$W/parkcity.pdf"

# 2. the map image (the page with its paintings upscaled), the line pieces, names and symbols (prepare.py)
python3 $T/resorts/park-city/prepare.py
if [ -n "$IMAGES" ]; then
  python3 -c "from PIL import Image; Image.MAX_IMAGE_PIXELS = None; Image.open('$W/map.png').convert('RGB').save('public/maps/park-city.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py park-city
