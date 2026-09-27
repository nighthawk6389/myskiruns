import { useEffect, useState } from 'react';
import { detectTrailMask, DEFAULT_PARAMS, type DetectorParams } from './trailDetector.ts';

export interface TrailDetectionResult {
  /** A PNG data URL of the highlighted trail mask, sized to the source image. */
  overlayUrl: string | null;
  /** Fraction of (non-sky) pixels classified as trail. */
  coverage: number;
  loading: boolean;
}

interface Computed {
  overlayUrl: string | null;
  coverage: number;
}

/**
 * Runs the trail detector on an image (in a downscaled offscreen canvas) and
 * returns a transparent overlay highlighting the detected runs. The same
 * detection code is exercised by the Node evaluation harness, so what you see
 * here is exactly what `npm run detect:eval` scores.
 */
export function useTrailDetection(
  src: string,
  enabled: boolean,
  params: DetectorParams = DEFAULT_PARAMS,
  maxWidth = 1400,
): TrailDetectionResult {
  const [computed, setComputed] = useState<Computed | null>(null);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = src;
    img.onload = () => {
      const scale = Math.min(1, maxWidth / img.naturalWidth);
      const w = Math.round(img.naturalWidth * scale);
      const h = Math.round(img.naturalHeight * scale);
      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;
      ctx.drawImage(img, 0, 0, w, h);
      const imageData = ctx.getImageData(0, 0, w, h);
      const mask = detectTrailMask({ data: imageData.data, width: w, height: h }, params);

      let covered = 0;
      const out = ctx.createImageData(w, h);
      for (let px = 0; px < w * h; px++) {
        if (mask[px]) {
          covered++;
          const i = px * 4;
          out.data[i] = 56; // cyan highlight
          out.data[i + 1] = 245;
          out.data[i + 2] = 255;
          out.data[i + 3] = 150;
        }
      }
      ctx.putImageData(out, 0, 0);
      if (!cancelled) setComputed({ overlayUrl: canvas.toDataURL(), coverage: covered / (w * h) });
    };
    img.onerror = () => {
      if (!cancelled) setComputed({ overlayUrl: null, coverage: 0 });
    };

    return () => {
      cancelled = true;
    };
  }, [src, enabled, params, maxWidth]);

  if (!enabled) return { overlayUrl: null, coverage: 0, loading: false };
  if (!computed) return { overlayUrl: null, coverage: 0, loading: true };
  return { ...computed, loading: false };
}
