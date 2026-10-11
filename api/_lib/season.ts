// Season tallies across every resort, for rankings of the season's runs: the
// trail-conditions votes (api/conditions.ts keeps those only 24 hours; these
// last the season) and anonymous run marks (api/marks.ts: a run marked skied).
//
// Each counts once per device, per trail, per day (America/Denver's), so a
// skier's opinion of a run counts once a day however often they tap, and a
// change of mind the same day moves their count instead of adding one:
//   myskiruns:season:<season>:votes:<resort>   hash  <trail>:up / <trail>:down -> count
//   myskiruns:season:<season>:marks:<resort>   hash  <trail> -> skier-days
//   myskiruns:day:<day>:marks:<resort>         hash  <trail> -> skiers that day (kept 15 days)
//   myskiruns:season:<season>:resorts          set   the resorts with any tally
//   myskiruns:voted:<day>:<resort>:<trail>:<device>, myskiruns:marked:...   what a device counted today (2 days)
// No trip, account or name is stored; a device id is kept only in the two-day
// "counted today" keys. A season runs from July 1 to June 30 ("2026-27").
import { counts, type Command, type Redis } from './redis.js';

const DAY_TZ = 'America/Denver';
const SEEN_TTL = 2 * 24 * 3600;
const DAY_TTL = 15 * 24 * 3600;
/** a run needs this many votes to rank as loved */
export const MIN_VOTES = 5;

export const TRAIL_ID = /^[a-z0-9-]{1,64}$/;
export const RESORT_ID = /^[a-z0-9-]{1,32}$/;
export const DEVICE_ID = /^[a-zA-Z0-9-]{8,64}$/;
export const SEASON_ID = /^\d{4}-\d{2}$/;

/** "2026-27" for any day from July 1, 2026 to June 30, 2027. */
export function seasonOf(ms: number): string {
  const [y, m] = dayOf(ms).split('-').map(Number);
  const start = m >= 7 ? y : y - 1;
  return `${start}-${String((start + 1) % 100).padStart(2, '0')}`;
}

/** The ski day (YYYY-MM-DD) in Mountain time: a mark late on a Vermont evening is still that day. */
export function dayOf(ms: number): string {
  return new Date(ms).toLocaleDateString('en-CA', { timeZone: DAY_TZ });
}

const k = {
  votes: (s: string, r: string) => `myskiruns:season:${s}:votes:${r}`,
  marks: (s: string, r: string) => `myskiruns:season:${s}:marks:${r}`,
  dayMarks: (d: string, r: string) => `myskiruns:day:${d}:marks:${r}`,
  resorts: (s: string) => `myskiruns:season:${s}:resorts`,
  voted: (d: string, r: string, t: string, dev: string) => `myskiruns:voted:${d}:${r}:${t}:${dev}`,
  marked: (d: string, r: string, t: string, dev: string) => `myskiruns:marked:${d}:${r}:${t}:${dev}`,
};

/** A device's vote on a trail (1, -1, or 0 to take it back), counted once a day. */
export async function recordVote(
  redis: Redis,
  v: { resort: string; trail: string; device: string; vote: number; now: number },
): Promise<void> {
  const s = seasonOf(v.now);
  const seen = k.voted(dayOf(v.now), v.resort, v.trail, v.device);
  const [prev] = (await redis.pipeline([['GET', seen]])) as (string | null)[];
  const before = prev === '1' ? 1 : prev === '-1' ? -1 : 0;
  if (before === v.vote) return;
  const cmds: Command[] = [];
  const side = (vote: number) => `${v.trail}:${vote > 0 ? 'up' : 'down'}`;
  if (before) cmds.push(['HINCRBY', k.votes(s, v.resort), side(before), -1]);
  if (v.vote) cmds.push(['HINCRBY', k.votes(s, v.resort), side(v.vote), 1], ['SET', seen, v.vote, 'EX', SEEN_TTL]);
  else cmds.push(['DEL', seen]);
  cmds.push(['SADD', k.resorts(s), v.resort]);
  await redis.pipeline(cmds);
}

/** A run marked skied (or unmarked again the same day), counted once a day per device. */
export async function recordMark(
  redis: Redis,
  m: { resort: string; trail: string; device: string; marked: boolean; now: number },
): Promise<void> {
  const s = seasonOf(m.now);
  const d = dayOf(m.now);
  const seen = k.marked(d, m.resort, m.trail, m.device);
  const [res] = await redis.pipeline([m.marked ? ['SET', seen, 1, 'NX', 'EX', SEEN_TTL] : ['DEL', seen]]);
  const changed = m.marked ? res === 'OK' : Number(res) === 1;
  if (!changed) return;
  const by = m.marked ? 1 : -1;
  await redis.pipeline([
    ['HINCRBY', k.marks(s, m.resort), m.trail, by],
    ['HINCRBY', k.dayMarks(d, m.resort), m.trail, by],
    ['EXPIRE', k.dayMarks(d, m.resort), DAY_TTL],
    ['SADD', k.resorts(s), m.resort],
  ]);
}

/** Lower bound of the Wilson score interval (95%): how good a run is at least,
 * given its votes, so 40 up and 2 down outranks 1 up and 0 down. */
export function wilson(up: number, n: number, z = 1.96): number {
  if (n <= 0) return 0;
  const p = up / n;
  return (p + (z * z) / (2 * n) - z * Math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)) / (1 + (z * z) / n);
}

export interface Ranked {
  resort: string;
  trail: string;
}

export interface SeasonSummary {
  season: string;
  /** the last 7 days, newest first */
  week: string[];
  /** most loved: at least MIN_VOTES votes, by Wilson score */
  loved: (Ranked & { up: number; down: number; score: number })[];
  /** most skied this season: skier-days */
  skied: (Ranked & { count: number })[];
  /** most skied in the last 7 days */
  skiedWeek: (Ranked & { count: number })[];
  totals: { votes: number; marks: number; resorts: number };
}

/** Every resort's tallies for a season, ranked (at most `limit` each). */
export async function seasonSummary(redis: Redis, season: string, now: number, limit = 50): Promise<SeasonSummary> {
  const week = Array.from({ length: 7 }, (_, i) => dayOf(now - i * 86400000));
  const [members] = (await redis.pipeline([['SMEMBERS', k.resorts(season)]])) as string[][];
  const resorts = (members ?? []).filter((r) => RESORT_ID.test(r)).sort();
  const cmds: Command[] = resorts.flatMap((r) => [
    ['HGETALL', k.votes(season, r)],
    ['HGETALL', k.marks(season, r)],
    ...week.map((d): Command => ['HGETALL', k.dayMarks(d, r)]),
  ]);
  const res = await redis.pipeline(cmds);
  const loved: SeasonSummary['loved'] = [];
  const skied: SeasonSummary['skied'] = [];
  const skiedWeek: SeasonSummary['skiedWeek'] = [];
  let votes = 0;
  let marks = 0;
  const per = 2 + week.length;
  resorts.forEach((resort, i) => {
    const v = counts(res[i * per]);
    const trails = new Set(Object.keys(v).map((f) => f.slice(0, f.lastIndexOf(':'))));
    for (const trail of trails) {
      const up = Math.max(0, v[`${trail}:up`] ?? 0);
      const down = Math.max(0, v[`${trail}:down`] ?? 0);
      votes += up + down;
      if (up + down >= MIN_VOTES) loved.push({ resort, trail, up, down, score: Math.round(wilson(up, up + down) * 1000) / 1000 });
    }
    for (const [trail, count] of Object.entries(counts(res[i * per + 1]))) {
      if (count > 0) skied.push({ resort, trail, count });
      marks += Math.max(0, count);
    }
    const w: Record<string, number> = {};
    for (let d = 0; d < week.length; d++) {
      for (const [trail, count] of Object.entries(counts(res[i * per + 2 + d]))) w[trail] = (w[trail] ?? 0) + count;
    }
    for (const [trail, count] of Object.entries(w)) if (count > 0) skiedWeek.push({ resort, trail, count });
  });
  const byCount = (a: { count: number; resort: string; trail: string }, b: typeof a) =>
    b.count - a.count || a.resort.localeCompare(b.resort) || a.trail.localeCompare(b.trail);
  loved.sort((a, b) => b.score - a.score || b.up - a.up || a.resort.localeCompare(b.resort) || a.trail.localeCompare(b.trail));
  return {
    season,
    week,
    loved: loved.slice(0, limit),
    skied: skied.sort(byCount).slice(0, limit),
    skiedWeek: skiedWeek.sort(byCount).slice(0, limit),
    totals: { votes, marks, resorts: resorts.length },
  };
}

const json = (body: unknown, status = 200, cache = 'no-store') =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': cache } });

/** POST /api/marks {resort, trailId, deviceId, marked}: a run marked skied, or unmarked. */
export async function handleMarks(req: Request, redis: Redis | null, now = Date.now()): Promise<Response> {
  if (req.method !== 'POST') return json({ error: 'Method not allowed.' }, 405);
  if (!redis) return json({ error: 'Season tallies are not set up on this server.' }, 503);
  let body: { resort?: unknown; trailId?: unknown; deviceId?: unknown; marked?: unknown };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return json({ error: 'Expected JSON.' }, 400);
  }
  const { resort, trailId, deviceId, marked } = body;
  if (typeof resort !== 'string' || !RESORT_ID.test(resort)) return json({ error: 'Bad resort.' }, 400);
  if (typeof trailId !== 'string' || !TRAIL_ID.test(trailId)) return json({ error: 'Bad trailId.' }, 400);
  if (typeof deviceId !== 'string' || !DEVICE_ID.test(deviceId)) return json({ error: 'Bad deviceId.' }, 400);
  if (typeof marked !== 'boolean') return json({ error: 'marked must be true or false.' }, 400);
  await recordMark(redis, { resort, trail: trailId, device: deviceId, marked, now });
  return json({ ok: true });
}

/** GET /api/season[?season=2026-27]: the season's rankings across every resort (cached 10 minutes). */
export async function handleSeason(req: Request, redis: Redis | null, now = Date.now()): Promise<Response> {
  if (req.method !== 'GET') return json({ error: 'Method not allowed.' }, 405);
  if (!redis) return json({ error: 'Season tallies are not set up on this server.' }, 503);
  const season = new URL(req.url).searchParams.get('season') ?? seasonOf(now);
  if (!SEASON_ID.test(season)) return json({ error: 'Bad season.' }, 400);
  return json(await seasonSummary(redis, season, now), 200, 'public, max-age=60, s-maxage=600, stale-while-revalidate=3600');
}
