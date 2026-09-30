// Build the app's clickable trail paths from per-trail line proposals and
// human review decisions.
//
//   node scripts/applyTrailProposals.mjs [--resort killington]
//
// Inputs (src/data/resorts/<resort>/):
//   linePolylines.json   detected line pieces (percent coords)
//   trailProposals.json  proposed pieces per trail (tile reading)
//   trailReviews.json    review decisions; override proposals
// Output: trailPaths.json  {trails: {id: {segments, source}}}
//
// A review with status "confirmed" uses its own pieces plus any hand-drawn
// line (source "verified"); "no-line" (e.g. a glade drawn only as a label)
// becomes a clickable marker at the label when its position is known;
// "not-on-map" removes the trail from the map. Unreviewed trails use
// high/medium-confidence proposals (source "proposed"). Everything else gets
// no overlay rather than a guess.
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { jpegSize, resortPaths } from './lib/resort.mjs';

const R = resortPaths();
const read = (p) => JSON.parse(readFileSync(p, 'utf8'));
const { width: W, height: H } = jpegSize(R.map);
const MAX_DRAWN_STEP = 400; // source px

const pieces = new Map(read(R.polylines).polylines.map((p) => [p.id, p.points]));
const proposals = existsSync(R.proposals) ? read(R.proposals).trails : {};
const reviews = existsSync(R.reviews) ? read(R.reviews).reviews : {};

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

function joinEnds(segs) {
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
    if (!best) return segs;
    const a = best.ei ? segs[best.i] : [...segs[best.i]].reverse();
    const b = best.ej ? [...segs[best.j]].reverse() : segs[best.j];
    const merged = [...a, ...(best.d < 1 ? b.slice(1) : b)];
    segs = segs.filter((_, k) => k !== best.i && k !== best.j).concat([merged]);
  }
}

// Y-junctions: extend a free end onto the nearest point of another piece
function bridgeJunctions(segs) {
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
  return segs;
}

// Every detected line piece on the map, as a graph, so a gap between two
// parts of a trail can be bridged along the line actually drawn there (often
// a stretch assigned to another trail, or a piece nobody claimed).
const NETWORK_LINK = 25; // px: pieces this close are treated as connected
const network = (() => {
  const nodes = [];
  const edges = [];
  for (const pts of pieces.values()) {
    let prev = -1;
    for (const [x, y] of pts) {
      const id = nodes.push([(x * W) / 100, (y * H) / 100]) - 1;
      edges.push([]);
      if (prev >= 0) {
        const d = Math.hypot(nodes[id][0] - nodes[prev][0], nodes[id][1] - nodes[prev][1]);
        edges[id].push([prev, d]);
        edges[prev].push([id, d]);
      }
      prev = id;
    }
  }
  const cell = (p) => `${Math.floor(p[0] / NETWORK_LINK)},${Math.floor(p[1] / NETWORK_LINK)}`;
  const grid = new Map();
  nodes.forEach((p, i) => {
    const k = cell(p);
    if (!grid.has(k)) grid.set(k, []);
    grid.get(k).push(i);
  });
  const near = (p, r) => {
    const out = [];
    const cx = Math.floor(p[0] / NETWORK_LINK);
    const cy = Math.floor(p[1] / NETWORK_LINK);
    const span = Math.ceil(r / NETWORK_LINK);
    for (let dx = -span; dx <= span; dx++) {
      for (let dy = -span; dy <= span; dy++) {
        for (const i of grid.get(`${cx + dx},${cy + dy}`) ?? []) {
          const d = Math.hypot(nodes[i][0] - p[0], nodes[i][1] - p[1]);
          if (d <= r) out.push([i, d]);
        }
      }
    }
    return out;
  };
  nodes.forEach((p, i) => {
    for (const [j, d] of near(p, NETWORK_LINK)) if (j !== i) edges[i].push([j, d]);
  });
  return { nodes, edges, near };
})();

/** Shortest path along drawn lines from p to q, or null if longer than maxLen. */
function routeAlongLines(p, q, maxLen) {
  const start = network.near(p, NETWORK_LINK).sort((a, b) => a[1] - b[1])[0];
  const goal = network.near(q, NETWORK_LINK).sort((a, b) => a[1] - b[1])[0];
  if (!start || !goal) return null;
  const dist = new Map([[start[0], start[1]]]);
  const prev = new Map();
  const open = [[start[1], start[0]]];
  while (open.length) {
    open.sort((a, b) => a[0] - b[0]);
    const [d, u] = open.shift();
    if (d > (dist.get(u) ?? Infinity) || d > maxLen) continue;
    if (u === goal[0]) {
      const path = [q];
      for (let v = u; v !== undefined; v = prev.get(v)) path.push(network.nodes[v]);
      path.push(p);
      return d + goal[1] <= maxLen ? path.reverse() : null;
    }
    for (const [v, w] of network.edges[u]) {
      const nd = d + w;
      if (nd < (dist.get(v) ?? Infinity)) {
        dist.set(v, nd);
        prev.set(v, u);
        open.push([nd, v]);
      }
    }
  }
  return null;
}

// Remaining gaps between separate parts of one trail: follow the drawn line
// network when a route of reasonable length exists, else bridge short gaps
// straight. Parts further apart stay separate.
const ROUTE_SLACK = 1.6;
const ROUTE_EXTRA = 80;
const STRAIGHT_MAX = 180;
const PART_MAX = 400;

function connectParts(segs) {
  const parent = segs.map((_, i) => i);
  const find = (i) => (parent[i] === i ? i : (parent[i] = find(parent[i])));
  const touching = (a, b) =>
    [a[0], a.at(-1)].some((e) => nearestOnSegment(e, b).d < 2) || [b[0], b.at(-1)].some((e) => nearestOnSegment(e, a).d < 2);
  for (let i = 0; i < segs.length; i++)
    for (let j = i + 1; j < segs.length; j++) if (touching(segs[i], segs[j])) parent[find(i)] = find(j);

  const failed = new Set();
  for (;;) {
    let best = null;
    for (let i = 0; i < segs.length; i++) {
      for (let j = 0; j < segs.length; j++) {
        if (i === j || find(i) === find(j) || failed.has(`${find(i)}-${find(j)}`)) continue;
        for (const e of [segs[i][0], segs[i].at(-1)]) {
          const h = nearestOnSegment(e, segs[j]);
          if (h.d <= PART_MAX && (!best || h.d < best.d)) best = { i, j, p: e, q: h.q, d: h.d };
        }
      }
    }
    if (!best) return segs;
    const route = routeAlongLines(best.p, best.q, ROUTE_SLACK * best.d + ROUTE_EXTRA);
    if (route || best.d <= STRAIGHT_MAX) {
      segs.push(route ?? [best.p, best.q]);
      parent.push(parent.length);
      parent[find(best.i)] = find(best.j);
      parent[find(parent.length - 1)] = find(best.j);
    } else {
      failed.add(`${find(best.i)}-${find(best.j)}`);
      failed.add(`${find(best.j)}-${find(best.i)}`);
    }
  }
}

function joinSegments(segments) {
  let segs = segments.map((s) => s.map(([x, y]) => [(x * W) / 100, (y * H) / 100])).filter((s) => s.length > 1);
  segs = bridgeJunctions(joinEnds(segs));
  segs = joinEnds(connectParts(segs));
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
  R.paths,
  JSON.stringify({
    _note: 'Clickable trail overlays (percent coords). source: verified = human-reviewed; proposed = from tile reading, not yet reviewed.',
    trails: out,
  }) + '\n',
);
console.log(
  `trail paths: ${counts.verified} verified, ${counts.proposed} proposed, ` +
    `${counts.labels} label markers; ${counts.removed} with no overlay by review`,
);
