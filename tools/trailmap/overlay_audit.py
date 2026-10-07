"""Per-trail audit sheets: one cell per trail, to check every overlay on the map, trail by trail (the "every overlay
audited on crops" step of docs/trail-map-playbook.md).

    python3 tools/trailmap/overlay_audit.py --resort park-city --out work/park-city/audit
    python3 tools/trailmap/overlay_audit.py --resort vail --panel back-bowls --out work/vail/audit_bb --only riva-ridge

Each cell is the map cropped around one trail: its overlay thick orange (red dots at each part's ends; a marker is
a ring), every other trail's overlay thin cyan, and, for a resort read by pdf_resort.py, each label printing the
trail's name boxed in magenta, with the caption saying how its pieces were named (auto: by where the name is printed;
checked: settled on a crop, decisions.py; stretch: along the name's own characters; marker). Look at every cell:
the overlay should lie on the trail's own drawn line along its whole length, from the name (or its symbol) to where
the line ends, and nowhere else. Cells go 4 to a sheet (`--per`), each about `--max` px.

The map is public/maps/<id>[-<panel>].jpg, or (labels) the full-size work/<id>[/<panel>]/map.png a regen.sh leaves,
or --image. Overlays are in percent of the map, so any copy of it works.
"""
import argparse
import contextlib
import io
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resort_files import resort_files, trail_info  # noqa: E402

Image.MAX_IMAGE_PIXELS = None


def slug(nm):
    return re.sub(r'[^a-z0-9]+', '-', nm.lower().replace('’', '').replace("'", '')).strip('-')


def pdf_reading(rid, panel):
    """For a resort read by pdf_resort.py: {trail id: [label point lists in percent]}, {trail id: {how named}}, and
    the full-size map image it read; else empty."""
    f = resort_files(rid, panel)
    if not os.path.exists(os.path.join(f['tools'], *(['panels', panel] if panel else []), 'decisions.py')):
        return {}, {}, None
    import pdf_resort as pr
    r = pr.Resort(f'{rid}/{panel}' if panel else rid)
    if not os.path.exists(r.work('map.png')):
        print(f'(no {r.work("map.png")}: run the resort\'s regen.sh for its labels and naming)', file=sys.stderr)
        return {}, {}, None
    with contextlib.redirect_stdout(io.StringIO()):
        r.build()
    labels, how = {}, {}
    for n in r.names_:
        labels.setdefault(slug(n['name']), []).append([(100 * x / r.W, 100 * y / r.H) for x, y in n['pts']])
    for pid, v in r.assign.items():
        tag = 'stretch' if pid in r.traced else ('checked' if r.why.get(pid, '') == 'checked' else 'auto')
        for name in v:
            how.setdefault(slug(name), set()).add(tag)
    return labels, how, r.work('map.png')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--resort', required=True)
    ap.add_argument('--panel')
    ap.add_argument('--out', required=True, help='folder for the sheets (JPEG)')
    ap.add_argument('--only', default='', help='trail ids, comma-separated')
    ap.add_argument('--per', type=int, default=4, help='cells per sheet (2 columns; 3 from 6 on)')
    ap.add_argument('--max', type=int, default=560, help='longest side of a cell, px')
    ap.add_argument('--image', help='the map image (default: the work map.png, else public/maps)')
    ap.add_argument('--no-labels', action='store_true', help="don't read the PDF's labels (faster)")
    a = ap.parse_args()
    f = resort_files(a.resort, a.panel)
    labels, how, work_map = ({}, {}, None) if a.no_labels else pdf_reading(a.resort, a.panel)
    img = Image.open(a.image or work_map or f['map']).convert('RGB')
    W, H = img.size
    paths = json.load(open(f['paths']))['trails']
    info = trail_info(f['trails'])
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
    px = lambda q: (q[0] * W / 100, q[1] * H / 100)  # noqa: E731
    ids = [i for i in (a.only.split(',') if a.only else sorted(paths)) if i in paths and i in info]
    os.makedirs(a.out, exist_ok=True)
    cells = []
    for tid in ids:
        p = paths[tid]
        pts = [px(q) for s in p.get('segments', []) for q in s] + ([px(p['label'])] if p.get('label') else [])
        pts += [px(q) for lab in labels.get(tid, []) for q in lab]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        box = (max(0, int(min(xs)) - 70), max(0, int(min(ys)) - 70), min(W, int(max(xs)) + 70), min(H, int(max(ys)) + 70))
        s = min(2.5, a.max / max(box[2] - box[0], box[3] - box[1]))
        crop = img.crop(box).resize((int((box[2] - box[0]) * s), int((box[3] - box[1]) * s)), Image.LANCZOS)
        crop = crop.convert('RGBA')
        ov = Image.new('RGBA', crop.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        tr = lambda q: ((q[0] - box[0]) * s, (q[1] - box[1]) * s)  # noqa: E731
        for oid, op in paths.items():
            if oid != tid:
                for seg in op.get('segments', []):
                    d.line([tr(px(q)) for q in seg], fill=(0, 230, 255, 110), width=2)
        for lab in labels.get(tid, []):
            lx, ly = [px(q)[0] for q in lab], [px(q)[1] for q in lab]
            d.rectangle(tr((min(lx) - 8, min(ly) - 8)) + tr((max(lx) + 8, max(ly) + 8)), outline=(255, 0, 255, 230),
                        width=2)
        for seg in p.get('segments', []):
            d.line([tr(px(q)) for q in seg], fill=(255, 110, 0, 190), width=5)
            for e in (seg[0], seg[-1]):
                x, y = tr(px(e))
                d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 0, 0, 230))
        if p.get('label'):
            x, y = tr(px(p['label']))
            d.ellipse((x - 10, y - 10, x + 10, y + 10), outline=(255, 110, 0, 255), width=4)
        cell = Image.alpha_composite(crop, ov).convert('RGB')
        cap = Image.new('RGB', (cell.width, cell.height + 20), 'white')
        cap.paste(cell, (0, 20))
        name, dif, _peak = info[tid]
        named = '+'.join(sorted(how.get(tid, set()))) if how else ''
        ImageDraw.Draw(cap).text((3, 2), f"{tid}: {name} ({dif}) x{s:.1f} {named}{' MARKER' if p.get('label') else ''}",
                                 fill='black', font=F)
        cells.append((tid, cap))
    cols = 3 if a.per >= 6 else 2
    for k in range(0, len(cells), a.per):
        grp = cells[k:k + a.per]
        cw, ch = max(c.width for _, c in grp), max(c.height for _, c in grp)
        rows = (len(grp) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cw + 10 * (cols - 1), rows * ch + 10 * (rows - 1)), (90, 90, 90))
        for n, (_, c) in enumerate(grp):
            sheet.paste(c, ((n % cols) * (cw + 10), (n // cols) * (ch + 10)))
        sheet.save(os.path.join(a.out, f"{k // a.per:03d}_{'+'.join(t for t, _ in grp)[:120]}.jpg"), quality=85)
    print(f'{len(cells)} trails, {(len(cells) + a.per - 1) // a.per} sheets -> {a.out}')


if __name__ == '__main__':
    main()
