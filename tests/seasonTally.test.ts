// Run with `npm test`. The season's tallies across resorts (api/_lib/season.ts)
// on the in-memory Redis (api/_lib/redis.ts). api/ imports with .js extensions
// (as Vercel runs it), so the modules are bundled with esbuild first.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { build } from 'esbuild';

const dir = mkdtempSync(join(tmpdir(), 'season-'));
const entry = join(dir, 'entry.ts');
const api = new URL('../api/_lib/', import.meta.url).pathname;
writeFileSync(entry, `export * from '${api}season.ts';\nexport { memoryRedis } from '${api}redis.ts';\n`);
await build({ entryPoints: [entry], bundle: true, platform: 'node', format: 'esm', outfile: join(dir, 'out.mjs'), logLevel: 'warning' });
const s = await import(join(dir, 'out.mjs'));

const JAN15 = Date.parse('2027-01-15T18:00:00Z');
const DAY = 86400000;

test('seasons run July to June; ski days are Mountain time', () => {
  assert.equal(s.seasonOf(Date.parse('2026-07-01T12:00:00Z')), '2026-27');
  assert.equal(s.seasonOf(Date.parse('2027-06-30T12:00:00Z')), '2026-27');
  assert.equal(s.seasonOf(Date.parse('2026-06-30T12:00:00Z')), '2025-26');
  // 2am UTC on Jan 16 is still Jan 15 in Colorado
  assert.equal(s.dayOf(Date.parse('2027-01-16T02:00:00Z')), '2027-01-15');
});

test('a vote counts once per device, trail and day; a change of mind moves it', async () => {
  const redis = s.memoryRedis(() => JAN15);
  const vote = (device: string, v: number, now = JAN15) => s.recordVote(redis, { resort: 'stowe', trail: 'nose-dive', device, vote: v, now });
  await vote('device-aaaa', 1);
  await vote('device-aaaa', 1); // tapped again
  await vote('device-bbbb', 1);
  await vote('device-bbbb', -1); // changed their mind
  await vote('device-cccc', 1);
  await vote('device-cccc', 0); // took it back
  await vote('device-aaaa', 1, JAN15 + DAY); // the next day counts again
  const sum = await s.seasonSummary(redis, '2026-27', JAN15 + DAY);
  assert.deepEqual(sum.totals, { votes: 3, marks: 0, resorts: 1 });
  assert.equal(sum.loved.length, 0, `fewer than ${s.MIN_VOTES} votes don't rank`);
});

test('marks count once per device, trail and day, by season and by the last 7 days', async () => {
  let now = JAN15;
  const redis = s.memoryRedis(() => now);
  const mark = (resort: string, trail: string, device: string, marked = true) => s.recordMark(redis, { resort, trail, device, marked, now });
  await mark('vail', 'riva-ridge', 'device-aaaa');
  await mark('vail', 'riva-ridge', 'device-aaaa'); // marked twice the same day
  await mark('vail', 'riva-ridge', 'device-bbbb');
  await mark('vail', 'riva-ridge', 'device-bbbb', false); // undone the same day
  await mark('vail', 'riva-ridge', 'device-bbbb');
  await mark('stowe', 'nose-dive', 'device-aaaa');
  now += 10 * DAY;
  await mark('stowe', 'nose-dive', 'device-aaaa'); // ten days later: a new skier-day
  await mark('stowe', 'nose-dive', 'device-cccc');
  await mark('stowe', 'nose-dive', 'device-cccc', false);
  const sum = await s.seasonSummary(redis, '2026-27', now);
  assert.deepEqual(sum.skied, [
    { resort: 'stowe', trail: 'nose-dive', count: 2 },
    { resort: 'vail', trail: 'riva-ridge', count: 2 },
  ]);
  assert.deepEqual(sum.skiedWeek, [{ resort: 'stowe', trail: 'nose-dive', count: 1 }]);
  assert.equal(sum.week.length, 7);
  assert.equal(sum.week[0], s.dayOf(now));
});

test('loved runs rank by the Wilson score, not the raw ratio', async () => {
  const redis = s.memoryRedis(() => JAN15);
  let n = 0;
  const votes = async (trail: string, up: number, down: number) => {
    for (let i = 0; i < up + down; i++) {
      await s.recordVote(redis, { resort: 'alta', trail, device: `device-${String(n++).padStart(6, '0')}`, vote: i < up ? 1 : -1, now: JAN15 });
    }
  };
  await votes('high-rustler', 40, 2);
  await votes('baldy-chutes', 5, 0);
  await votes('collins-face', 6, 6);
  const sum = await s.seasonSummary(redis, '2026-27', JAN15);
  assert.deepEqual(sum.loved.map((l: { trail: string }) => l.trail), ['high-rustler', 'baldy-chutes', 'collins-face']);
  assert.ok(s.wilson(5, 5) < s.wilson(40, 42));
  assert.equal(s.wilson(0, 0), 0);
});

test('the endpoints check what they are sent', async () => {
  const redis = s.memoryRedis(() => JAN15);
  const post = (body: unknown) => s.handleMarks(new Request('http://x/api/marks', { method: 'POST', body: JSON.stringify(body) }), redis, JAN15);
  assert.equal((await post({ resort: 'vail', trailId: 'riva-ridge', deviceId: 'device-aaaa', marked: true })).status, 200);
  for (const bad of [
    { resort: 'Vail!', trailId: 'riva-ridge', deviceId: 'device-aaaa', marked: true },
    { resort: 'vail', trailId: '../x', deviceId: 'device-aaaa', marked: true },
    { resort: 'vail', trailId: 'riva-ridge', deviceId: 'short', marked: true },
    { resort: 'vail', trailId: 'riva-ridge', deviceId: 'device-aaaa', marked: 'yes' },
  ]) assert.equal((await post(bad)).status, 400, JSON.stringify(bad));
  assert.equal((await s.handleMarks(new Request('http://x/api/marks', { method: 'POST', body: '{}' }), null)).status, 503);
  const res = await s.handleSeason(new Request('http://x/api/season'), redis, JAN15);
  assert.equal(res.status, 200);
  assert.match(res.headers.get('cache-control') ?? '', /s-maxage=600/);
  assert.equal((await res.json()).skied[0].trail, 'riva-ridge');
  assert.equal((await s.handleSeason(new Request('http://x/api/season?season=2026'), redis)).status, 400);
});
