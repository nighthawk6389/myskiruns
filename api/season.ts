// Vercel function: GET /api/season[?season=2026-27], the season's runs ranked
// across every resort: most loved (votes), most skied this season and this
// week (marks). See api/_lib/season.ts.
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import { upstash } from './_lib/redis.js';
import { handleSeason } from './_lib/season.js';

export async function GET(req: Request) {
  return handleSeason(req, upstash());
}
