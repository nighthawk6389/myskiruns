// Detection-driven hotspot placement v2: place each trail's hotspot ON a
// detected trail LINE whose color class matches the trail's difficulty
// (green trails on green lines, blue on blue, black/double-black on black),
// within the trail's peak region. Farthest-point sampling spreads a peak's
// trails across its line network.
//
//   node scripts/placeTrailsOnLines.mjs [--render]
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { detectTrailLines, CLS } from './lib/lineDetector.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

const det = await detectTrailLines(resolve(root, 'public/killington-trail-map.jpg'));
const { width: W, height: H, centerMask } = det;

// peak regions (percent coords) — parse from the app's TS source
const regionSrc = readFileSync(resolve(root, 'src/data/peakRegions.ts'), 'utf8');
const PEAK_REGIONS = {};
for (const m of regionSrc.matchAll(/'([\w-]+)':\s*\{\s*cx:\s*([\d.]+),\s*cy:\s*([\d.]+),\s*w:\s*([\d.]+),\s*h:\s*([\d.]+)/g)) {
  PEAK_REGIONS[m[1]] = { cx: +m[2], cy: +m[3], w: +m[4], h: +m[5] };
}

const trailSrc = readFileSync(resolve(root, 'src/data/trails.ts'), 'utf8');
const trails = [];
for (const m of trailSrc.matchAll(/id:\s*'([^']+)'[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'/g)) {
  trails.push({ id: m[1], difficulty: m[2], peak: m[3] });
}

const CLASS_FOR = {
  green: CLS.green,
  blue: CLS.blue,
  black: CLS.black,
  'double-black': CLS.black,
};

// skeleton points per class inside a region (percent coords)
function linePointsInRegion(region, cls) {
  const x0 = ((region.cx - region.w / 2) / 100) * W;
  const x1 = ((region.cx + region.w / 2) / 100) * W;
  const y0 = ((region.cy - region.h / 2) / 100) * H;
  const y1 = ((region.cy + region.h / 2) / 100) * H;
  const pts = [];
  for (let y = Math.max(0, y0 | 0); y < Math.min(H, y1); y += 3) {
    for (let x = Math.max(0, x0 | 0); x < Math.min(W, x1); x += 3) {
      if (centerMask[y * W + x] === cls) pts.push({ x: (x / W) * 100, y: (y / H) * 100 });
    }
  }
  return pts;
}

function farthestPoints(pts, k, center) {
  if (pts.length === 0) return [];
  let seed = 0, best = Infinity;
  for (let i = 0; i < pts.length; i++) {
    const d = (pts[i].x - center.x) ** 2 + (pts[i].y - center.y) ** 2;
    if (d < best) { best = d; seed = i; }
  }
  const chosen = [pts[seed]];
  const minDist = pts.map((p) => (p.x - pts[seed].x) ** 2 + (p.y - pts[seed].y) ** 2);
  while (chosen.length < k) {
    let far = -1, farD = -1;
    for (let i = 0; i < pts.length; i++) if (minDist[i] > farD) { farD = minDist[i]; far = i; }
    if (far < 0 || farD <= 0) break;
    chosen.push(pts[far]);
    for (let i = 0; i < pts.length; i++) {
      const d = (pts[i].x - pts[far].x) ** 2 + (pts[i].y - pts[far].y) ** 2;
      if (d < minDist[i]) minDist[i] = d;
    }
  }
  while (chosen.length < k) chosen.push(chosen[chosen.length % Math.max(1, pts.length)]);
  return chosen;
}

const positions = {};
let onLine = 0, fallback = 0;
for (const [peakId, region] of Object.entries(PEAK_REGIONS)) {
  const peakTrails = trails.filter((t) => t.peak === peakId);
  if (!peakTrails.length) continue;
  const center = { x: region.cx, y: region.cy };
  // group by line class so each difficulty is spread over ITS color's lines
  const byClass = new Map();
  for (const t of peakTrails) {
    const c = CLASS_FOR[t.difficulty] ?? CLS.blue;
    if (!byClass.has(c)) byClass.set(c, []);
    byClass.get(c).push(t);
  }
  for (const [c, group] of byClass) {
    let pts = linePointsInRegion(region, c);
    if (pts.length < group.length) {
      // not enough lines of that color in the region: fall back to any class
      const any = [CLS.green, CLS.blue, CLS.black].flatMap((k) => linePointsInRegion(region, k));
      pts = pts.concat(any);
    }
    if (pts.length >= group.length) {
      const chosen = farthestPoints(pts, group.length, center).sort((a, b) => a.y - b.y);
      // hardest first onto highest points: difficulty tracks elevation
      const rank = { 'double-black': 0, black: 1, blue: 2, green: 3 };
      const ordered = [...group].sort((a, b) => (rank[a.difficulty] ?? 9) - (rank[b.difficulty] ?? 9));
      ordered.forEach((t, i) => {
        positions[t.id] = {
          x: Math.round(Math.max(2, Math.min(98, chosen[i].x)) * 10) / 10,
          y: Math.round(Math.max(5, Math.min(95, chosen[i].y)) * 10) / 10,
        };
        onLine++;
      });
    } else {
      group.forEach((t, i) => {
        positions[t.id] = {
          x: Math.round((region.cx - region.w / 2 + ((i + 0.5) / group.length) * region.w) * 10) / 10,
          y: Math.round(region.cy * 10) / 10,
        };
        fallback++;
      });
    }
  }
}

writeFileSync(resolve(root, 'src/data/trailPositions.json'), JSON.stringify(positions) + '\n');
console.log(`wrote ${Object.keys(positions).length} positions (${onLine} on color-matched lines, ${fallback} fallback)`);

if (process.argv.includes('--render')) {
  const { decodeJpeg, downscale, encodeJpeg } = await import('./lib/image.mjs');
  const { drawDot } = await import('./lib/draw.mjs');
  const img = downscale(decodeJpeg(resolve(root, 'public/killington-trail-map.jpg')), 1300);
  const colors = { green: [34, 197, 94], blue: [59, 130, 246], black: [20, 20, 20], 'double-black': [239, 68, 68] };
  for (const t of trails) {
    const p = positions[t.id];
    if (!p) continue;
    const px = Math.round((p.x / 100) * img.width), py = Math.round((p.y / 100) * img.height);
    const c = colors[t.difficulty] ?? [255, 255, 0];
    drawDot(img, px, py, 255, 255, 255, 5);
    drawDot(img, px, py, c[0], c[1], c[2], 3);
  }
  encodeJpeg(img, '/tmp/explore2/placement2.jpg', 92);
  console.log('audit render -> /tmp/explore2/placement2.jpg');
}
