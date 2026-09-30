// Which resort a pipeline script works on: `--resort <id>` (default
// killington), and where that resort's files live.
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export function resortArg(argv = process.argv) {
  const i = argv.indexOf('--resort');
  const id = i > 0 ? argv[i + 1] : 'killington';
  if (!/^[a-z0-9-]+$/.test(id ?? '')) throw new Error(`bad --resort ${id}`);
  return id;
}

/** Absolute paths of a resort's data files and map image. */
export function resortPaths(id = resortArg()) {
  const dir = resolve(root, 'src/data/resorts', id);
  return {
    id,
    dir,
    trails: resolve(dir, 'trails.ts'),
    polylines: resolve(dir, 'linePolylines.json'),
    proposals: resolve(dir, 'trailProposals.json'),
    reviews: resolve(dir, 'trailReviews.json'),
    paths: resolve(dir, 'trailPaths.json'),
    map: resolve(root, 'public/maps', `${id}.jpg`),
  };
}

/** Pixel size of a JPEG, read from its SOF header (no decoding). */
import { readFileSync } from 'node:fs';
export function jpegSize(file) {
  const b = readFileSync(file);
  let i = 2;
  while (i < b.length) {
    const marker = b[i + 1];
    const len = b.readUInt16BE(i + 2);
    // SOF0..SOF15 except DHT (C4), JPG (C8) and DAC (CC)
    if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
      return { width: b.readUInt16BE(i + 7), height: b.readUInt16BE(i + 5) };
    }
    i += 2 + len;
  }
  throw new Error(`no JPEG size in ${file}`);
}
