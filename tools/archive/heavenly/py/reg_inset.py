import sys, numpy as np, cv2, pymupdf
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
pdf, png = sys.argv[1], sys.argv[2]
pg = pymupdf.open(pdf)[0]
z = 3652 / pg.rect.width
# the inset region of the page, rendered at the image's scale
clip = pymupdf.Rect(0, 960, 765, 1330)
pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, alpha=False)
A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
B = np.asarray(Image.open(png).convert('RGB'))[2990:4150, 0:2400]
sift = cv2.SIFT_create(8000)
ka, da = sift.detectAndCompute(cv2.cvtColor(A, cv2.COLOR_RGB2GRAY), None)
kb, db = sift.detectAndCompute(cv2.cvtColor(B, cv2.COLOR_RGB2GRAY), None)
m = cv2.BFMatcher().knnMatch(da, db, k=2)
good = [p for p, q in m if p.distance < 0.7 * q.distance]
src = np.float32([ka[g.queryIdx].pt for g in good])
dst = np.float32([kb[g.trainIdx].pt for g in good])
# A px -> pt: pt = clip.tl + a/z ; B px -> full image px: + (0, 2990)
src_pt = src / z + np.float32([clip.x0, clip.y0])
dst_px = dst + np.float32([0, 2990])
M, inl = cv2.estimateAffine2D(src_pt, dst_px, ransacReprojThreshold=1.5, maxIters=20000, confidence=0.999)
inl = inl.ravel().astype(bool)
res = np.linalg.norm((src_pt[inl] @ M[:, :2].T + M[:, 2]) - dst_px[inl], axis=1)
print('matches', len(good), 'inliers', inl.sum(), 'median residual px', np.median(res).round(3), 'p90', np.percentile(res, 90).round(3))
print(M)
