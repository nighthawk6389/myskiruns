"""Replace lines of the reading notes during the audit (they were kept as front_lines.txt and mineral_lines.txt, joined
into reading/lines.txt): fix_lines.py NAME 'waypoints' [NAME 'waypoints' ...] (an unknown NAME is added)."""
import sys
pairs = list(zip(sys.argv[1::2], sys.argv[2::2]))
for f in ('front_lines.txt', 'mineral_lines.txt'):
    s = open(f).read().split('\n')
    out = []
    for l in s:
        n = l.split(' | ')[0] if ' | ' in l else None
        hit = next((p for p in pairs if p[0] == n), None)
        if hit:
            l = f'{hit[0]} | {hit[1]}'
            pairs.remove(hit)
        out.append(l)
    open(f, 'w').write('\n'.join(out))
for n, w in pairs:  # new ones
    open('front_lines.txt', 'a').write(f'\n{n} | {w}')
    print('added', n)
