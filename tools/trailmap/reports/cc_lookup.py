"""Look up a URL in a Common Crawl crawl without the (flaky) index server.

Binary-searches the crawl's sorted cluster.idx with HTTP range requests, downloads the
matching CDX block(s), and optionally fetches the WARC records of matching captures.

Usage: python3 -I cc_lookup.py <crawl-id> <surt-prefix> <outdir> [--fetch]
"""
import gzip
import io
import json
import subprocess
import sys
from pathlib import Path

BASE = 'https://data.commoncrawl.org'


def get_range(url, start, end):
    for attempt in range(4):
        r = subprocess.run(
            ['curl', '-sS', '-f', '-m', '120', '-r', f'{start}-{end}', url],
            capture_output=True,
        )
        if r.returncode == 0:
            return r.stdout
    raise RuntimeError(f'range fetch failed: {url} {start}-{end}: {r.stderr[:200]!r}')


def content_length(url):
    r = subprocess.run(['curl', '-sS', '-I', '-m', '60', url], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.lower().startswith('content-length:'):
            return int(line.split(':', 1)[1])
    raise RuntimeError('no content-length')


def line_at(url, pos, size):
    """Return (line_start, line_text) for the first full line starting at or after pos."""
    chunk = get_range(url, pos, min(size - 1, pos + 65535))
    if pos == 0:
        i = 0
    else:
        i = chunk.find(b'\n') + 1
    j = chunk.find(b'\n', i)
    return pos + i, chunk[i:j].decode('utf-8', 'replace')


def main():
    crawl, prefix, outdir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    fetch = '--fetch' in sys.argv
    outdir.mkdir(parents=True, exist_ok=True)
    idx_url = f'{BASE}/cc-index/collections/{crawl}/indexes/cluster.idx'
    size = content_length(idx_url)
    lo, hi = 0, size - 1
    # Binary search for the last line whose key < prefix.
    best = 0
    while hi - lo > 65536:
        mid = (lo + hi) // 2
        start, text = line_at(idx_url, mid, size)
        key = text.split(' ', 1)[0]
        if key < prefix:
            lo = mid
            best = start
        else:
            hi = mid
    window = get_range(idx_url, best, min(size - 1, hi + 200000)).decode('utf-8', 'replace').splitlines()
    blocks = []
    prev = None
    for line in window:
        if not line.strip():
            continue
        key = line.split(' ', 1)[0]
        if key < prefix:
            prev = line
            continue
        if prev is not None and not blocks:
            blocks.append(prev)
        if key.startswith(prefix) or not blocks:
            blocks.append(line)
            if not key.startswith(prefix):
                break
        else:
            break
    if not blocks and prev:
        blocks.append(prev)
    hits = []
    for b in blocks:
        _, rest = b.split(' ', 1)
        parts = rest.split('\t')
        cdx_file, off, length = parts[1], int(parts[2]), int(parts[3])
        data = get_range(f'{BASE}/cc-index/collections/{crawl}/indexes/{cdx_file}', off, off + length - 1)
        for line in gzip.decompress(data).decode('utf-8', 'replace').splitlines():
            if line.startswith(prefix):
                surt, ts, js = line.split(' ', 2)
                rec = json.loads(js)
                rec['surt'] = surt
                rec['timestamp'] = ts
                hits.append(rec)
    seen = set()
    uniq = []
    for h in hits:
        k = (h['timestamp'], h['url'], h.get('digest'))
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    (outdir / f'{crawl}_cdx.json').write_text(json.dumps(uniq, indent=1))
    for h in uniq:
        print(crawl, h['timestamp'], h.get('status'), h.get('mime'), h.get('length'), h['url'][:140])
    if fetch:
        for h in uniq:
            if h.get('status') != '200':
                continue
            off, length = int(h['offset']), int(h['length'])
            raw = get_range(f"{BASE}/{h['filename']}", off, off + length - 1)
            rec = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
            fn = outdir / f"{crawl}_{h['timestamp']}.warc"
            fn.write_bytes(rec)
            print('saved', fn, len(rec))


if __name__ == '__main__':
    main()
