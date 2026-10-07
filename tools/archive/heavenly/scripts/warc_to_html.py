"""Split one uncompressed WARC response record into its HTTP headers and body.

Common Crawl's crawler stores the decoded payload (original Content-Encoding is
kept as X-Crawler-content-encoding), so the body is the page's HTML as served.
Handles a chunked body too, in case Transfer-Encoding was kept.

Usage: python3 -I warc_to_html.py <record.warc> <out.html>
"""
import sys
from pathlib import Path


def dechunk(body):
    out = bytearray()
    i = 0
    while True:
        j = body.find(b'\r\n', i)
        if j < 0:
            break
        size = int(body[i:j].split(b';')[0].strip() or b'0', 16)
        if size == 0:
            break
        out += body[j + 2:j + 2 + size]
        i = j + 2 + size + 2
    return bytes(out)


def main():
    raw = Path(sys.argv[1]).read_bytes()
    warc_end = raw.index(b'\r\n\r\n')
    warc_headers = raw[:warc_end].decode('utf-8', 'replace')
    http = raw[warc_end + 4:]
    http_end = http.index(b'\r\n\r\n')
    http_headers = http[:http_end].decode('utf-8', 'replace')
    body = http[http_end + 4:]
    hl = http_headers.lower()
    if 'transfer-encoding: chunked' in hl and 'x-crawler-transfer-encoding' not in hl:
        body = dechunk(body)
    # Trim the WARC record's trailing CRLFs, if present.
    body = body.rstrip(b'\r\n') + b'\n'
    Path(sys.argv[2]).write_bytes(body)
    status = http_headers.splitlines()[0]
    uri = next((l.split(':', 1)[1].strip() for l in warc_headers.splitlines()
                if l.lower().startswith('warc-target-uri:')), '?')
    date = next((l.split(':', 1)[1].strip() for l in warc_headers.splitlines()
                 if l.lower().startswith('warc-date:')), '?')
    print(f'{uri} {date} {status!r} body={len(body)} bytes -> {sys.argv[2]}')


if __name__ == '__main__':
    main()
