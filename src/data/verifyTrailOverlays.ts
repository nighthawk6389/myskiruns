/**
 * Verification tool for trail overlay positions.
 * Run with: npx tsx src/data/verifyTrailOverlays.ts
 *
 * Checks:
 * 1. Every trail in trails.ts has a coordinate entry
 * 2. Every coordinate entry corresponds to a real trail
 * 3. Each trail's coordinates fall within its peak's region
 * 4. No two trails are too close together (minimum distance check)
 * 5. Peak regions don't have excessive overlap
 */

import { trails, peaks, getTrailsByPeak } from './trails';
import { TRAIL_COORDINATES, PEAK_REGIONS } from './trailCoordinates';

interface Issue {
  severity: 'error' | 'warning';
  message: string;
}

const issues: Issue[] = [];
let passCount = 0;
let checkCount = 0;

function check(description: string, pass: boolean, errorMsg: string, severity: 'error' | 'warning' = 'error') {
  checkCount++;
  if (pass) {
    passCount++;
  } else {
    issues.push({ severity, message: `${description}: ${errorMsg}` });
  }
}

// ─── CHECK 1: Every trail has coordinates ───
console.log('\n═══ CHECK 1: Every trail has coordinates ═══');
const trailIds = new Set(trails.map(t => t.id));
const coordIds = new Set(Object.keys(TRAIL_COORDINATES));
const missingCoords: string[] = [];
const extraCoords: string[] = [];

for (const trail of trails) {
  const has = TRAIL_COORDINATES[trail.id] != null;
  check(
    `Trail "${trail.name}" (${trail.id})`,
    has,
    `Missing coordinates for trail "${trail.name}" (${trail.id}, peak: ${trail.peak})`
  );
  if (!has) missingCoords.push(trail.id);
}

if (missingCoords.length === 0) {
  console.log(`  ✅ All ${trails.length} trails have coordinates`);
} else {
  console.log(`  ❌ ${missingCoords.length} trails missing coordinates:`);
  for (const id of missingCoords) {
    const t = trails.find(t => t.id === id)!;
    console.log(`     - ${t.name} (${id}, peak: ${t.peak})`);
  }
}

// ─── CHECK 2: No orphan coordinates ───
console.log('\n═══ CHECK 2: No orphan coordinate entries ═══');
for (const id of coordIds) {
  const exists = trailIds.has(id);
  check(`Coord "${id}"`, exists, `Coordinate entry "${id}" has no matching trail`);
  if (!exists) extraCoords.push(id);
}

if (extraCoords.length === 0) {
  console.log(`  ✅ All ${coordIds.size} coordinate entries match real trails`);
} else {
  console.log(`  ❌ ${extraCoords.length} orphan coordinate entries:`);
  for (const id of extraCoords) {
    console.log(`     - ${id}`);
  }
}

// ─── CHECK 3: Every peak has a region ───
console.log('\n═══ CHECK 3: Every peak has a region ═══');
for (const peak of peaks) {
  const has = PEAK_REGIONS[peak.id] != null;
  check(`Peak region "${peak.name}"`, has, `Missing region for peak "${peak.name}" (${peak.id})`);
}
const allPeaksHaveRegions = peaks.every(p => PEAK_REGIONS[p.id] != null);
if (allPeaksHaveRegions) {
  console.log(`  ✅ All ${peaks.length} peaks have regions defined`);
}

// ─── CHECK 4: Trail coordinates within peak region ───
console.log('\n═══ CHECK 4: Trail coordinates within peak regions ═══');
let inRegionCount = 0;
let outOfRegionCount = 0;

for (const trail of trails) {
  const coord = TRAIL_COORDINATES[trail.id];
  const region = PEAK_REGIONS[trail.peak];
  if (!coord || !region) continue;

  // Allow a small margin (2%) outside region bounds for trails near edges
  const margin = 2;
  const inRegion =
    coord.x >= region.xMin - margin &&
    coord.x <= region.xMax + margin &&
    coord.y >= region.yMin - margin &&
    coord.y <= region.yMax + margin;

  check(
    `Trail "${trail.name}" in ${trail.peak} region`,
    inRegion,
    `Trail "${trail.name}" (${trail.id}) at (${coord.x}, ${coord.y}) is outside ${trail.peak} region [x:${region.xMin}-${region.xMax}, y:${region.yMin}-${region.yMax}]`
  );

  if (inRegion) {
    inRegionCount++;
  } else {
    outOfRegionCount++;
  }
}

if (outOfRegionCount === 0) {
  console.log(`  ✅ All ${inRegionCount} trails are within their peak regions`);
} else {
  console.log(`  ❌ ${outOfRegionCount} trails are outside their peak regions`);
}

// ─── CHECK 5: Minimum distance between trail dots ───
console.log('\n═══ CHECK 5: Minimum distance between trails ═══');
const MIN_DISTANCE = 1.5; // percentage points
const tooCloseTrails: { a: string; b: string; dist: number }[] = [];

const coordEntries = Object.entries(TRAIL_COORDINATES);
for (let i = 0; i < coordEntries.length; i++) {
  for (let j = i + 1; j < coordEntries.length; j++) {
    const [idA, posA] = coordEntries[i];
    const [idB, posB] = coordEntries[j];
    const dx = posA.x - posB.x;
    const dy = posA.y - posB.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < MIN_DISTANCE) {
      tooCloseTrails.push({ a: idA, b: idB, dist });
    }
  }
}

check(
  'Minimum distance check',
  tooCloseTrails.length === 0,
  `${tooCloseTrails.length} trail pairs are too close (< ${MIN_DISTANCE}% apart)`,
  'warning'
);

if (tooCloseTrails.length === 0) {
  console.log(`  ✅ All trails have adequate spacing (>= ${MIN_DISTANCE}% apart)`);
} else {
  console.log(`  ⚠️  ${tooCloseTrails.length} trail pairs are too close:`);
  for (const pair of tooCloseTrails.slice(0, 20)) {
    const trailA = trails.find(t => t.id === pair.a);
    const trailB = trails.find(t => t.id === pair.b);
    console.log(`     - "${trailA?.name}" & "${trailB?.name}" dist=${pair.dist.toFixed(2)}%`);
  }
  if (tooCloseTrails.length > 20) {
    console.log(`     ... and ${tooCloseTrails.length - 20} more`);
  }
}

// ─── CHECK 6: Trails from same peak are clustered together ───
console.log('\n═══ CHECK 6: Peak trail clustering ═══');
for (const peak of peaks) {
  const peakTrails = getTrailsByPeak(peak.id);
  const coords = peakTrails
    .map(t => TRAIL_COORDINATES[t.id])
    .filter(Boolean);

  if (coords.length < 2) continue;

  const avgX = coords.reduce((s, c) => s + c.x, 0) / coords.length;
  const avgY = coords.reduce((s, c) => s + c.y, 0) / coords.length;

  // Check that no trail is more than 20% away from the peak's centroid
  const MAX_SPREAD = 25;
  let maxDist = 0;
  let farthestTrail = '';

  for (const trail of peakTrails) {
    const coord = TRAIL_COORDINATES[trail.id];
    if (!coord) continue;
    const dist = Math.sqrt((coord.x - avgX) ** 2 + (coord.y - avgY) ** 2);
    if (dist > maxDist) {
      maxDist = dist;
      farthestTrail = trail.name;
    }
  }

  check(
    `${peak.name} clustering`,
    maxDist <= MAX_SPREAD,
    `${peak.name}: trail "${farthestTrail}" is ${maxDist.toFixed(1)}% from centroid (max: ${MAX_SPREAD}%)`,
    'warning'
  );

  console.log(`  ${peak.name}: centroid=(${avgX.toFixed(1)}, ${avgY.toFixed(1)}), max spread=${maxDist.toFixed(1)}%, ${coords.length} trails`);
}

// ─── CHECK 7: No trail from peak A is closer to peak B's centroid ───
console.log('\n═══ CHECK 7: Trail-to-peak assignment validation ═══');
const peakCentroids: Record<string, { x: number; y: number }> = {};
for (const peak of peaks) {
  const peakTrails = getTrailsByPeak(peak.id);
  const coords = peakTrails
    .map(t => TRAIL_COORDINATES[t.id])
    .filter(Boolean);
  if (coords.length === 0) continue;
  peakCentroids[peak.id] = {
    x: coords.reduce((s, c) => s + c.x, 0) / coords.length,
    y: coords.reduce((s, c) => s + c.y, 0) / coords.length,
  };
}

let misassignedCount = 0;
for (const trail of trails) {
  const coord = TRAIL_COORDINATES[trail.id];
  if (!coord) continue;

  const assignedCentroid = peakCentroids[trail.peak];
  if (!assignedCentroid) continue;

  const distToAssigned = Math.sqrt((coord.x - assignedCentroid.x) ** 2 + (coord.y - assignedCentroid.y) ** 2);

  let closerPeak: string | null = null;
  for (const peak of peaks) {
    if (peak.id === trail.peak) continue;
    const otherCentroid = peakCentroids[peak.id];
    if (!otherCentroid) continue;
    const distToOther = Math.sqrt((coord.x - otherCentroid.x) ** 2 + (coord.y - otherCentroid.y) ** 2);
    // Only flag if significantly closer to another peak (>30% closer)
    if (distToOther < distToAssigned * 0.7) {
      closerPeak = peak.id;
      break;
    }
  }

  if (closerPeak) {
    misassignedCount++;
    check(
      `Trail "${trail.name}" assignment`,
      false,
      `Trail "${trail.name}" (${trail.id}) assigned to ${trail.peak} but positioned much closer to ${closerPeak}`,
      'warning'
    );
  }
}

if (misassignedCount === 0) {
  console.log(`  ✅ All trails are positioned near their assigned peak's area`);
} else {
  console.log(`  ⚠️  ${misassignedCount} trails may be positioned near the wrong peak`);
}

// ─── SUMMARY ───
console.log('\n' + '═'.repeat(50));
const errors = issues.filter(i => i.severity === 'error');
const warnings = issues.filter(i => i.severity === 'warning');

console.log(`\n📊 RESULTS: ${passCount}/${checkCount} checks passed`);
if (errors.length > 0) {
  console.log(`\n❌ ${errors.length} ERRORS:`);
  for (const e of errors) {
    console.log(`   ${e.message}`);
  }
}
if (warnings.length > 0) {
  console.log(`\n⚠️  ${warnings.length} WARNINGS:`);
  for (const w of warnings) {
    console.log(`   ${w.message}`);
  }
}
if (errors.length === 0 && warnings.length === 0) {
  console.log('\n✅ ALL CHECKS PASSED! Trail overlays are correctly positioned.');
}

// Exit with error code if there are errors
process.exit(errors.length > 0 ? 1 : 0);
