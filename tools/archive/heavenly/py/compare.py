"""Side-by-side crops: the 2022 page (warped onto the 2024 image) and the 2024 image, for boxes in main-panel px."""
import sys, json, numpy as np, cv2
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
S = sys.argv[1]
out = sys.argv[2]
boxes = [tuple(int(v) for v in b.split(',')) for b in sys.argv[3:]]
z = np.asarray(Image.open(f'{S}/hv/pdf22/page_z.png').convert('RGB'))
M = np.load(f'{S}/hv/pdf22/affine_pz.npy')
new = np.asarray(Image.open('/home/user/myskiruns/work/heavenly/main/map.png').convert('RGB'))
old = cv2.warpAffine(z, M, (new.shape[1], new.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
for k, (x0, y0, x1, y1) in enumerate(boxes):
    a = Image.fromarray(old[y0:y1, x0:x1]); b = Image.fromarray(new[y0:y1, x0:x1])
    w, h = a.size
    im = Image.new('RGB', (2 * w + 10, h), 'white')
    im.paste(a, (0, 0)); im.paste(b, (w + 10, 0))
    im.save(f'{out}_{k}.png')
    print(f'{out}_{k}.png', im.size)
