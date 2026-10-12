// Run with `npm test`. Skiers' reports of a wrong trail (api/_lib/reports.ts) on
// the in-memory Redis (api/_lib/redis.ts). api/ imports with .js extensions
// (as Vercel runs it), so the modules are bundled with esbuild first.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { build } from 'esbuild';

const dir = mkdtempSync(join(tmpdir(), 'reports-'));
const entry = join(dir, 'entry.ts');
const api = new URL('../api/_lib/', import.meta.url).pathname;
writeFileSync(entry, `export * from '${api}reports.ts';\nexport { memoryRedis } from '${api}redis.ts';\n`);
await build({ entryPoints: [entry], bundle: true, platform: 'node', format: 'esm', outfile: join(dir, 'out.mjs'), logLevel: 'warning' });
const r = await import(join(dir, 'out.mjs'));

const JAN15 = Date.parse('2027-01-15T18:00:00Z');
const DAY = 86400000;
const TOKEN = 'a-long-enough-review-token';
const GOOD = { resort: 'stowe', panel: 'map', trailId: 'nose-dive', kind: 'name', note: 'This is Goat', x: 41.234, y: 55.5, deviceId: 'device-aaaa' };

const post = (redis: unknown, body: unknown, now = JAN15) =>
  r.handleReport(new Request('http://x/api/report', { method: 'POST', body: JSON.stringify(body) }), redis, now);
const list = (redis: unknown, query = '', auth = `Bearer ${TOKEN}`) =>
  r.handleReports(new Request(`http://x/api/reports${query}`, { headers: { authorization: auth } }), redis, TOKEN);

test('a report is kept without the device that sent it, newest first', async () => {
  const redis = r.memoryRedis(() => JAN15);
  assert.equal((await post(redis, GOOD)).status, 200);
  const missing = { ...GOOD, trailId: null, kind: 'missing', note: 'Line one\nline two\u0007', x: null, y: null };
  assert.equal((await post(redis, missing)).status, 200);
  const res = await list(redis);
  assert.equal(res.status, 200);
  const { count, reports } = await res.json();
  assert.equal(count, 2);
  assert.deepEqual(reports[0], { at: '2027-01-15T18:00:00.000Z', resort: 'stowe', panel: 'map', trailId: null, kind: 'missing', note: 'Line one line two', x: null, y: null });
  assert.deepEqual(reports[1], { at: '2027-01-15T18:00:00.000Z', resort: 'stowe', panel: 'map', trailId: 'nose-dive', kind: 'name', note: 'This is Goat', x: 41.23, y: 55.5 });
  assert.ok(!JSON.stringify(reports).includes('device-aaaa'));
});

test('bad reports are refused', async () => {
  const redis = r.memoryRedis(() => JAN15);
  for (const bad of [
    { ...GOOD, resort: 'Stowe!' },
    { ...GOOD, trailId: '../x' },
    { ...GOOD, trailId: null }, // a wrong name needs a trail
    { ...GOOD, kind: 'rude' },
    { ...GOOD, panel: 'Main Map' },
    { ...GOOD, deviceId: 'short' },
  ]) assert.equal((await post(redis, bad)).status, 400, JSON.stringify(bad));
  const long = await post(redis, { ...GOOD, note: 'x'.repeat(2000), x: 140 });
  assert.equal(long.status, 200);
  const [kept] = (await (await list(redis)).json()).reports;
  assert.equal(kept.note.length, r.NOTE_MAX);
  assert.equal(kept.x, null, 'a tap off the map is dropped');
  assert.equal((await r.handleReport(new Request('http://x/api/report', { method: 'POST', body: '{' }), redis)).status, 400);
  assert.equal((await r.handleReport(new Request('http://x/api/report'), redis)).status, 405);
  assert.equal((await post(null, GOOD)).status, 503);
});

test('a device may send a few reports a day', async () => {
  let now = JAN15;
  const redis = r.memoryRedis(() => now);
  for (let i = 0; i < r.DAILY_LIMIT; i++) assert.equal((await post(redis, GOOD, now)).status, 200);
  assert.equal((await post(redis, GOOD, now)).status, 429);
  assert.equal((await post(redis, { ...GOOD, deviceId: 'device-bbbb' }, now)).status, 200, 'another device still can');
  now += DAY;
  assert.equal((await post(redis, GOOD, now)).status, 200, 'and so can this one the next day');
});

test('reading the reports needs the token', async () => {
  const redis = r.memoryRedis(() => JAN15);
  await post(redis, GOOD);
  await post(redis, { ...GOOD, resort: 'vail', panel: 'front-side', trailId: 'riva-ridge', kind: 'line' });
  assert.equal((await list(redis, '', 'Bearer wrong-token-of-some-length')).status, 401);
  assert.equal((await list(redis, '', '')).status, 401);
  const none = (token: string | undefined) => r.handleReports(new Request('http://x/api/reports', { headers: { authorization: `Bearer ${token}` } }), redis, token);
  assert.equal((await none(undefined)).status, 404, 'no token set: no endpoint');
  assert.equal((await none('short')).status, 404, 'too short a token: no endpoint');
  const vail = await (await list(redis, '?resort=vail')).json();
  assert.deepEqual(vail.reports.map((x: { trailId: string }) => x.trailId), ['riva-ridge']);
  assert.equal((await (await list(redis, '?limit=1')).json()).count, 1);
});
