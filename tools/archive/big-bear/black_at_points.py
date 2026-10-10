import numpy as np, cv2, sys, collections
from PIL import Image
from skimage.morphology import skeletonize
sys.path.insert(0, 'tools/trailmap')
import raster_lines as rl
A = np.asarray(Image.open('work/big-bear/snow-summit/map.png').convert('RGB')).astype(np.int16)
mx, mn = A.max(2), A.min(2)
m = (mx < 70) & (mx - mn < 30)
cm = rl.clean(m, [(1730, 1190, 1995, 1625), (0, 0, 2500, 300)], k=1.0, text_max=40)
n, lab, st, _ = cv2.connectedComponentsWithStats(cm.astype(np.uint8), connectivity=8)
sk = skeletonize(cm)
for (x, y) in ((800, 600), (830, 670), (900, 715), (950, 670), (735, 795)):
    win = lab[y - 6:y + 7, x - 6:x + 7]; ids = set(np.unique(win)) - {0}
    rawwin = m[y - 6:y + 7, x - 6:x + 7].sum()
    for i in ids:
        L = int(sk[lab == i].sum())
        print((x, y), 'raw', rawwin, 'comp', i, 'area', st[i, 4], 'skel', L, 'bbox', st[i, :4])
    if not ids: print((x, y), 'raw', rawwin, 'no comp after clean')
