"""Alta's trail report from its lift and terrain status page (https://www.alta.com/lift-terrain-status, plain curl):
the page sets `window.Alta = {...}` with every lift and its runs (name, difficulty, status), out of season too.
Writes report.json rows [name, lift, rating] in the page's order (the rating as the other resorts' reports give it:
Green, Blue, Black).

    python3 -I tools/trailmap/resorts/alta/status_report.py page.html --source "..." --out report.json
"""
import argparse
import html
import json
import re


def window_alta(s):
    """The object assigned to window.Alta (a JSON literal: the braces balanced, strings skipped)."""
    i = s.index('window.Alta')
    i = s.index('{', i)
    depth, j, quote = 0, i, False
    while True:
        ch = s[j]
        if quote:
            if ch == '\\':
                j += 1
            elif ch == '"':
                quote = False
        elif ch == '"':
            quote = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if not depth:
                return json.loads(s[i:j + 1])
        j += 1


RATING = {'beginner': 'Green', 'easiest': 'Green', 'green': 'Green', 'intermediate': 'Blue', 'blue': 'Blue',
          'more difficult': 'Blue', 'advanced': 'Black', 'expert': 'Black', 'black': 'Black', 'most difficult': 'Black'}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('page')
    ap.add_argument('--source', default='')
    ap.add_argument('--out')
    a = ap.parse_args()
    d = window_alta(open(a.page, encoding='utf-8').read())
    rows = []

    def walk(o, lift=None):
        if isinstance(o, dict):
            name = o.get('name')
            if name and ('difficulty' in o or 'trail_difficulty' in o or 'difficulty_id' in o):
                diff = o.get('difficulty') or o.get('trail_difficulty')
                diff = diff.get('name') if isinstance(diff, dict) else diff
                rows.append([html.unescape(name).strip(), lift or '', RATING.get(str(diff).lower(), str(diff))])
                return
            here = html.unescape(o['name']).strip() if o.get('name') and ('runs' in o or 'trails' in o) else lift
            for v in o.values():
                walk(v, here)
        elif isinstance(o, list):
            for v in o:
                walk(v, lift)
    walk(d)
    seen, out = set(), []
    for r in rows:
        if tuple(r) not in seen:
            seen.add(tuple(r))
            out.append(r)
    print(len(out), 'runs;', sorted({r[1] for r in out}), sorted({r[2] for r in out}))
    if a.out:
        json.dump({'_source': a.source, 'trails': out}, open(a.out, 'w'), indent=1, ensure_ascii=False)
        print('->', a.out)
    else:
        for r in out:
            print(r)


if __name__ == '__main__':
    main()
