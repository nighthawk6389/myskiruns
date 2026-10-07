#!/bin/bash
# Big Sky: rebuild the app data (src/data/resorts/big-sky/: one trail list, and per map panel in panels/<panel>/
# its pieces, proposals, reviews and overlays) from the 2025-26 trail-map PDFs, the maps' reading (resort.py,
# report.json, panels/<panel>/resort.py) and the naming decisions (panels/<panel>/decisions.py).
# Run from anywhere; working files go to $BIG_SKY_WORK (default work/big-sky, git-ignored).
#
#   tools/trailmap/resorts/big-sky/regen.sh            # data only
#   IMAGES=1 tools/trailmap/resorts/big-sky/regen.sh   # also rewrite public/maps/big-sky-*.jpg
#   FORCE=1 ...                                        # go on although a source's SHA-256 differs (a new edition)
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

# the files this data was built from: another file (a new edition) stops the rebuild until its decisions are
# checked (docs/trail-map-playbook.md, "A new season's map"); FORCE=1 runs on it anyway
check() {
  local s; s=$(sha256sum "$1" | cut -d' ' -f1); [ "$s" = "$2" ] && return 0
  echo "$1: SHA-256 $s, not $2 (the file this data was built from). A new edition needs its decisions" \
    "checked first (docs/trail-map-playbook.md, \"A new season's map\"); FORCE=1 runs on it anyway." >&2
  [ -n "$FORCE" ] || exit 1
}
check "$W/bigsky_main.pdf" 869d819c2363cc7dfb4dfa01c6c435c2c5812285c3d5a5501512522bd99c14be  # 1949422 bytes
check "$W/bigsky_south-face.pdf" d76ff50995a86b155ff2bfa6ebda7e7b114ac7d0a3e905e2a846a1d622832d83  # 939014 bytes
check "$W/bigsky_bowl.pdf" cc96539aead2e6e36ed1048978b67d487e6f403ff58d3a21f88944c241e30256  # 683124 bytes

# 2. per panel: the map image (the page rendered over an upscaled painting), line pieces, names and symbols
python3 $T/resorts/big-sky/prepare.py
if [ -n "$IMAGES" ]; then
  for p in main south-face bowl; do
    python3 -c "from PIL import Image; Image.open('$W/$p/map.png').convert('RGB').save('public/maps/big-sky-$p.jpg', quality=82, optimize=True, progressive=True)"
  done
fi

# 3. name every piece of every panel, then the trail list, and per panel the proposals, Claude's reviews and overlays
python3 $T/pdf_resort.py big-sky
