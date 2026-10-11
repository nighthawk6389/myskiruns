// Redis for the season tallies (api/_lib/season.ts): Upstash's REST API, one
// pipeline of commands per request, or an in-memory stand-in for the Vite dev
// server and the tests (just the commands the tallies use).

export type Command = (string | number)[];

export interface Redis {
  /** run the commands in order, one round trip; each command's result */
  pipeline(commands: Command[]): Promise<unknown[]>;
}

/** Upstash (KV_REST_API_* from the Vercel Marketplace, or UPSTASH_REDIS_REST_*), or null when not set up. */
export function upstash(env: Record<string, string | undefined> = process.env): Redis | null {
  const url = env.KV_REST_API_URL ?? env.UPSTASH_REDIS_REST_URL;
  const token = env.KV_REST_API_TOKEN ?? env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  return {
    async pipeline(commands) {
      if (!commands.length) return [];
      const res = await fetch(`${url}/pipeline`, {
        method: 'POST',
        headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
        body: JSON.stringify(commands.map((c) => c.map(String))),
      });
      if (!res.ok) throw new Error(`Redis pipeline failed: ${res.status}`);
      const out = (await res.json()) as { result?: unknown; error?: string }[];
      return out.map((r) => {
        if (r.error) throw new Error(`Redis: ${r.error}`);
        return r.result;
      });
    },
  };
}

/** In memory: GET, SET (EX, NX), DEL, EXPIRE, HINCRBY, HGETALL, SADD, SMEMBERS. */
export function memoryRedis(now: () => number = Date.now): Redis {
  const strings = new Map<string, { v: string; until: number }>();
  const hashes = new Map<string, Map<string, number>>();
  const sets = new Map<string, Set<string>>();
  const expiry = new Map<string, number>();
  const alive = (k: string) => {
    const t = expiry.get(k);
    if (t !== undefined && t <= now()) {
      strings.delete(k);
      hashes.delete(k);
      sets.delete(k);
      expiry.delete(k);
    }
    const s = strings.get(k);
    if (s && s.until <= now()) strings.delete(k);
  };
  const run = (c: Command): unknown => {
    const [cmd, key, ...a] = c.map(String);
    alive(key);
    switch (cmd.toUpperCase()) {
      case 'GET':
        return strings.get(key)?.v ?? null;
      case 'SET': {
        const nx = a.includes('NX');
        const ex = a.indexOf('EX');
        if (nx && strings.has(key)) return null;
        strings.set(key, { v: a[0], until: ex >= 0 ? now() + Number(a[ex + 1]) * 1000 : Infinity });
        return 'OK';
      }
      case 'DEL': {
        const had = strings.delete(key) || hashes.delete(key) || sets.delete(key);
        return had ? 1 : 0;
      }
      case 'EXPIRE':
        expiry.set(key, now() + Number(a[0]) * 1000);
        return 1;
      case 'HINCRBY': {
        const h = hashes.get(key) ?? new Map<string, number>();
        hashes.set(key, h);
        const v = (h.get(a[0]) ?? 0) + Number(a[1]);
        h.set(a[0], v);
        return v;
      }
      case 'HGETALL':
        return [...(hashes.get(key) ?? new Map()).entries()].flatMap(([f, v]) => [f, String(v)]);
      case 'SADD': {
        const s = sets.get(key) ?? new Set<string>();
        sets.set(key, s);
        const before = s.size;
        a.forEach((m) => s.add(m));
        return s.size - before;
      }
      case 'SMEMBERS':
        return [...(sets.get(key) ?? [])];
      default:
        throw new Error(`memoryRedis: ${cmd} not supported`);
    }
  };
  return { pipeline: async (commands) => commands.map(run) };
}

/** HGETALL's flat [field, value, ...] list as numbers by field. */
export function counts(flat: unknown): Record<string, number> {
  const list = Array.isArray(flat) ? (flat as string[]) : [];
  const out: Record<string, number> = {};
  for (let i = 0; i + 1 < list.length; i += 2) out[list[i]] = Number(list[i + 1]) || 0;
  return out;
}
