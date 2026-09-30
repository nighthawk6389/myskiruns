// Shared trail-conditions votes (thumbs up / down), used by the Vercel
// function in api/conditions.ts and by the Vite dev server (vite.config.ts).
//
// Storage is one Redis hash: field "<trailId>:<deviceId>" ->
// "<vote>:<ms>[:<tag>,<tag>]". A device has at most one report per trail (a
// vote of 1 / -1 / 0 plus up to MAX_TAGS condition tags); only reports from
// the last WINDOW_MS count, because conditions change day to day.
import { MAX_TAGS, TAG_KEYS } from '../../src/conditionTags';

export interface VoteStore {
  getAll(): Promise<Record<string, string>>;
  set(field: string, value: string): Promise<void>;
  remove(fields: string[]): Promise<void>;
}

export interface ConditionCounts {
  up: number;
  down: number;
  /** tag -> number of reports carrying it */
  tags: Record<string, number>;
}

export const WINDOW_MS = 24 * 60 * 60 * 1000;
const TRAIL_ID = /^[a-z0-9-]{1,64}$/;
const DEVICE_ID = /^[a-zA-Z0-9-]{8,64}$/;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  });

export function tally(all: Record<string, string>, now: number) {
  const trails: Record<string, ConditionCounts> = {};
  const stale: string[] = [];
  for (const [field, value] of Object.entries(all)) {
    const [trailId] = field.split(':');
    const [voteStr, atStr, tagStr = ''] = value.split(':');
    const vote = Number(voteStr);
    if (!(now - Number(atStr) < WINDOW_MS)) {
      stale.push(field);
      continue;
    }
    const c = (trails[trailId] ??= { up: 0, down: 0, tags: {} });
    if (vote > 0) c.up++;
    else if (vote < 0) c.down++;
    for (const tag of tagStr.split(',')) if (TAG_KEYS.has(tag)) c.tags[tag] = (c.tags[tag] ?? 0) + 1;
  }
  return { trails, stale };
}

export async function handleConditions(req: Request, store: VoteStore | null): Promise<Response> {
  if (!store) return json({ error: 'Shared conditions are not set up on this server.' }, 503);
  const now = Date.now();

  if (req.method === 'GET') {
    const { trails } = tally(await store.getAll(), now);
    return json({ windowHours: WINDOW_MS / 3600000, trails });
  }

  if (req.method === 'POST') {
    let body: { trailId?: unknown; deviceId?: unknown; vote?: unknown; tags?: unknown };
    try {
      body = (await req.json()) as typeof body;
    } catch {
      return json({ error: 'Expected JSON.' }, 400);
    }
    const { trailId, deviceId, vote, tags = [] } = body;
    if (typeof trailId !== 'string' || !TRAIL_ID.test(trailId)) return json({ error: 'Bad trailId.' }, 400);
    if (typeof deviceId !== 'string' || !DEVICE_ID.test(deviceId)) return json({ error: 'Bad deviceId.' }, 400);
    if (vote !== 1 && vote !== -1 && vote !== 0) return json({ error: 'vote must be 1, -1 or 0.' }, 400);
    if (!Array.isArray(tags) || tags.length > MAX_TAGS || !tags.every((t) => typeof t === 'string' && TAG_KEYS.has(t))) {
      return json({ error: `tags must be up to ${MAX_TAGS} known condition tags.` }, 400);
    }

    const field = `${trailId}:${deviceId}`;
    if (vote === 0 && tags.length === 0) await store.remove([field]);
    else await store.set(field, `${vote}:${now}:${[...new Set(tags)].join(',')}`);

    const { trails, stale } = tally(await store.getAll(), now);
    if (stale.length) await store.remove(stale);
    return json({ windowHours: WINDOW_MS / 3600000, trails });
  }

  return json({ error: 'Method not allowed.' }, 405);
}

/** In-memory store for local development. */
export function memoryStore(): VoteStore {
  const data = new Map<string, string>();
  return {
    getAll: async () => Object.fromEntries(data),
    set: async (f, v) => void data.set(f, v),
    remove: async (fs) => fs.forEach((f) => data.delete(f)),
  };
}
