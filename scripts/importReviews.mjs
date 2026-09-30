// Merge review decisions exported from the Killington Trail Check page into
// src/data/resorts/killington/trailReviews.json.
//
//   node scripts/importReviews.mjs <dir-of-exported-review-json-files> [--resort killington]
//
// Each file is one `reviews` document named <page-id>.json. The page uses
// `new-…` ids for trails added from the map (new-racer-s-edge -> racers-edge).
// A decision replaces the stored one only when it is newer, trails no longer
// in trails.ts are ignored, and a stored label position is kept when the page
// doesn't send one. Run `npm run trails:apply` afterwards.
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { basename, join } from 'node:path';
import { resortPaths } from './lib/resort.mjs';

const R = resortPaths();
const dir = process.argv[2];
if (!dir) {
  console.error('usage: node scripts/importReviews.mjs <dir>');
  process.exit(1);
}

const roster = new Set(
  [...readFileSync(R.trails, 'utf8').matchAll(/\{ id: '([^']+)', name:/g)].map((m) => m[1]),
);
const pageToRoster = (id) => (id.startsWith('new-') ? id.slice(4).replace(/-s(-|$)/g, 's$1') : id);

const path = R.reviews;
const doc = existsSync(path) ? JSON.parse(readFileSync(path, 'utf8')) : { reviews: {} };
const counts = { updated: [], unchanged: 0, ignored: [] };
for (const file of readdirSync(dir).filter((f) => f.endsWith('.json'))) {
  const raw = JSON.parse(readFileSync(join(dir, file), 'utf8'));
  const incoming = raw.data ?? raw;
  const id = pageToRoster(basename(file, '.json'));
  if (!roster.has(id)) {
    counts.ignored.push(id);
    continue;
  }
  const current = doc.reviews[id];
  if (current && current.at >= incoming.at) {
    counts.unchanged++;
    continue;
  }
  const next = {
    status: incoming.status,
    polylines: incoming.polylines ?? [],
    drawn: incoming.drawn ?? [],
    mapDifficulty: incoming.mapDifficulty ?? null,
    note: incoming.note ?? '',
    at: incoming.at,
  };
  if (current?.labelAt && !incoming.labelAt) next.labelAt = current.labelAt;
  doc.reviews[id] = next;
  counts.updated.push(id);
}
writeFileSync(path, JSON.stringify(doc, null, 1));
console.log(`updated ${counts.updated.length}: ${counts.updated.join(', ')}`);
console.log(`unchanged ${counts.unchanged}; ignored ${counts.ignored.length} not in trails.ts`);
