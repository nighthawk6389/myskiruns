// Vercel function: POST /api/marks, a run marked skied (or unmarked) for the
// season's tallies (api/_lib/season.ts). Uses the same Redis as the trail
// conditions (KV_REST_API_* or UPSTASH_REDIS_REST_*); without it, 503.
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import { upstash } from './_lib/redis.js';
import { handleMarks } from './_lib/season.js';

export async function POST(req: Request) {
  return handleMarks(req, upstash());
}
