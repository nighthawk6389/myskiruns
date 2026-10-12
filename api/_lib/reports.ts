// "Something wrong with this trail?": skiers' reports of a wrong name, line or
// rating on a map (or a trail missing from it), kept for review in the same
// Redis as the trail conditions. Each report says which resort, map panel and
// trail, where on the map the skier tapped (percent of the image), what's wrong
// and an optional note; no device id or name is kept with it. A device may send
// DAILY_LIMIT reports a day. The newest KEEP are kept.
//   POST /api/report   (api/report.ts)  a report
//   GET  /api/reports  (api/reports.ts) the latest, with the REPORTS_TOKEN set in Vercel
import type { Redis } from './redis.js';
import { DEVICE_ID, RESORT_ID, TRAIL_ID, dayOf } from './season.js';

export const KINDS = ['name', 'line', 'rating', 'missing', 'other'] as const;
export type ReportKind = (typeof KINDS)[number];
export const NOTE_MAX = 500;
export const DAILY_LIMIT = 20;
const KEEP = 5000;
const LIST = 'myskiruns:reports';
const PANEL_ID = /^[a-z0-9-]{1,40}$/;

export interface Report {
  at: string;
  resort: string;
  panel: string | null;
  trailId: string | null;
  kind: ReportKind;
  note: string;
  /** where on the map the skier tapped, percent of the image */
  x: number | null;
  y: number | null;
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

const percent = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) && v >= 0 && v <= 100 ? Math.round(v * 100) / 100 : null);

export async function handleReport(req: Request, redis: Redis | null, now = Date.now()): Promise<Response> {
  if (req.method !== 'POST') return json({ error: 'Method not allowed.' }, 405);
  if (!redis) return json({ error: 'Reports are not set up on this server.' }, 503);
  let b: Record<string, unknown>;
  try {
    b = (await req.json()) as Record<string, unknown>;
  } catch {
    return json({ error: 'Expected JSON.' }, 400);
  }
  if (typeof b.resort !== 'string' || !RESORT_ID.test(b.resort)) return json({ error: 'Bad resort.' }, 400);
  if (typeof b.deviceId !== 'string' || !DEVICE_ID.test(b.deviceId)) return json({ error: 'Bad deviceId.' }, 400);
  if (typeof b.kind !== 'string' || !(KINDS as readonly string[]).includes(b.kind)) return json({ error: 'Bad kind.' }, 400);
  const trailId = typeof b.trailId === 'string' ? b.trailId : null;
  if (b.trailId != null && (trailId === null || !TRAIL_ID.test(trailId))) return json({ error: 'Bad trailId.' }, 400);
  if (trailId === null && b.kind !== 'missing' && b.kind !== 'other') return json({ error: 'Which trail?' }, 400);
  const panel = typeof b.panel === 'string' ? b.panel : null;
  if (b.panel != null && (panel === null || !PANEL_ID.test(panel))) return json({ error: 'Bad panel.' }, 400);
  // control characters (newlines included) become spaces
  const note =
    typeof b.note === 'string'
      ? [...b.note].map((c) => (c.charCodeAt(0) < 32 || c.charCodeAt(0) === 127 ? ' ' : c)).join('').replace(/\s+/g, ' ').trim().slice(0, NOTE_MAX)
      : '';

  const limit = `myskiruns:reports:limit:${dayOf(now)}:${b.deviceId}`;
  const [count] = await redis.pipeline([
    ['INCR', limit],
    ['EXPIRE', limit, 2 * 24 * 3600],
  ]);
  if (Number(count) > DAILY_LIMIT) return json({ error: 'That is a lot of reports for one day: thanks, and try again tomorrow.' }, 429);

  const report: Report = {
    at: new Date(now).toISOString(),
    resort: b.resort,
    panel,
    trailId,
    kind: b.kind as ReportKind,
    note,
    x: percent(b.x),
    y: percent(b.y),
  };
  await redis.pipeline([
    ['LPUSH', LIST, JSON.stringify(report)],
    ['LTRIM', LIST, 0, KEEP - 1],
  ]);
  return json({ ok: true });
}

/** Equal strings, compared in constant time. */
function same(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

/** GET /api/reports[?resort=<id>&limit=500], with "Authorization: Bearer <REPORTS_TOKEN>": the latest reports. */
export async function handleReports(req: Request, redis: Redis | null, token: string | undefined): Promise<Response> {
  if (!token || token.length < 16) return json({ error: 'Not found.' }, 404);
  const given = (req.headers.get('authorization') ?? '').replace(/^Bearer\s+/i, '');
  if (!same(given, token)) return json({ error: 'Not allowed.' }, 401);
  if (!redis) return json({ error: 'Reports are not set up on this server.' }, 503);
  const url = new URL(req.url);
  const resort = url.searchParams.get('resort');
  const limit = Math.min(KEEP, Math.max(1, Number(url.searchParams.get('limit')) || 500));
  const [raw] = (await redis.pipeline([['LRANGE', LIST, 0, KEEP - 1]])) as string[][];
  const reports = (raw ?? [])
    .map((r) => {
      try {
        return JSON.parse(r) as Report;
      } catch {
        return null;
      }
    })
    .filter((r): r is Report => !!r && (!resort || r.resort === resort))
    .slice(0, limit);
  return json({ count: reports.length, reports });
}
