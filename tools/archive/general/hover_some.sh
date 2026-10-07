#!/bin/bash
# hover_some.sh RESORT[:PANEL]... : serve dist-hover on 4199, hover-check each, stop the server by PID
cd /home/user/myskiruns
S=/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad
node $S/offline/serve.cjs $S/dist-hover 4199 > $S/hover-server.log 2>&1 &
SP=$!
for i in $(seq 1 50); do curl -s -o /dev/null http://localhost:4199/ && break; python3 -c "import time; time.sleep(0.2)"; done
export PLAYWRIGHT_PATH=$(npm root -g)/playwright
for a in "$@"; do
  r=${a%%:*}; p=${a#*:}
  if [ "$p" = "$a" ]; then
    echo "== $r $(node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort $r 2>&1 | head -3 | tr '\n' ' ')"
  else
    echo "== $r $p $(node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort $r --panel $p 2>&1 | head -3 | tr '\n' ' ')"
  fi
done
kill $SP 2>/dev/null
exit 0
