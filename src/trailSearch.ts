/** Search over every resort's trails, for the resort picker ("which mountain has
 * an Outer Limits?"). The index is built with the app (dist/trail-index.json,
 * vite.config.ts) and fetched the first time a search needs it; the matching
 * is plain functions, so tests/trailSearch.test.ts runs them without a browser. */
import type { Difficulty } from './types.ts';
import { fold } from './resortSearch.ts';

export interface TrailHit {
  resortId: string;
  resortName: string;
  region: string;
  trailId: string;
  name: string;
  difficulty: Difficulty;
}

export interface TrailIndex {
  resorts: [id: string, name: string, region: string][];
  trails: [resort: number, id: string, name: string, difficulty: Difficulty][];
}

// apostrophes dropped ("ullrs" finds "Ullr's"), other punctuation a space
const bare = (s: string) =>
  fold(s)
    .replace(/['’]/g, '')
    .replace(/[.\-/&,()]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

/** How well a trail name matches a query: 0 the same name, 1 it starts with
 * it, 2 a word of it does, 3 every word of the query starts a word of it (any
 * order: "lower ridge" finds "Ridge Run, Lower"), null no match. */
function rank(name: string, q: string, words: string[]): number | null {
  if (name === q) return 0;
  if (name.startsWith(q)) return 1;
  const nameWords = name.split(' ');
  if (name.includes(` ${q}`)) return 2;
  if (words.every((w) => nameWords.some((n) => n.startsWith(w)))) return 3;
  return null;
}

/** Trails whose name matches the query, best match first, then by name and
 * resort; at most `limit`, with the total count. Queries under 2 characters find nothing. */
export function searchTrails(index: TrailIndex, query: string, limit = 30): { hits: TrailHit[]; total: number } {
  const q = bare(query);
  if (q.length < 2) return { hits: [], total: 0 };
  const words = q.split(' ');
  const found: { r: number; name: string; t: TrailIndex['trails'][number] }[] = [];
  for (const t of index.trails) {
    const name = bare(t[2]);
    const r = rank(name, q, words);
    if (r !== null) found.push({ r, name, t });
  }
  found.sort(
    (a, b) => a.r - b.r || a.name.localeCompare(b.name) || index.resorts[a.t[0]][1].localeCompare(index.resorts[b.t[0]][1]),
  );
  return {
    total: found.length,
    hits: found.slice(0, limit).map(({ t }) => {
      const [resortId, resortName, region] = index.resorts[t[0]];
      return { resortId, resortName, region, trailId: t[1], name: t[2], difficulty: t[3] };
    }),
  };
}

let loading: Promise<TrailIndex> | null = null;

/** The index, fetched once (the service worker keeps it for offline use). */
export function loadTrailIndex(): Promise<TrailIndex> {
  loading ??= fetch('/trail-index.json')
    .then((r) => {
      if (!r.ok) throw new Error(`trail index: ${r.status}`);
      return r.json() as Promise<TrailIndex>;
    })
    .catch((e) => {
      loading = null; // try again next time (offline, before it was ever fetched)
      throw e;
    });
  return loading;
}
