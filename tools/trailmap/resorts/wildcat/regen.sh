#!/bin/bash
# Wildcat Mountain: rebuild the app data (src/data/resorts/wildcat/) from the trail-map sources, the map's reading
# (resort.py) and the naming decisions (decisions.py). Run from anywhere; working files go to $WILDCAT_WORK
# (default work/wildcat, git-ignored).
#
#   tools/trailmap/resorts/wildcat/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/wildcat/regen.sh   # also rewrite public/maps/wildcat.jpg
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -e
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export WILDCAT_WORK=${WILDCAT_WORK:-$PWD/work/wildcat}; W=$WILDCAT_WORK
mkdir -p "$W"

# 1. sources: the artwork with live strokes and text (skimap.org map 33684), and the 2025-26 page as an image
#    from Vail Resorts' CDN (plain curl works there). The 2025-26 PDF itself (outlined names, flattened lines) is
#    only needed to re-check the registration: tools/trailmap/fetch_pdf.cjs (skiwildcat.com refuses curl).
[ -f "$W/wildcat_text.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/wildcat_text.pdf" \
  https://files.skimap.org/w18ct5ihtid1a6eekf9icq9qaqtj.pdf
[ -f "$W/scene7.png" ] || curl -sSf -o "$W/scene7.png" \
  "https://scene7.vailresorts.com/is/image/vailresorts/20251226_WC_winter-trail_map_001?fmt=png-alpha&wid=3575&qlt=100"

# 2. the map image (the painting down to the legend bar), the trail lines (3.27 pt strokes in the three trail
#    colours; the green FIRST AID CENTER lettering is left out), the names (text) and the symbols, all on the
#    image's grid: 3.380039 px per pt of the export, whose page is the 2025-26 page plus 23.77 pt of bleed
CLIP=23.77,23.77,1081.45,1182
python3 -c "
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
Image.open('$W/scene7.png').convert('RGB').crop((0, 0, 3575, 3915)).save('$W/map.png')"
python3 $T/extract_pdf_vectors.py "$W/wildcat_text.pdf" --clip $CLIP --scale 3.380039 --color green=0.16,0.64,0.26 \
  --color blue=0.09,0.52,0.75 --color black=0,0,0 --min-width 3 --max-width 3.5 --min-length 0.8 \
  --exclude 460,1020,570,1090 --out "$W/pieces.json"
python3 $T/pdf_labels.py "$W/wildcat_text.pdf" --out "$W/printed.json" > /dev/null
python3 $T/pdf_symbols.py "$W/wildcat_text.pdf" --clip $CLIP --scale 3.380039 --circle 0.16,0.64,0.26 \
  --square 0.09,0.52,0.75 --diamond 0,0,0 --max-size 16 --max-diamond 11.5 --out "$W/symbols.json"
if [ -n "$IMAGES" ]; then  # saved at 3200 px wide (3.5 MB): overlays are in percent of the image
  python3 -c "
from PIL import Image
im = Image.open('$W/map.png')
im.resize((3200, round(im.height * 3200 / im.width)), Image.LANCZOS).save('public/maps/wildcat.jpg', quality=82, optimize=True, progressive=True)"
fi

# 3. name every piece, then the trail list, proposals, Claude's reviews and the overlays
python3 $T/pdf_resort.py wildcat
