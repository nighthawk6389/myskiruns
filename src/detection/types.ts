// Raw RGBA image buffer (4 bytes per pixel), as produced by a <canvas>
// getImageData call in the browser or a JPEG decoder in Node.
export interface RgbaImage {
  data: Uint8Array | Uint8ClampedArray;
  width: number;
  height: number;
}

export type TrailLabel = 'trail' | 'off';

export interface GroundTruthPoint {
  id: number;
  x: number; // normalized [0,1]
  y: number; // normalized [0,1]
  label: TrailLabel;
}
