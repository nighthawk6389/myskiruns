#!/bin/bash
# Whiteface's crop audit: the 11 full-resolution regions every overlay was checked on (each drawn in its own colour
# and tagged with its name; tools/trailmap/region_audit.py), as on 2026-09-30. Run regen.sh first (it makes
# $WHITEFACE_WORK/map.png); writes $WHITEFACE_WORK/regions/r<k>_<x>_<y>.jpg.
#
#   tools/trailmap/resorts/whiteface/checks/audit.sh
set -eo pipefail
cd "$(dirname "$0")/../../../../.."
W=${WHITEFACE_WORK:-$PWD/work/whiteface}
rm -rf "$W/regions"
python3 tools/trailmap/region_audit.py --image "$W/map.png" --paths src/data/resorts/whiteface/trailPaths.json \
  --trails src/data/resorts/whiteface/trails.ts --out "$W/regions" --box 1300,450,2000,1000 \
  --box 1950,450,2650,1100 --box 2600,420,3550,1450 --box 1250,950,1800,1500 --box 1750,950,2350,1500 \
  --box 1150,1450,1750,2050 --box 1700,1450,2250,2000 --box 1300,1950,1900,2700 --box 1850,1950,2550,2700 \
  --box 550,2050,1350,2850 --box 2300,1350,3450,2300
ls "$W/regions"
