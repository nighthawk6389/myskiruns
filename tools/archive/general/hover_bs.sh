#!/bin/bash
cd /home/user/myskiruns
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad
node $S/offline/serve.cjs $S/dist-hover 4199 > $S/hover-server.log 2>&1 &
SP=$!
for i in $(seq 1 50); do curl -s -o /dev/null http://localhost:4199/ && break; python3 -c "import time; time.sleep(0.2)"; done
export PLAYWRIGHT_PATH=$(npm root -g)/playwright
for p in main south-face bowl; do
  echo "== $p"
  node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort big-sky --panel $p 2>&1 | tail -15
done
kill $SP
