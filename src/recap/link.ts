// A trip recap packed into a link (?resort=<id>&recap=<payload>), so a day can
// be shared and opened as a read-only map with no server and no account.
// Pure functions (no DOM): tests/recapLink.test.ts checks them.
//
// payload: 1~<name>~<YYYYMMDD>~<days>~<new>~<runs>
//   name  the trip's name, UTF-8 in base64url (at most NAME_MAX characters)
//   days  how many days the trip logged runs on, base 36
//   new   how many of its runs were new to the skier, base 36
//   runs  each skied trail as HASH_CHARS base64url characters of a hash of its
//         id, so the link doesn't depend on the order of the resort's trail
//         list (ids stay put when a trail list is rebuilt; a trail gone from
//         the list is left out when the link is opened)

const VERSION = '1';
const SEP = '~';
const HASH_CHARS = 5; // 30 bits: a collision within one resort's few hundred trails is about 1 in 10,000
export const NAME_MAX = 60;
const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';

export interface Recap {
  name: string;
  /** YYYY-MM-DD: the first day with runs */
  start: string;
  days: number;
  newCount: number;
  /** skied trail ids */
  trailIds: string[];
}

/** FNV-1a over the id's UTF-16 code units, folded to 30 bits. */
function hash30(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return (h ^ (h >>> 30)) & 0x3fffffff;
}

export function trailHash(id: string): string {
  let h = hash30(id);
  let out = '';
  for (let i = 0; i < HASH_CHARS; i++) {
    out = B64[h & 63] + out;
    h >>>= 6;
  }
  return out;
}

function toBase64Url(text: string): string {
  const bytes = new TextEncoder().encode(text);
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function fromBase64Url(s: string): string {
  const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/'));
  return new TextDecoder().decode(Uint8Array.from(bin, (c) => c.charCodeAt(0)));
}

export function encodeRecap(r: Recap): string {
  const name = [...r.name.trim()].slice(0, NAME_MAX).join('');
  const runs = [...new Set(r.trailIds.map(trailHash))].sort().join('');
  return [
    VERSION,
    toBase64Url(name),
    r.start.replace(/-/g, ''),
    Math.max(1, r.days).toString(36),
    Math.max(0, r.newCount).toString(36),
    runs,
  ].join(SEP);
}

/** The recap in a payload, its runs matched against a resort's trail ids;
 * null when the payload isn't one. */
export function decodeRecap(payload: string, trailIds: string[]): Recap | null {
  const parts = payload.split(SEP);
  if (parts.length !== 6 || parts[0] !== VERSION) return null;
  const [, name64, date, days36, new36, runs] = parts;
  if (!/^\d{8}$/.test(date) || runs.length % HASH_CHARS !== 0 || /[^A-Za-z0-9_-]/.test(runs)) return null;
  let name: string;
  try {
    name = [...fromBase64Url(name64)].slice(0, NAME_MAX).join('');
  } catch {
    return null;
  }
  const days = parseInt(days36, 36);
  const newCount = parseInt(new36, 36);
  if (!(days >= 1) || !(newCount >= 0)) return null;
  const byHash = new Map<string, string[]>();
  for (const id of trailIds) {
    const h = trailHash(id);
    byHash.set(h, [...(byHash.get(h) ?? []), id]);
  }
  const ids: string[] = [];
  for (let i = 0; i < runs.length; i += HASH_CHARS) ids.push(...(byHash.get(runs.slice(i, i + HASH_CHARS)) ?? []));
  return {
    name,
    start: `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6)}`,
    days,
    newCount: Math.min(newCount, ids.length),
    trailIds: ids,
  };
}

/** The address that opens a recap: this site's, so a preview deploy shares its own. */
export function recapUrl(origin: string, resortId: string, r: Recap): string {
  const u = new URL('/', origin);
  u.searchParams.set('resort', resortId);
  u.searchParams.set('recap', encodeRecap(r));
  return u.toString();
}
