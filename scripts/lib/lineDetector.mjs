// Trail-line detector: finds the colored multi-segment trail lines (green /
// blue / black strokes) on the Killington trail map.
//
// Pipeline (per the raster-map line-extraction literature):
//   1. per-pixel ink classification in HSV (green/blue/black + reject inks),
//      plus shadowed-blue recovery (region growing from confirmed blue ink)
//   2. per-column skyline exclusion (sky is bright and line-colored)
//   3. structure punch-outs: label-box slabs (35x35 fill), solid markers and
//      thick illustration fills (13x13 / 21x21 fill), lift outlines (black
//      hugging long maroon comps)
//   4. connected components per class (union-find, 8-connectivity)
//   5. shape filtering: keep long+thin components (lines); small/compact
//      pieces become "weak" and must endpoint-link to a strong segment
//   6. group filters: length, strong anchoring, sign leader-line rejection,
//      and lift-furniture rejection (groups living inside the lift corridor)
//   7. centerline skeleton (Zhang-Suen + spur pruning) with marker interiors
//      and lift-crossing connectors excluded: those spots are not "on a line"
//
// Everything is tunable via PARAMS so the evaluation harness can sweep.

import sharp from 'sharp';

export const DEFAULT_PARAMS = {
  // Hysteresis segmentation per ink: "core" is unmistakable saturated ink,
  // "grow" admits anti-aliased edges. Components are built on the grow mask
  // but kept only if they contain enough core pixels — tree clusters and
  // shadow chains have no vivid core and die here.
  green: { hMin: 125, hMax: 170, coreS: 0.72, coreV: 0.40, growS: 0.42, growV: 0.33 },
  blue: { hMin: 183, hMax: 216, coreS: 0.72, coreV: 0.50, growS: 0.42, growV: 0.40 },
  // shadowed-blue recovery: where a blue line runs under forest shadow its ink
  // drops to a dark muted teal that fails the blue gates entirely. Those
  // pixels are re-admitted by REGION GROWING from confirmed blue ink only —
  // teal forest texture with no blue seed nearby stays out.
  shadowBlue: { hMin: 132, hMax: 210, sMin: 0.24, vMin: 0.10, vMax: 0.48, steps: 50 },
  // no-core recovered comps are demoted to weak only when they look like a
  // dense ink band (a shadowed line run), not like porous recovered forest
  shadowSolidityMin: 7.0,
  shadowFillMax: 0.50,
  black: { coreV: 0.20, coreDiff: 36 / 255, growV: 0.30, growDiff: 48 / 255, greenCastMax: 7 },
  maroon: { hMin: 328, hMax: 14, sMin: 0.40, vMin: 0.14, vMax: 0.8 },
  yellow: { hMin: 40, hMax: 72, sMin: 0.5, vMin: 0.5 },
  magenta: { hMin: 298, hMax: 330, sMin: 0.38, vMin: 0.4 },
  minCorePixels: 30, // component must contain this much core ink
  // wide-structure punch-out: pixels surviving `wideErode` erosions are the
  // cores of boxes/blobs (sign panels, lakes); those cores dilated by
  // `wideDilate` are removed before component analysis. Lines are at most
  // ~9px wide so they never survive the erosions and are unaffected.
  wideErodeColored: 15, // colored: only true panels die; square/circle markers survive
  wideDilate: 10,
  // black label boxes: after closing (text gaps fill in) a box is a huge solid
  // blob that survives deep erosion; diamonds (25px) and closed word-blobs
  // (~35px tall) do not. Survivors are punched with a halo.
  blackBoxWin: 17, // half-size of the local-fill window (35x35)
  blackBoxFill: 0.66, // window fill above this = sign-box slab (lines max ~0.25)
  blackBoxPunchDilate: 12,
  // solid black markers (difficulty diamonds, squares) and other locally-thick
  // black shapes (illustration fills): a 13x13 window centered on a marker
  // interior is nearly all ink; a trail stroke (<=9px wide) tops out ~0.69.
  // Punched markers leave a gap on the line (linked by endpoint linking); the
  // punched zone is also excluded from the centerline skeleton because marker
  // interiors are NOT "on the line" (GT labels diamond centers as negatives).
  markerWin: 6, // half-size of the local-fill window (13x13)
  markerFill: 0.80, // window fill above this = solid marker/illustration core
  markerWin2: 10, // coarse scale (21x21) for medium-thick illustration slabs
  markerFill2: 0.55,
  markerPunchDilate: 4,
  // gap bridging: same-class components within 2*bridgeRadius px are analyzed
  // as one line (crossings and icons interrupt the ink). Colored classes get a
  // wider radius: snowflake/marker icons ON green/blue lines chop them into
  // clusters ~8-12px apart, and colored ink is rare enough in nature that the
  // extra reach is safe; black stays tight (text and forest specks are black).
  bridgeRadius: 3,
  bridgeRadiusColored: 6,
  // shape filter
  glyphDiag: 42, // px: raw segments below this are glyphs UNLESS thin (weak fragments)
  weakThinMax: 8, // px: area/diag ceiling for a small fragment to stay "weak" rather than glyph
  markerFillMin: 0.35, // compact colored comps this filled are markers (weak, rescuable)
  blackMarkerFillMin: 0.55, // solid diamonds on black lines (text glyphs are less filled)
  markerElongMax: 1.8, // PCA axis ratio ceiling: diamonds ~1, stub line pieces >2
  markerZoneRad: 8, // px: skeleton-exclusion disk radius around a marker centroid
  fragStraightMax: 0.22, // straightness ceiling for weak black thin fragments
  // (line pieces chopped by markers/crossings bend slightly; text letters are
  // far curvier AND still have to pass endpoint linking to a strong segment)
  minDiagColored: 50, // px: minimum bridged-group extent, green/blue
  minDiagBlack: 60, // px: minimum bridged-group extent, black
  weakChainMinDiag: 60, // px: weak-only colored group kept if this long (band-covered lines)
  leaderMaxDiag: 400, // black groups shorter than this touching a punched box = sign leader lines
  liftClearDist: 5, // px: black pixels this close to LIFT maroon are outline — cleared
  liftMinDiag: 150, // px: maroon comps at least this long count as lift lines (not icons)
  // lift furniture: lifts carry parallel black furniture the outline clearing
  // misses — a thin drop-shadow line offset ~10-18px from the cable, and dark
  // end-of-lift stubs. Such ink spends nearly ALL of its length inside the
  // lift corridor; real trails only cross it briefly (measured max 0.38).
  liftSideDist: 14, // px (Chebyshev): corridor half-width around lift maroon
  liftSideFracMax: 0.55, // black groups above this in-corridor fraction = lift furniture
  liftConnClearDist: 5, // px: synthetic connectors this close to lift maroon carry no skeleton
  linkGap: 32, // px: max gap endpoint linking will jump along a segment's axis
  linkLateral: 4, // px: corridor half-width for the linking march
  maxAreaPerDiag: 18, // px: area/diagonal ceiling (thinness) for lines
  compactFillMax: 0.30, // bbox fill ratio ceiling for mid-size components
  compactRescueFillMax: 0.45, // moderately-compact black elbows may still link-rescue
  minSolidity: 5.7, // colored classes: ribbons are solid, speckle is not
  minSolidityBlack: 6.1, // black needs a stricter floor (forest shadow chains)
  // black lift rejection: a gondola/lift line is STRAIGHT and hugs maroon ink
  // (red cable core / red station text); black trail lines curve.
  liftNearDist: 5, // px: gondolas have maroon immediately inside their black outline
  liftFracMax: 0.45, // fraction of samples near maroon above which black CC = lift
  liftStraightMax: 0.025, // PCA residual RMS / diag below which a CC counts as straight
  // final mask erosion (0 = keep full ink body; the centerline skeleton is
  // computed separately and is what position-sensitive consumers should use)
  erode: 0,
  skyDarkV: 0.5,
};

export async function loadImage(path) {
  const { data, info } = await sharp(path).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  return { data, width: info.width, height: info.height };
}

function hsvOf(data, i) {
  const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  let h = 0;
  if (d > 0) {
    if (mx === r) h = ((g - b) / d + 6) % 6;
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
  }
  return [h * 60, mx > 0 ? d / mx : 0, mx, d];
}

function inHue(h, min, max) {
  return min <= max ? h >= min && h < max : h >= min || h < max;
}

// class ids in the label map
export const CLS = { none: 0, green: 1, blue: 2, black: 3, maroon: 4, yellow: 5, magenta: 6 };

/**
 * Per-pixel ink classification + skyline.
 * Returns {cls, core, skyline}: `cls` holds the GROW-level class per pixel,
 * `core` is 1 where the pixel is unmistakable core ink of that class.
 */
export function classifyPixels(img, P = DEFAULT_PARAMS) {
  const { data, width: W, height: H } = img;
  const cls = new Uint8Array(W * H);
  const core = new Uint8Array(W * H);
  const skyline = new Int32Array(W);
  for (let x = 0; x < W; x++) {
    let run = 0, y = 0;
    const maxScan = Math.floor(H * 0.45);
    for (; y < maxScan; y++) {
      const [, , v] = hsvOf(data, (y * W + x) * 4);
      if (v < P.skyDarkV) { run++; if (run >= 3) break; } else run = 0;
    }
    skyline[x] = y - run + 1;
  }
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const px = y * W + x;
      const [h, s, v, d] = hsvOf(data, px * 4);
      let c = CLS.none, isCore = 0;
      // saturated reject inks take priority
      if (inHue(h, P.maroon.hMin, P.maroon.hMax) && s >= P.maroon.sMin && v >= P.maroon.vMin && v <= P.maroon.vMax) c = CLS.maroon;
      else if (inHue(h, P.magenta.hMin, P.magenta.hMax) && s >= P.magenta.sMin && v >= P.magenta.vMin) c = CLS.magenta;
      else if (inHue(h, P.yellow.hMin, P.yellow.hMax) && s >= P.yellow.sMin && v >= P.yellow.vMin) c = CLS.yellow;
      else if (y > skyline[x] && inHue(h, P.green.hMin, P.green.hMax) && s >= P.green.growS && v >= P.green.growV) {
        c = CLS.green;
        isCore = s >= P.green.coreS && v >= P.green.coreV ? 1 : 0;
      } else if (y > skyline[x] && inHue(h, P.blue.hMin, P.blue.hMax) && s >= P.blue.growS && v >= P.blue.growV) {
        c = CLS.blue;
        isCore = s >= P.blue.coreS && v >= P.blue.coreV ? 1 : 0;
      } else if (v <= P.black.growV && d <= P.black.growDiff) {
        // guard against green-cast forest shadow: true line ink is neutral
        const gcast = data[px * 4 + 1] - (data[px * 4] + data[px * 4 + 2]) / 2;
        if (gcast <= P.black.greenCastMax) {
          c = CLS.black;
          isCore = v <= P.black.coreV && d <= P.black.coreDiff ? 1 : 0;
        }
      }
      cls[px] = c;
      core[px] = isCore;
    }
  }
  return { cls, core, skyline };
}

/**
 * Connected components of cls===target after morphological bridging: the
 * binary mask is dilated by `bridge` so segments separated by small gaps
 * (line crossings, icons, anti-aliased pinches) group into one component;
 * per-component pixel lists and bboxes are restricted to ORIGINAL pixels.
 */
export function bridgedComponents(cls, W, H, target, bridge) {
  let bin = new Uint8Array(W * H);
  for (let p = 0; p < W * H; p++) bin[p] = cls[p] === target ? 1 : 0;
  const orig = bin;
  let dil = bin;
  for (let r = 0; r < bridge; r++) {
    const next = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const p = y * W + x;
        if (dil[p]) { next[p] = 1; continue; }
        const up = y > 0, dn = y < H - 1, lf = x > 0, rt = x < W - 1;
        if ((up && dil[p - W]) || (dn && dil[p + W]) || (lf && dil[p - 1]) || (rt && dil[p + 1]) ||
            (up && lf && dil[p - W - 1]) || (up && rt && dil[p - W + 1]) ||
            (dn && lf && dil[p + W - 1]) || (dn && rt && dil[p + W + 1])) next[p] = 1;
      }
    }
    dil = next;
  }
  const dilCls = dil; // treat as cls with target=1
  const { comps: dilComps, labels } = components(dilCls, W, H, 1);
  const comps = [];
  for (const dc of dilComps) {
    let n = 0, minX = Infinity, maxX = -1, minY = Infinity, maxY = -1;
    const pixels = [];
    for (const p of dc.pixels) {
      if (!orig[p]) continue;
      pixels.push(p);
      n++;
      const x = p % W, y = (p / W) | 0;
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }
    if (n === 0) continue;
    comps.push({ id: comps.length, n, minX, maxX, minY, maxY, pixels });
  }
  return { comps, labels };
}

/** Union-find connected components of cls===target (8-conn). Returns {labels, comps}. */
export function components(cls, W, H, target) {
  const labels = new Int32Array(W * H).fill(-1);
  const stackX = new Int32Array(1 << 20);
  const stackY = new Int32Array(1 << 20);
  const comps = [];
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const p = y * W + x;
      if (cls[p] !== target || labels[p] !== -1) continue;
      const id = comps.length;
      let sp = 0, n = 0;
      let minX = x, maxX = x, minY = y, maxY = y;
      stackX[sp] = x; stackY[sp] = y; sp++;
      labels[p] = id;
      const pixels = [];
      while (sp > 0) {
        sp--;
        const cx = stackX[sp], cy = stackY[sp];
        pixels.push(cy * W + cx);
        n++;
        if (cx < minX) minX = cx; if (cx > maxX) maxX = cx;
        if (cy < minY) minY = cy; if (cy > maxY) maxY = cy;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          if (!dx && !dy) continue;
          const nx = cx + dx, ny = cy + dy;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
          const np = ny * W + nx;
          if (cls[np] === target && labels[np] === -1) {
            labels[np] = id;
            stackX[sp] = nx; stackY[sp] = ny; sp++;
          }
        }
      }
      comps.push({ id, n, minX, maxX, minY, maxY, pixels });
    }
  }
  return { labels, comps };
}

/**
 * Quality filter on RAW (unmerged) segments: keep stroke-like pieces, drop
 * text glyphs, icons, tree clusters, speckle and blobs. Length is judged
 * later on bridged groups, not here.
 */
export function segmentQualityFilter(comps, core, cls, W, H, target, P = DEFAULT_PARAMS, debug = null) {
  const kept = [];
  const reject = (c, reason, extra) => {
    if (debug) debug.push({ target, reason, extra, minX: c.minX, maxX: c.maxX, minY: c.minY, maxY: c.maxY, n: c.n });
  };
  const weak = [];
  const markers = []; // black diamond/square marker comps (kept for connectivity only)
  for (const c of comps) {
    const w = c.maxX - c.minX + 1, h = c.maxY - c.minY + 1;
    const diag = Math.hypot(w, h);
    const fill = c.n / (w * h);
    if (diag < P.glyphDiag) {
      // Small fragments: colored thin stroke pieces may be rescued by grouping
      // with a strong segment. Small BLACK fragments are never rescued — dark
      // specks blanket the forest and text is black, so rescue costs precision.
      const thinFrag = c.n / diag <= P.weakThinMax;
      const markerLike = diag >= 18 && fill >= P.markerFillMin;
      // a diamond/square marker is solid AND isotropic (PCA axes comparable);
      // a stubby chopped LINE piece can match the fill test but is elongated —
      // both are weak (rescuable by linking) but only true markers get their
      // interiors excluded from the centerline skeleton
      const solidSmall = diag >= 18 && diag <= 40 && fill >= P.blackMarkerFillMin;
      const blackDiamond = solidSmall && elongation(c, W) <= P.markerElongMax;
      const blackStub = solidSmall && !blackDiamond;
      if (target === CLS.black && blackDiamond) markers.push(c);
      // black thin fragments are admitted only if STRAIGHT (line pieces are
      // smooth segments of a stroke; letters are curved multi-stroke shapes) —
      // and even then they must pass collinear linking to a strong segment
      const straightFrag = thinFrag && straightness(c, W) <= P.fragStraightMax;
      if (diag >= 10 && (((target !== CLS.black) && (thinFrag || markerLike)) || (target === CLS.black && (straightFrag || blackDiamond || blackStub)))) {
        weak.push(c);
      } else reject(c, 'glyph', diag.toFixed(0));
      continue;
    }
    if (c.n / diag > P.maxAreaPerDiag) { reject(c, 'thinness', (c.n / diag).toFixed(1)); continue; }
    // compact filter: black only — colored "compact" comps are markers on
    // lines (rescued by bridging); colored blobs without vivid core already
    // die at the core test below. Mid-size compact pieces are usually icons or
    // big text glyphs, BUT a junction elbow (a curved line piece chopped short
    // by two crossings) also looks compact: those stay rescuable as weak —
    // they must still endpoint-link to a strong segment to survive.
    if (target === CLS.black && diag < 120 && fill > P.compactFillMax) {
      if (fill <= P.compactRescueFillMax && c.n / diag <= P.maxAreaPerDiag) weak.push(c);
      else reject(c, 'compact', fill.toFixed(2));
      continue;
    }
    // solidity: line ribbons are solid (interior pixels have ~8 same-class
    // neighbours); forest-shadow speckle chains are porous
    let neigh = 0;
    const step = Math.max(1, Math.floor(c.pixels.length / 600));
    let sampled = 0;
    for (let k = 0; k < c.pixels.length; k += step) {
      const p = c.pixels[k];
      const x = p % W, y = (p / W) | 0;
      sampled++;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        if (cls[ny * W + nx] === target) neigh++;
      }
    }
    const solidity = sampled > 0 ? neigh / sampled : 0;
    // hysteresis: require enough unmistakable core ink. BLUE comps recovered
    // from forest shadow can be all-muted (no core at all): demote SOLID,
    // reasonably thin ones to weak — they only survive if they group with an
    // anchored (core-rich) segment of the same line. Porous recovered webs
    // (forest shadow texture) stay rejected.
    let coreN = 0;
    for (const p of c.pixels) if (core[p]) coreN++;
    if (coreN < P.minCorePixels) {
      if (target === CLS.blue && solidity >= P.shadowSolidityMin && fill <= P.shadowFillMax) weak.push(c);
      else reject(c, 'core', coreN);
      continue;
    }
    const solidityFloor = target === CLS.black ? P.minSolidityBlack : P.minSolidity;
    if (solidity < solidityFloor) { reject(c, 'solidity', solidity.toFixed(1)); continue; }
    kept.push(c);
  }
  return { strong: kept, weak, markers };
}

/** PCA axis-length ratio sqrt(lMax/lMin): ~1 for isotropic shapes (diamonds,
 * squares), >2 for elongated stroke pieces. */
function elongation(c, W) {
  let sx = 0, sy = 0;
  const n = c.pixels.length;
  for (const p of c.pixels) { sx += p % W; sy += (p / W) | 0; }
  const mx = sx / n, my = sy / n;
  let cxx = 0, cxy = 0, cyy = 0;
  for (const p of c.pixels) {
    const dx = (p % W) - mx, dy = ((p / W) | 0) - my;
    cxx += dx * dx; cxy += dx * dy; cyy += dy * dy;
  }
  const tr = cxx + cyy, det = cxx * cyy - cxy * cxy;
  const disc = Math.sqrt(Math.max(0, (tr * tr) / 4 - det));
  const lMax = tr / 2 + disc, lMin = Math.max(1e-6, tr / 2 - disc);
  return Math.sqrt(lMax / lMin);
}

/** PCA line-fit residual RMS divided by diagonal: ~0 for straight components. */
function straightness(c, W) {
  let sx = 0, sy = 0;
  const n = c.pixels.length;
  const step = Math.max(1, Math.floor(n / 400));
  const xs = [], ys = [];
  for (let k = 0; k < n; k += step) {
    const p = c.pixels[k];
    const x = p % W, y = (p / W) | 0;
    xs.push(x); ys.push(y); sx += x; sy += y;
  }
  const m = xs.length;
  const mx = sx / m, my = sy / m;
  let cxx = 0, cxy = 0, cyy = 0;
  for (let k = 0; k < m; k++) {
    const dx = xs[k] - mx, dy = ys[k] - my;
    cxx += dx * dx; cxy += dx * dy; cyy += dy * dy;
  }
  // smallest eigenvalue of 2x2 covariance = variance perpendicular to main axis
  const tr = cxx + cyy, det = cxx * cyy - cxy * cxy;
  const lMin = tr / 2 - Math.sqrt(Math.max(0, (tr * tr) / 4 - det));
  const diag = Math.hypot(c.maxX - c.minX + 1, c.maxY - c.minY + 1);
  return Math.sqrt(Math.max(0, lMin / m)) / Math.max(1, diag);
}

/**
 * Drop black components that are BOTH straight and run alongside maroon ink —
 * that combination is a lift/gondola line (cable + red core/text). Black trail
 * lines that merely parallel a lift keep their curvature and survive.
 */
export function rejectLifts(blackComps, cls, W, H, P = DEFAULT_PARAMS, debug = null) {
  const R = P.liftNearDist;
  const kept = [];
  for (const c of blackComps) {
    if (straightness(c, W) > P.liftStraightMax) { kept.push(c); continue; }
    let near = 0, samples = 0;
    const step = Math.max(1, Math.floor(c.pixels.length / 200));
    for (let k = 0; k < c.pixels.length; k += step) {
      const p = c.pixels[k];
      const x = p % W, y = (p / W) | 0;
      samples++;
      let found = false;
      for (let dy = -R; dy <= R && !found; dy += 3) {
        for (let dx = -R; dx <= R && !found; dx += 3) {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
          if (cls[ny * W + nx] === CLS.maroon) found = true;
        }
      }
      if (found) near++;
    }
    if (samples > 0 && near / samples > P.liftFracMax) {
      if (debug) debug.push({ target: CLS.black, reason: 'lift', extra: (near / samples).toFixed(2), minX: c.minX, maxX: c.maxX, minY: c.minY, maxY: c.maxY, n: c.n });
      continue;
    }
    kept.push(c);
  }
  return kept;
}

/**
 * Remove wide structures (sign boxes, filled panels) from a single-class
 * binary view of `cls`: erode `rounds` times; survivors are blob cores; dilate
 * them back out by `dilate` and clear those pixels to CLS.none.
 */
export function punchOutWideStructures(cls, W, H, target, rounds, dilate, punchedOut = null) {
  let cur = new Uint8Array(W * H);
  for (let p = 0; p < W * H; p++) cur[p] = cls[p] === target ? 1 : 0;
  for (let r = 0; r < rounds; r++) {
    const next = new Uint8Array(W * H);
    for (let y = 1; y < H - 1; y++) {
      for (let x = 1; x < W - 1; x++) {
        const p = y * W + x;
        if (cur[p] && cur[p - 1] && cur[p + 1] && cur[p - W] && cur[p + W]) next[p] = 1;
      }
    }
    cur = next;
  }
  // collect core pixels, then clear a disk around each
  const cores = [];
  for (let p = 0; p < W * H; p++) if (cur[p]) cores.push(p);
  for (const p of cores) {
    const x = p % W, y = (p / W) | 0;
    for (let dy = -dilate; dy <= dilate; dy++) {
      for (let dx = -dilate; dx <= dilate; dx++) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const np = ny * W + nx;
        if (cls[np] === target) { cls[np] = CLS.none; if (punchedOut) punchedOut[np] = 1; }
      }
    }
  }
  return cores.length;
}

/**
 * Zhang-Suen thinning of a binary mask to its 1px centerline (skeleton).
 * Operates only inside the given bbox for speed.
 */
export function thinMask(bin, W, H) {
  let changed = true;
  const toClear = [];
  while (changed) {
    changed = false;
    for (let pass = 0; pass < 2; pass++) {
      toClear.length = 0;
      for (let y = 1; y < H - 1; y++) {
        for (let x = 1; x < W - 1; x++) {
          const p = y * W + x;
          if (!bin[p]) continue;
          const p2 = bin[p - W], p3 = bin[p - W + 1], p4 = bin[p + 1], p5 = bin[p + W + 1];
          const p6 = bin[p + W], p7 = bin[p + W - 1], p8 = bin[p - 1], p9 = bin[p - W - 1];
          const B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
          if (B < 2 || B > 6) continue;
          let A = 0;
          const seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2];
          for (let k = 0; k < 8; k++) if (seq[k] === 0 && seq[k + 1] === 1) A++;
          if (A !== 1) continue;
          if (pass === 0) {
            if (p2 * p4 * p6 !== 0 || p4 * p6 * p8 !== 0) continue;
          } else {
            if (p2 * p4 * p8 !== 0 || p2 * p6 * p8 !== 0) continue;
          }
          toClear.push(p);
        }
      }
      if (toClear.length) {
        changed = true;
        for (const p of toClear) bin[p] = 0;
      }
    }
  }
  return bin;
}

/**
 * Directional endpoint linking (the dashed-line workhorse): for each thin
 * fragment, march outward along its principal axis from both extreme points;
 * if a strong pixel lies within a narrow corridor within `linkGap`, draw the
 * connector into `outMask` and report success. Used to jump the gaps that
 * diamond markers, icons and park features punch into a line.
 */
export function linkFragmentToStrong(c, strongPx, outMask, W, H, P, maroonNear = null, requireCollinear = false) {
  // principal axis via covariance
  let sx = 0, sy = 0;
  for (const p of c.pixels) { sx += p % W; sy += (p / W) | 0; }
  const n = c.pixels.length, mx = sx / n, my = sy / n;
  let cxx = 0, cxy = 0, cyy = 0;
  for (const p of c.pixels) {
    const dx = (p % W) - mx, dy = ((p / W) | 0) - my;
    cxx += dx * dx; cxy += dx * dy; cyy += dy * dy;
  }
  const tr = cxx + cyy, det = cxx * cyy - cxy * cxy;
  const lMax = tr / 2 + Math.sqrt(Math.max(0, (tr * tr) / 4 - det));
  let ax = cxy, ay = lMax - cxx;
  const norm = Math.hypot(ax, ay);
  if (norm < 1e-6) { ax = 1; ay = 0; } else { ax /= norm; ay /= norm; }
  // extreme pixels along the axis
  let minProj = Infinity, maxProj = -Infinity, pMin = c.pixels[0], pMax = c.pixels[0];
  for (const p of c.pixels) {
    const proj = ((p % W) - mx) * ax + (((p / W) | 0) - my) * ay;
    if (proj < minProj) { minProj = proj; pMin = p; }
    if (proj > maxProj) { maxProj = proj; pMax = p; }
  }
  let linked = false;
  for (const [start, dir0] of [[pMax, 1], [pMin, -1]]) {
    const x0 = start % W, y0 = (start / W) | 0;
    // march along the LOCAL tangent at this end rather than the global axis:
    // a curved segment's end points where the line actually continues. Local
    // PCA over the pixels near this extreme, oriented outward.
    let dax = ax * dir0, day = ay * dir0;
    {
      let sx2 = 0, sy2 = 0, m = 0, cxx2 = 0, cxy2 = 0, cyy2 = 0;
      const pts = [];
      for (const p of c.pixels) {
        const px = p % W, py = (p / W) | 0;
        if (Math.abs(px - x0) > 22 || Math.abs(py - y0) > 22) continue;
        pts.push([px, py]); sx2 += px; sy2 += py; m++;
      }
      if (m >= 8) {
        const mx2 = sx2 / m, my2 = sy2 / m;
        for (const [px, py] of pts) {
          const dx = px - mx2, dy = py - my2;
          cxx2 += dx * dx; cxy2 += dx * dy; cyy2 += dy * dy;
        }
        const tr2 = cxx2 + cyy2, det2 = cxx2 * cyy2 - cxy2 * cxy2;
        const lMax2 = tr2 / 2 + Math.sqrt(Math.max(0, (tr2 * tr2) / 4 - det2));
        let bx = cxy2, by = lMax2 - cxx2;
        const bn = Math.hypot(bx, by);
        if (bn > 1e-6) {
          bx /= bn; by /= bn;
          // orient outward: from the local centroid toward this extreme
          if (bx * (x0 - mx2) + by * (y0 - my2) < 0) { bx = -bx; by = -by; }
          dax = bx; day = by;
        }
      }
    }
    const dir = 1; // direction is baked into the oriented tangent
    for (let t = 2; t <= P.linkGap; t++) {
      const tx = x0 + dir * dax * t, ty = y0 + dir * day * t;
      let hit = false;
      for (let l = -P.linkLateral; l <= P.linkLateral && !hit; l++) {
        const px = Math.round(tx - dir * day * l), py = Math.round(ty + dir * dax * l);
        if (px < 0 || py < 0 || px >= W || py >= H) continue;
        if (strongPx[py * W + px]) hit = true;
      }
      if (hit) {
        // collinearity: the strong ink at the hit point must run in the same
        // direction as this fragment. A chopped line piece continues its line;
        // a text glyph (e.g. a vertical "I") meets the line at an angle.
        if (requireCollinear) {
          let sx2 = 0, sy2 = 0, m = 0;
          const hx = Math.round(tx), hy = Math.round(ty);
          const pts = [];
          for (let dy = -8; dy <= 8; dy++) for (let dx = -8; dx <= 8; dx++) {
            const px = hx + dx, py = hy + dy;
            if (px < 0 || py < 0 || px >= W || py >= H) continue;
            if (strongPx[py * W + px]) { pts.push([px, py]); sx2 += px; sy2 += py; m++; }
          }
          if (m >= 6) {
            const mx2 = sx2 / m, my2 = sy2 / m;
            let cxx2 = 0, cxy2 = 0, cyy2 = 0;
            for (const [px, py] of pts) {
              const dx = px - mx2, dy = py - my2;
              cxx2 += dx * dx; cxy2 += dx * dy; cyy2 += dy * dy;
            }
            const tr2 = cxx2 + cyy2, det2 = cxx2 * cyy2 - cxy2 * cxy2;
            const lMax2 = tr2 / 2 + Math.sqrt(Math.max(0, (tr2 * tr2) / 4 - det2));
            let bx = cxy2, by = lMax2 - cxx2;
            const bn = Math.hypot(bx, by);
            if (bn > 1e-6) {
              bx /= bn; by /= bn;
              const cosang = Math.abs(dax * bx + day * by);
              if (cosang < 0.82) { continue; } // >~35 degrees: not a continuation
            }
          }
        }
        // a connector that runs ALONGSIDE lift ink is re-stitching a cleared
        // gondola outline — abort. Perpendicular lift crossings only brush
        // maroon briefly and stay under the threshold.
        if (maroonNear) {
          let alongside = 0;
          for (let u = 0; u <= t; u++) {
            const px = Math.round(x0 + dir * dax * u), py = Math.round(y0 + dir * day * u);
            if (px < 3 || py < 3 || px >= W - 3 || py >= H - 3) continue;
            let m = false;
            for (let dy = -3; dy <= 3 && !m; dy += 3) for (let dx = -3; dx <= 3 && !m; dx += 3) if (maroonNear[(py + dy) * W + px + dx]) m = true;
            if (m) alongside++;
          }
          if (alongside / (t + 1) > 0.4) break;
        }
        for (let u = 0; u <= t; u++) {
          const px = Math.round(x0 + dir * dax * u), py = Math.round(y0 + dir * day * u);
          if (px < 1 || py < 1 || px >= W - 1 || py >= H - 1) continue;
          outMask[py * W + px] = 1;
          outMask[py * W + px + 1] = 1;
          outMask[(py + 1) * W + px] = 1;
        }
        linked = true;
        break;
      }
    }
  }
  return linked;
}

/**
 * Branch-aware spur pruning: walk from each degree-1 endpoint; if a junction
 * (degree>=3) is reached within `maxLen` steps, the walked chain is a thinning
 * artifact and is deleted. Real line ends walk further and are kept intact.
 */
export function pruneSpurs(bin, W, H, maxLen) {
  const deg = (p) => bin[p - 1] + bin[p + 1] + bin[p - W] + bin[p + W] +
    bin[p - W - 1] + bin[p - W + 1] + bin[p + W - 1] + bin[p + W + 1];
  const OFF = [-W - 1, -W, -W + 1, -1, 1, W - 1, W, W + 1];
  const endpoints = [];
  for (let y = 1; y < H - 1; y++) {
    for (let x = 1; x < W - 1; x++) {
      const p = y * W + x;
      if (bin[p] && deg(p) === 1) endpoints.push(p);
    }
  }
  for (const ep of endpoints) {
    if (!bin[ep]) continue;
    const chain = [ep];
    let prev = -1, cur = ep, isSpur = false;
    for (let step = 0; step < maxLen; step++) {
      let next = -1;
      for (const o of OFF) {
        const q = cur + o;
        if (q === prev || !bin[q]) continue;
        next = q;
        break;
      }
      if (next === -1) break; // isolated short chain: treat as spur
      if (deg(next) >= 3) { isSpur = true; break; }
      chain.push(next);
      prev = cur; cur = next;
    }
    if (isSpur) for (const p of chain) bin[p] = 0;
  }
  return bin;
}

/**
 * Skeleton tip extension: Zhang-Suen thinning retracts the centerline by about
 * half a stroke width at rounded stroke ends, and spur pruning at a flared tip
 * can retract it further. Walk outward from each degree-1 skeleton endpoint
 * along its local direction and re-extend the centerline while the ink mask
 * continues (never into `stop` pixels), so the skeleton reaches the true
 * stroke end.
 */
export function extendTips(bin, mask, stop, W, H, maxExt = 14) {
  const deg = (p) => bin[p - 1] + bin[p + 1] + bin[p - W] + bin[p + W] +
    bin[p - W - 1] + bin[p - W + 1] + bin[p + W - 1] + bin[p + W + 1];
  const OFF = [-W - 1, -W, -W + 1, -1, 1, W - 1, W, W + 1];
  const endpoints = [];
  for (let y = 1; y < H - 1; y++) {
    for (let x = 1; x < W - 1; x++) {
      const p = y * W + x;
      if (bin[p] && deg(p) === 1) endpoints.push(p);
    }
  }
  for (const ep of endpoints) {
    // local direction: endpoint minus the skeleton pixel a few steps back
    let prev = ep, cur = ep, steps = 0;
    for (; steps < 7; steps++) {
      let next = -1;
      for (const o of OFF) {
        const q = cur + o;
        if (q === prev || !bin[q]) continue;
        next = q;
        break;
      }
      if (next === -1) break;
      prev = cur; cur = next;
    }
    if (steps < 3) continue;
    const ex = ep % W, ey = (ep / W) | 0;
    let dx = ex - (cur % W), dy = ey - ((cur / W) | 0);
    const n = Math.hypot(dx, dy);
    if (n < 1e-6) continue;
    dx /= n; dy /= n;
    for (let t = 1; t <= maxExt; t++) {
      const x = Math.round(ex + dx * t), y = Math.round(ey + dy * t);
      if (x < 1 || y < 1 || x >= W - 1 || y >= H - 1) break;
      const p = y * W + x;
      if (!mask[p] || (stop && stop[p])) break;
      bin[p] = 1;
    }
  }
  return bin;
}

/** In-place 1px erosion of a labeled mask (4-neighbour). */
export function erodeMask(mask, W, H, rounds = 1) {
  for (let r = 0; r < rounds; r++) {
    const drop = [];
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const p = y * W + x;
        if (!mask[p]) continue;
        if (
          x === 0 || y === 0 || x === W - 1 || y === H - 1 ||
          !mask[p - 1] || !mask[p + 1] || !mask[p - W] || !mask[p + W]
        ) drop.push(p);
      }
    }
    for (const p of drop) mask[p] = 0;
  }
  return mask;
}

/**
 * Full detection: returns { lineMask, cls, skyline } where lineMask is a
 * Uint8Array with CLS.green/blue/black at kept line pixels, 0 elsewhere.
 */
export async function detectTrailLines(path, P = DEFAULT_PARAMS, debug = null) {
  const img = await loadImage(path);
  const { width: W, height: H } = img;
  const { cls, core, skyline } = classifyPixels(img, P);
  // Shadowed-blue recovery: bounded BFS from classified blue ink into
  // contiguous dark muted-teal pixels (blue ink under forest shadow). The
  // growth is seeded only by real blue ink, so isolated forest texture is
  // never admitted; the step bound keeps a line from swallowing a hillside.
  {
    const SB = P.shadowBlue;
    let ring = [];
    for (let p = 0; p < W * H; p++) if (cls[p] === CLS.blue) ring.push(p);
    for (let d = 0; d < SB.steps && ring.length; d++) {
      const next = [];
      for (const p of ring) {
        const x = p % W, y = (p / W) | 0;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          if (!dx && !dy) continue;
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
          const np = ny * W + nx;
          if (cls[np] !== CLS.none) continue;
          const [h, s, v] = hsvOf(img.data, np * 4);
          if (h >= SB.hMin && h < SB.hMax && s >= SB.sMin && v >= SB.vMin && v <= SB.vMax) {
            cls[np] = CLS.blue;
            next.push(np);
          }
        }
      }
      ring = next;
    }
  }
  const lineMask = new Uint8Array(W * H);
  const punched = new Uint8Array(W * H);
  // synthetic connector pixels (drawn by endpoint linking, not real ink)
  const synth = new Uint8Array(W * H);
  // Red/maroon label boxes: large, compact maroon components (lift lines are
  // large but thin — excluded by fill). Black graphics attached to them (sign
  // poles, leader lines) get rejected via the `punched` proximity test.
  {
    const { comps: maroonComps } = components(cls, W, H, CLS.maroon);
    for (const c of maroonComps) {
      const w = c.maxX - c.minX + 1, h = c.maxY - c.minY + 1;
      if (c.n >= 1500 && c.n / (w * h) >= 0.35) {
        for (const p of c.pixels) punched[p] = 1;
      }
    }
  }
  // lift/gondola lines are maroon with a black outline: clear black pixels
  // hugging maroon ink. Trails crossing a lift lose only a bridgeable sliver.
  let liftMaroon;
  {
    const R = P.liftClearDist;
    // only LONG maroon components are lifts; compact red icons (trees,
    // first-aid) must not trigger clearing of adjacent trail ink
    const isMaroon = new Uint8Array(W * H);
    const { comps: mComps } = components(cls, W, H, CLS.maroon);
    for (const c of mComps) {
      const diag = Math.hypot(c.maxX - c.minX + 1, c.maxY - c.minY + 1);
      if (diag >= P.liftMinDiag) for (const p of c.pixels) isMaroon[p] = 1;
    }
    let dil = isMaroon;
    for (let r = 0; r < R; r++) {
      const next = new Uint8Array(W * H);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const p = y * W + x;
        if (dil[p]) { next[p] = 1; continue; }
        if ((y > 0 && dil[p - W]) || (y < H - 1 && dil[p + W]) || (x > 0 && dil[p - 1]) || (x < W - 1 && dil[p + 1])) next[p] = 1;
      }
      dil = next;
    }
    for (let p = 0; p < W * H; p++) if (dil[p] && cls[p] === CLS.black) cls[p] = CLS.none;
    liftMaroon = isMaroon;
  }
  // lift corridor mask: everything within liftSideDist (Chebyshev) of lift
  // maroon. Used to reject black "lift furniture" (drop-shadow lines, end
  // stubs) that lives its whole life alongside a cable.
  const liftZone = new Uint8Array(W * H);
  // tight inner corridor: where a synthetic connector crossing a lift must
  // not contribute skeleton (the map breaks lines at lifts; GT counts the
  // interruption as off-line)
  const liftNear = new Uint8Array(W * H);
  {
    let ring = [];
    for (let p = 0; p < W * H; p++) if (liftMaroon[p]) { liftZone[p] = 1; liftNear[p] = 1; ring.push(p); }
    for (let d = 0; d < P.liftSideDist && ring.length; d++) {
      const next = [];
      for (const p of ring) {
        const x = p % W, y = (p / W) | 0;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          if (!dx && !dy) continue;
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
          const np = ny * W + nx;
          if (!liftZone[np]) {
            liftZone[np] = 1;
            if (d < P.liftConnClearDist) liftNear[np] = 1;
            next.push(np);
          }
        }
      }
      ring = next;
    }
  }
  // Black label boxes: a box interior fills its neighbourhood with dark ink
  // in a way no line geometry can. Integral image -> local 35x35 fill ratio;
  // slab pixels punched with a halo.
  {
    const iw = W + 1;
    const integral = new Float64Array((W + 1) * (H + 1));
    for (let y = 0; y < H; y++) {
      let rowSum = 0;
      for (let x = 0; x < W; x++) {
        rowSum += cls[y * W + x] === CLS.black ? 1 : 0;
        integral[(y + 1) * iw + x + 1] = integral[y * iw + x + 1] + rowSum;
      }
    }
    const R2 = P.blackBoxWin;
    const slab = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) {
      const y0 = Math.max(0, y - R2), y1 = Math.min(H - 1, y + R2);
      for (let x = 0; x < W; x++) {
        if (cls[y * W + x] !== CLS.black) continue;
        const x0 = Math.max(0, x - R2), x1 = Math.min(W - 1, x + R2);
        const sum = integral[(y1 + 1) * iw + x1 + 1] - integral[y0 * iw + x1 + 1] -
          integral[(y1 + 1) * iw + x0] + integral[y0 * iw + x0 + 1 - 1];
        const frac = sum / ((y1 - y0 + 1) * (x1 - x0 + 1));
        if (frac >= P.blackBoxFill) slab[y * W + x] = 1;
      }
    }
    // dilate slab by punch halo, clear black + record anchors
    let zone = slab;
    for (let r = 0; r < P.blackBoxPunchDilate; r++) {
      const next = new Uint8Array(W * H);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const q = y * W + x;
        if (zone[q]) { next[q] = 1; continue; }
        if ((y > 0 && zone[q - W]) || (y < H - 1 && zone[q + W]) || (x > 0 && zone[q - 1]) || (x < W - 1 && zone[q + 1])) next[q] = 1;
      }
      zone = next;
    }
    for (let p = 0; p < W * H; p++) {
      if (zone[p]) { punched[p] = 1; if (cls[p] === CLS.black) cls[p] = CLS.none; }
    }
  }
  // Solid black markers (diamonds/squares) + locally-thick illustration fills:
  // same integral-image trick at marker scale. NOT recorded in `punched` —
  // markers sit ON trails, and the leader-line tests must not fire on the
  // trail segments beside them. Recorded in `markerZone` instead, which is
  // subtracted from the centerline skeleton at the end.
  const markerZone = new Uint8Array(W * H);
  {
    const iw = W + 1;
    const integral = new Float64Array((W + 1) * (H + 1));
    for (let y = 0; y < H; y++) {
      let rowSum = 0;
      for (let x = 0; x < W; x++) {
        rowSum += cls[y * W + x] === CLS.black ? 1 : 0;
        integral[(y + 1) * iw + x + 1] = integral[y * iw + x + 1] + rowSum;
      }
    }
    const core = [];
    // two scales: 13x13 catches solid diamonds/squares; 21x21 catches
    // medium-thick illustration slabs (rooflines) that are porous at 13x13
    // but dominate the coarser window in a way no stroke geometry can
    // (measured: roof strip 0.67 vs 0.43 at the busiest real-trail junction).
    for (const [R2, fillMin] of [[P.markerWin, P.markerFill], [P.markerWin2, P.markerFill2]]) {
      for (let y = 0; y < H; y++) {
        const y0 = Math.max(0, y - R2), y1 = Math.min(H - 1, y + R2);
        for (let x = 0; x < W; x++) {
          if (cls[y * W + x] !== CLS.black) continue;
          const x0 = Math.max(0, x - R2), x1 = Math.min(W - 1, x + R2);
          const sum = integral[(y1 + 1) * iw + x1 + 1] - integral[y0 * iw + x1 + 1] -
            integral[(y1 + 1) * iw + x0] + integral[y0 * iw + x0];
          if (sum / ((y1 - y0 + 1) * (x1 - x0 + 1)) >= fillMin) core.push(y * W + x);
        }
      }
    }
    const D = P.markerPunchDilate;
    for (const p of core) {
      const x = p % W, y = (p / W) | 0;
      for (let dy = -D; dy <= D; dy++) for (let dx = -D; dx <= D; dx++) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const np = ny * W + nx;
        markerZone[np] = 1;
        if (cls[np] === CLS.black) cls[np] = CLS.none;
      }
    }
  }
  for (const target of [CLS.green, CLS.blue, CLS.black]) {
    if (target !== CLS.black) punchOutWideStructures(cls, W, H, target, P.wideErodeColored, P.wideDilate, punched);
    // Stage A: quality-filter RAW segments (metrics are only valid on simple,
    // unmerged strokes). Strong = definite stroke pieces; weak = small thin
    // fragments that may be rescued by grouping with a strong neighbour.
    let { comps: raw } = components(cls, W, H, target);
    // Sign graphics: black RAW segments attached to a label box (poles,
    // leader lines, strips between text rows) — reject before bridging can
    // absorb them into larger groups.
    if (target === CLS.black) {
      raw = raw.filter((c) => {
        const diag = Math.hypot(c.maxX - c.minX + 1, c.maxY - c.minY + 1);
        if (diag >= 300) return true;
        let near = false;
        for (let k = 0; k < c.pixels.length && !near; k += 3) {
          const p = c.pixels[k];
          const x = p % W, y = (p / W) | 0;
          for (let dy = -10; dy <= 10 && !near; dy += 5) {
            for (let dx = -10; dx <= 10 && !near; dx += 5) {
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
              if (punched[ny * W + nx]) near = true;
            }
          }
        }
        if (near && debug) debug.push({ target, reason: 'leaderRaw', extra: diag.toFixed(0), minX: c.minX, maxX: c.maxX, minY: c.minY, maxY: c.maxY, n: c.n });
        return !near;
      });
    }
    const { strong, weak, markers } = segmentQualityFilter(raw, core, cls, W, H, target, P, debug);
    // diamond/square markers that escaped the integral-image punch (small
    // diamonds fill a 13x13 window no better than a wide stroke): their
    // CENTERS are not "on the line" — exclude a disk around the centroid from
    // the skeleton. Only the center is excluded (not the whole comp) so the
    // line's centerline resumes right at the marker's rim, where the trail
    // genuinely continues.
    for (const c of markers) {
      let sx = 0, sy = 0;
      for (const p of c.pixels) { sx += p % W; sy += (p / W) | 0; }
      const mx = Math.round(sx / c.pixels.length), my = Math.round(sy / c.pixels.length);
      const R3 = P.markerZoneRad;
      for (let dy = -R3; dy <= R3; dy++) for (let dx = -R3; dx <= R3; dx++) {
        if (dx * dx + dy * dy > R3 * R3) continue;
        const nx = mx + dx, ny = my + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        markerZone[ny * W + nx] = 1;
      }
    }
    const clean = new Uint8Array(W * H);
    const strongPx = new Uint8Array(W * H);
    for (const c of strong) for (const p of c.pixels) { clean[p] = 1; strongPx[p] = 1; }
    // Weak fragments: colored ones join freely (colored ink is rare in
    // nature); BLACK ones are admitted only when directional endpoint linking
    // connects them to a strong segment along their own axis — that is what
    // separates a chopped line piece from a text glyph.
    const connectors = new Uint8Array(W * H);
    for (const c of weak) {
      if (target === CLS.black) {
        if (!linkFragmentToStrong(c, strongPx, connectors, W, H, P)) continue;
      } else {
        // colored weak comps join freely, but ALSO try to draw a connector to
        // strong ink: a circle marker sits ON its line, and the snowflake/park
        // icons beside it can push the resuming line ink beyond bridge reach
        linkFragmentToStrong(c, strongPx, connectors, W, H, P);
      }
      for (const p of c.pixels) clean[p] = 1;
    }
    // strong-to-strong linking across icon/feature gaps (e.g. a park feature
    // or highlight band interrupting a line)
    for (const c of strong) linkFragmentToStrong(c, strongPx, connectors, W, H, P);
    for (let p = 0; p < W * H; p++) if (connectors[p]) { clean[p] = 1; synth[p] = 1; }
    // Stage B: bridge across small gaps (crossings, icons). Keep a group only
    // if it is long enough AND anchored by at least one strong segment —
    // isolated chains of weak fragments (text) have no anchor and die.
    const { comps: groups } = bridgedComponents(clean, W, H, 1, target === CLS.black ? P.bridgeRadius : P.bridgeRadiusColored);
    const minDiag = target === CLS.black ? P.minDiagBlack : P.minDiagColored;
    for (const g of groups) {
      const diag = Math.hypot(g.maxX - g.minX + 1, g.maxY - g.minY + 1);
      let strongN = 0;
      for (const p of g.pixels) if (strongPx[p]) strongN++;
      // weak-only groups pass if they form a LONG chain (a line hidden inside a
      // highlight band fragments into all-weak pieces; map text is never
      // green/blue so long colored chains are safe)
      const weakChainOk = target !== CLS.black && strongN === 0 && diag >= P.weakChainMinDiag;
      if (diag < minDiag || (strongN === 0 && !weakChainOk)) {
        if (debug) debug.push({ target, reason: strongN === 0 ? 'noAnchor' : 'groupDiag', extra: diag.toFixed(0), minX: g.minX, maxX: g.maxX, minY: g.minY, maxY: g.maxY, n: g.n });
        continue;
      }
      // lift furniture: a black group that spends most of its length inside
      // the lift corridor is the cable's drop shadow / end stub, not a trail
      // (trails cross lifts at an angle and leave the corridor quickly)
      if (target === CLS.black) {
        let inZone = 0, zSamples = 0;
        const zStep = Math.max(1, Math.floor(g.pixels.length / 500));
        for (let k = 0; k < g.pixels.length; k += zStep) { zSamples++; if (liftZone[g.pixels[k]]) inZone++; }
        if (zSamples > 0 && inZone / zSamples >= P.liftSideFracMax) {
          if (debug) debug.push({ target, reason: 'liftSide', extra: (inZone / zSamples).toFixed(2), minX: g.minX, maxX: g.maxX, minY: g.minY, maxY: g.maxY, n: g.n });
          continue;
        }
      }
      // sign leader lines: short black stubs emanating from a punched-out box
      if (target === CLS.black && diag < P.leaderMaxDiag) {
        let nearPunched = false;
        for (let k = 0; k < g.pixels.length && !nearPunched; k += 4) {
          const p = g.pixels[k];
          const x = p % W, y = (p / W) | 0;
          for (let dy = -10; dy <= 10 && !nearPunched; dy += 5) {
            for (let dx = -10; dx <= 10 && !nearPunched; dx += 5) {
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
              if (punched[ny * W + nx]) nearPunched = true;
            }
          }
        }
        if (nearPunched) {
          if (debug) debug.push({ target, reason: 'leader', extra: diag.toFixed(0), minX: g.minX, maxX: g.maxX, minY: g.minY, maxY: g.maxY, n: g.n });
          continue;
        }
      }
      for (const p of g.pixels) lineMask[p] = target;
    }
  }
  if (P.erode > 0) erodeMask(lineMask, W, H, P.erode);
  // 1px centerline skeleton per class — the position-faithful line trace.
  // Short spurs (thinning artifacts at junctions and bumps) are pruned so the
  // centerline stays on the true line axis.
  const centerMask = new Uint8Array(W * H);
  for (const target of [CLS.green, CLS.blue, CLS.black]) {
    const bin = new Uint8Array(W * H);
    for (let p = 0; p < W * H; p++) bin[p] = lineMask[p] === target ? 1 : 0;
    thinMask(bin, W, H);
    pruneSpurs(bin, W, H, 2);
    // re-extend thinning-retracted tips to the true stroke ends (but never
    // into a lift corridor: the stroke ends there because the line breaks)
    {
      const clsMask = new Uint8Array(W * H);
      for (let p = 0; p < W * H; p++) clsMask[p] = lineMask[p] === target ? 1 : 0;
      extendTips(bin, clsMask, liftNear, W, H);
    }
    // marker interiors are not "on the line": connectors may cross a punched
    // diamond to keep the group connected, but the centerline must not claim
    // those pixels as line positions. Likewise a synthetic connector crossing
    // a lift cable is grouping glue, not line position: the map genuinely
    // breaks the line there.
    for (let p = 0; p < W * H; p++) {
      if (!bin[p]) continue;
      if (target === CLS.black && markerZone[p]) continue;
      if (synth[p] && liftNear[p]) continue;
      centerMask[p] = target;
    }
  }
  return { lineMask, centerMask, cls, core, skyline, width: W, height: H };
}
