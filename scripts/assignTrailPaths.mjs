// Assign detected line polylines to named trails.
//
//   node scripts/assignTrailPaths.mjs [--render]
//
// Inputs: src/data/linePolylines.json (traced centerline polylines),
//         src/data/trailAnchors.json (OCR name anchors),
//         src/data/trails.ts, src/data/peakRegions.ts
// Output: src/data/trailPaths.json  { trails: { id: { points, source } } }
//
// Anchored trails claim the polyline of their difficulty color nearest their
// name label. Unanchored trails get remaining same-color polylines inside
// their peak region, hardest-highest. Trails left over keep dot placement
// (the app falls back to hotspot dots for them).
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

const polys = JSON.parse(readFileSync(resolve(root, 'src/data/linePolylines.json'), 'utf8')).polylines;
const anchors = JSON.parse(readFileSync(resolve(root, 'src/data/trailAnchors.json'), 'utf8')).anchors;

const trailSrc = readFileSync(resolve(root, 'src/data/trails.ts'), 'utf8');
const trails = [];
for (const m of trailSrc.matchAll(/id:\s*'([^']+)'[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'/g)) {
  trails.push({ id: m[1], difficulty: m[2], peak: m[3] });
}
const regionSrc = readFileSync(resolve(root, 'src/data/peakRegions.ts'), 'utf8');
const REGIONS = {};
for (const m of regionSrc.matchAll(/'([\w-]+)':\s*\{\s*cx:\s*([\d.]+),\s*cy:\s*([\d.]+),\s*w:\s*([\d.]+),\s*h:\s*([\d.]+)/g)) {
  REGIONS[m[1]] = { cx: +m[2], cy: +m[3], w: +m[4], h: +m[5] };
}

const CLASS_FOR = { green: 'green', blue: 'blue', black: 'black', 'double-black': 'black' };

// distance (percent-x units) from a point to a polyline
function distToPoly(px, py, points) {
  let best = Infinity;
  for (let i = 0; i < points.length - 1; i++) {
    const [x1, y1] = points[i], [x2, y2] = points[i + 1];
    const dx = x2 - x1, dy = y2 - y1;
    const L2 = dx * dx + dy * dy;
    let t = L2 ? ((px - x1) * dx + (py - y1) * dy) / L2 : 0;
    t = Math.max(0, Math.min(1, t));
    const d = Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
    if (d < best) best = d;
  }
  return best;
}
function centroid(points) {
  let sx = 0, sy = 0;
  for (const [x, y] of points) { sx += x; sy += y; }
  return [sx / points.length, sy / points.length];
}
function inRegion(pt, r, slack = 1.35) {
  return Math.abs(pt[0] - r.cx) <= (r.w / 2) * slack && Math.abs(pt[1] - r.cy) <= (r.h / 2) * slack;
}

const assigned = {}; // trailId -> {points, source}
const taken = new Set(); // polyline ids claimed by anchored trails

// direction at a polyline end (unit vector pointing outward)
function endDir(points, atStart) {
  const k = Math.min(4, points.length - 1);
  const [x1, y1] = atStart ? points[k] : points[points.length - 1 - k];
  const [x2, y2] = atStart ? points[0] : points[points.length - 1];
  const n = Math.hypot(x2 - x1, y2 - y1) || 1;
  return [(x2 - x1) / n, (y2 - y1) / n];
}

// Trails often split into 2-4 polylines at busy junctions: extend a claimed
// polyline with unclaimed same-class continuations (near endpoint + collinear).
function stitchChain(seed, cls) {
  const chain = [...seed.points];
  taken.add(seed.id);
  let grew = true;
  while (grew && chain.length < 400) {
    grew = false;
    for (const atStart of [false, true]) {
      const tip = atStart ? chain[0] : chain[chain.length - 1];
      const dir = endDir(chain, atStart);
      let best = null, bestScore = 0, bestFlip = false;
      for (const p of polys) {
        if (p.cls !== cls || taken.has(p.id)) continue;
        for (const flip of [false, true]) {
          const cand = flip ? [...p.points].reverse() : p.points;
          const gap = Math.hypot(cand[0][0] - tip[0], cand[0][1] - tip[1]);
          if (gap > 1.1) continue;
          const cdir = endDir(cand, true);
          const dot = dir[0] * cdir[0] + dir[1] * cdir[1];
          if (dot < 0.5) continue; // must continue roughly the same direction
          const score = dot - gap * 0.3;
          if (score > bestScore) { bestScore = score; best = p; bestFlip = flip; }
        }
      }
      if (best) {
        const cand = bestFlip ? [...best.points].reverse() : best.points;
        if (atStart) chain.unshift(...[...cand].reverse());
        else chain.push(...cand);
        taken.add(best.id);
        grew = true;
      }
    }
  }
  return chain;
}

// pass 1: anchored trails claim the polyline their name label hugs (greedy by
// anchor confidence). The label is the identity evidence, so a very close
// line of ANY class wins over a distant line of the roster's class — several
// roster difficulties disagree with the map's drawn color.
// Global nearest-first matching: collect all (trail, polyline) candidate
// pairs, sort by label-to-line distance, and claim greedily. This prevents a
// farther label from stealing the line that another label sits right on.
const anchoredTrails = trails.filter((t) => anchors[t.id]);
const colorMismatches = [];
// local direction (degrees, mod 180) of a polyline near a point
function localAngle(px, py, points) {
  let bi = 0, best = Infinity;
  for (let i = 0; i < points.length - 1; i++) {
    const [x1, y1] = points[i], [x2, y2] = points[i + 1];
    const d = Math.hypot(px - (x1 + x2) / 2, py - (y1 + y2) / 2);
    if (d < best) { best = d; bi = i; }
  }
  const i0 = Math.max(0, bi - 2), i1 = Math.min(points.length - 1, bi + 3);
  const dx = points[i1][0] - points[i0][0], dy = points[i1][1] - points[i0][1];
  return ((Math.atan2(dy, dx) * 180) / Math.PI + 180) % 180;
}
const pairs = [];
for (const t of anchoredTrails) {
  const a = anchors[t.id];
  const cls = CLASS_FOR[t.difficulty];
  const ax = a.x * 100, ay = a.y * 100;
  for (const p of polys) {
    const d = distToPoly(ax, ay, p.points);
    const sameCls = p.cls === cls;
    if (!(sameCls ? d <= 3.5 : d <= 1.2)) continue;
    // a trail name is set along its own line: penalize direction mismatch
    let anglePen = 0;
    if (typeof a.angleDeg === 'number') {
      const la = ((a.angleDeg % 180) + 180) % 180;
      const pa = localAngle(ax, ay, p.points);
      // note: label y-angle sign convention matches image coords, compare mod 180
      let diff = Math.abs(la - pa);
      if (diff > 90) diff = 180 - diff;
      if (diff > 35) anglePen = 1.5;
      else if (diff > 22) anglePen = 0.5;
    }
    pairs.push({ t, p, d, sameCls, score: d + anglePen - (sameCls ? 0.4 : 0) });
  }
}
pairs.sort((a, b) => a.score - b.score);
for (const { t, p, d, sameCls } of pairs) {
  if (assigned[t.id] || taken.has(p.id)) continue;
  if (!sameCls) colorMismatches.push(`${t.id} (data ${t.difficulty}, map line ${p.cls}, d=${d.toFixed(2)})`);
  assigned[t.id] = { points: stitchChain(p, p.cls), source: 'anchor' };
}
if (colorMismatches.length) {
  console.log('anchored to other-class line (roster difficulty likely wrong):');
  for (const mm of colorMismatches) console.log('  ' + mm);
}

// pass 2: unanchored trails get remaining same-class polylines in their peak
// region, longest polylines first, hardest trails highest
const rank = { 'double-black': 0, black: 1, blue: 2, green: 3 };
for (const [peakId, region] of Object.entries(REGIONS)) {
  for (const cls of ['green', 'blue', 'black']) {
    const group = trails
      .filter((t) => t.peak === peakId && CLASS_FOR[t.difficulty] === cls && !assigned[t.id])
      .sort((a, b) => (rank[a.difficulty] ?? 9) - (rank[b.difficulty] ?? 9));
    if (!group.length) continue;
    const avail = polys
      .filter((p) => p.cls === cls && !taken.has(p.id) && p.points.length >= 2 && inRegion(centroid(p.points), region))
      .sort((a, b) => b.lengthPx - a.lengthPx)
      .slice(0, group.length * 2)
      // hardest-highest pairing: sort chosen polylines by top elevation
      .sort((a, b) => Math.min(...a.points.map((q) => q[1])) - Math.min(...b.points.map((q) => q[1])));
    for (let i = 0; i < group.length && i < avail.length; i++) {
      if (taken.has(avail[i].id)) continue;
      assigned[group[i].id] = { points: stitchChain(avail[i], cls), source: 'region' };
    }
  }
}

const out = { _note: 'Detected line polylines per trail (percent coords). source: anchor = claimed via OCR name label; region = heuristic within peak region.', trails: assigned };
writeFileSync(resolve(root, 'src/data/trailPaths.json'), JSON.stringify(out) + '\n');
const nAnchor = Object.values(assigned).filter((a) => a.source === 'anchor').length;
console.log(`assigned paths: ${Object.keys(assigned).length}/${trails.length} (${nAnchor} by name anchor, ${Object.keys(assigned).length - nAnchor} by region heuristic)`);
console.log(`trails without a path (dot fallback): ${trails.filter((t) => !assigned[t.id]).map((t) => t.id).join(', ') || 'none'}`);

if (process.argv.includes('--render')) {
  const { decodeJpeg, downscale, encodeJpeg } = await import('./lib/image.mjs');
  const img = downscale(decodeJpeg(resolve(root, 'public/killington-trail-map.jpg')), 1400);
  const COLORS = { anchor: [255, 240, 0], region: [255, 0, 255] };
  for (const [, a] of Object.entries(assigned)) {
    const c = COLORS[a.source];
    for (let i = 0; i < a.points.length - 1; i++) {
      const [x1, y1] = a.points[i], [x2, y2] = a.points[i + 1];
      const steps = Math.max(1, Math.round(Math.hypot(x2 - x1, y2 - y1) * 14));
      for (let s = 0; s <= steps; s++) {
        const x = Math.round(((x1 + ((x2 - x1) * s) / steps) / 100) * img.width);
        const y = Math.round(((y1 + ((y2 - y1) * s) / steps) / 100) * img.height);
        if (x < 0 || y < 0 || x >= img.width || y >= img.height) continue;
        const o = (y * img.width + x) * 4;
        img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2];
      }
    }
  }
  encodeJpeg(img, '/tmp/explore2/assigned_paths.jpg', 92);
  console.log('audit render -> /tmp/explore2/assigned_paths.jpg (yellow=anchored, magenta=heuristic)');
}
