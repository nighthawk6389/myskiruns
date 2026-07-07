// Reconcile OCR'd map labels with the trail roster.
//
//   node scripts/reconcileTrails.mjs [--apply]
//
// Reads src/data/labelAnchors.json (produced by scripts/extractLabels.mjs),
// fuzzy-matches label text against data/trails.ts names, and:
//   - writes src/data/trailAnchors.json: per-trail name-anchor positions
//   - reports map labels that match no roster entry (missing trails), with
//     difficulty inferred from the nearest detected line's color class
//   - with --apply, appends the missing trails to src/data/trails.ts
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { detectTrailLines, CLS } from './lib/lineDetector.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

const labels = JSON.parse(readFileSync(resolve(root, 'src/data/labelAnchors.json'), 'utf8')).labels;

const trailSrc = readFileSync(resolve(root, 'src/data/trails.ts'), 'utf8');
const trails = [];
for (const m of trailSrc.matchAll(/\{ id:\s*'([^']+)',\s*name:\s*'([^']+)'[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'/g)) {
  trails.push({ id: m[1], name: m[2], difficulty: m[3], peak: m[4] });
}

// non-trail vocabulary that appears on maps: never propose these as trails
const STOP = /\b(LODGE|PARKING|CONDOS?|ROAD|BAR|GRILL|HOTEL|RESTAURANT|CLUBHOUSE|YURT|EXPRESS|QUAD|GONDOLA|POMA|SIX|LOT|VALE|BASE|CAMP|PEAK|MOUNTAIN|MTN|KILLINGTON|ROUTE|CABIN|WAFFLE|UMBRELLA|TUBING|PARK|VILLAGE|HOMES|LIVE|STAGE|LEARN|SKI|CLINIC|CENTER|MAP|VISTA)\b/;

function norm(s) {
  return s.toUpperCase().replace(/[^A-Z' ]/g, '').replace(/\s+/g, ' ').trim();
}
function lev(a, b) {
  const m = a.length, n = b.length;
  const d = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
  for (let j = 1; j <= n; j++) d[0][j] = j;
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[m][n];
}
function sim(a, b) {
  const L = Math.max(a.length, b.length);
  return L === 0 ? 0 : 1 - lev(a, b) / L;
}

// difficulty from the nearest detected line's class around a point
const det = await detectTrailLines(resolve(root, 'public/killington-trail-map.jpg'));
const CLASS_DIFF = { [CLS.green]: 'green', [CLS.blue]: 'blue', [CLS.black]: 'black' };
function nearestLineClass(nx, ny, rad = 60) {
  const cx = Math.round(nx * det.width), cy = Math.round(ny * det.height);
  let best = null, bestD = Infinity;
  for (let dy = -rad; dy <= rad; dy += 2) {
    for (let dx = -rad; dx <= rad; dx += 2) {
      const x = cx + dx, y = cy + dy;
      if (x < 0 || y < 0 || x >= det.width || y >= det.height) continue;
      const m = det.centerMask[y * det.width + x];
      if (m) {
        const d = dx * dx + dy * dy;
        if (d < bestD) { bestD = d; best = m; }
      }
    }
  }
  return best ? { cls: CLASS_DIFF[best], dist: Math.sqrt(bestD) } : null;
}

// peak region containment
const regionSrc = readFileSync(resolve(root, 'src/data/peakRegions.ts'), 'utf8');
const regions = [];
for (const m of regionSrc.matchAll(/'([\w-]+)':\s*\{\s*cx:\s*([\d.]+),\s*cy:\s*([\d.]+),\s*w:\s*([\d.]+),\s*h:\s*([\d.]+)/g)) {
  regions.push({ id: m[1], cx: +m[2], cy: +m[3], w: +m[4], h: +m[5] });
}
function peakFor(nx, ny) {
  let best = null, bestD = Infinity;
  for (const r of regions) {
    const d = ((nx * 100 - r.cx) / r.w) ** 2 + ((ny * 100 - r.cy) / r.h) ** 2;
    if (d < bestD) { bestD = d; best = r.id; }
  }
  return best;
}

const anchors = {}; // trailId -> {x,y,text,confidence}
const missing = [];
const usedLabels = new Set();

for (const lab of labels) {
  const text = norm(lab.text);
  if (text.length < 4 || STOP.test(text)) continue;
  let best = null, bestS = 0;
  for (const t of trails) {
    const name = norm(t.name);
    let s = sim(text, name);
    // OCR truncations ("ROUNDAB") and merges ("VAGABOND TIN MAN"): containment
    // of a long-enough fragment is strong evidence
    if (s < 0.9 && (name.includes(text) || text.includes(name)) && Math.min(text.length, name.length) >= 5) {
      s = Math.max(s, 0.85);
    }
    if (s > bestS) { bestS = s; best = t; }
  }
  if (best && bestS >= 0.72) {
    // keep the highest-confidence anchor per trail
    if (!anchors[best.id] || anchors[best.id].confidence < lab.confidence) {
      anchors[best.id] = { x: lab.x, y: lab.y, text, matchScore: +bestS.toFixed(2), confidence: lab.confidence, angleDeg: lab.angleDeg ?? null };
    }
    usedLabels.add(lab);
  } else if (lab.confidence >= 75) {
    const line = nearestLineClass(lab.x, lab.y);
    if (line && line.dist <= 45) {
      missing.push({
        text,
        x: lab.x,
        y: lab.y,
        confidence: lab.confidence,
        inferredDifficulty: line.cls,
        lineDist: +line.dist.toFixed(0),
        peak: peakFor(lab.x, lab.y),
      });
    }
  }
}

writeFileSync(
  resolve(root, 'src/data/trailAnchors.json'),
  JSON.stringify({ _note: 'OCR-derived name anchors: normalized label centroid per matched trail id', anchors }, null, 1),
);

const matchedIds = Object.keys(anchors);
console.log(`labels: ${labels.length}  matched trails: ${matchedIds.length}/${trails.length}`);
console.log(`\nmatched (top 40 by confidence):`);
matchedIds
  .map((id) => ({ id, ...anchors[id] }))
  .sort((a, b) => b.confidence - a.confidence)
  .slice(0, 40)
  .forEach((a) => console.log(`  ${a.id.padEnd(24)} <- "${a.text}" (conf ${a.confidence}, sim ${a.matchScore})`));

// dedupe missing by text
const seen = new Set();
const missingDedup = missing.filter((mi) => (seen.has(mi.text) ? false : (seen.add(mi.text), true)));
console.log(`\nmap labels with NO roster match (candidate missing trails): ${missingDedup.length}`);
missingDedup
  .sort((a, b) => b.confidence - a.confidence)
  .forEach((mi) => console.log(`  "${mi.text}" @ ${mi.x.toFixed(3)},${mi.y.toFixed(3)} -> ${mi.inferredDifficulty} (line ${mi.lineDist}px, peak ${mi.peak}, conf ${mi.confidence})`));

if (process.argv.includes('--apply') && missingDedup.length) {
  const toId = (t) => t.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim().replace(/ +/g, '-');
  const title = (t) => t.toLowerCase().replace(/(^|[\s'-])[a-z]/g, (c) => c.toUpperCase());
  const existingIds = new Set(trails.map((t) => t.id));
  const lines = missingDedup
    .filter((mi) => !existingIds.has(toId(mi.text)))
    .map(
      (mi) =>
        `  { id: '${toId(mi.text)}', name: '${title(mi.text).replace(/'/g, "\\'")}', difficulty: '${mi.inferredDifficulty === 'black' ? 'black' : mi.inferredDifficulty}', peak: '${mi.peak}' },`,
    );
  const marker = '\n  // === ADDED FROM MAP OCR (see src/detection/LINES.md) ===\n';
  const updated = trailSrc.replace(/\n\];/, `${marker}${lines.join('\n')}\n];`);
  writeFileSync(resolve(root, 'src/data/trails.ts'), updated);
  console.log(`\napplied: ${lines.length} trails appended to src/data/trails.ts`);
}
