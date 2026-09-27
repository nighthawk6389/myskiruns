import type { RgbaImage } from './types.ts';
import { pixelFeatures } from './features.ts';

// Tunable thresholds for the trail detector. Defaults are calibrated against
// the labelled ground-truth points (see groundTruth.json) by the evaluation
// harness in scripts/evaluate.ts.
export interface DetectorParams {
  /** Minimum brightness for a snow/trail pixel. */
  valueMin: number;
  /** Maximum saturation; snow is near-neutral. */
  saturationMax: number;
  /** Maximum green tint; rejects forest. */
  greenExcessMax: number;
  /** Maximum blue/teal tint; rejects sky and deep shadow. */
  blueExcessMax: number;
  /**
   * Normalized y below which pixels are never trail. The map's sky/horizon
   * haze is bright and neutral (indistinguishable from snow by colour), but it
   * sits above the highest runs, so a row cutoff removes it cleanly.
   */
  skyYMax: number;
}

export const DEFAULT_PARAMS: DetectorParams = {
  valueMin: 0.5,
  saturationMax: 0.1,
  greenExcessMax: 0.03,
  blueExcessMax: 0.04,
  skyYMax: 0.07,
};

/** Colour-only test: does this RGB look like snow/trail surface? */
export function isTrailColor(
  r: number,
  g: number,
  b: number,
  p: DetectorParams = DEFAULT_PARAMS,
): boolean {
  const f = pixelFeatures(r, g, b);
  return (
    f.value >= p.valueMin &&
    f.saturation <= p.saturationMax &&
    f.greenExcess <= p.greenExcessMax &&
    f.blueExcess <= p.blueExcessMax
  );
}

/**
 * Per-column height (in rows) of the sky band at the top of the image. Sky and
 * horizon haze form a bright / non-forest region contiguous from the top edge;
 * the band ends at the first run of forest pixels (the ridge silhouette). White
 * runs lower on the mountain are not contiguous with the top, so they survive.
 */
export function computeSkyHeights(img: RgbaImage): Int32Array {
  const { data, width, height } = img;
  const heights = new Int32Array(width);
  const maxScan = Math.floor(height * 0.45);
  for (let x = 0; x < width; x++) {
    let forestRun = 0;
    let y = 0;
    for (; y < maxScan; y++) {
      const i = (y * width + x) * 4;
      const f = pixelFeatures(data[i], data[i + 1], data[i + 2]);
      // Sky (teal gradient + white horizon haze) is uniformly bright; the
      // mountain ridge below it is dark forest. Key the ridge on darkness so the
      // green-tinted sky is not mistaken for terrain.
      const isRidge = f.value < 0.5;
      if (isRidge) {
        forestRun++;
        if (forestRun >= 3) break; // hit the ridge
      } else {
        forestRun = 0;
      }
    }
    heights[x] = y - forestRun + 1;
  }
  return heights;
}

/** Produce a 0/1 trail mask (one byte per pixel) for an RGBA image. */
export function detectTrailMask(
  img: RgbaImage,
  p: DetectorParams = DEFAULT_PARAMS,
): Uint8Array {
  const { data, width, height } = img;
  const mask = new Uint8Array(width * height);
  const minSkyRows = Math.floor(p.skyYMax * height);
  const skyHeights = computeSkyHeights(img);
  for (let x = 0; x < width; x++) {
    const skyRows = Math.max(minSkyRows, skyHeights[x]);
    for (let y = skyRows; y < height; y++) {
      const px = y * width + x;
      const i = px * 4;
      mask[px] = isTrailColor(data[i], data[i + 1], data[i + 2], p) ? 1 : 0;
    }
  }
  return mask;
}

/**
 * Sample the detector at a normalized point: returns true when at least
 * `minFraction` of the pixels in a window of the given `radius` look like
 * trail surface. A fraction (rather than a strict majority) is the right model
 * for this map because runs are narrow corridors threaded through forest and
 * overlaid with coloured lift lines.
 */
export function sampleTrailAt(
  img: RgbaImage,
  nx: number,
  ny: number,
  p: DetectorParams = DEFAULT_PARAMS,
  radius = 5,
  minFraction = 0.3,
): boolean {
  if (ny < p.skyYMax) return false;
  const { data, width, height } = img;
  const cx = Math.round(nx * (width - 1));
  const cy = Math.round(ny * (height - 1));
  let trail = 0;
  let total = 0;
  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      const x = cx + dx;
      const y = cy + dy;
      if (x < 0 || y < 0 || x >= width || y >= height) continue;
      const i = (y * width + x) * 4;
      if (isTrailColor(data[i], data[i + 1], data[i + 2], p)) trail++;
      total++;
    }
  }
  return total > 0 && trail / total >= minFraction;
}
