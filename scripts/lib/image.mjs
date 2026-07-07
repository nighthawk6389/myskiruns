import jpeg from 'jpeg-js';
import { readFileSync, writeFileSync } from 'node:fs';

// Decode a JPEG file to {data:Uint8Array RGBA, width, height}
export function decodeJpeg(path) {
  const raw = readFileSync(path);
  const img = jpeg.decode(raw, { useTArray: true, formatAsRGBA: true });
  return { data: img.data, width: img.width, height: img.height };
}

// Nearest-neighbor downscale to target width, preserving aspect.
export function downscale(img, targetW) {
  const scale = targetW / img.width;
  const w = Math.round(img.width * scale);
  const h = Math.round(img.height * scale);
  const out = new Uint8Array(w * h * 4);
  for (let y = 0; y < h; y++) {
    const sy = Math.min(img.height - 1, Math.floor(y / scale));
    for (let x = 0; x < w; x++) {
      const sx = Math.min(img.width - 1, Math.floor(x / scale));
      const si = (sy * img.width + sx) * 4;
      const di = (y * w + x) * 4;
      out[di] = img.data[si];
      out[di + 1] = img.data[si + 1];
      out[di + 2] = img.data[si + 2];
      out[di + 3] = 255;
    }
  }
  return { data: out, width: w, height: h };
}

export function encodeJpeg(img, path, quality = 85) {
  const buf = jpeg.encode({ data: Buffer.from(img.data), width: img.width, height: img.height }, quality);
  writeFileSync(path, buf.data);
}
