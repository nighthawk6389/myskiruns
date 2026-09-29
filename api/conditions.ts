// Vercel function: GET / POST /api/conditions (see api/_lib/conditions.ts).
//
// Needs a Redis database with a REST API (Upstash, added from the Vercel
// Marketplace). Connecting it to the project sets KV_REST_API_URL and
// KV_REST_API_TOKEN (or the UPSTASH_REDIS_REST_* equivalents). Without them
// the endpoint answers 503 and the app keeps votes on the device.
import { handleConditions, type VoteStore } from './_lib/conditions';

const HASH = 'myskiruns:conditions';

function upstashStore(): VoteStore | null {
  const url = process.env.KV_REST_API_URL ?? process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.KV_REST_API_TOKEN ?? process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  const cmd = async (...args: string[]) => {
    const res = await fetch(url, {
      method: 'POST',
      headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
      body: JSON.stringify(args),
    });
    if (!res.ok) throw new Error(`Redis ${args[0]} failed: ${res.status}`);
    return ((await res.json()) as { result: unknown }).result;
  };
  return {
    async getAll() {
      // HGETALL comes back as a flat [field, value, field, value, ...] list
      const flat = ((await cmd('HGETALL', HASH)) as string[] | null) ?? [];
      const out: Record<string, string> = {};
      for (let i = 0; i + 1 < flat.length; i += 2) out[flat[i]] = flat[i + 1];
      return out;
    },
    async set(field, value) {
      await cmd('HSET', HASH, field, value);
    },
    async remove(fields) {
      if (fields.length) await cmd('HDEL', HASH, ...fields);
    },
  };
}

export async function GET(req: Request) {
  return handleConditions(req, upstashStore());
}

export async function POST(req: Request) {
  return handleConditions(req, upstashStore());
}
