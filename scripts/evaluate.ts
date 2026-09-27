// Trail-detection evaluation harness.
//
//   node --experimental-strip-types scripts/evaluate.ts          # evaluate defaults
//   node --experimental-strip-types scripts/evaluate.ts --sweep  # grid-search params
//
// Reports precision / recall / F1 of the detector against the hand-labelled
// ground-truth points, plus per-class colour statistics to aid calibration.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { decodeJpeg } from './lib/image.mjs';
import { pixelFeatures } from '../src/detection/features.ts';
import {
  DEFAULT_PARAMS,
  sampleTrailAt,
  type DetectorParams,
} from '../src/detection/trailDetector.ts';
import type { GroundTruthPoint } from '../src/detection/types.ts';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

const img = decodeJpeg(resolve(root, 'public/killington-trail-map.jpg'));
const gt: GroundTruthPoint[] = JSON.parse(
  readFileSync(resolve(root, 'src/detection/groundTruth.json'), 'utf8'),
).points;

interface Metrics {
  tp: number;
  fp: number;
  tn: number;
  fn: number;
  precision: number;
  recall: number;
  f1: number;
  accuracy: number;
}

function evaluate(params: DetectorParams): Metrics {
  let tp = 0;
  let fp = 0;
  let tn = 0;
  let fn = 0;
  for (const pt of gt) {
    const pred = sampleTrailAt(img, pt.x, pt.y, params);
    const actual = pt.label === 'trail';
    if (pred && actual) tp++;
    else if (pred && !actual) fp++;
    else if (!pred && actual) fn++;
    else tn++;
  }
  const precision = tp + fp === 0 ? 0 : tp / (tp + fp);
  const recall = tp + fn === 0 ? 0 : tp / (tp + fn);
  const f1 = precision + recall === 0 ? 0 : (2 * precision * recall) / (precision + recall);
  const accuracy = (tp + tn) / gt.length;
  return { tp, fp, tn, fn, precision, recall, f1, accuracy };
}

function pct(x: number): string {
  return (x * 100).toFixed(1).padStart(5) + '%';
}

function printMetrics(label: string, m: Metrics): void {
  console.log(`\n${label}`);
  console.log(`  confusion:  TP=${m.tp}  FP=${m.fp}  FN=${m.fn}  TN=${m.tn}`);
  console.log(`  precision:  ${pct(m.precision)}   recall: ${pct(m.recall)}`);
  console.log(`  F1:         ${pct(m.f1)}   accuracy: ${pct(m.accuracy)}`);
}

// Per-class colour statistics: helps see whether classes are separable.
function classStats(): void {
  const acc: Record<string, { n: number; v: number; s: number; ge: number; be: number }> = {
    trail: { n: 0, v: 0, s: 0, ge: 0, be: 0 },
    off: { n: 0, v: 0, s: 0, ge: 0, be: 0 },
  };
  for (const pt of gt) {
    const cx = Math.round(pt.x * (img.width - 1));
    const cy = Math.round(pt.y * (img.height - 1));
    const i = (cy * img.width + cx) * 4;
    const f = pixelFeatures(img.data[i], img.data[i + 1], img.data[i + 2]);
    const a = acc[pt.label];
    a.n++;
    a.v += f.value;
    a.s += f.saturation;
    a.ge += f.greenExcess;
    a.be += f.blueExcess;
  }
  console.log('\nper-class mean features (value, saturation, greenExcess, blueExcess):');
  for (const k of ['trail', 'off']) {
    const a = acc[k];
    console.log(
      `  ${k.padEnd(6)} n=${a.n}  v=${(a.v / a.n).toFixed(3)}  s=${(a.s / a.n).toFixed(3)}` +
        `  ge=${(a.ge / a.n).toFixed(3)}  be=${(a.be / a.n).toFixed(3)}`,
    );
  }
}

function listErrors(params: DetectorParams): void {
  const errs = gt.filter((pt) => sampleTrailAt(img, pt.x, pt.y, params) !== (pt.label === 'trail'));
  if (errs.length === 0) {
    console.log('\nno misclassified points 🎉');
    return;
  }
  console.log('\nmisclassified points (id @ x,y  expected -> predicted):');
  for (const pt of errs) {
    const pred = sampleTrailAt(img, pt.x, pt.y, params) ? 'trail' : 'off';
    const cx = Math.round(pt.x * (img.width - 1));
    const cy = Math.round(pt.y * (img.height - 1));
    const i = (cy * img.width + cx) * 4;
    const f = pixelFeatures(img.data[i], img.data[i + 1], img.data[i + 2]);
    console.log(
      `  #${String(pt.id).padStart(2)} @ ${pt.x.toFixed(3)},${pt.y.toFixed(3)}  ` +
        `${pt.label} -> ${pred}   ` +
        `[v=${f.value.toFixed(2)} s=${f.saturation.toFixed(2)} ge=${f.greenExcess.toFixed(2)} be=${f.blueExcess.toFixed(2)}]`,
    );
  }
}

function sweep(): DetectorParams {
  const valueMins = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75];
  const satMaxes = [0.1, 0.14, 0.18, 0.22, 0.26, 0.3];
  const geMaxes = [-0.02, 0, 0.02, 0.04, 0.06, 0.1];
  const beMaxes = [0.02, 0.04, 0.06, 0.08, 0.12, 1.0];
  let best: { f1: number; params: DetectorParams; m: Metrics } | null = null;
  for (const valueMin of valueMins)
    for (const saturationMax of satMaxes)
      for (const greenExcessMax of geMaxes)
        for (const blueExcessMax of beMaxes) {
          const params = {
            valueMin,
            saturationMax,
            greenExcessMax,
            blueExcessMax,
            skyYMax: DEFAULT_PARAMS.skyYMax,
          };
          const m = evaluate(params);
          // Prefer F1, break ties toward higher recall then precision.
          if (
            !best ||
            m.f1 > best.f1 + 1e-9 ||
            (Math.abs(m.f1 - best.f1) < 1e-9 && m.recall > best.m.recall)
          ) {
            best = { f1: m.f1, params, m };
          }
        }
  console.log('\n=== grid search best ===');
  console.log('  params:', JSON.stringify(best!.params));
  printMetrics('best', best!.m);
  return best!.params;
}

console.log(`image ${img.width}x${img.height}, ${gt.length} ground-truth points`);
classStats();
printMetrics('DEFAULT_PARAMS', evaluate(DEFAULT_PARAMS));
listErrors(DEFAULT_PARAMS);

if (process.argv.includes('--sweep')) {
  const best = sweep();
  listErrors(best);
}
