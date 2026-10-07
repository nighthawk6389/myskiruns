/** The resort picker's search: plain functions, so tests/resortSearch.test.ts
 * can run them without a browser. */

export interface ResortOption {
  id: string;
  name: string;
  /** state or province */
  region: string;
  /** other places it is found by: a second state (a resort on a state line), its lake */
  also?: readonly string[];
}

/** Lower case, no accents, straight apostrophes: "Smugglers’" finds "smugglers'". */
export function fold(s: string): string {
  return s
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[’‘`]/g, "'")
    .toLowerCase()
    .trim();
}

/** Postal abbreviations, so "vt" or "co" finds a state's resorts. */
const ABBREVIATIONS: Record<string, string> = {
  alberta: 'ab',
  'british columbia': 'bc',
  california: 'ca',
  colorado: 'co',
  idaho: 'id',
  maine: 'me',
  montana: 'mt',
  nevada: 'nv',
  'new hampshire': 'nh',
  'new mexico': 'nm',
  'new york': 'ny',
  oregon: 'or',
  quebec: 'qc',
  utah: 'ut',
  vermont: 'vt',
  washington: 'wa',
  wyoming: 'wy',
};

/** How well a resort matches a query: 0 the name starts with it, 1 a word of
 * the name does, 2 the name contains it, 3 its region or another place it is
 * found by (or a state's postal abbreviation) matches, null no match.
 * Apostrophes, hyphens and dots don't count ("smugglers notch", "jaypeak"). */
function rank(r: ResortOption, q: string): number | null {
  const name = fold(r.name);
  const bare = (s: string) => s.replace(/['\-.]/g, '');
  const qb = bare(q).replace(/\s+/g, ' ');
  const nb = bare(name);
  if (nb.startsWith(qb) || nb.replace(/\s+/g, '').startsWith(qb.replace(/\s+/g, ''))) return 0;
  if (nb.split(/\s+/).some((w) => w.startsWith(qb))) return 1;
  if (nb.includes(qb) || nb.replace(/\s+/g, '').includes(qb.replace(/\s+/g, ''))) return 2;
  for (const place of [r.region, ...(r.also ?? [])].map(fold)) {
    if (place.startsWith(q) || place.split(/\s+/).some((w) => w.startsWith(q))) return 3;
    if (ABBREVIATIONS[place] === qb) return 3;
  }
  return null;
}

/** The resorts matching a query, best match first, then by name. An empty
 * query lists every resort by name. */
export function searchResorts<T extends ResortOption>(resorts: readonly T[], query: string): T[] {
  const q = fold(query);
  const byName = (a: T, b: T) => a.name.localeCompare(b.name);
  if (!q) return [...resorts].sort(byName);
  return resorts
    .map((r) => ({ r, k: rank(r, q) }))
    .filter((x): x is { r: T; k: number } => x.k !== null)
    .sort((a, b) => a.k - b.k || byName(a.r, b.r))
    .map((x) => x.r);
}

/** Resorts grouped by region (regions and resorts in alphabetical order), for
 * the list shown before anything is typed. */
export function byRegion<T extends ResortOption>(resorts: readonly T[]): { region: string; resorts: T[] }[] {
  const groups = new Map<string, T[]>();
  for (const r of searchResorts(resorts, '')) {
    groups.set(r.region, [...(groups.get(r.region) ?? []), r]);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([region, rs]) => ({ region, resorts: rs }));
}
