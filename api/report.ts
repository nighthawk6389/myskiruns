// Vercel function: POST /api/report, a skier's report of something wrong with a
// trail on a map (api/_lib/reports.ts). Same Redis as the trail conditions.
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import { upstash } from './_lib/redis.js';
import { handleReport } from './_lib/reports.js';

export async function POST(req: Request) {
  return handleReport(req, upstash());
}
