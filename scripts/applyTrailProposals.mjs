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

// Detected pieces break at junctions, markers and inline labels, so one
// trail arrives as several polylines with small gaps. Join them so the trail
// draws as continuous lines: ends closer than JOIN_NEAR always join; ends up
// to JOIN_FAR apart join when both pieces point at each other (the gap left by
// a label printed along the line); an end that stops just short of the middle
// of another piece is extended to touch it (Y-junctions). Wider gaps are real
// separate sections and stay apart. Distances are source px.
const JOIN_NEAR = 40;
const JOIN_FAR = 250;
const COLLINEAR = Math.cos((45 * Math.PI) / 180);

function outward(s, atEnd) {
  const n = s.length;
  const e = atEnd ? s[n - 1] : s[0];
  const k = atEnd ? s[Math.max(0, n - 4)] : s[Math.min(n - 1, 3)];
  const dx = e[0] - k[0];
  const dy = e[1] - k[1];
  const len = Math.hypot(dx, dy) || 1;
  return [dx / len, dy / len];
}

function nearestOnSegment(p, s) {
  let best = { d: Infinity, q: null };
  for (let i = 1; i < s.length; i++) {
    const [ax, ay] = s[i - 1];
    const [bx, by] = s[i];
    const dx = bx - ax;
    const dy = by - ay;
    const len = dx * dx + dy * dy;
    const t = len ? Math.max(0, Math.min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / len)) : 0;
    const q = [ax + t * dx, ay + t * dy];
    const d = Math.hypot(p[0] - q[0], p[1] - q[1]);
    if (d < best.d) best = { d, q };
  }
  return best;
}

function joinSegments(segments) {
  let segs = segments.map((s) => s.map(([x, y]) => [(x * W) / 100, (y * H) / 100])).filter((s) => s.length > 1);
  for (;;) {
    let best = null;
    for (let i = 0; i < segs.length; i++) {
      for (let j = i + 1; j < segs.length; j++) {
        for (const ei of [false, true]) {
          for (const ej of [false, true]) {
            const p = ei ? segs[i].at(-1) : segs[i][0];
            const q = ej ? segs[j].at(-1) : segs[j][0];
            const d = Math.hypot(q[0] - p[0], q[1] - p[1]);
            if (d > JOIN_FAR || (best && d >= best.d)) continue;
            if (d > JOIN_NEAR) {
              const c = [(q[0] - p[0]) / d, (q[1] - p[1]) / d];
              const di = outward(segs[i], ei);
              const dj = outward(segs[j], ej);
              if (di[0] * c[0] + di[1] * c[1] < COLLINEAR || -(dj[0] * c[0] + dj[1] * c[1]) < COLLINEAR) continue;
            }
            best = { i, j, ei, ej, d };
          }
        }
      }
    }
    if (!best) break;
    const a = best.ei ? segs[best.i] : [...segs[best.i]].reverse();
    const b = best.ej ? [...segs[best.j]].reverse() : segs[best.j];
    const merged = [...a, ...(best.d < 1 ? b.slice(1) : b)];
    segs = segs.filter((_, k) => k !== best.i && k !== best.j).concat([merged]);
  }
  // Y-junctions: extend a free end onto the nearest point of another piece
  for (const s of segs) {
    for (const atEnd of [false, true]) {
      const p = atEnd ? s.at(-1) : s[0];
      let hit = { d: Infinity, q: null };
      for (const o of segs) {
        if (o === s) continue;
        const h = nearestOnSegment(p, o);
        if (h.d < hit.d) hit = h;
      }
      if (hit.d > 1 && hit.d <= JOIN_NEAR) {
        if (atEnd) s.push(hit.q);
        else s.unshift(hit.q);
      }
    }
  }
  return segs.map((s) => s.map(([x, y]) => [+((100 * x) / W).toFixed(2), +((100 * y) / H).toFixed(2)]));
}

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
  out[id] = { segments: joinSegments(segments), source };
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
