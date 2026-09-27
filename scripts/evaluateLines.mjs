// Trail-LINE detection evaluation harness (ground truth v2).
//
//   node scripts/evaluateLines.mjs            # evaluate
//   node scripts/evaluateLines.mjs --overlay  # also render overlay to /tmp/explore2/lines_overlay.jpg
//
// Metrics: precision / recall / F1 for "point is on a trail line" (binary),
// per-class breakdown, false positives grouped by negative subtype, and a
// full list of misses for debugging.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { detectTrailLines, DEFAULT_PARAMS, CLS } from './lib/lineDetector.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const MAP = resolve(root, 'public/killington-trail-map.jpg');

const gt = JSON.parse(readFileSync(resolve(root, 'src/detection/groundTruthLines.json'), 'utf8')).points;
// Prediction radius against the CENTERLINE skeleton: a point labeled "on the
// line" sits within ~4px of the line center (the GT labeling rule), so its
// distance to a faithful centerline is <=4px; near-line negatives at 6px+ stay
// clear. Using the skeleton makes the metric independent of stroke width.
const R = 5;

const CLASS_NAME = { [CLS.green]: 'green', [CLS.blue]: 'blue', [CLS.black]: 'black' };

function predictAt(det, nx, ny) {
  const { centerMask: lineMask, width: W, height: H } = det;
  const cx = Math.round(nx * (W - 1)), cy = Math.round(ny * (H - 1));
  let best = null, bestD = Infinity;
  for (let dy = -R; dy <= R; dy++) {
    for (let dx = -R; dx <= R; dx++) {
      const x = cx + dx, y = cy + dy;
      if (x < 0 || y < 0 || x >= W || y >= H) continue;
      const m = lineMask[y * W + x];
      if (m) {
        const d = dx * dx + dy * dy;
        if (d < bestD) { bestD = d; best = m; }
      }
    }
  }
  return best ? CLASS_NAME[best] : null;
}

const t0 = Date.now();
const debug = process.argv.includes('--why') ? [] : null;
const det = await detectTrailLines(MAP, DEFAULT_PARAMS, debug);
console.log(`detection ran in ${((Date.now() - t0) / 1000).toFixed(1)}s on ${det.width}x${det.height}`);

let tp = 0, fp = 0, tn = 0, fn = 0, clsRight = 0;
const fpBySubtype = {}, fnList = [], fpList = [];
for (const p of gt) {
  const pred = predictAt(det, p.x, p.y);
  const isPos = ['green', 'blue', 'black'].includes(p.label);
  if (isPos) {
    if (pred) { tp++; if (pred === p.label) clsRight++; }
    else { fn++; fnList.push(p); }
  } else {
    if (pred) {
      fp++;
      const sub = p.label.replace('off:', '');
      fpBySubtype[sub] = (fpBySubtype[sub] || 0) + 1;
      fpList.push({ ...p, pred });
    } else tn++;
  }
}
const precision = tp + fp ? tp / (tp + fp) : 0;
const recall = tp + fn ? tp / (tp + fn) : 0;
const f1 = precision + recall ? (2 * precision * recall) / (precision + recall) : 0;
console.log(`\npoints: ${gt.length}  (pos ${tp + fn}, neg ${fp + tn})`);
console.log(`TP=${tp} FP=${fp} FN=${fn} TN=${tn}`);
console.log(`precision = ${(precision * 100).toFixed(1)}%   recall = ${(recall * 100).toFixed(1)}%   F1 = ${(f1 * 100).toFixed(1)}%`);
console.log(`class accuracy on detected positives: ${tp ? ((clsRight / tp) * 100).toFixed(1) : 0}%`);

// per-class recall
for (const c of ['green', 'blue', 'black']) {
  const pos = gt.filter((p) => p.label === c);
  const hit = pos.filter((p) => predictAt(det, p.x, p.y) !== null).length;
  console.log(`  recall[${c}] = ${hit}/${pos.length}`);
}
if (fp) {
  console.log('\nfalse positives by subtype:', fpBySubtype);
  for (const p of fpList) console.log(`  FP #${p.id} (${p.label}) -> ${p.pred} @ ${p.x},${p.y}`);
}
if (fn) {
  console.log('\nmisses:');
  for (const p of fnList) {
    let why = '';
    if (debug) {
      const cx = Math.round(p.x * det.width), cy = Math.round(p.y * det.height);
      const near = debug.filter((d) => cx >= d.minX - 6 && cx <= d.maxX + 6 && cy >= d.minY - 6 && cy <= d.maxY + 6);
      if (near.length) {
        near.sort((a, b) => b.n - a.n);
        why = '  dropped-as: ' + near.slice(0, 3).map((d) => `${d.reason}(${d.extra},n=${d.n})`).join(' ');
      } else why = '  (no component near: not classified as ink)';
    }
    console.log(`  FN #${p.id} (${p.label}) @ ${p.x},${p.y}${why}`);
  }
}

if (process.argv.includes('--overlay')) {
  const { decodeJpeg, downscale, encodeJpeg } = await import('./lib/image.mjs');
  const full = decodeJpeg(MAP);
  const outW = 1400;
  const small = downscale(full, outW);
  const sc = det.width / outW;
  const TINT = { [CLS.green]: [0, 255, 0], [CLS.blue]: [0, 128, 255], [CLS.black]: [255, 0, 0] };
  for (let y = 0; y < small.height; y++) {
    for (let x = 0; x < outW; x++) {
      // max-pool the source block so thin lines stay visible
      let m = 0;
      const sy0 = Math.floor(y * sc), sy1 = Math.min(det.height, Math.ceil((y + 1) * sc));
      const sx0 = Math.floor(x * sc), sx1 = Math.min(det.width, Math.ceil((x + 1) * sc));
      for (let sy = sy0; sy < sy1 && !m; sy++) for (let sx = sx0; sx < sx1 && !m; sx++) m = det.lineMask[sy * det.width + sx];
      if (m) {
        const o = (y * outW + x) * 4, t = TINT[m];
        small.data[o] = t[0]; small.data[o + 1] = t[1]; small.data[o + 2] = t[2];
      }
    }
  }
  encodeJpeg(small, '/tmp/explore2/lines_overlay.jpg', 92);
  console.log('\noverlay -> /tmp/explore2/lines_overlay.jpg');
}
