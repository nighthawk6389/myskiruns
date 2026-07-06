// Trail-name OCR pipeline for the Killington ski map.
//
// Extracts the black uppercase trail/lift/lodge name labels (usually rotated
// to follow their trail line) and emits src/data/labelAnchors.json with
// { text, x, y, angleDeg, confidence } anchors (x,y normalized [0,1]).
//
// Pipeline:
//   1. classify dark "text ink" pixels (near-black, low chroma)
//   2. connected components -> glyph-sized comps; reject line pieces,
//      solid markers, forest speckle (glyphs carry a bright halo ring)
//   3. greedy union of nearby glyphs -> words; PCA baseline angle
//   4. collinear merge of words along the baseline -> label blocks
//   5. per block: crop, counter-rotate to horizontal, upscale, OCR
//      (tesseract.js, local langdata); near-horizontal blocks also get an
//      unrotated pass, best result wins
//   6. extra pass: solid dark label boxes (lodges/peaks) OCR'd inverted
//   7. filter (confidence, A-Z dictionary-plausible), dedup, emit JSON
//
// Usage:
//   node scripts/extractLabels.mjs              # full run
//   node scripts/extractLabels.mjs --detect-only  # skip OCR, render block debug
//
// Debug/verification images go to /tmp/explore2/.

import sharp from 'sharp';
import { createWorker, PSM } from 'tesseract.js';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdirSync, writeFileSync } from 'node:fs';
import { drawText, drawDot } from './lib/draw.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MAP = resolve(root, 'public/killington-trail-map.jpg');
const OUT = resolve(root, 'src/data/labelAnchors.json');
const DBG = '/tmp/explore2';
const DETECT_ONLY = process.argv.includes('--detect-only');

const P = {
  darkV: 77,           // max(r,g,b) ceiling for text ink
  darkDiff: 48,        // max-min ceiling (neutral ink, not green shadow)
  glyphDiagMin: 9,     // px
  glyphDiagMax: 48,    // px (letters ~14-30px tall)
  glyphMinN: 14,       // px of ink
  glyphFillMin: 0.14,
  glyphFillMax: 0.88,
  haloBrightV: 168,    // ring pixel counts as "bright halo"
  haloFracMin: 0.32,   // fraction of bbox ring that must be bright
  lineStraightMax: 0.14, // straight+thin+long = trail-line piece, not glyph
  lineThinMax: 6.0,
  lineDiagMin: 26,
  wordGap: 10,         // px bbox gap for glyph->word union
  wordMinGlyphs: 3,
  mergeGapAlong: 60,   // px gap along baseline for word->label merge
  mergePerp: 11,       // px max perpendicular offset between word centroids
  mergeAngle: 22,      // deg tolerance word-angle vs join direction
  cropMargin: 12,      // px around block bbox
  upscale: 2.5,
  minWordConf: 60,
  boxMinW: 70,         // solid label-box pass (lodges): bbox width range
  boxMaxW: 520,
  boxMinH: 22,
  boxMaxH: 130,
  boxFillMin: 0.55,
};

// ---------------------------------------------------------------- image load
async function loadRaw(path) {
  const { data, info } = await sharp(path).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  return { data, W: info.width, H: info.height };
}

// ------------------------------------------------------- connected components
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

// PCA smallest-eigenvalue residual / diag (0 = perfectly straight)
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

// -------------------------------------------------------------- glyph filter
function isBright(data, W, H, x, y, v) {
  if (x < 0 || y < 0 || x >= W || y >= H) return false;
  const i = (y * W + x) * 4;
  return Math.max(data[i], data[i + 1], data[i + 2]) >= v;
}

// fraction of a 3px-expanded bbox ring that is bright (text halo / snow)
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

function detectGlyphsAndBoxes(img) {
  const { data, W, H } = img;
  const mask = new Uint8Array(W * H);
  for (let p = 0; p < W * H; p++) {
    const i = p * 4;
    const r = data[i], g = data[i + 1], b = data[i + 2];
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    if (mx <= P.darkV && mx - mn <= P.darkDiff) mask[p] = 1;
  }
  // ink-only greyscale image for OCR crops: original luminance where the
  // (dilated) dark mask is set, white elsewhere — kills forest clutter
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
  const boxes = [];
  for (const c of comps) {
    const w = c.maxX - c.minX + 1, h = c.maxY - c.minY + 1;
    const diag = Math.hypot(w, h);
    const fill = c.n / (w * h);
    // solid label boxes (lodge/peak signs) for the inverted pass
    if (w >= P.boxMinW && w <= P.boxMaxW && h >= P.boxMinH && h <= P.boxMaxH &&
        fill >= P.boxFillMin && w > h) {
      boxes.push(c);
      continue;
    }
    if (diag < P.glyphDiagMin || diag > P.glyphDiagMax) continue;
    if (c.n < P.glyphMinN) continue;
    if (fill < P.glyphFillMin || fill > P.glyphFillMax) continue;
    // long straight thin pieces are trail-line fragments
    if (diag >= P.lineDiagMin && c.n / diag <= P.lineThinMax && straightness(c, W) <= P.lineStraightMax)
      continue;
    // forest speckle has no bright halo; text always does
    if (haloFraction(img, c) < P.haloFracMin) continue;
    const [cx, cy] = centroid(c, W);
    const xs = new Int16Array(c.n), ys = new Int16Array(c.n);
    c.pixels.forEach((p, k) => { xs[k] = p % W; ys[k] = (p / W) | 0; });
    glyphs.push({ minX: c.minX, maxX: c.maxX, minY: c.minY, maxY: c.maxY, n: c.n, cx, cy, h, w, xs, ys });
  }
  return { glyphs, boxes, inkImg };
}

// ------------------------------------------------- glyph -> word clustering
function bboxGap(a, b) {
  const dx = Math.max(0, Math.max(a.minX, b.minX) - Math.min(a.maxX, b.maxX));
  const dy = Math.max(0, Math.max(a.minY, b.minY) - Math.min(a.maxY, b.maxY));
  return Math.max(dx, dy);
}

function unionWords(glyphs) {
  const parent = glyphs.map((_, i) => i);
  const find = (i) => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; } return i; };
  // spatial grid to keep pairing cheap
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
        const o = glyphs[j];
        if (bboxGap(g, o) <= P.wordGap) {
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

// word block stats: area-weighted centroid + PCA baseline angle over glyph
// centroids; angle normalized to (-90, 90]
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
    if (ax < 0) { ax = -ax; ay = -ay; } // read left-to-right
    angle = Math.atan2(ay, ax) * 180 / Math.PI;
    if (angle > 90) angle -= 180;
  }
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  let medH = 0;
  const hs = [];
  for (const g of glyphList) {
    minX = Math.min(minX, g.minX); maxX = Math.max(maxX, g.maxX);
    minY = Math.min(minY, g.minY); maxY = Math.max(maxY, g.maxY);
    hs.push(Math.max(g.w, g.h));
  }
  hs.sort((a, b) => a - b);
  medH = hs[(hs.length / 2) | 0];
  // extent along the baseline
  const rad = angle * Math.PI / 180;
  const ux = Math.cos(rad), uy = Math.sin(rad);
  let pMin = Infinity, pMax = -Infinity;
  for (const g of glyphList) {
    const t = (g.cx - cx) * ux + (g.cy - cy) * uy;
    pMin = Math.min(pMin, t); pMax = Math.max(pMax, t);
  }
  // geometric word segmentation: project glyph bboxes on the baseline; a gap
  // clearly wider than a letter gap is a word space. Yields letter counts per
  // word, used to re-space the OCR text (tesseract's spacing is unreliable
  // on this condensed font).
  const proj = glyphList.map((g) => {
    let lo = Infinity, hi = -Infinity;
    for (let k = 0; k < g.xs.length; k++) {
      const t = (g.xs[k] - cx) * ux + (g.ys[k] - cy) * uy;
      if (t < lo) lo = t; if (t > hi) hi = t;
    }
    return { lo, hi };
  }).sort((a, b) => (a.lo + a.hi) - (b.lo + b.hi));
  const gaps = [];
  for (let i = 1; i < proj.length; i++) gaps.push(proj[i].lo - proj[i - 1].hi);
  // adaptive break: word spaces are clearly wider than this block's typical
  // letter gap and at least ~a quarter of the glyph size
  const sorted = [...gaps].sort((a, b) => a - b);
  const medGap = sorted.length ? sorted[(sorted.length / 2) | 0] : 0;
  const breakGap = Math.max(5, medGap + 0.18 * medH);
  const wordLens = [1];
  for (const gap of gaps) {
    if (gap > breakGap) wordLens.push(1);
    else wordLens[wordLens.length - 1]++;
  }
  return { glyphs: glyphList, cx, cy, angle, minX, maxX, minY, maxY, medH, halfLen: Math.max(pMax, -pMin), wordLens, gaps: gaps.map((g) => Math.round(g * 10) / 10) };
}

// --------------------------------------------- word -> label collinear merge
function mergeCollinear(words) {
  let blocks = words.map((g) => blockStats(g));
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
        // both words (when their own angle is reliable) must agree with the
        // join direction
        if (a.glyphs.length >= 3 && angOK(a.angle, jd) > P.mergeAngle) continue;
        if (b.glyphs.length >= 3 && angOK(b.angle, jd) > P.mergeAngle) continue;
        if (a.glyphs.length >= 3 && b.glyphs.length >= 3 && angOK(a.angle, b.angle) > P.mergeAngle) continue;
        // similar glyph size
        if (Math.max(a.medH, b.medH) > 2.0 * Math.min(a.medH, b.medH)) continue;
        // gap along the reference baseline (the longer word's axis, or join dir)
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

// ------------------------------------------------------------------ OCR pass
const WORD_RE = /^[A-Z][A-Z'’\-\.]*[A-Z'\.]$|^[A-Z]{2,}$|^\d{1,2}(,\d{3})?'?$/;

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
          words.push({
            text: t, conf: w.confidence,
            x: (w.bbox.x0 + w.bbox.x1) / 2, y: (w.bbox.y0 + w.bbox.y1) / 2,
            x0: w.bbox.x0, x1: w.bbox.x1, y0: w.bbox.y0, y1: w.bbox.y1,
          });
        }
      }
    }
  }
  return words;
}

// accept words, assemble in reading order (x in the horizontalized crop).
// Tesseract often splits a word into fragments ("ROU"+"NDABOUT") and its
// space decisions are unreliable on this condensed font, so spacing is
// re-derived GEOMETRICALLY: if the concatenated OCR letters match the
// glyph-count word pattern from detection (wordLens), split by that.
// Otherwise fall back to joining only unmistakable fragments (tiny gaps).
function joinFragments(cand, maxGapRatio) {
  const joined = [];
  for (const w of cand) {
    const prev = joined[joined.length - 1];
    if (prev) {
      const h = Math.max(prev.y1 - prev.y0, w.y1 - w.y0);
      const gap = w.x0 - prev.x1;
      const yOverlap = Math.min(prev.y1, w.y1) - Math.max(prev.y0, w.y0);
      if (gap <= maxGapRatio * h && gap > -0.6 * h && yOverlap > 0.5 * h) {
        const lp = prev.text.length, lw = w.text.length;
        prev.text += w.text;
        prev.conf = (prev.conf * lp + w.conf * lw) / (lp + lw);
        prev.x1 = Math.max(prev.x1, w.x1);
        prev.y0 = Math.min(prev.y0, w.y0); prev.y1 = Math.max(prev.y1, w.y1);
        continue;
      }
    }
    joined.push({ ...w });
  }
  return joined;
}

function assemble(words, wordLens) {
  const cand = words.filter((w) => w.conf >= 45 && /[A-Z0-9]/.test(w.text));
  if (!cand.length) return null;
  cand.sort((a, b) => a.x - b.x);

  // attempt A: geometric re-spacing. Merge everything on the main baseline
  // into one letter string; if its length matches the glyph word pattern,
  // insert the spaces where the glyph gaps are.
  if (wordLens && wordLens.length) {
    const line = joinFragments(cand, 2.5).sort((a, b) => (b.x1 - b.x0) - (a.x1 - a.x0))[0];
    const letters = line ? line.text : '';
    const total = wordLens.reduce((a, b) => a + b, 0);
    if (letters.length === total && line.conf >= P.minWordConf) {
      const toks = [];
      let off = 0;
      for (const len of wordLens) { toks.push(letters.slice(off, off + len)); off += len; }
      if (toks.every((t) => t.length >= 2 && WORD_RE.test(t)) && toks.some((t) => t.length >= 3)) {
        return { text: toks.join(' '), conf: line.conf, nWords: toks.length };
      }
    }
  }

  // attempt B: tesseract's own segmentation, joining only tiny-gap fragments
  const joined = joinFragments(cand, 0.15);
  const ok = joined.filter((w) => w.conf >= P.minWordConf && w.text.length >= 3 && WORD_RE.test(w.text));
  if (!ok.length) return null;
  // reading order: line by line (y bands), then left to right
  ok.sort((a, b) => {
    const ay = (a.y0 + a.y1) / 2, by = (b.y0 + b.y1) / 2;
    const h = Math.max(a.y1 - a.y0, b.y1 - b.y0);
    if (Math.abs(ay - by) > 0.9 * h) return ay - by; // clearly separate lines
    return a.x - b.x;
  });
  const text = ok.map((w) => w.text).join(' ');
  const conf = ok.reduce((s, w) => s + w.conf, 0) / ok.length;
  return { text, conf, nWords: ok.length };
}

async function ocrBlock(worker, inkImg, block, W, H, dbgLog) {
  // margins: generous along the baseline (recovers end letters the glyph
  // filter may have dropped), tighter perpendicular (avoid neighbour lines)
  const rad = block.angle * Math.PI / 180;
  const ux = Math.abs(Math.cos(rad)), uy = Math.abs(Math.sin(rad));
  const along = P.cropMargin + 1.3 * block.medH;
  const perp = 8 + 0.3 * block.medH;
  const mx = Math.round(along * ux + perp * uy);
  const my = Math.round(along * uy + perp * ux);
  const x0 = Math.max(0, block.minX - mx), y0 = Math.max(0, block.minY - my);
  const x1 = Math.min(W - 1, block.maxX + mx), y1 = Math.min(H - 1, block.maxY + my);
  const cw = x1 - x0 + 1, ch = y1 - y0 + 1;
  if (cw < 12 || ch < 12) return null;
  // crop from the ink-only greyscale image (background clutter removed)
  const cropRaw = Buffer.allocUnsafe(cw * ch);
  for (let y = 0; y < ch; y++) inkImg.copy(cropRaw, y * cw, (y0 + y) * W + x0, (y0 + y) * W + x0 + cw);
  const crop = await sharp(cropRaw, { raw: { width: cw, height: ch, channels: 1 } }).png().toBuffer();

  const attempts = [];
  if (Math.abs(block.angle) >= 1.5) attempts.push(-block.angle);
  else attempts.push(0);
  // horizontal pass for near-horizontal blocks
  if (Math.abs(block.angle) < 8 && Math.abs(block.angle) >= 1.5) attempts.push(0);
  // near-vertical text may read bottom-up: try the flip too
  if (Math.abs(block.angle) >= 70) attempts.push(-block.angle + 180);

  let best = null;
  for (const rot of attempts) {
    let pipe = sharp(crop);
    if (rot !== 0) pipe = pipe.rotate(rot, { background: '#ffffff' });
    const buf = await pipe
      .flatten({ background: '#ffffff' })
      .resize(Math.round(Math.hypot(cw, ch) * P.upscale), null, { kernel: 'cubic' })
      .greyscale()
      .normalise()
      .png()
      .toBuffer();
    const words = await ocrBuffer(worker, buf);
    if (dbgLog) dbgLog.push({ block: [block.minX, block.minY, block.maxX, block.maxY], angle: block.angle, rot, wordLens: block.wordLens, gaps: block.gaps, medH: block.medH, words });
    const res = assemble(words, block.wordLens);
    if (res && (!best || res.conf * res.nWords > best.conf * best.nWords)) best = res;
  }
  if (!best) return null;
  return {
    text: best.text,
    x: block.cx / W,
    y: block.cy / H,
    angleDeg: Math.round(block.angle * 10) / 10,
    confidence: Math.round(best.conf),
    nGlyphs: block.glyphs.length,
  };
}

// inverted OCR of solid label boxes (lodge / peak signs, white text on black)
async function ocrBox(worker, mapSharp, box, W, H) {
  const m = 4;
  const x0 = Math.max(0, box.minX + m), y0 = Math.max(0, box.minY + m);
  const x1 = Math.min(W - 1, box.maxX - m), y1 = Math.min(H - 1, box.maxY - m);
  const cw = x1 - x0 + 1, ch = y1 - y0 + 1;
  if (cw < 30 || ch < 14) return null;
  const buf = await mapSharp.clone().extract({ left: x0, top: y0, width: cw, height: ch })
    .negate({ alpha: false })
    .resize(Math.round(cw * 3), null, { kernel: 'cubic' })
    .greyscale()
    .normalise()
    .png()
    .toBuffer();
  const words = await ocrBuffer(worker, buf);
  const ok = words.filter((w) => w.conf >= P.minWordConf && ((w.text.length >= 3 && WORD_RE.test(w.text)) || /^\d/.test(w.text)));
  if (!ok.length) return null;
  ok.sort((a, b) => (a.y - b.y) * 2 + (a.x - b.x) / cw);
  // keep alphabetic words first line style: just join in y-then-x order
  const text = ok.map((w) => w.text).join(' ');
  const conf = ok.reduce((s, w) => s + w.conf, 0) / ok.length;
  const alpha = ok.filter((w) => /[A-Z]{3,}/.test(w.text));
  if (!alpha.length) return null;
  return {
    text,
    x: (x0 + x1) / 2 / W,
    y: (y0 + y1) / 2 / H,
    angleDeg: 0,
    confidence: Math.round(conf),
    nGlyphs: 0,
  };
}

// ------------------------------------------------------------ filter + dedup
function postFilter(labels, W, H) {
  const out = [];
  for (const l of labels) {
    let text = l.text.replace(/[\.\-,]+$/g, '').replace(/^[\.\-,]+/g, '').trim();
    if (!text) continue;
    const wordsArr = text.split(' ');
    // single very short tokens are fragments/noise ("ROU", "HIG", "NNS")
    if (wordsArr.length === 1 && text.replace(/[^A-Z0-9]/g, '').length < 4) continue;
    // pronounceable: needs a vowel somewhere
    if (!/[AEIOUY0-9]/.test(text)) continue;
    out.push({ ...l, text });
  }
  out.sort((a, b) => b.confidence - a.confidence);
  const kept = [];
  for (const l of out) {
    let dup = false;
    for (const k of kept) {
      const d = Math.hypot((l.x - k.x) * W, (l.y - k.y) * H);
      if (d >= 90) continue;
      const lw = new Set(l.text.split(' ')), kw = new Set(k.text.split(' '));
      const subset = [...lw].every((w) => kw.has(w)) || [...kw].every((w) => lw.has(w));
      if (subset || k.text.includes(l.text) || l.text.includes(k.text)) { dup = true; break; }
    }
    if (!dup) kept.push(l);
  }
  return kept;
}

// ------------------------------------------------------------- verification
async function renderVerify(labels) {
  const outW = 1400;
  const scale = 1400 / 4572;
  const outH = Math.round(2704 * scale);
  const raw = await sharp(MAP).resize(outW, outH).ensureAlpha().raw().toBuffer();
  const img = { data: raw, width: outW, height: outH };
  const top = labels.slice(0, 60);
  top.forEach((l, i) => {
    const x = Math.round(l.x * outW), y = Math.round(l.y * outH);
    drawDot(img, x, y, 255, 0, 0, 4);
    drawText(img, x + 6, y - 12, String(i + 1), 255, 0, 0, 2);
  });
  await sharp(img.data, { raw: { width: outW, height: outH, channels: 4 } })
    .jpeg({ quality: 88 }).toFile(`${DBG}/labels_verify.jpg`);
  return top;
}

async function renderBlocksDebug(blocks, boxes) {
  const outW = 2286;
  const sc = outW / 4572;
  const outH = Math.round(2704 * sc);
  const raw = await sharp(MAP).resize(outW, outH).ensureAlpha().raw().toBuffer();
  const img = { data: raw, width: outW, height: outH };
  const drawRect = (minX, minY, maxX, maxY, r, g, b) => {
    const x0 = Math.round(minX * sc), x1 = Math.round(maxX * sc);
    const y0 = Math.round(minY * sc), y1 = Math.round(maxY * sc);
    for (let x = x0; x <= x1; x++) { drawDot(img, x, y0, r, g, b, 0); drawDot(img, x, y1, r, g, b, 0); }
    for (let y = y0; y <= y1; y++) { drawDot(img, x0, y, r, g, b, 0); drawDot(img, x1, y, r, g, b, 0); }
  };
  for (const b of blocks) drawRect(b.minX, b.minY, b.maxX, b.maxY, 255, 0, 0);
  for (const b of boxes) drawRect(b.minX, b.minY, b.maxX, b.maxY, 0, 90, 255);
  await sharp(img.data, { raw: { width: outW, height: outH, channels: 4 } })
    .jpeg({ quality: 88 }).toFile(`${DBG}/blocks_debug.jpg`);
}

// --------------------------------------------------------------------- main
async function main() {
  mkdirSync(DBG, { recursive: true });
  const t0 = Date.now();
  console.log('loading map...');
  const img = await loadRaw(MAP);
  const { W, H } = img;

  console.log('detecting glyphs...');
  const { glyphs, boxes, inkImg } = detectGlyphsAndBoxes(img);
  console.log(`  ${glyphs.length} glyph candidates, ${boxes.length} label boxes`);

  const words = unionWords(glyphs).filter((g) => g.length >= 2);
  console.log(`  ${words.length} word candidates`);
  let blocks = mergeCollinear(words);
  blocks = blocks.filter((b) => b.glyphs.length >= P.wordMinGlyphs);
  // sanity: a text block is longer than tall along its axis
  blocks = blocks.filter((b) => b.halfLen * 2 + b.medH >= 2.0 * b.medH);
  console.log(`  ${blocks.length} label blocks after collinear merge`);

  await renderBlocksDebug(blocks, boxes);
  if (DETECT_ONLY) {
    console.log('detect-only: wrote', `${DBG}/blocks_debug.jpg`);
    return;
  }

  console.log('starting OCR worker...');
  const worker = await createWorker('eng', 1, {
    langPath: resolve(root, 'node_modules/@tesseract.js-data/eng/4.0.0_best_int'),
    gzip: true,
    cachePath: DBG, // keep the unpacked traineddata cache out of the repo
  });
  await worker.setParameters({
    tessedit_pageseg_mode: PSM.SPARSE_TEXT,
    tessedit_char_whitelist: "ABCDEFGHIJKLMNOPQRSTUVWXYZ'-.,0123456789 ",
  });

  const mapSharp = sharp(MAP);
  const labels = [];
  const dbgLog = [];
  let done = 0;
  for (const b of blocks) {
    try {
      const res = await ocrBlock(worker, inkImg, b, W, H, dbgLog);
      if (res) labels.push(res);
    } catch (e) {
      console.error('  block OCR failed:', e.message);
    }
    if (++done % 25 === 0) console.log(`  OCR ${done}/${blocks.length} blocks, ${labels.length} labels`);
  }
  writeFileSync(`${DBG}/ocr_debug.json`, JSON.stringify(dbgLog, null, 1));
  console.log(`  block pass: ${labels.length} labels`);
  for (const b of boxes) {
    try {
      const res = await ocrBox(worker, mapSharp, b, W, H);
      if (res) labels.push(res);
    } catch (e) {
      console.error('  box OCR failed:', e.message);
    }
  }
  console.log(`  with box pass: ${labels.length} labels`);
  await worker.terminate();

  const final = postFilter(labels, W, H).map((l) => ({
    text: l.text,
    x: Math.round(l.x * 10000) / 10000,
    y: Math.round(l.y * 10000) / 10000,
    angleDeg: l.angleDeg,
    confidence: l.confidence,
  }));
  final.sort((a, b) => b.confidence - a.confidence);
  writeFileSync(OUT, JSON.stringify({ labels: final }, null, 2) + '\n');

  const meanConf = final.reduce((s, l) => s + l.confidence, 0) / Math.max(1, final.length);
  console.log(`\nwrote ${OUT}`);
  console.log(`labels: ${final.length}, mean confidence: ${meanConf.toFixed(1)}`);
  const bands = { '90+': 0, '80-89': 0, '70-79': 0, '60-69': 0 };
  for (const l of final) {
    if (l.confidence >= 90) bands['90+']++;
    else if (l.confidence >= 80) bands['80-89']++;
    else if (l.confidence >= 70) bands['70-79']++;
    else bands['60-69']++;
  }
  console.log('confidence bands:', JSON.stringify(bands));

  const top = await renderVerify(final);
  console.log(`\nverification sheet: ${DBG}/labels_verify.jpg (top ${top.length})`);
  top.forEach((l, i) => {
    console.log(`  #${i + 1}: "${l.text}" (${l.confidence}) at ${l.x.toFixed(3)},${l.y.toFixed(3)} angle ${l.angleDeg}`);
  });
  console.log('\nall texts:');
  for (const l of final) console.log(`  ${l.confidence} ${l.text}`);
  console.log(`\ntotal time ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}

main().catch((e) => { console.error(e); process.exit(1); });
