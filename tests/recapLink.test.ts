// Run with `npm test`. A trip recap packed into a link (src/recap/link.ts).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync } from 'node:fs';
import { decodeRecap, encodeRecap, recapUrl, trailHash, NAME_MAX } from '../src/recap/link.ts';

const ids = ['upper-wildcat', 'lower-wildcat', 'skye-terrain-park', 'fireball', 'superstar', 'cascade'];
const recap = {
  name: 'Presidents Day weekend ⛷️ with Zoë',
  start: '2026-02-14',
  days: 3,
  newCount: 2,
  trailIds: ['fireball', 'superstar', 'cascade'],
};

test('a recap comes back from its payload', () => {
  const back = decodeRecap(encodeRecap(recap), ids);
  assert.ok(back);
  assert.equal(back.name, recap.name);
  assert.equal(back.start, recap.start);
  assert.equal(back.days, 3);
  assert.equal(back.newCount, 2);
  assert.deepEqual([...back.trailIds].sort(), [...recap.trailIds].sort());
});

test('the payload is short and safe in a URL as it is', () => {
  const p = encodeRecap(recap);
  assert.match(p, /^[A-Za-z0-9_~-]+$/);
  assert.ok(p.length < 100, p);
  const url = recapUrl('https://www.myskiruns.app', 'killington', recap);
  assert.equal(new URL(url).searchParams.get('recap'), p);
  assert.equal(new URL(url).searchParams.get('resort'), 'killington');
});

test('runs whose trail is gone from the list are left out, and new never exceeds runs', () => {
  const back = decodeRecap(encodeRecap({ ...recap, newCount: 3 }), ['fireball', 'cascade']);
  assert.deepEqual([...back!.trailIds].sort(), ['cascade', 'fireball']);
  assert.equal(back!.newCount, 2);
});

test('long names are cut, by characters not bytes', () => {
  const back = decodeRecap(encodeRecap({ ...recap, name: '🏔'.repeat(100) }), ids);
  assert.equal([...back!.name].length, NAME_MAX);
});

test('anything that is not a payload is refused', () => {
  for (const bad of ['', 'hello', '2~a~20260214~1~0~', '1~a~2026-02-14~1~0~', '1~a~20260214~1~0~abc', '1~%%~20260214~1~0~']) {
    assert.equal(decodeRecap(bad, ids), null, bad);
  }
});

test("no two trails of any resort share a hash", async () => {
  const root = new URL('../src/data/resorts/', import.meta.url);
  const resorts = readdirSync(root);
  assert.ok(resorts.length >= 50);
  for (const r of resorts) {
    const { trails } = (await import(new URL(`${r}/trails.ts`, root).href)) as { trails: { id: string }[] };
    const seen = new Map<string, string>();
    for (const t of trails) {
      const h = trailHash(t.id);
      assert.ok(!seen.has(h) || seen.get(h) === t.id, `${r}: ${t.id} and ${seen.get(h)}`);
      seen.set(h, t.id);
    }
  }
});
