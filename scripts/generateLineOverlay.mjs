// Render the detected trail lines to a transparent PNG the app can overlay
// on the trail map (public/trail-lines.png), plus refresh the docs snapshot.
//
//   node scripts/generateLineOverlay.mjs
import sharp from 'sharp';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { detectTrailLines, CLS } from './lib/lineDetector.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const MAP = resolve(root, 'public/killington-trail-map.jpg');
const OUT = resolve(root, 'public/trail-lines.png');

const det = await detectTrailLines(MAP);
const { width: W, height: H, lineMask } = det;

// Bright, difficulty-coded highlight colors (alpha only where lines are).
const COLOR = {
  [CLS.green]: [34, 255, 120, 230],
  [CLS.blue]: [64, 156, 255, 230],
  [CLS.black]: [255, 64, 64, 230],
};

// Render at half resolution to keep the PNG small; dilate by 1 source pixel
// (max-pool) so 1px-thin structures survive the downscale.
const outW = Math.round(W / 2), outH = Math.round(H / 2);
const rgba = new Uint8Array(outW * outH * 4);
for (let y = 0; y < outH; y++) {
  for (let x = 0; x < outW; x++) {
    let m = 0;
    for (let sy = y * 2; sy < Math.min(H, y * 2 + 2) && !m; sy++) {
      for (let sx = x * 2; sx < Math.min(W, x * 2 + 2) && !m; sx++) {
        m = lineMask[sy * W + sx];
      }
    }
    if (m) {
      const o = (y * outW + x) * 4, c = COLOR[m];
      rgba[o] = c[0]; rgba[o + 1] = c[1]; rgba[o + 2] = c[2]; rgba[o + 3] = c[3];
    }
  }
}

await sharp(Buffer.from(rgba), { raw: { width: outW, height: outH, channels: 4 } })
  .png({ compressionLevel: 9, palette: true })
  .toFile(OUT);
const covered = lineMask.reduce((a, b) => a + (b ? 1 : 0), 0);
console.log(`wrote ${OUT} (${outW}x${outH}, ${((covered / (W * H)) * 100).toFixed(2)}% of source pixels are trail line)`);
