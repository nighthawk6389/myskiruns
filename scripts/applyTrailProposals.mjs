// Build the app's clickable trail paths from per-trail line proposals and
// human review decisions.
//
//   node scripts/applyTrailProposals.mjs
//
// Inputs:  src/data/linePolylines.json   detected line pieces (percent coords)
//          src/data/trailProposals.json  proposed pieces per trail (tile reading)
//          src/data/trailReviews.json    review decisions; override proposals
// Output:  src/data/trailPaths.json      {trails: {id: {segments, source}}}
//
// A review with status "confirmed" uses its own pieces plus any hand-drawn
// line (source "verified"); "no-line" (e.g. a glade drawn only as a label)
// becomes a clickable marker at the label when its position is known;
// "not-on-map" removes the trail from the map. Unreviewed trails use
// high/medium-confidence proposals (source "proposed"). Everything else gets
// no overlay rather than a guess.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => JSON.parse(readFileSync(resolve(root, p), 'utf8'));
const W = 4572;
const H = 2704;
const MAX_DRAWN_STEP = 400; // source px

const pieces = new Map(read('src/data/linePolylines.json').polylines.map((p) => [p.id, p.points]));
const proposals = read('src/data/trailProposals.json').trails;
const reviews = read('src/data/trailReviews.json').reviews;

const out = {};
const counts = { verified: 0, proposed: 0, labels: 0, removed: 0 };
for (const id of new Set([...Object.keys(proposals), ...Object.keys(reviews)])) {
  const r = reviews[id];
  const p = proposals[id];
  let ids = [];
  let drawn = [];
  let source;
  if (r) {
    if (r.status === 'no-line' && r.labelAt) {
      out[id] = { segments: [], label: r.labelAt, source: 'verified' };
      counts.labels++;
      continue;
    }
    if (r.status !== 'confirmed') {
      if (r.status !== 'skip') counts.removed++;
      if (r.status !== 'skip' || !p) continue;
      ids = p.polylines;
      source = 'proposed';
    } else {
      ids = r.polylines ?? [];
      drawn = r.drawn ?? [];
      source = 'verified';
    }
  } else if (p && (p.confidence === 'high' || p.confidence === 'medium')) {
    ids = p.polylines;
    source = 'proposed';
  } else {
    continue;
  }
  const segments = ids.filter((i) => pieces.has(i)).map((i) => pieces.get(i));
  // hand-drawn points are in source pixels; the review tool records one
  // stroke, so a long jump means the reviewer started a separate stretch
  const strokes = [[]];
  drawn.forEach((q, i) => {
    const prev = drawn[i - 1];
    if (prev && Math.hypot(q[0] - prev[0], q[1] - prev[1]) > MAX_DRAWN_STEP) strokes.push([]);
    strokes.at(-1).push(q);
  });
  for (const stroke of strokes) {
    if (stroke.length < 2) continue;
    segments.push(stroke.map(([x, y]) => [+(100 * x / W).toFixed(2), +(100 * y / H).toFixed(2)]));
  }
  if (!segments.length) continue;
  out[id] = { segments, source };
  counts[source]++;
}

writeFileSync(
  resolve(root, 'src/data/trailPaths.json'),
  JSON.stringify({
    _note: 'Clickable trail overlays (percent coords). source: verified = human-reviewed; proposed = from tile reading, not yet reviewed.',
    trails: out,
  }) + '\n',
);
console.log(
  `trail paths: ${counts.verified} verified, ${counts.proposed} proposed, ` +
    `${counts.labels} label markers; ${counts.removed} with no overlay by review`,
);
