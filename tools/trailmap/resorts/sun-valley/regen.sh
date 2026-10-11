#!/bin/bash
# Sun Valley: rebuild the app data (src/data/resorts/sun-valley/) from this season's Bald Mountain and Dollar Mountain
# map images (sunvalley.com: each a PDF holding one picture), the 2023-24 vector exports of both artworks
# (skimap.org), the maps' reading (resort.py, panels/*/resort.py, letters.json, report.json) and the naming decisions
# (panels/*/decisions.py). Run from anywhere; working files go to $SUN_VALLEY_WORK (default work/sun-valley).
#
#   tools/trailmap/resorts/sun-valley/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/sun-valley/regen.sh   # also rewrite public/maps/sun-valley-<panel>.jpg
#   FORCE=1 ...                                           # go on although a source's SHA-256 differs (a new edition)
#
# report.json is the interactive maps' trail list (report_ml.py, from mountain.live's staticPoiData); it is kept, not
# refetched. A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export SUN_VALLEY_WORK=${SUN_VALLEY_WORK:-$PWD/work/sun-valley}; W=$SUN_VALLEY_WORK
mkdir -p "$W"

# 1. the sources (plain curl): this season's maps (sunvalley.com's trail-maps page) and the 2023-24 exports
#    (skimap.org maps 24666, Bald, and 24667, Dollar)
[ -f "$W/baldy_2627.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/baldy_2627.pdf" \
  https://www.sunvalley.com/getmedia/a75ad925-ada1-4ffe-ae8a-7dcf6840b228/2627_SV_Baldy_Map_26-27_2580X1456.pdf
[ -f "$W/dollar_2627.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/dollar_2627.pdf" \
  https://www.sunvalley.com/getmedia/07905a95-1b12-4af8-9b56-abcdace12d49/2627_SV_Dollar_Map_26-27_5002X2000.pdf
[ -f "$W/baldy_2023.pdf" ] || curl -sSfL -o "$W/baldy_2023.pdf" https://skimap.org/skimaps/view/24666
[ -f "$W/dollar_2023.pdf" ] || curl -sSfL -o "$W/dollar_2023.pdf" https://skimap.org/skimaps/view/24667

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/baldy_2627.pdf" 91bebbc5e29bffe52fab969810ebc040c1d0f2a07ca0391e13ab83db36f54770  # 3813909 bytes
check "$W/dollar_2627.pdf" fcaea36236e789e6061ee6f7af126740bc431bddebac1ac3a765b1a8544ae31c  # 2373757 bytes
check "$W/baldy_2023.pdf" f4047f3dfe84cd49464fe017701603a7502f6487a58876afc67044aeb0d67a30  # 10947356 bytes
check "$W/dollar_2023.pdf" b9773cf37321bfae9587eac40a76207611fa675b861aa4ca7cc408c84f644d84  # 2556099 bytes

# 2. this season's images, then per panel the image, the line pieces, the names and the symbols (prepare.py)
for f in baldy_2627 dollar_2627; do
  [ -f "$W/$f.png" ] || python3 -I $T/extract_pdf_image.py "$W/$f.pdf" "$W/$f.png" > /dev/null
done
python3 $T/resorts/sun-valley/prepare.py
if [ -n "$IMAGES" ]; then
  for p in bald-mountain dollar-mountain; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/sun-valley-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py sun-valley
