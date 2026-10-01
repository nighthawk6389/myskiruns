// Which resort a pipeline script works on: `--resort <id>` (default
// killington), optionally `--panel <id>`, and where that resort's files live.
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export function resortArg(argv = process.argv) {
  const i = argv.indexOf('--resort');
  const id = i > 0 ? argv[i + 1] : 'killington';
  if (!/^[a-z0-9-]+$/.test(id ?? '')) throw new Error(`bad --resort ${id}`);
  return id;
}

/** `--panel <id>` for a resort drawn on several map panels (Vail), or null. */
export function panelArg(argv = process.argv) {
  const i = argv.indexOf('--panel');
  if (i < 0) return null;
  const id = argv[i + 1];
  if (!/^[a-z0-9-]+$/.test(id ?? '')) throw new Error(`bad --panel ${id}`);
  return id;
}

/** Absolute paths of a resort's data files and map image. A resort drawn on
 * several map panels keeps one trail list (trails.ts) and, per panel, its own
 * line pieces, proposals, reviews and paths in panels/<panel>/, with the map
 * in public/maps/<resort>-<panel>.jpg. */
export function resortPaths(id = resortArg(), panel = panelArg()) {
  const dir = resolve(root, 'src/data/resorts', id);
  const pdir = panel ? resolve(dir, 'panels', panel) : dir;
  return {
    id,
    panel,
    dir,
    trails: resolve(dir, 'trails.ts'),
    polylines: resolve(pdir, 'linePolylines.json'),
    proposals: resolve(pdir, 'trailProposals.json'),
    reviews: resolve(pdir, 'trailReviews.json'),
    paths: resolve(pdir, 'trailPaths.json'),
    map: resolve(root, 'public/maps', panel ? `${id}-${panel}.jpg` : `${id}.jpg`),
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
