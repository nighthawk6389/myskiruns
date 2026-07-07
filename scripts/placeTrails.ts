// Detection-driven hotspot placement.
//
//   node --experimental-strip-types scripts/placeTrails.ts
//
// Runs the trail detector on the map, then distributes each peak's trails across
// the *detected* run pixels inside that peak's region (farthest-point sampling
// for a good spread). Writes src/data/trailPositions.json, consumed by the
// image-map view. Identity within a peak is heuristic — the map's run labels
// are not machine-readable here — but every hotspot lands on real snow.
import { writeFileSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { decodeJpeg, downscale, encodeJpeg } from './lib/image.mjs';
import { drawDot } from './lib/draw.mjs';
import { detectTrailMask, DEFAULT_PARAMS } from '../src/detection/trailDetector.ts';
import { PEAK_REGIONS } from '../src/data/peakRegions.ts';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

const full = decodeJpeg(resolve(root, 'public/killington-trail-map.jpg'));
const img = downscale(full, 1300);
const mask = detectTrailMask(img, DEFAULT_PARAMS);

interface TrailRow {
  id: string;
  difficulty: string;
  peak: string;
}

// trails.ts is TS, not JSON; parse the fields out of it directly so this
// script has no dependency on the app's module graph.
function loadTrailsFromTs(): TrailRow[] {
  const src = readFileSync(resolve(root, 'src/data/trails.ts'), 'utf8');
  const rows: TrailRow[] = [];
  const re = /id:\s*'([^']+)'[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(src))) rows.push({ id: m[1], difficulty: m[2], peak: m[3] });
  return rows;
}

const trails: TrailRow[] = loadTrailsFromTs();

// Hardest runs sit highest on the mountain; use that to make the (otherwise
// arbitrary) trail-to-point assignment within a peak plausible.
const DIFFICULTY_RANK: Record<string, number> = {
  'double-black': 0,
  black: 1,
  blue: 2,
  green: 3,
};

interface Pt {
  x: number;
  y: number;
}

// Fraction of mask pixels set in a box around (x, y). Used to reject isolated
// false-positive speckles: farthest-point sampling maximises spread, so without
// this it would preferentially pick exactly those outliers.
function maskDensity(x: number, y: number, radius: number): number {
  let on = 0;
  let total = 0;
  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      const px = x + dx;
      const py = y + dy;
      if (px < 0 || py < 0 || px >= img.width || py >= img.height) continue;
      on += mask[py * img.width + px];
      total++;
    }
  }
  return total === 0 ? 0 : on / total;
}

// Collect detected run pixels (as percent coords) inside a region box, keeping
// only pixels that sit on a substantial run (dense neighborhood), not speckle.
function runPixelsInRegion(cx: number, cy: number, w: number, h: number): Pt[] {
  const x0 = ((cx - w / 2) / 100) * img.width;
  const x1 = ((cx + w / 2) / 100) * img.width;
  const y0 = ((cy - h / 2) / 100) * img.height;
  const y1 = ((cy + h / 2) / 100) * img.height;
  const pts: Pt[] = [];
  for (let y = Math.max(0, y0 | 0); y < Math.min(img.height, y1); y += 2) {
    for (let x = Math.max(0, x0 | 0); x < Math.min(img.width, x1); x += 2) {
      if (mask[y * img.width + x] && maskDensity(x, y, 3) >= 0.5) {
        pts.push({ x: (x / img.width) * 100, y: (y / img.height) * 100 });
      }
    }
  }
  return pts;
}

// Greedy farthest-point sampling: pick k well-spread points from the candidates.
function farthestPoints(pts: Pt[], k: number, center: Pt): Pt[] {
  if (pts.length === 0) return [];
  const chosen: Pt[] = [];
  // seed with the candidate nearest the region centre
  let seed = 0;
  let best = Infinity;
  for (let i = 0; i < pts.length; i++) {
    const d = (pts[i].x - center.x) ** 2 + (pts[i].y - center.y) ** 2;
    if (d < best) {
      best = d;
      seed = i;
    }
  }
  chosen.push(pts[seed]);
  const minDist = pts.map((p) => (p.x - pts[seed].x) ** 2 + (p.y - pts[seed].y) ** 2);
  while (chosen.length < k) {
    let far = -1;
    let farD = -1;
    for (let i = 0; i < pts.length; i++) {
      if (minDist[i] > farD) {
        farD = minDist[i];
        far = i;
      }
    }
    if (far < 0) break;
    chosen.push(pts[far]);
    for (let i = 0; i < pts.length; i++) {
      const d = (pts[i].x - pts[far].x) ** 2 + (pts[i].y - pts[far].y) ** 2;
      if (d < minDist[i]) minDist[i] = d;
    }
  }
  // if fewer candidates than trails, cycle through with small jitter
  while (chosen.length < k) {
    const base = chosen[chosen.length % Math.max(1, pts.length)];
    chosen.push({ x: base.x + (Math.random() - 0.5), y: base.y + (Math.random() - 0.5) });
  }
  return chosen;
}

const positions: Record<string, Pt> = {};
let placedFromDetection = 0;
let fallback = 0;

for (const [peakId, region] of Object.entries(PEAK_REGIONS)) {
  const peakTrails = trails.filter((t) => t.peak === peakId);
  if (peakTrails.length === 0) continue;
  const pts = runPixelsInRegion(region.cx, region.cy, region.w, region.h);
  const center = { x: region.cx, y: region.cy };
  if (pts.length >= peakTrails.length) {
    // Spread points across the detected runs, then pair hardest trails with the
    // highest points (smallest y): difficulty tracks elevation on a ski hill.
    const chosen = farthestPoints(pts, peakTrails.length, center).sort((a, b) => a.y - b.y);
    const ordered = [...peakTrails].sort(
      (a, b) => (DIFFICULTY_RANK[a.difficulty] ?? 9) - (DIFFICULTY_RANK[b.difficulty] ?? 9),
    );
    ordered.forEach((t, i) => {
      positions[t.id] = round(chosen[i]);
      placedFromDetection++;
    });
  } else {
    // not enough detected runs: lay trails on a grid within the box
    const cols = Math.ceil(Math.sqrt(peakTrails.length));
    const rows = Math.ceil(peakTrails.length / cols);
    peakTrails.forEach((t, i) => {
      const c = i % cols;
      const r = Math.floor(i / cols);
      positions[t.id] = round({
        x: region.cx - region.w / 2 + ((c + 0.5) / cols) * region.w,
        y: region.cy - region.h / 2 + ((r + 0.5) / rows) * region.h,
      });
      fallback++;
    });
  }
}

function round(p: Pt): Pt {
  return {
    x: Math.round(Math.max(2, Math.min(98, p.x)) * 10) / 10,
    y: Math.round(Math.max(5, Math.min(95, p.y)) * 10) / 10,
  };
}

writeFileSync(
  resolve(root, 'src/data/trailPositions.json'),
  JSON.stringify(positions, null, 0) + '\n',
);
console.log(
  `wrote ${Object.keys(positions).length} positions ` +
    `(${placedFromDetection} from detection, ${fallback} grid fallback)`,
);

// --render: draw the placed hotspots on the map for visual auditing.
if (process.argv.includes('--render')) {
  const colors: Record<string, [number, number, number]> = {
    green: [34, 197, 94],
    blue: [59, 130, 246],
    black: [20, 20, 20],
    'double-black': [239, 68, 68],
  };
  for (const t of trails) {
    const p = positions[t.id];
    if (!p) continue;
    const px = Math.round((p.x / 100) * img.width);
    const py = Math.round((p.y / 100) * img.height);
    const c = colors[t.difficulty] ?? [255, 255, 0];
    drawDot(img, px, py, 255, 255, 255, 5);
    drawDot(img, px, py, c[0], c[1], c[2], 3);
  }
  const out = '/tmp/explore/placement.jpg';
  encodeJpeg(img, out, 92);
  console.log(`audit render -> ${out}`);
}
