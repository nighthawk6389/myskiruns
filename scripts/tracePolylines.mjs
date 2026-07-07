// tracePolylines.mjs — vectorize the trail-line detector's 1px centerline
// skeletons into simplified polylines.
//
// Pipeline (per class, standard skeleton-graph vectorization):
//   1. build the skeleton graph: nodes = pixel clusters with degree != 2
//      (endpoints deg 1, junctions deg >= 3), edges = 8-connected pixel
//      chains between nodes; pure cycles get an arbitrary start
//   2. merge edges through junctions by straightest continuation (end
//      tangents over the last ~12 chain pixels, pair when the turn angle
//      is > ~140 deg) so X crossings resolve into two through-paths
//   3. drop tiny fragments (< 40 px) unless they connect two junctions
//   4. Douglas-Peucker simplification (epsilon 2.5 px)
//   5. percent coordinates, 2 decimals
//
// Output: src/data/linePolylines.json  +  audit render /tmp/explore2/polylines_audit.jpg

import { writeFileSync, mkdirSync } from 'node:fs';
import { detectTrailLines, CLS } from './lib/lineDetector.mjs';
import { decodeJpeg, downscale, encodeJpeg } from './lib/image.mjs';

const MAP = 'public/killington-trail-map.jpg';
const OUT_JSON = 'src/data/linePolylines.json';
const AUDIT = '/tmp/explore2/polylines_audit.jpg';

const TANGENT_WIN = 12; // chain pixels used to estimate an edge-end tangent
const CONTRACT_LEN = 12; // px: junction-junction edges shorter than this are
// contracted into one junction node (thinning splits an X crossing into a
// "bowtie" of two Y junctions joined by a short bar; contraction lets the two
// through-paths pair up at a single junction)
const MERGE_DOT = Math.cos((140 * Math.PI) / 180); // pair ends when dot < this (~-0.766)
const MIN_FRAG_LEN = 40; // px: shorter fragments dropped unless junction-to-junction
const DP_EPS = 2.5; // Douglas-Peucker tolerance, px

const CLASS_NAMES = { [CLS.green]: 'green', [CLS.blue]: 'blue', [CLS.black]: 'black' };

// ---------------------------------------------------------------- graph build

/** Extract the skeleton graph of a binary mask: node clusters + pixel-chain edges. */
function buildSkeletonGraph(bin, W, H) {
  const N = W * H;
  const OFF = [-W - 1, -W, -W + 1, -1, 1, W - 1, W, W + 1];
  // Branch count per pixel = CROSSING NUMBER: the number of connected groups
  // of set neighbors around the 8-ring. Raw 8-degree is wrong on a digital
  // skeleton — a staircase step (orthogonal+diagonal pixel pair) gives both
  // pixels degree 3 even though the curve passes straight through. Ring order:
  // N, NE, E, SE, S, SW, W, NW (consecutive ring cells are actually adjacent),
  // groups = number of 0->1 transitions in the circular sequence.
  const branches = new Uint8Array(N); // crossing number, 0..4
  {
    const ringOff = [-W, -W + 1, 1, W + 1, W, W - 1, -1, -W - 1];
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const p = y * W + x;
        if (!bin[p]) continue;
        const ring = new Uint8Array(8);
        for (let k = 0; k < 8; k++) {
          const q = p + ringOff[k];
          const qx = q % W, qy = (q / W) | 0;
          if (q < 0 || q >= N || Math.abs(qx - x) > 1 || Math.abs(qy - y) > 1) continue;
          ring[k] = bin[q];
        }
        let t = 0;
        for (let k = 0; k < 8; k++) if (!ring[k] && ring[(k + 1) & 7]) t++;
        branches[p] = t;
      }
    }
  }

  // Node pixels = branch count != 2 (endpoints 1, junctions >= 3, isolated 0).
  // Cluster 8-adjacent node pixels into single graph nodes (junction blobs).
  const nodeId = new Int32Array(N).fill(-1);
  const nodes = []; // { pixels: [p...], isJunction }
  for (let p = 0; p < N; p++) {
    if (!bin[p] || branches[p] === 2 || nodeId[p] !== -1) continue;
    const id = nodes.length;
    const pixels = [];
    let isJunction = false;
    const stack = [p];
    nodeId[p] = id;
    while (stack.length) {
      const q = stack.pop();
      pixels.push(q);
      if (branches[q] >= 3) isJunction = true;
      const qx = q % W, qy = (q / W) | 0;
      for (const o of OFF) {
        const r = q + o;
        const rx = r % W, ry = (r / W) | 0;
        if (Math.abs(rx - qx) > 1 || Math.abs(ry - qy) > 1) continue; // no wrap
        if (r < 0 || r >= N || !bin[r] || branches[r] === 2 || nodeId[r] !== -1) continue;
        nodeId[r] = id;
        stack.push(r);
      }
    }
    nodes.push({ pixels, isJunction });
  }

  // Walk chains from every node pixel along unvisited branch-2 pixels.
  const visited = new Uint8Array(N); // chain pixels consumed
  const edges = []; // { chain:[p...], nodeA, nodeB }
  // orthogonal neighbors first: on a staircase pair, taking the orthogonal
  // partner before the diagonal continuation walks BOTH pixels instead of
  // orphaning one
  const NB_OFF = [-W, W, -1, 1, -W - 1, -W + 1, W - 1, W + 1];
  const neighborsOf = (p) => {
    const res = [];
    const px = p % W, py = (p / W) | 0;
    for (const o of NB_OFF) {
      const q = p + o;
      const qx = q % W, qy = (q / W) | 0;
      if (q < 0 || q >= N || Math.abs(qx - px) > 1 || Math.abs(qy - py) > 1) continue;
      if (bin[q]) res.push(q);
    }
    return res;
  };

  const directPairs = new Set(); // dedupe node-to-node adjacency edges
  for (let id = 0; id < nodes.length; id++) {
    for (const np of nodes[id].pixels) {
      for (const q of neighborsOf(np)) {
        if (nodeId[q] !== -1 || visited[q]) continue; // chain starts only on deg-2 pixels
        // walk the chain
        const chain = [np, q];
        visited[q] = 1;
        let prev = np, cur = q, endNode = -1;
        for (;;) {
          let next = -1;
          let nodeNext = -1;
          for (const r of neighborsOf(cur)) {
            if (r === prev) continue;
            if (nodeId[r] !== -1) { if (nodeNext === -1) nodeNext = r; continue; }
            if (!visited[r] && next === -1) next = r;
          }
          if (nodeNext !== -1) {
            // prefer terminating at a node pixel
            chain.push(nodeNext);
            endNode = nodeId[nodeNext];
            break;
          }
          if (next === -1) { endNode = -1; break; } // dead end (shouldn't happen often)
          chain.push(next);
          visited[next] = 1;
          prev = cur; cur = next;
        }
        if (endNode === -1) {
          // chain died without reaching a node (numeric oddity): make a
          // degenerate terminal node so the edge still exists
          endNode = nodes.length;
          nodes.push({ pixels: [chain[chain.length - 1]], isJunction: false });
        }
        // discard micro self-loops: a chain that leaves a junction cluster and
        // immediately re-enters it is thinning glue inside the junction area
        if (endNode === id && chain.length <= 5) continue;
        edges.push({ chain, nodeA: id, nodeB: endNode });
      }
      // direct node-to-node adjacency (chain of zero interior pixels)
      for (const q of neighborsOf(np)) {
        const qid = nodeId[q];
        if (qid === -1 || qid === id || qid < id) continue;
        const key = `${id}:${qid}`;
        if (directPairs.has(key)) continue; // one edge per cluster pair
        directPairs.add(key);
        edges.push({ chain: [np, q], nodeA: id, nodeB: qid });
      }
    }
  }

  // Pure cycles: leftover unvisited branch-2 pixels form closed loops.
  const cycles = [];
  for (let p = 0; p < N; p++) {
    if (!bin[p] || branches[p] !== 2 || visited[p] || nodeId[p] !== -1) continue;
    const chain = [p];
    visited[p] = 1;
    let prev = -1, cur = p;
    for (;;) {
      let next = -1;
      for (const r of neighborsOf(cur)) {
        if (r === prev || visited[r]) continue;
        next = r;
        break;
      }
      if (next === -1) break;
      chain.push(next);
      visited[next] = 1;
      prev = cur; cur = next;
    }
    chain.push(p); // close the loop
    cycles.push(chain);
  }

  return { nodes, edges, cycles };
}

// ------------------------------------------------------- junction-merge logic

/**
 * Contract short junction-to-junction edges: union the two junction nodes and
 * drop the bar edge (its few pixels become part of the junction; the gap is
 * far below the DP tolerance scale). Returns { nodes, edges, contracted }.
 */
function contractShortJunctionBars(nodes, edges, W) {
  const parent = nodes.map((_, i) => i);
  const find = (i) => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; } return i; };
  let contracted = 0;
  for (const e of edges) {
    if (e.nodeA === e.nodeB) continue;
    if (!nodes[e.nodeA].isJunction || !nodes[e.nodeB].isJunction) continue;
    const pts = e.chain.map((p) => [p % W, (p / W) | 0]);
    if (chainLength(pts) >= CONTRACT_LEN) continue;
    const a = find(e.nodeA), b = find(e.nodeB);
    if (a !== b) { parent[b] = a; contracted++; }
    e.dead = true;
  }
  if (!contracted) return { nodes, edges, contracted };
  // rebuild node list keyed by root
  const rootToNew = new Map();
  const newNodes = [];
  for (let i = 0; i < nodes.length; i++) {
    const r = find(i);
    if (!rootToNew.has(r)) { rootToNew.set(r, newNodes.length); newNodes.push({ pixels: [], isJunction: false }); }
    const nn = newNodes[rootToNew.get(r)];
    nn.pixels.push(...nodes[i].pixels);
    nn.isJunction = nn.isJunction || nodes[i].isJunction;
  }
  const newEdges = [];
  for (const e of edges) {
    if (e.dead) continue;
    newEdges.push({ chain: e.chain, nodeA: rootToNew.get(find(e.nodeA)), nodeB: rootToNew.get(find(e.nodeB)) });
  }
  return { nodes: newNodes, edges: newEdges, contracted };
}

/** Unit tangent pointing away from the given end of a pixel chain. */
function endTangent(chain, W, fromStart) {
  const n = chain.length;
  const k = Math.min(TANGENT_WIN, n - 1);
  const a = fromStart ? chain[0] : chain[n - 1];
  const b = fromStart ? chain[k] : chain[n - 1 - k];
  let dx = (b % W) - (a % W), dy = ((b / W) | 0) - ((a / W) | 0);
  const d = Math.hypot(dx, dy);
  if (d < 1e-9) return [1, 0];
  return [dx / d, dy / d];
}

/**
 * At each junction, pair incident edge ends whose away-tangents are most
 * anti-parallel (turn angle > ~140 deg), greedily best-first.
 * Returns { links: Map endKey->endKey, mergeCount }.
 */
function pairAtJunctions(nodes, edges, W) {
  // collect edge ends per node
  const endsAt = nodes.map(() => []);
  edges.forEach((e, i) => {
    endsAt[e.nodeA].push({ edge: i, end: 0 });
    endsAt[e.nodeB].push({ edge: i, end: 1 });
  });
  const links = new Map();
  let mergeCount = 0;
  for (let id = 0; id < nodes.length; id++) {
    if (!nodes[id].isJunction) continue;
    const ends = endsAt[id];
    if (ends.length < 2) continue;
    const tangents = ends.map((e) => endTangent(edges[e.edge].chain, W, e.end === 0));
    const cand = [];
    for (let i = 0; i < ends.length; i++) {
      for (let j = i + 1; j < ends.length; j++) {
        if (ends[i].edge === ends[j].edge) continue; // don't self-pair a loop
        const dot = tangents[i][0] * tangents[j][0] + tangents[i][1] * tangents[j][1];
        if (dot < MERGE_DOT) cand.push({ i, j, dot });
      }
    }
    cand.sort((a, b) => a.dot - b.dot); // most anti-parallel first
    const used = new Set();
    for (const { i, j } of cand) {
      if (used.has(i) || used.has(j)) continue;
      const ki = `${ends[i].edge}:${ends[i].end}`;
      const kj = `${ends[j].edge}:${ends[j].end}`;
      if (links.has(ki) || links.has(kj)) continue; // end already paired elsewhere
      links.set(ki, kj);
      links.set(kj, ki);
      used.add(i); used.add(j);
      mergeCount++;
    }
  }
  return { links, mergeCount };
}

/** Follow pair-links to join edges into merged pixel chains. */
function assemblePolylines(nodes, edges, links) {
  const consumed = new Uint8Array(edges.length);
  const polylines = []; // { chain:[p...], endNodes:[a,b] }

  const traverse = (startEdge, startEnd) => {
    const chain = [];
    let e = startEdge, s = startEnd;
    const startNode = s === 0 ? edges[e].nodeA : edges[e].nodeB;
    let lastNode = startNode;
    for (;;) {
      consumed[e] = 1;
      const c = edges[e].chain;
      const oriented = s === 0 ? c : [...c].reverse();
      const from = chain.length && chain[chain.length - 1] === oriented[0] ? 1 : 0;
      for (let k = from; k < oriented.length; k++) chain.push(oriented[k]);
      const t = 1 - s;
      lastNode = t === 0 ? edges[e].nodeA : edges[e].nodeB;
      const link = links.get(`${e}:${t}`);
      if (!link) break;
      const [ne, ns] = link.split(':').map(Number);
      if (consumed[ne]) break; // closed merge loop
      e = ne; s = ns;
    }
    return { chain, endNodes: [startNode, lastNode] };
  };

  // start from ends with no link (true polyline termini)
  for (let e = 0; e < edges.length; e++) {
    if (consumed[e]) continue;
    for (const s of [0, 1]) {
      if (!links.has(`${e}:${s}`)) {
        if (!consumed[e]) polylines.push(traverse(e, s));
        break;
      }
    }
  }
  // leftover edges belong to fully-linked loops: start anywhere
  for (let e = 0; e < edges.length; e++) {
    if (!consumed[e]) polylines.push(traverse(e, 0));
  }
  return polylines;
}

// -------------------------------------------------------------- simplification

function chainLength(pts) {
  let len = 0;
  for (let k = 1; k < pts.length; k++) {
    len += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  }
  return len;
}

/** Iterative Douglas-Peucker on [[x,y],...]. */
function douglasPeucker(pts, eps) {
  const n = pts.length;
  if (n <= 2) return pts.slice();
  const keep = new Uint8Array(n);
  keep[0] = keep[n - 1] = 1;
  const stack = [[0, n - 1]];
  while (stack.length) {
    const [a, b] = stack.pop();
    const [ax, ay] = pts[a], [bx, by] = pts[b];
    const dx = bx - ax, dy = by - ay;
    const dd = dx * dx + dy * dy;
    let maxD = -1, maxI = -1;
    for (let i = a + 1; i < b; i++) {
      const [px, py] = pts[i];
      let d;
      if (dd < 1e-12) d = Math.hypot(px - ax, py - ay);
      else {
        const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / dd));
        d = Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
      }
      if (d > maxD) { maxD = d; maxI = i; }
    }
    if (maxD > eps) {
      keep[maxI] = 1;
      stack.push([a, maxI], [maxI, b]);
    }
  }
  const out = [];
  for (let i = 0; i < n; i++) if (keep[i]) out.push(pts[i]);
  return out;
}

// ----------------------------------------------------------------------- main

let centerMask, W, H;
if (process.env.LINE_MASK_CACHE) {
  // dev convenience: reuse a cached centerMask (raw bytes + dims.json in the
  // given directory) instead of re-running the ~9s detector
  const { readFileSync } = await import('node:fs');
  const dims = JSON.parse(readFileSync(`${process.env.LINE_MASK_CACHE}/dims.json`, 'utf8'));
  W = dims.W; H = dims.H;
  centerMask = new Uint8Array(readFileSync(`${process.env.LINE_MASK_CACHE}/centerMask.bin`));
} else {
  console.time('detect');
  const det = await detectTrailLines(MAP);
  console.timeEnd('detect');
  ({ centerMask, width: W, height: H } = det);
}

const stats = [];
const result = [];
let cycleCount = 0, droppedTiny = 0, keptJJ = 0;

for (const target of [CLS.green, CLS.blue, CLS.black]) {
  const clsName = CLASS_NAMES[target];
  const bin = new Uint8Array(W * H);
  let px = 0;
  for (let p = 0; p < W * H; p++) if (centerMask[p] === target) { bin[p] = 1; px++; }

  const g = buildSkeletonGraph(bin, W, H);
  const cycles = g.cycles;
  const { nodes, edges, contracted } = contractShortJunctionBars(g.nodes, g.edges, W);
  const { links, mergeCount } = pairAtJunctions(nodes, edges, W);
  const merged = assemblePolylines(nodes, edges, links);
  cycleCount += cycles.length;

  const candidates = [];
  for (const m of merged) {
    const bothJunctions = m.endNodes.every((id) => nodes[id] && nodes[id].isJunction);
    candidates.push({ chain: m.chain, bothJunctions });
  }
  for (const c of cycles) candidates.push({ chain: c, bothJunctions: false });

  let kept = 0;
  for (const cand of candidates) {
    const pts = cand.chain.map((p) => [p % W, (p / W) | 0]);
    const lengthPx = chainLength(pts);
    if (lengthPx < MIN_FRAG_LEN && !cand.bothJunctions) { droppedTiny++; continue; }
    if (lengthPx < MIN_FRAG_LEN && cand.bothJunctions) keptJJ++;
    const simp = douglasPeucker(pts, DP_EPS);
    // percent coords, 2 decimals, dedupe consecutive rounded duplicates
    const pct = [];
    for (const [x, y] of simp) {
      const q = [Math.round((x / W) * 10000) / 100, Math.round((y / H) * 10000) / 100];
      const last = pct[pct.length - 1];
      if (last && last[0] === q[0] && last[1] === q[1]) continue;
      pct.push(q);
    }
    if (pct.length < 2) { droppedTiny++; continue; }
    result.push({ cls: clsName, lengthPx: Math.round(lengthPx), points: pct });
    kept++;
  }

  const junctions = nodes.filter((n) => n.isJunction).length;
  const endpoints = nodes.length - junctions;
  stats.push({ clsName, px, endpoints, junctions, edges: edges.length, cycles: cycles.length, contracted, mergeCount, kept });
}

result.sort((a, b) => b.lengthPx - a.lengthPx);
const polylines = result.map((r, i) => ({ id: i, cls: r.cls, lengthPx: r.lengthPx, points: r.points }));
writeFileSync(OUT_JSON, JSON.stringify({ polylines }));
console.log(`wrote ${OUT_JSON}: ${polylines.length} polylines`);

// ------------------------------------------------------------------ reporting

for (const s of stats) {
  const lens = polylines.filter((p) => p.cls === s.clsName).map((p) => p.lengthPx).sort((a, b) => a - b);
  const median = lens.length ? lens[(lens.length / 2) | 0] : 0;
  const max = lens.length ? lens[lens.length - 1] : 0;
  console.log(
    `${s.clsName}: skelPx=${s.px} endpoints=${s.endpoints} junctions=${s.junctions} edges=${s.edges} ` +
    `cycles=${s.cycles} contractedBars=${s.contracted} junctionMerges=${s.mergeCount} ` +
    `polylines=${lens.length} medianLen=${median} maxLen=${max}`
  );
}
console.log(`droppedTiny=${droppedTiny} keptShortJunctionToJunction=${keptJJ} cycles=${cycleCount}`);

// ---------------------------------------------------------------- audit image

mkdirSync('/tmp/explore2', { recursive: true });
const full = decodeJpeg(MAP);
const small = downscale(full, 1400);
const sw = small.width, sh = small.height;
// fade the base map toward white so strokes pop
for (let i = 0; i < small.data.length; i += 4) {
  small.data[i] = (small.data[i] * 0.35 + 255 * 0.65) | 0;
  small.data[i + 1] = (small.data[i + 1] * 0.35 + 255 * 0.65) | 0;
  small.data[i + 2] = (small.data[i + 2] * 0.35 + 255 * 0.65) | 0;
}
const PALETTE = {
  green: [[0, 130, 0], [0, 220, 90], [130, 200, 0]],
  blue: [[10, 40, 200], [0, 170, 255], [130, 110, 255]],
  black: [[0, 0, 0], [150, 150, 150], [200, 90, 0]],
};
function plot(x, y, rgb) {
  for (let dy = 0; dy < 2; dy++) {
    for (let dx = 0; dx < 2; dx++) {
      const px2 = x + dx, py2 = y + dy;
      if (px2 < 0 || py2 < 0 || px2 >= sw || py2 >= sh) continue;
      const i = (py2 * sw + px2) * 4;
      small.data[i] = rgb[0]; small.data[i + 1] = rgb[1]; small.data[i + 2] = rgb[2];
    }
  }
}
function drawSeg(x0, y0, x1, y1, rgb) {
  const steps = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0)));
  for (let t = 0; t <= steps; t++) {
    plot(Math.round(x0 + ((x1 - x0) * t) / steps), Math.round(y0 + ((y1 - y0) * t) / steps), rgb);
  }
}
for (const p of polylines) {
  const rgb = PALETTE[p.cls][p.id % 3];
  for (let k = 1; k < p.points.length; k++) {
    const [ax, ay] = p.points[k - 1], [bx, by] = p.points[k];
    drawSeg((ax / 100) * sw, (ay / 100) * sh, (bx / 100) * sw, (by / 100) * sh, rgb);
  }
}
encodeJpeg(small, AUDIT, 90);
console.log(`wrote ${AUDIT}`);
