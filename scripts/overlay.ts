// Render the detector's trail mask as a red overlay on the trail map, with
// ground-truth points drawn on top, so detection quality can be judged
// visually across the whole image (not just at the labelled points).
//
//   node --experimental-strip-types scripts/overlay.ts [outPath]
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { decodeJpeg, downscale, encodeJpeg } from './lib/image.mjs';
import { drawDot } from './lib/draw.mjs';
import { detectTrailMask, DEFAULT_PARAMS } from '../src/detection/trailDetector.ts';
import type { GroundTruthPoint } from '../src/detection/types.ts';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const out = process.argv[2] ?? '/tmp/explore/overlay.jpg';
mkdirSync(dirname(out), { recursive: true });

const full = decodeJpeg(resolve(root, 'public/killington-trail-map.jpg'));
const img = downscale(full, 1300);
const mask = detectTrailMask(img, DEFAULT_PARAMS);

// Tint detected pixels red.
for (let px = 0; px < img.width * img.height; px++) {
  if (mask[px]) {
    const i = px * 4;
    img.data[i] = Math.min(255, img.data[i] * 0.25 + 255 * 0.75);
    img.data[i + 1] = img.data[i + 1] * 0.25;
    img.data[i + 2] = img.data[i + 2] * 0.25;
  }
}

const gt: GroundTruthPoint[] = JSON.parse(
  readFileSync(resolve(root, 'src/detection/groundTruth.json'), 'utf8'),
).points;
for (const pt of gt) {
  const px = Math.round(pt.x * img.width);
  const py = Math.round(pt.y * img.height);
  const col = pt.label === 'trail' ? [0, 255, 0] : [0, 120, 255];
  drawDot(img, px, py, 0, 0, 0, 5);
  drawDot(img, px, py, col[0], col[1], col[2], 3);
}

encodeJpeg(img, out, 92);
const covered = mask.reduce((a, b) => a + b, 0);
console.log(`overlay -> ${out}  (${((covered / mask.length) * 100).toFixed(1)}% of pixels flagged)`);
