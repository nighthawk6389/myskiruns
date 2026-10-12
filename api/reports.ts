// Vercel function: GET /api/reports, the latest trail problem reports for
// review (api/_lib/reports.ts). Needs REPORTS_TOKEN set in Vercel (16+
// characters), sent as "Authorization: Bearer <token>"; without it, 404.
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import { upstash } from './_lib/redis.js';
import { handleReports } from './_lib/reports.js';

export async function GET(req: Request) {
  return handleReports(req, upstash(), process.env.REPORTS_TOKEN);
}
