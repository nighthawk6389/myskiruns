"""Trail-name labels straight from a trail-map PDF's text (Whiteface and
Winter Park print every name as real text).

    python3 tools/trailmap/pdf_labels.py map.pdf --out work/pdf_labels.json \\
        --glyph 316=- --glyph '63=‘'

One label per text object: {seq, text, color, font, size, c, pts} in PDF
points, c the centre of its characters and pts each character's centre in
reading order (match names to the lines they are printed along or at the
end of; draw label-gap stretches along them). An object that holds a second,
identical copy of its text (a halo pass) is cut to one copy, one that holds
two names far apart is split, and the spaces the PDF leaves out are put back
from the character spacing. Keep the trail-name font, size and colours (the
legend's) and drop the rest.

Fonts with no Unicode map (Winter Park's name font): pymupdf reports U+FFFD
and each glyph's index in the subset; the subset's CFF charset names the
glyph `gidNNNNN`, its index in the full font, which in the usual Adobe order
is space 1, 0-9 17-26, A-Z 34-59 and a-z 66-91. Give any other glyph with
--glyph N=char after checking it on a rendered label; unknown ones print as
{N}.

Requires: pip install pymupdf fonttools
"""
import argparse
import collections
import io
import json
import math

import pymupdf


def gid_char(k, extra):
    if k in extra:
        return extra[k]
    if k == 1:
        return ' '
    if k == 8:
        return '’'
    if 17 <= k <= 26:
        return chr(ord('0') + k - 17)
    if 34 <= k <= 59:
        return chr(ord('A') + k - 34)
    if 66 <= k <= 91:
        return chr(ord('a') + k - 66)
    return '{%d}' % k


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--glyph', action='append', default=[], help='N=char: full-font glyph index N prints as char')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    extra = {int(k): v for k, v in (g.split('=', 1) for g in a.glyph)}

    doc = pymupdf.open(a.pdf)
    page = doc[a.page]
    charsets = {}
    for xref, ext, _typ, name, *_ in page.get_fonts(full=True):
        if ext == 'cff':
            from fontTools.cffLib import CFFFontSet
            cff = CFFFontSet()
            cff.decompile(io.BytesIO(doc.extract_font(xref)[3]), None)
            charsets[name.split('+')[-1]] = cff[cff.fontNames[0]].charset

    chars = collections.defaultdict(list)
    meta = {}
    for s in page.get_texttrace():
        cs = next((v for n, v in charsets.items() if n.startswith(s['font'])), None)
        meta.setdefault(s['seqno'], ([round(x, 2) for x in s['color']], s['font'], round(s['size'], 1)))
        for c in s['chars']:
            ch = chr(c[0])
            if c[0] == 0xFFFD and cs and c[1] < len(cs) and cs[c[1]].startswith('gid'):
                ch = gid_char(int(cs[c[1]][3:]), extra)
            chars[s['seqno']].append((ch, tuple(c[3]), tuple(c[2])))

    out = []
    for seq, cl in chars.items():
        color, font, size = meta[seq]
        n = len(cl)
        if n % 2 == 0 and all(cl[i][0] == cl[i + n // 2][0] and math.dist(cl[i][2], cl[i + n // 2][2]) < 0.5
                              for i in range(n // 2)):
            cl = cl[: n // 2]  # the same text drawn twice in one object
        parts, cur, prev = [], [], None
        for ch, box, origin in cl:
            if not ch.strip():
                if cur:
                    cur.append((' ', box, origin))
                continue
            if prev is not None:
                gap = math.dist(origin, prev[2])  # origin to origin
                adv = math.dist(prev[1][:2], prev[1][2:]) * 0.7
                if gap > 1.65 * size + adv:
                    parts.append(cur)  # far apart: another name
                    cur = []
                elif cur and cur[-1][0] != ' ' and gap > 0.75 * size and gap > 1.3 * adv:
                    cur.append((' ', box, origin))  # a word gap the PDF left out
            cur.append((ch, box, origin))
            prev = (ch, box, origin)
        if cur:
            parts.append(cur)
        for part in parts:
            boxes = [b for ch, b, _ in part if ch.strip()]
            if not boxes:
                continue
            pts = [[round((b[0] + b[2]) / 2, 1), round((b[1] + b[3]) / 2, 1)] for b in boxes]
            out.append({'seq': seq, 'text': ' '.join(''.join(ch for ch, _, _ in part).split()), 'color': color,
                        'font': font, 'size': size, 'pts': pts,
                        'c': [round(sum(q[0] for q in pts) / len(pts), 1), round(sum(q[1] for q in pts) / len(pts), 1)]})
    json.dump(out, open(a.out, 'w'))
    tally = collections.Counter((o['font'], o['size'], tuple(o['color'])) for o in out)
    print(f'{len(out)} labels -> {a.out}; by font/size/colour:')
    for k, v in tally.most_common(12):
        print(f'  {v:4d}  {k}')
    unknown = sorted({t for o in out for t in o['text'].split() if '{' in t})
    if unknown:
        print('undecoded glyphs (check on a rendered label, then --glyph N=char):', unknown[:20])


if __name__ == '__main__':
    main()
