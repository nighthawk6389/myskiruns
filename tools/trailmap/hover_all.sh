#!/bin/bash
# The hover check (hover_check.cjs) for every resort and map panel, or the ones given, against a production build
# served the way Vercel serves it (tools/serve_dist.cjs). One line per resort/panel: "<hits>/<points> hover points
# show the right name", plus the misses. Run it after any change to shared app code (the map, src/resorts.ts):
# every resort should keep its previous score.
#
#   tools/trailmap/hover_all.sh                         # build into work/dist-check, check everything
#   tools/trailmap/hover_all.sh vail hunter:            # some resorts (all their panels)
#   tools/trailmap/hover_all.sh vail:back-bowls         # one panel
#   DIST=dist tools/trailmap/hover_all.sh               # an existing build instead of a new one
#
# Needs Playwright (PLAYWRIGHT_PATH, default $(npm root -g)/playwright). The server is stopped by its PID.
set -e
cd "$(dirname "$0")/../.."
PORT=${PORT:-4199}
if [ -z "$DIST" ]; then
  DIST=work/dist-check
  npx vite build --outDir "$DIST" --emptyOutDir > work/dist-check.log 2>&1 || { tail -20 work/dist-check.log; exit 1; }
fi
export PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-$(npm root -g)/playwright}
node tools/serve_dist.cjs "$DIST" "$PORT" > work/serve-dist.log 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
for i in $(seq 1 50); do curl -s -o /dev/null "http://localhost:$PORT/" && break; python3 -c "import time; time.sleep(0.2)"; done

targets=("$@")
[ ${#targets[@]} -eq 0 ] && targets=($(ls src/data/resorts))
for t in "${targets[@]}"; do
  r=${t%%:*}; p=${t#*:}; [ "$p" = "$t" ] && p=
  if [ -n "$p" ]; then panels=("$p")
  elif [ -d "src/data/resorts/$r/panels" ]; then panels=($(ls "src/data/resorts/$r/panels"))
  else panels=(""); fi
  for p in "${panels[@]}"; do
    out=$(node tools/trailmap/hover_check.cjs "http://localhost:$PORT/" --resort "$r" ${p:+--panel "$p"} 2>&1 || true)
    echo "== $r${p:+ $p}: $(echo "$out" | head -1)"
    echo "$out" | sed -n '2,6p' | sed 's/^/     /'
  done
done
