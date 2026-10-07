#!/bin/bash
# Usage: cc_query.sh <url-pattern> <outfile> <collection>...
# Queries Common Crawl CDX indexes for a URL pattern (with retries), appending JSON lines to outfile.
pat="$1"; out="$2"; shift 2
: > "$out"
for c in "$@"; do
  for attempt in 1 2 3 4 5; do
    code=$(curl -sS -m 120 -G "https://index.commoncrawl.org/${c}-index" \
      --data-urlencode "url=${pat}" --data-urlencode "output=json" \
      -o "$out.tmp" -w "%{http_code}" 2>/dev/null)
    if [ "$code" = "200" ] || [ "$code" = "404" ]; then break; fi
    sleep_s=$((attempt * 4)); timeout $sleep_s tail -f /dev/null 2>/dev/null
  done
  n=$( [ -s "$out.tmp" ] && wc -l < "$out.tmp" || echo 0)
  echo "$c http=$code lines=$n attempts=$attempt"
  if [ "$code" = "200" ]; then cat "$out.tmp" >> "$out"; fi
  rm -f "$out.tmp"
done
