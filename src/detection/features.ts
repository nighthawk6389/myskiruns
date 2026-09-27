// Per-pixel color features used by the trail detector.
// Everything is derived from a single RGB triple (0-255) so the same code
// runs in the browser and in the Node evaluation harness.

export interface PixelFeatures {
  /** Brightness / value: max(r,g,b) in [0,1]. Snow runs are bright. */
  value: number;
  /** Saturation in [0,1]. Snow is near-neutral (low saturation). */
  saturation: number;
  /** g - (r+b)/2 in [-1,1]. Positive => green forest tint. */
  greenExcess: number;
  /** b - (r+g)/2 in [-1,1]. Positive => blue/teal tint (sky, shadows). */
  blueExcess: number;
}

export function pixelFeatures(r: number, g: number, b: number): PixelFeatures {
  const rf = r / 255;
  const gf = g / 255;
  const bf = b / 255;
  const max = Math.max(rf, gf, bf);
  const min = Math.min(rf, gf, bf);
  const saturation = max <= 0 ? 0 : (max - min) / max;
  return {
    value: max,
    saturation,
    greenExcess: gf - (rf + bf) / 2,
    blueExcess: bf - (rf + gf) / 2,
  };
}
