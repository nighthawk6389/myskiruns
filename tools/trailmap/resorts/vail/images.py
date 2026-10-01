"""Vail's map images for the app: each panel as public/maps/vail-<panel>.jpg. Overlays are stored in percent of
the image, so a panel can be scaled down to keep the download small without touching any data: Front Side keeps
its full 4990 px (dense, small labels); Back Bowls (0.7) and Blue Sky (0.6) are drawn at a larger scale."""
import os

from PIL import Image

from common import PANELS, REPO, work

Image.MAX_IMAGE_PIXELS = None
SCALE = {'front-side': 1.0, 'back-bowls': 0.7, 'blue-sky': 0.6}
for p in PANELS:
    im = Image.open(work(f'{p}.png')).convert('RGB')
    if SCALE[p] != 1.0:
        im = im.resize((round(im.width * SCALE[p]), round(im.height * SCALE[p])), Image.LANCZOS)
    out = os.path.join(REPO, f'public/maps/vail-{p}.jpg')
    im.save(out, 'JPEG', quality=82, optimize=True, progressive=True)
    print(out, im.size, round(os.path.getsize(out) / 1e6, 2), 'MB')
