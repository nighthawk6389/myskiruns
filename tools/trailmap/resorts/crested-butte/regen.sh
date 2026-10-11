#!/bin/bash
# Crested Butte: rebuild the app data (src/data/resorts/crested-butte/: one trail list, and per map panel in
# panels/<panel>/ its pieces, proposals, reviews and overlays) from the 2025-26 trail map PDF, the 2022-23 PDF's
# sharper copy of the same painting, the map's reading (resort.py, panels/<panel>/resort.py, letters.json,
# teocalli_letters.json, report.json) and the naming decisions (panels/<panel>/decisions.py). Run from anywhere;
# working files go to $CRESTED_BUTTE_WORK (default work/crested-butte, git-ignored).
#
#   tools/trailmap/resorts/crested-butte/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/crested-butte/regen.sh   # also rewrite public/maps/crested-butte-*.jpg
#   FORCE=1 ...                                              # go on although a source's SHA-256 differs (a new edition)
#
# A person's reviews in trailReviews.json are kept; Claude's ("by": "claude") are rebuilt, keeping their
# timestamps when nothing changed.
set -eo pipefail
cd "$(dirname "$0")/../../../.."
T=tools/trailmap
export CRESTED_BUTTE_WORK=${CRESTED_BUTTE_WORK:-$PWD/work/crested-butte}; W=$CRESTED_BUTTE_WORK
mkdir -p "$W"

# 1. the sources: this season's trail map PDF (skicb.com's trail-maps page; Vail Resorts' sites refuse curl, so it
# is fetched from inside the page; skimap.org's map 36782 is the same file), and the 2022-23 PDF (skimap.org's map
# 23099), whose painting is the same at 269 dpi
if [ ! -f "$W/crested-butte_2025-26.pdf" ]; then
  curl -sSfL -A 'Mozilla/5.0' -o "$W/crested-butte_2025-26.pdf" 'https://skimap.org/skimaps/view/36782' ||
    PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright} node $T/fetch_pdf.cjs 'https://www.skicb.com/the-mountain/about-the-mountain/trail-maps.aspx' \
      'https://www.skicb.com/-/aemasset/sitecore/crested-butte/maps/winter-2025-2026/20251103_CB_winter-trail_map_001.pdf' \
      "$W/crested-butte_2025-26.pdf"
fi
[ -f "$W/crested-butte_2022-23.pdf" ] || curl -sSfL -A 'Mozilla/5.0' -o "$W/crested-butte_2022-23.pdf" \
  'https://skimap.org/skimaps/view/23099'

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are checked
# (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/crested-butte_2025-26.pdf" 2abcca154d1286c27ce188108d3f5cfe0939cf41427c081f65c06b965ca4d2d6  # 12754648 bytes
check "$W/crested-butte_2022-23.pdf" 707cd12b281b1d22de0a17d539549cb398d632a436acfc43efca7563156b353c  # 51542890 bytes

# 2. per panel: the map image, the line pieces, the names and the symbols (prepare.py)
python3 $T/resorts/crested-butte/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main teocalli-bowls; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/crested-butte-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py crested-butte
