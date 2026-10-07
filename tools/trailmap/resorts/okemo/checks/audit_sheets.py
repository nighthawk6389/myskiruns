"""Crops of overlays on the map (tools/trailmap/render_crops.py) as contact sheets, for the three audits Okemo had:

    python3 tools/trailmap/resorts/okemo/checks/audit_sheets.py sample   # 16 auto-accepted trails, 2x2 sheets
    python3 tools/trailmap/resorts/okemo/checks/audit_sheets.py traced   # the 23 trails pre-filled for review, 3x2
    python3 tools/trailmap/resorts/okemo/checks/audit_sheets.py pairs    # the 3 trails the reviewer edited + neighbour

From the repo root, after regen.sh. Reads $OKEMO_WORK/okemo_source.png and src/data/resorts/okemo/trailPaths.json;
writes $OKEMO_WORK/audit/ + audit_sheet_<k>.jpg, tracecheck/ + tracesheet_<k>.jpg, postreview/. (Scratch inline
scripts of 2026-09-30: 08:08 UTC, the sample drawn with random.seed(7) from the 108 auto-accepted line trails of
that hour's proposals, all 16 on their own labelled line along the full run; 08:50, all 23 checked; 11:11, after
the review import.)
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W_DIR = os.environ.get('OKEMO_WORK', 'work/okemo')
SAMPLE = ('link eclipse lower-world-cup the-narrows buckhorn chute white-lightning roundhouse-run cutters-folly '
          'lower-moonshadow ski-school-slope cat-nap rim-rock fast-track blue-moon countdown').split()
TRACED = ('switchback sundog scooter drop-off sidekick rt-103 mountain-road fast-track inn-bound turkey-shoot '
          'challenger rum-run kettle-brook lower-mountain-road searles-way tomahawk tomahawk-park jack-a-lope '
          'upper-moonshadow sunset-strip galaxy-bowl bright-star-basin tree-tap').split()
PAIRS = [('turkey-shoot', 'challenger'), ('mountain-road', 'lower-mountain-road'), ('fast-track', 'inn-bound')]
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)


def crops(out, names, *extra):
    subprocess.run([sys.executable, 'tools/trailmap/render_crops.py', '--image', f'{W_DIR}/okemo_source.png',
                    '--paths', 'src/data/resorts/okemo/trailPaths.json', '--out', out, *extra, *names],
                   check=True, stdout=subprocess.DEVNULL)


def sheets(src, names, prefix, cols, rows, cell, dx, dy, top):
    per = cols * rows
    for k in range(0, len(names), per):
        batch = names[k:k + per]
        ims = [Image.open(f'{src}/{n}.jpg') for n in batch]
        ims = [im.resize((int(im.width * cell / max(im.size)), int(im.height * cell / max(im.size)))) for im in ims]
        sheet = Image.new('RGB', (cols * dx, rows * dy), 'white')
        d = ImageDraw.Draw(sheet)
        for i, (n, im) in enumerate(zip(batch, ims)):
            x, y = (i % cols) * dx, (i // cols) * dy
            sheet.paste(im, (x, y + top))
            d.text((x + 4, y + 4 if top > 26 else y + 3), n, fill='black', font=FONT)
        sheet.save(f'{W_DIR}/{prefix}_{k // per}.jpg', quality=85)
        print(f'{W_DIR}/{prefix}_{k // per}.jpg', ' '.join(batch))


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else ''
    if what == 'sample':
        crops(f'{W_DIR}/audit', SAMPLE, '--max', '700')
        sheets(f'{W_DIR}/audit', SAMPLE, 'audit_sheet', 2, 2, 520, 530, 555, 28)
    elif what == 'traced':
        subprocess.run(['rm', '-rf', f'{W_DIR}/tracecheck'], check=True)
        crops(f'{W_DIR}/tracecheck', TRACED, '--max', '700')
        sheets(f'{W_DIR}/tracecheck', TRACED, 'tracesheet', 3, 2, 430, 440, 462, 26)
    elif what == 'pairs':
        subprocess.run(['rm', '-rf', f'{W_DIR}/postreview'], check=True)
        for pair in PAIRS:
            crops(f'{W_DIR}/postreview', pair, '--pair', '--max', '900')
        print(f'{W_DIR}/postreview/', ', '.join('__'.join(p) + '.jpg' for p in PAIRS))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
