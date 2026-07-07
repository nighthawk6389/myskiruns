// Pass-2 anchor enrichment: dictionary-constrained OCR for roster trails that
// scripts/extractLabels.mjs + reconcileTrails.mjs left unanchored.
//
// Key idea: we know the exact names we are looking for, so a low-confidence
// read like "JWISTER" is safe to accept when it uniquely matches one
// UNANCHORED roster name (sim >= 0.68) with no runner-up within 0.12.
//
// Two candidate sources:
//   a) re-detected label blocks that pass 1 rejected: re-OCR them with extra
//      variants (contrast boost, non-ink crop, inverted, vertical flips)
//   b) pass-1 labels in src/data/labelAnchors.json that reconcile could not
//      match at 0.72: retry with the dictionary-constrained rule
//
// Usage:
//   node scripts/enrichAnchors.mjs                 # propose + contact sheets
//   node scripts/enrichAnchors.mjs --commit id1,id2,...   # append verified
//
// Proposals + sheets go to the scratchpad dir; --commit appends the accepted
// subset to src/data/labelAnchors.json with "pass": 2 (existing entries are
// never touched). Then re-run: node scripts/reconcileTrails.mjs
import sharp from 'sharp';
import { createWorker, PSM } from 'tesseract.js';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { decodeJpeg, encodeJpeg } from './lib/image.mjs';
import { cropScaled, drawText } from './lib/draw.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MAP = resolve(root, 'public/killington-trail-map.jpg');
const ANCHORS = resolve(root, 'src/data/labelAnchors.json');
const SCRATCH = '/tmp/claude-0/-home-user-myskiruns/1c44806e-766f-55ff-af2b-8d49ae9b9cf4/scratchpad';
const PROPOSALS = `${SCRATCH}/enrich_proposals.json`;

// ---------------------------------------------------------------- commit mode
if (process.argv.includes('--commit')) {
  const ids = (process.argv[process.argv.indexOf('--commit') + 1] ?? '').split(',').filter(Boolean);
  const props = JSON.parse(readFileSync(PROPOSALS, 'utf8'));
  const accepted = props.filter((p) => ids.includes(p.trailId));
  const doc = JSON.parse(readFileSync(ANCHORS, 'utf8'));
  const before = doc.labels.length;
  for (const p of accepted) {
    doc.labels.push({
      text: p.text, x: p.x, y: p.y, angleDeg: p.angleDeg,
      confidence: p.confidence, pass: 2, ocr: p.ocr,
    });
  }
  writeFileSync(ANCHORS, JSON.stringify(doc, null, 2) + '\n');
  console.log(`appended ${doc.labels.length - before} pass-2 anchors (${before} -> ${doc.labels.length})`);
  accepted.forEach((p) => console.log(`  ${p.trailId.padEnd(24)} "${p.text}" (ocr "${p.ocr}") @ ${p.x},${p.y}`));
  process.exit(0);
}

// ------------------------------------------------- roster + matching helpers
const trailSrc = readFileSync(resolve(root, 'src/data/trails.ts'), 'utf8');
const trails = [];
for (const m of trailSrc.matchAll(/\{ id:\s*'([^']+)',\s*name:\s*'([^']+)'[^}]*?difficulty:\s*'([^']+)'[^}]*?peak:\s*'([^']+)'/g)) {
  trails.push({ id: m[1], name: m[2] });
}
const STOP = /\b(LODGE|PARKING|CONDOS?|ROAD|BAR|GRILL|HOTEL|RESTAURANT|CLUBHOUSE|YURT|EXPRESS|QUAD|GONDOLA|POMA|SIX|LOT|VALE|BASE|CAMP|PEAK|MOUNTAIN|MTN|KILLINGTON|ROUTE|CABIN|WAFFLE|UMBRELLA|TUBING|PARK|VILLAGE|HOMES|LIVE|STAGE|LEARN|SKI|CLINIC|CENTER|MAP|VISTA)\b/;
// like STOP but only unambiguous map furniture: used to reject OCR *source*
// text. ROAD / PARK are excluded because HIGH ROAD, LOW ROAD, START PARK,
// WOODWARD PEACE PARK are real roster trails.
const FURNITURE = /\b(LODGE|PARKING|CONDOS?|BAR|GRILL|HOTEL|RESTAURANT|CLUBHOUSE|YURT|EXPRESS|QUAD|GONDOLA|POMA|SIX|LOT|VALE|BASE|CAMP|PEAK|MOUNTAIN|MTN|KILLINGTON|ROUTE|CABIN|WAFFLE|UMBRELLA|TUBING|VILLAGE|HOMES|LIVE|STAGE|LEARN|SKI|CLINIC|CENTER|MAP|VISTA)\b/;

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
// reconcile-compatible score: levenshtein sim + containment boost, computed
// both with and without spaces (OCR spacing is unreliable)
function score(cand, name) {
  let s = Math.max(sim(cand, name), sim(cand.replace(/ /g, ''), name.replace(/ /g, '')));
  if (s < 0.9 && (name.includes(cand) || cand.includes(name)) && Math.min(cand.length, name.length) >= 5) {
    s = Math.max(s, 0.85);
  }
  return s;
}

// anchored set = what reconcile currently matches from pass-1 labels
const passOne = JSON.parse(readFileSync(ANCHORS, 'utf8')).labels.filter((l) => l.pass !== 2);
const anchoredIds = new Set();
const unmatchedLabels = [];
for (const lab of passOne) {
  const text = norm(lab.text);
  if (text.length < 4 || STOP.test(text)) { unmatchedLabels.push(lab); continue; }
  let best = null, bestS = 0;
  for (const t of trails) {
    const s = score(text, norm(t.name));
    if (s > bestS) { bestS = s; best = t; }
  }
  if (best && bestS >= 0.72) anchoredIds.add(best.id);
  else unmatchedLabels.push(lab);
}
const unanchored = trails.filter((t) => !anchoredIds.has(t.id)).map((t) => ({ ...t, n: norm(t.name) }));
const anchored = trails.filter((t) => anchoredIds.has(t.id)).map((t) => ({ ...t, n: norm(t.name) }));
console.log(`roster ${trails.length}, anchored by pass 1: ${anchoredIds.size}, targets: ${unanchored.length}`);

// simulate reconcileTrails.mjs on a stored text: which trail would it match?
function reconcileSim(text) {
  if (text.length < 4 || STOP.test(text)) return null;
  let best = null, bestS = 0;
  for (const t of trails) {
    let s = sim(text, norm(t.name));
    const name = norm(t.name);
    if (s < 0.9 && (name.includes(text) || text.includes(name)) && Math.min(text.length, name.length) >= 5) {
      s = Math.max(s, 0.85);
    }
    if (s > bestS) { bestS = s; best = t; }
  }
  return best && bestS >= 0.72 ? best.id : null;
}

// storable text for a resolved trail name: normally the normalized name; for
// names colliding with reconcile's STOP vocabulary (HIGH ROAD, LOW ROAD, ...)
// fall back to the spaceless form iff it evades STOP and still reconciles to
// the same trail (tesseract routinely drops spaces on this font anyway)
function storableText(trail) {
  const n = norm(trail.name);
  if (reconcileSim(n) === trail.id) return n;
  const fused = n.replace(/ /g, '');
  if (reconcileSim(fused) === trail.id) return fused;
  return null;
}

// dictionary-constrained acceptance. Returns {trail, s, margin, store} or null.
function dictMatch(candRaw) {
  const cand = norm(candRaw);
  if (cand.length < 4 || !/[AEIOUY]/.test(cand)) return null;
  const scored = unanchored.map((t) => ({ t, s: score(cand, t.n) })).sort((a, b) => b.s - a.s);
  const best = scored[0], second = scored[1];
  if (!best || best.s < 0.68) return null;
  if (second && best.s - second.s < 0.12) return null;
  // if an already-anchored trail name explains the text at least as well,
  // this is probably a duplicate label of that trail — not evidence
  for (const t of anchored) if (score(cand, t.n) >= best.s - 0.05) return null;
  // stored text must reconcile back to exactly this trail
  const store = storableText(best.t);
  if (!store) return null;
  return { trail: best.t, s: best.s, margin: second ? best.s - second.s : 1, store };
}

// candidate strings from OCR words: every contiguous run, at several
// confidence floors (dropping low-conf junk words recovers e.g.
// "GREAT [AY WV] EASTERN" -> "GREAT EASTERN")
function candidateStrings(words) {
  const out = [];
  const seen = new Set();
  for (const floor of [35, 55, 75]) {
    const ws = words.filter((w) => w.conf >= floor && w.text.replace(/[^A-Z]/g, '').length >= 2)
      .sort((a, b) => a.x - b.x)
      .map((w) => ({ text: w.text.replace(/[^A-Z' ]/g, ''), conf: w.conf }));
    for (let i = 0; i < ws.length && i < 8; i++) {
      let txt = '', confSum = 0, len = 0;
      for (let j = i; j < ws.length && j - i < 5; j++) {
        txt = txt ? `${txt} ${ws[j].text}` : ws[j].text;
        confSum += ws[j].conf * ws[j].text.length; len += ws[j].text.length;
        if (!seen.has(txt)) { seen.add(txt); out.push({ text: txt, conf: confSum / Math.max(1, len) }); }
      }
      // skip-grams: OCR junk between real words ("GREAT [AY WV] EASTERN")
      for (let j = i + 2; j < ws.length && j - i <= 3; j++) {
        const txt2 = `${ws[i].text} ${ws[j].text}`;
        const conf2 = (ws[i].conf * ws[i].text.length + ws[j].conf * ws[j].text.length) /
          (ws[i].text.length + ws[j].text.length);
        if (!seen.has(txt2)) { seen.add(txt2); out.push({ text: txt2, conf: conf2 }); }
      }
    }
  }
  return out;
}

// ========================================================== detection (pass 1
// logic from scripts/extractLabels.mjs, relaxed: 2-glyph words kept)
const P = {
  darkV: 77, darkDiff: 48,
  glyphDiagMin: 9, glyphDiagMax: 48, glyphMinN: 14,
  glyphFillMin: 0.14, glyphFillMax: 0.88,
  haloBrightV: 168, haloFracMin: 0.32,
  lineStraightMax: 0.14, lineThinMax: 6.0, lineDiagMin: 26,
  wordGap: 10, wordMinGlyphs: 2,
  mergeGapAlong: 60, mergePerp: 11, mergeAngle: 22,
  cropMargin: 12, upscale: 2.5,
};

async function loadRaw(path) {
  const { data, info } = await sharp(path).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  return { data, W: info.width, H: info.height };
}

function components(mask, W, H) {
  const labels = new Int32Array(W * H).fill(-1);
  const stack = new Int32Array(1 << 21);
  const comps = [];
  for (let start = 0; start < W * H; start++) {
    if (!mask[start] || labels[start] !== -1) continue;
    const id = comps.length;
    let sp = 0;
    stack[sp++] = start;
    labels[start] = id;
    const pixels = [];
    let minX = W, maxX = 0, minY = H, maxY = 0;
    while (sp > 0) {
      const p = stack[--sp];
      pixels.push(p);
      const x = p % W, y = (p / W) | 0;
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const np = ny * W + nx;
        if (mask[np] && labels[np] === -1) { labels[np] = id; stack[sp++] = np; }
      }
    }
    comps.push({ id, n: pixels.length, minX, maxX, minY, maxY, pixels });
  }
  return comps;
}

function centroid(c, W) {
  let sx = 0, sy = 0;
  for (const p of c.pixels) { sx += p % W; sy += (p / W) | 0; }
  return [sx / c.n, sy / c.n];
}

function straightness(c, W) {
  const n = c.pixels.length;
  const step = Math.max(1, Math.floor(n / 400));
  let sx = 0, sy = 0, m = 0;
  const pts = [];
  for (let k = 0; k < n; k += step) {
    const p = c.pixels[k];
    const x = p % W, y = (p / W) | 0;
    pts.push([x, y]); sx += x; sy += y; m++;
  }
  const mx = sx / m, my = sy / m;
  let cxx = 0, cxy = 0, cyy = 0;
  for (const [x, y] of pts) {
    const dx = x - mx, dy = y - my;
    cxx += dx * dx; cxy += dx * dy; cyy += dy * dy;
  }
  const tr = cxx + cyy, det = cxx * cyy - cxy * cxy;
  const lMin = tr / 2 - Math.sqrt(Math.max(0, (tr * tr) / 4 - det));
  const diag = Math.hypot(c.maxX - c.minX + 1, c.maxY - c.minY + 1);
  return Math.sqrt(Math.max(0, lMin / m)) / Math.max(1, diag);
}

function isBright(data, W, H, x, y, v) {
  if (x < 0 || y < 0 || x >= W || y >= H) return false;
  const i = (y * W + x) * 4;
  return Math.max(data[i], data[i + 1], data[i + 2]) >= v;
}

function haloFraction(img, c) {
  const { data, W, H } = img;
  const m = 3;
  const x0 = c.minX - m, x1 = c.maxX + m, y0 = c.minY - m, y1 = c.maxY + m;
  let bright = 0, total = 0;
  for (let x = x0; x <= x1; x += 2) {
    total += 2;
    if (isBright(data, W, H, x, y0, P.haloBrightV)) bright++;
    if (isBright(data, W, H, x, y1, P.haloBrightV)) bright++;
  }
  for (let y = y0 + 1; y < y1; y += 2) {
    total += 2;
    if (isBright(data, W, H, x0, y, P.haloBrightV)) bright++;
    if (isBright(data, W, H, x1, y, P.haloBrightV)) bright++;
  }
  return total ? bright / total : 0;
}

function detectGlyphs(img) {
  const { data, W, H } = img;
  const mask = new Uint8Array(W * H);
  for (let p = 0; p < W * H; p++) {
    const i = p * 4;
    const r = data[i], g = data[i + 1], b = data[i + 2];
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    if (mx <= P.darkV && mx - mn <= P.darkDiff) mask[p] = 1;
  }
  const inkImg = Buffer.alloc(W * H, 255);
  const R = 2;
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      if (!mask[y * W + x]) continue;
      for (let dy = -R; dy <= R; dy++) for (let dx = -R; dx <= R; dx++) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const q = ny * W + nx;
        if (inkImg[q] !== 255) continue;
        const i = q * 4;
        const lum = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
        inkImg[q] = Math.min(254, lum);
      }
    }
  }
  const comps = components(mask, W, H);
  const glyphs = [];
  for (const c of comps) {
    const w = c.maxX - c.minX + 1, h = c.maxY - c.minY + 1;
    const diag = Math.hypot(w, h);
    const fill = c.n / (w * h);
    if (diag < P.glyphDiagMin || diag > P.glyphDiagMax) continue;
    if (c.n < P.glyphMinN) continue;
    if (fill < P.glyphFillMin || fill > P.glyphFillMax) continue;
    if (diag >= P.lineDiagMin && c.n / diag <= P.lineThinMax && straightness(c, W) <= P.lineStraightMax)
      continue;
    if (haloFraction(img, c) < P.haloFracMin) continue;
    const [cx, cy] = centroid(c, W);
    const xs = new Int16Array(c.n), ys = new Int16Array(c.n);
    c.pixels.forEach((p, k) => { xs[k] = p % W; ys[k] = (p / W) | 0; });
    glyphs.push({ minX: c.minX, maxX: c.maxX, minY: c.minY, maxY: c.maxY, n: c.n, cx, cy, h, w, xs, ys });
  }
  return { glyphs, inkImg };
}

function bboxGap(a, b) {
  const dx = Math.max(0, Math.max(a.minX, b.minX) - Math.min(a.maxX, b.maxX));
  const dy = Math.max(0, Math.max(a.minY, b.minY) - Math.min(a.maxY, b.maxY));
  return Math.max(dx, dy);
}

function unionWords(glyphs) {
  const parent = glyphs.map((_, i) => i);
  const find = (i) => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; } return i; };
  const cell = 64;
  const grid = new Map();
  glyphs.forEach((g, i) => {
    const k = `${(g.cx / cell) | 0},${(g.cy / cell) | 0}`;
    if (!grid.has(k)) grid.set(k, []);
    grid.get(k).push(i);
  });
  glyphs.forEach((g, i) => {
    const gx = (g.cx / cell) | 0, gy = (g.cy / cell) | 0;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const bucket = grid.get(`${gx + dx},${gy + dy}`);
      if (!bucket) continue;
      for (const j of bucket) {
        if (j <= i) continue;
        if (bboxGap(g, glyphs[j]) <= P.wordGap) {
          const ri = find(i), rj = find(j);
          if (ri !== rj) parent[rj] = ri;
        }
      }
    }
  });
  const groups = new Map();
  glyphs.forEach((g, i) => {
    const r = find(i);
    if (!groups.has(r)) groups.set(r, []);
    groups.get(r).push(g);
  });
  return [...groups.values()];
}

function blockStats(glyphList) {
  let wSum = 0, sx = 0, sy = 0;
  for (const g of glyphList) { wSum += g.n; sx += g.cx * g.n; sy += g.cy * g.n; }
  const cx = sx / wSum, cy = sy / wSum;
  let cxx = 0, cxy = 0, cyy = 0;
  for (const g of glyphList) {
    const dx = g.cx - cx, dy = g.cy - cy;
    cxx += dx * dx * g.n; cxy += dx * dy * g.n; cyy += dy * dy * g.n;
  }
  let angle = 0;
  if (glyphList.length >= 2) {
    const tr = cxx + cyy, det = cxx * cyy - cxy * cxy;
    const lMax = tr / 2 + Math.sqrt(Math.max(0, (tr * tr) / 4 - det));
    let ax = cxy, ay = lMax - cxx;
    if (Math.hypot(ax, ay) < 1e-6) { ax = 1; ay = 0; }
    if (ax < 0) { ax = -ax; ay = -ay; }
    angle = Math.atan2(ay, ax) * 180 / Math.PI;
    if (angle > 90) angle -= 180;
  }
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  const hs = [];
  for (const g of glyphList) {
    minX = Math.min(minX, g.minX); maxX = Math.max(maxX, g.maxX);
    minY = Math.min(minY, g.minY); maxY = Math.max(maxY, g.maxY);
    hs.push(Math.max(g.w, g.h));
  }
  hs.sort((a, b) => a - b);
  const medH = hs[(hs.length / 2) | 0];
  const rad = angle * Math.PI / 180;
  const ux = Math.cos(rad), uy = Math.sin(rad);
  let pMin = Infinity, pMax = -Infinity;
  for (const g of glyphList) {
    const t = (g.cx - cx) * ux + (g.cy - cy) * uy;
    pMin = Math.min(pMin, t); pMax = Math.max(pMax, t);
  }
  return { glyphs: glyphList, cx, cy, angle, minX, maxX, minY, maxY, medH, halfLen: Math.max(pMax, -pMin) };
}

function mergeCollinear(words) {
  const blocks = words.map((g) => blockStats(g));
  let merged = true;
  while (merged) {
    merged = false;
    outer:
    for (let i = 0; i < blocks.length; i++) {
      for (let j = i + 1; j < blocks.length; j++) {
        const a = blocks[i], b = blocks[j];
        const dx = b.cx - a.cx, dy = b.cy - a.cy;
        const dist = Math.hypot(dx, dy);
        if (dist > a.halfLen + b.halfLen + P.mergeGapAlong + a.medH + b.medH) continue;
        let jd = Math.atan2(dy, dx) * 180 / Math.PI;
        if (jd > 90) jd -= 180; if (jd < -90) jd += 180;
        const angOK = (x, y) => {
          let d = Math.abs(x - y) % 180;
          if (d > 90) d = 180 - d;
          return d;
        };
        if (a.glyphs.length >= 3 && angOK(a.angle, jd) > P.mergeAngle) continue;
        if (b.glyphs.length >= 3 && angOK(b.angle, jd) > P.mergeAngle) continue;
        if (a.glyphs.length >= 3 && b.glyphs.length >= 3 && angOK(a.angle, b.angle) > P.mergeAngle) continue;
        if (Math.max(a.medH, b.medH) > 2.0 * Math.min(a.medH, b.medH)) continue;
        const ref = (a.glyphs.length >= b.glyphs.length ? a : b);
        const refAng = ref.glyphs.length >= 3 ? ref.angle : jd;
        const rad = refAng * Math.PI / 180;
        const ux = Math.cos(rad), uy = Math.sin(rad);
        const along = Math.abs(dx * ux + dy * uy);
        const perp = Math.abs(-dx * uy + dy * ux);
        if (perp > P.mergePerp) continue;
        if (along - a.halfLen - b.halfLen > P.mergeGapAlong) continue;
        blocks[i] = blockStats(a.glyphs.concat(b.glyphs));
        blocks.splice(j, 1);
        merged = true;
        break outer;
      }
    }
  }
  return blocks;
}

// =============================================================== variant OCR
function cleanWord(t) {
  return t.replace(/[^A-Za-z0-9'’\-\.,]/g, '').toUpperCase();
}

async function ocrBuffer(worker, buf) {
  const { data } = await worker.recognize(buf, {}, { blocks: true, text: true });
  const words = [];
  for (const bl of data.blocks ?? []) {
    for (const par of bl.paragraphs ?? []) {
      for (const line of par.lines ?? []) {
        for (const w of line.words ?? []) {
          const t = cleanWord(w.text ?? '');
          if (!t) continue;
          words.push({ text: t, conf: w.confidence, x: (w.bbox.x0 + w.bbox.x1) / 2 });
        }
      }
    }
  }
  return words;
}

async function ocrBlockVariants(worker, inkImg, imgRaw, block, W, H) {
  const rad = block.angle * Math.PI / 180;
  const ux = Math.abs(Math.cos(rad)), uy = Math.abs(Math.sin(rad));
  const along = P.cropMargin + 1.3 * block.medH;
  const perp = 8 + 0.3 * block.medH;
  const mx = Math.round(along * ux + perp * uy);
  const my = Math.round(along * uy + perp * ux);
  const x0 = Math.max(0, block.minX - mx), y0 = Math.max(0, block.minY - my);
  const x1 = Math.min(W - 1, block.maxX + mx), y1 = Math.min(H - 1, block.maxY + my);
  const cw = x1 - x0 + 1, ch = y1 - y0 + 1;
  if (cw < 12 || ch < 12) return [];

  // ink-only crop (pass-1 style) + raw greyscale crop (recovers letters the
  // ink mask ate; also basis for the inverted variant)
  const inkCrop = Buffer.allocUnsafe(cw * ch);
  const rawCrop = Buffer.allocUnsafe(cw * ch);
  for (let y = 0; y < ch; y++) {
    inkImg.copy(inkCrop, y * cw, (y0 + y) * W + x0, (y0 + y) * W + x0 + cw);
    for (let x = 0; x < cw; x++) {
      const i = ((y0 + y) * W + x0 + x) * 4;
      rawCrop[y * cw + x] = Math.round(0.299 * imgRaw.data[i] + 0.587 * imgRaw.data[i + 1] + 0.114 * imgRaw.data[i + 2]);
    }
  }
  const inkPng = await sharp(inkCrop, { raw: { width: cw, height: ch, channels: 1 } }).png().toBuffer();
  const rawPng = await sharp(rawCrop, { raw: { width: cw, height: ch, channels: 1 } }).png().toBuffer();

  const rots = new Set();
  rots.add(Math.abs(block.angle) >= 1.5 ? -block.angle : 0);
  if (Math.abs(block.angle) < 8) rots.add(0);
  if (Math.abs(block.angle) >= 55) { rots.add(-block.angle + 180); rots.add(-block.angle - 90 + 180); }
  if (Math.abs(block.angle) <= 20) { rots.add(90); rots.add(-90); } // mis-estimated near-vertical

  const variants = [];
  for (const rot of rots) {
    variants.push({ src: inkPng, rot, mode: 'ink' });
    variants.push({ src: inkPng, rot, mode: 'contrast' });
    variants.push({ src: rawPng, rot, mode: 'raw' });
    variants.push({ src: rawPng, rot, mode: 'invert' });
  }

  const all = [];
  for (const v of variants) {
    try {
      let pipe = sharp(v.src);
      if (v.rot !== 0) pipe = pipe.rotate(v.rot, { background: '#ffffff' });
      pipe = pipe.flatten({ background: '#ffffff' })
        .resize(Math.round(Math.hypot(cw, ch) * P.upscale), null, { kernel: 'cubic' })
        .greyscale()
        .normalise();
      if (v.mode === 'contrast') pipe = pipe.linear(2, -128);
      if (v.mode === 'invert') pipe = pipe.negate();
      const words = await ocrBuffer(worker, await pipe.png().toBuffer());
      for (const w of words) all.push({ ...w, variant: `${v.mode}@${Math.round(v.rot)}` });
    } catch { /* rotate/resize can fail on degenerate crops */ }
  }
  return all;
}

// ==================================================================== main
async function main() {
  mkdirSync(SCRATCH, { recursive: true });
  const t0 = Date.now();
  const imgRaw = await loadRaw(MAP);
  const { W, H } = imgRaw;
  console.log('detecting blocks...');
  const { glyphs, inkImg } = detectGlyphs(imgRaw);
  const words = unionWords(glyphs).filter((g) => g.length >= 2);
  let blocks = mergeCollinear(words);
  blocks = blocks.filter((b) => b.glyphs.length >= P.wordMinGlyphs);
  blocks = blocks.filter((b) => b.halfLen * 2 + b.medH >= 2.0 * b.medH);
  console.log(`  ${blocks.length} blocks`);

  const target = blocks;
  const proposals = []; // trailId -> best proposal

  function propose(m, src) {
    const p = {
      trailId: m.trail.id, text: m.store, ocr: src.ocr,
      x: Math.round(src.x * 10000) / 10000, y: Math.round(src.y * 10000) / 10000,
      angleDeg: Math.round((src.angleDeg ?? 0) * 10) / 10,
      confidence: Math.round(src.conf), sim: +m.s.toFixed(2), margin: +m.margin.toFixed(2),
      via: src.via,
    };
    const prev = proposals.find((q) => q.trailId === p.trailId);
    if (!prev) proposals.push(p);
    else if (p.sim > prev.sim || (p.sim === prev.sim && p.confidence > prev.confidence)) {
      Object.assign(prev, p);
    }
  }

  // source (b): word runs of ALL pass-1 labels (a matched label like
  // "VAGABOND TIN MAN" can still carry an unanchored trail's words). Labels
  // whose full text hits the non-trail STOP vocabulary (lodges, bars, lifts)
  // are not trail evidence at all.
  for (const lab of passOne) {
    const full = norm(lab.text);
    if (FURNITURE.test(full)) continue;
    const toks = full.split(' ').map((t) => ({ text: t, conf: lab.confidence, x: 0 }));
    toks.forEach((t, i) => { t.x = i; });
    for (const cand of candidateStrings(toks)) {
      const m = dictMatch(cand.text);
      if (m) propose(m, { ocr: lab.text, x: lab.x, y: lab.y, angleDeg: lab.angleDeg, conf: lab.confidence, via: 'pass1-label' });
    }
  }
  console.log(`  after pass-1 label mining: ${proposals.length} proposals`);

  console.log('starting OCR worker...');
  const worker = await createWorker('eng', 1, {
    langPath: resolve(root, 'node_modules/@tesseract.js-data/eng/4.0.0_best_int'),
    gzip: true,
    cachePath: '/tmp/explore2',
  });
  await worker.setParameters({
    tessedit_pageseg_mode: PSM.SPARSE_TEXT,
    tessedit_char_whitelist: "ABCDEFGHIJKLMNOPQRSTUVWXYZ'-.,0123456789 ",
  });

  let done = 0;
  for (const b of target) {
    const wordsAll = await ocrBlockVariants(worker, inkImg, imgRaw, b, W, H);
    // group words per variant, generate contiguous-run candidates per variant
    const byVar = new Map();
    for (const w of wordsAll) {
      if (!byVar.has(w.variant)) byVar.set(w.variant, []);
      byVar.get(w.variant).push(w);
    }
    for (const [variant, vw] of byVar) {
      // a block whose confident text contains lodge/bar/lift vocabulary is
      // map furniture, not a trail label
      const fullTxt = vw.filter((w) => w.conf >= 50).map((w) => norm(w.text)).join(' ');
      if (FURNITURE.test(fullTxt)) continue;
      for (const cand of candidateStrings(vw)) {
        const m = dictMatch(cand.text);
        if (m) {
          propose(m, {
            ocr: cand.text, x: b.cx / W, y: b.cy / H, angleDeg: b.angle,
            conf: cand.conf, via: `block-${variant}`,
          });
        }
      }
    }
    if (++done % 40 === 0) console.log(`  OCR ${done}/${target.length}, proposals ${proposals.length}`);
  }
  await worker.terminate();

  proposals.sort((a, b) => b.sim - a.sim || b.confidence - a.confidence);
  writeFileSync(PROPOSALS, JSON.stringify(proposals, null, 1));
  console.log(`\n${proposals.length} proposals -> ${PROPOSALS}  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  proposals.forEach((p, i) => console.log(
    `  [${i}] ${p.trailId.padEnd(24)} "${p.ocr}" -> "${p.text}" sim ${p.sim} margin ${p.margin} conf ${p.confidence} via ${p.via} @ ${p.x},${p.y}`));

  // contact sheets for visual verification
  const img = decodeJpeg(MAP);
  const PER = 12, COLS = 4, CELL = 300, SRC = 220;
  for (let s = 0; s * PER < proposals.length; s++) {
    const batch = proposals.slice(s * PER, (s + 1) * PER);
    const rows = Math.ceil(batch.length / COLS);
    const sheet = { data: new Uint8Array(COLS * CELL * rows * CELL * 4).fill(30), width: COLS * CELL, height: rows * CELL };
    batch.forEach((p, bi) => {
      const cx = Math.round(p.x * img.width), cy = Math.round(p.y * img.height);
      const x0 = Math.max(0, (cx - SRC / 2)) / img.width, y0 = Math.max(0, (cy - SRC / 2)) / img.height;
      const x1 = Math.min(img.width, (cx + SRC / 2)) / img.width, y1 = Math.min(img.height, (cy + SRC / 2)) / img.height;
      const crop = cropScaled(img, x0, y0, x1, y1, CELL);
      const gx = (bi % COLS) * CELL, gy = Math.floor(bi / COLS) * CELL;
      for (let y = 0; y < Math.min(CELL, crop.height); y++) for (let x = 0; x < Math.min(CELL, crop.width); x++) {
        const si = (y * crop.width + x) * 4, di = ((gy + y) * sheet.width + gx + x) * 4;
        sheet.data[di] = crop.data[si]; sheet.data[di + 1] = crop.data[si + 1]; sheet.data[di + 2] = crop.data[si + 2]; sheet.data[di + 3] = 255;
      }
      const ccx = gx + Math.round((cx / img.width - x0) / (x1 - x0) * CELL);
      const ccy = gy + Math.round((cy / img.height - y0) / (y1 - y0) * CELL);
      for (let d = 6; d <= 18; d++) for (const [px, py] of [[ccx + d, ccy], [ccx - d, ccy], [ccx, ccy + d], [ccx, ccy - d]]) {
        if (px < gx || py < gy || px >= gx + CELL || py >= gy + CELL) continue;
        const o = (py * sheet.width + px) * 4; sheet.data[o] = 255; sheet.data[o + 1] = 0; sheet.data[o + 2] = 255;
      }
      const idx = s * PER + bi;
      drawText(sheet, gx + 8, gy + 8, String(idx), 0, 0, 0, 4);
      drawText(sheet, gx + 10, gy + 10, String(idx), 255, 255, 0, 4);
      drawText(sheet, gx + 8, gy + CELL - 26, p.trailId.slice(0, 22), 0, 0, 0, 2);
      drawText(sheet, gx + 9, gy + CELL - 25, p.trailId.slice(0, 22), 255, 255, 0, 2);
    });
    encodeJpeg(sheet, `${SCRATCH}/enrich_sheet${s}.jpg`, 90);
    console.log(`sheet ${SCRATCH}/enrich_sheet${s}.jpg: [${batch.map((p, bi) => `${s * PER + bi}=${p.trailId}`).join(', ')}]`);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
