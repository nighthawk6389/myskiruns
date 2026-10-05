"""Contact sheets with each line piece alone on its own crop: the piece in magenta (a circle at its first point), the
other pieces thin grey, symbols tagged with their names. For naming the pieces of a map where one drawn line carries
several runs (Wildcat): a whole-map tile hides which piece is which.

    python3 tools/trailmap/piece_sheet.py --image work/wildcat/map.png --pieces work/wildcat/pieces_cut.json \\
        --names work/wildcat/names.json --symbols work/wildcat/named_syms.json --out work/wildcat/pieces/sheet [ids]

--pieces: linePolylines.json-style pieces (percent of the image); --names: {id: name} (pdf_resort.py's names.json);
--symbols: [{c: [x, y], name}] in image px. Writes <out>_<n>.png, six pieces a sheet (all pieces, or the ids given).
"""
import argparse
import json

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SIDE, PAD = 520, 120


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--pieces', required=True)
    ap.add_argument('--names', default=None)
    ap.add_argument('--symbols', default=None)
    ap.add_argument('--out', required=True, help='path prefix: <out>_<n>.png')
    ap.add_argument('ids', nargs='*', type=int)
    a = ap.parse_args()
    im = Image.open(a.image).convert('RGB')
    W, H = im.size
    P = {p['id']: p for p in json.load(open(a.pieces))['polylines']}
    N = json.load(open(a.names)) if a.names else {}
    S = json.load(open(a.symbols)) if a.symbols else []
    font = ImageFont.truetype(FONT, 15)
    ids = a.ids or sorted(P)
    tiles = []
    for pid in ids:
        p = P[pid]
        pts = [(x * W / 100, y * H / 100) for x, y in p['points']]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        side = max(max(xs) - min(xs), max(ys) - min(ys)) + 2 * PAD
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        x0, y0 = cx - side / 2, cy - side / 2
        crop = im.crop((int(x0), int(y0), int(x0 + side), int(y0 + side))).resize((SIDE, SIDE))
        z = SIDE / side
        d = ImageDraw.Draw(crop)

        def tr(q):
            return ((q[0] - x0) * z, (q[1] - y0) * z)
        for o in P.values():
            if o['id'] != pid:
                d.line([tr((x * W / 100, y * H / 100)) for x, y in o['points']], fill=(160, 160, 160), width=1)
        d.line([tr(q) for q in pts], fill=(255, 0, 255), width=4)
        sx, sy = tr(pts[0])
        d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], outline=(255, 0, 255), width=3)
        for s in S:
            qx, qy = tr(s['c'])
            if 0 <= qx < SIDE and 0 <= qy < SIDE:
                d.text((qx + 8, qy - 8), (s.get('name') or '?')[:18], fill=(255, 0, 0), font=font, stroke_width=2,
                       stroke_fill='white')
        d.rectangle([0, 0, SIDE - 1, 24], fill='white')
        d.text((4, 3), f"{pid} {p['cls']} {N.get(str(pid), '?')[:30]}", fill='black', font=font)
        tiles.append(crop)
    for k in range(0, len(tiles), 6):
        group = tiles[k:k + 6]
        sheet = Image.new('RGB', (3 * (SIDE + 5), ((len(group) + 2) // 3) * (SIDE + 5)), 'white')
        for i, t in enumerate(group):
            sheet.paste(t, ((i % 3) * (SIDE + 5), (i // 3) * (SIDE + 5)))
        sheet.save(f'{a.out}_{k // 6}.png')
        print(f'{a.out}_{k // 6}.png', ids[k:k + 6])


if __name__ == '__main__':
    main()
