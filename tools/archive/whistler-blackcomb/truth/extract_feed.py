"""Extract every `<Name> = {json}` assignment for TerrainStatusFeed-like variables from an HTML file.

Usage: python3 -I extract_feed.py <page.html> <outdir>
"""
import json
import re
import sys
from pathlib import Path


def extract_json_at(text, start):
    """Return the JSON object text starting at text[start] == '{' using brace matching aware of strings."""
    depth = 0
    i = start
    in_str = False
    esc = False
    while i < len(text):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    return None


def main():
    html = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    for k, m in enumerate(re.finditer(r'([A-Za-z_.$]*(?:Feed|Status|Data)[A-Za-z_]*)\s*=\s*\{', html)):
        name = m.group(1)
        start = m.end() - 1
        js = extract_json_at(html, start)
        if not js:
            continue
        try:
            obj = json.loads(js)
        except Exception as e:
            print(f'{k} {name}: not JSON ({e}); len={len(js)}')
            continue
        fn = outdir / f'feed_{k:02d}_{re.sub(r"[^A-Za-z0-9]", "_", name)}.json'
        fn.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding='utf-8')
        keys = list(obj.keys()) if isinstance(obj, dict) else type(obj)
        print(f'{k} {name}: len={len(js)} keys={keys} -> {fn.name}')


if __name__ == '__main__':
    main()
