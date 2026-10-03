// Run with `npm test`. The merge rules for syncing trips between devices
// (src/trips/log.ts): what each change does once merged, and that merging
// gives the same result whatever the order and however often it runs.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  addTrips,
  canonical,
  deleteTrip,
  editTrip,
  isLive,
  mergeTrips,
  readTrips,
  toggleRun,
  type Trip,
} from '../src/trips/log.ts';
import { syncTrips } from '../src/trips/sync.ts';

const at = (minute: number) => new Date(Date.UTC(2026, 0, 10, 9, minute)).toISOString();
const trip = (id: string, minute = 0): Trip => ({
  id,
  resortId: 'stowe',
  name: id,
  startDate: '2026-01-10',
  createdAt: at(minute),
  updatedAt: at(minute),
  runs: [],
});
const live = (trips: Trip[]) => trips.filter(isLive);
const runsOf = (trips: Trip[], id: string) => live(trips).find((t) => t.id === id)?.runs.map((r) => r.trailId).sort();

test('runs logged on two devices are all kept', () => {
  const both = addTrips([], [trip('t')]);
  const phone = toggleRun(toggleRun(both, 't', 'nosedive', at(1)), 't', 'starr', at(2));
  const laptop = toggleRun(both, 't', 'chin-clip', at(3));
  assert.deepEqual(runsOf(mergeTrips(phone, laptop), 't'), ['chin-clip', 'nosedive', 'starr']);
});

test('a run unmarked after it was logged stays unmarked; marked again later, it is back', () => {
  const base = toggleRun([trip('t')], 't', 'starr', at(1));
  const unmarked = toggleRun(base, 't', 'starr', at(2));
  assert.deepEqual(runsOf(mergeTrips(base, unmarked), 't'), []);
  const again = toggleRun(unmarked, 't', 'starr', at(3));
  const merged = mergeTrips(mergeTrips(base, unmarked), again);
  assert.deepEqual(runsOf(merged, 't'), ['starr']);
  assert.equal(merged[0].unmarked, undefined, 'the moot unmarking is dropped');
});

test('the name edited last wins', () => {
  const base = [trip('t')];
  const a = editTrip(base, 't', { name: 'Presidents Day' }, at(5));
  const b = editTrip(base, 't', { name: 'Ski week' }, at(6));
  assert.equal(mergeTrips(a, b)[0].name, 'Ski week');
  assert.equal(mergeTrips(b, a)[0].name, 'Ski week');
});

test('a deleted trip stays deleted when merged with an older copy', () => {
  const base = toggleRun([trip('t')], 't', 'starr', at(1));
  const deleted = deleteTrip(base, 't', at(2));
  assert.equal(live(mergeTrips(base, deleted)).length, 0);
  assert.equal(live(mergeTrips(deleted, base)).length, 0);
});

test('a run logged after the trip was deleted brings it back with only the newer runs', () => {
  const base = toggleRun([trip('t')], 't', 'starr', at(1));
  const deleted = deleteTrip(base, 't', at(2));
  const offlinePhone = toggleRun(base, 't', 'nosedive', at(3));
  assert.deepEqual(runsOf(mergeTrips(deleted, offlinePhone), 't'), ['nosedive']);
});

test('readTrips keeps well-formed trips and drops the rest', () => {
  const trips = readTrips([
    { ...trip('ok'), unmarked: { a: at(1), b: 3 }, deletedAt: 5 },
    { id: 'no-name', startDate: '2026-01-10', createdAt: at(0), runs: [] },
    null,
    7,
  ]);
  assert.deepEqual(trips.map((t) => t.id), ['ok']);
  assert.deepEqual(trips[0].unmarked, { a: at(1) });
  assert.equal(trips[0].deletedAt, undefined);
  assert.deepEqual(readTrips('nope'), []);
});

// Devices making random changes and syncing in random pairs. Whatever the
// order, merging must agree (commutative, associative, idempotent), and once
// every device has synced with every other, all of them hold the same trips.
test('random changes on three devices converge, whatever the merge order', () => {
  let seed = 42;
  const rand = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const pick = <T>(xs: T[]) => xs[Math.floor(rand() * xs.length)];
  const trails = ['a', 'b', 'c', 'd'];

  for (let round = 0; round < 500; round++) {
    const devices: Trip[][] = [[], [], []];
    // every change, for the expected result: the last word on each thing wins
    const events: { kind: 'name' | 'mark' | 'unmark' | 'delete'; trip: string; value: string; at: string }[] = [];
    let clock = 0;
    for (let step = 0; step < 40; step++) {
      const i = Math.floor(rand() * 3);
      const d = devices[i];
      const shown = live(d);
      const now = at(++clock);
      const op = rand();
      if (op < 0.15 || !shown.length) {
        const id = `t${clock}`;
        devices[i] = addTrips(d, [{ ...trip(id, clock), createdAt: now, updatedAt: now }]);
        events.push({ kind: 'name', trip: id, value: id, at: now });
      } else if (op < 0.55) {
        const t = pick(shown);
        const trail = pick(trails);
        events.push({ kind: t.runs.some((r) => r.trailId === trail) ? 'unmark' : 'mark', trip: t.id, value: trail, at: now });
        devices[i] = toggleRun(d, t.id, trail, now);
      } else if (op < 0.65) {
        const t = pick(shown);
        devices[i] = editTrip(d, t.id, { name: `n${clock}` }, now);
        events.push({ kind: 'name', trip: t.id, value: `n${clock}`, at: now });
      } else if (op < 0.72) {
        const t = pick(shown);
        devices[i] = deleteTrip(d, t.id, now);
        events.push({ kind: 'delete', trip: t.id, value: '', at: now });
      } else {
        const j = (i + 1 + Math.floor(rand() * 2)) % 3;
        devices[i] = devices[j] = mergeTrips(devices[i], devices[j]);
      }
    }
    const [a, b, c] = devices;
    const same = (x: Trip[], y: Trip[], what: string) => assert.equal(canonical(x), canonical(y), `${what} (round ${round})`);
    same(mergeTrips(a, b), mergeTrips(b, a), 'commutative');
    same(mergeTrips(mergeTrips(a, b), c), mergeTrips(a, mergeTrips(b, c)), 'associative');
    const ab = mergeTrips(a, b);
    same(mergeTrips(ab, ab), ab, 'idempotent');
    same(mergeTrips(ab, a), ab, 'absorbs what it already has');
    const all = mergeTrips(mergeTrips(c, a), b);
    for (const d of devices) same(mergeTrips(d, all), all, 'converged');

    // and the result is what the changes, taken in time order, add up to
    const expected = new Map<string, { name: string; deleted: string; marks: Map<string, string>; unmarks: Map<string, string> }>();
    for (const e of events) {
      const t = expected.get(e.trip) ?? { name: '', deleted: '', marks: new Map(), unmarks: new Map() };
      expected.set(e.trip, t);
      if (e.kind === 'name') t.name = e.value;
      else if (e.kind === 'delete') t.deleted = e.at;
      else (e.kind === 'mark' ? t.marks : t.unmarks).set(e.value, e.at);
    }
    const lastNamed = new Map(events.filter((e) => e.kind === 'name').map((e) => [e.trip, e.at]));
    const want = [...expected]
      .map(([id, t]) => {
        const runs = [...t.marks].filter(([trail, when]) => when > (t.unmarks.get(trail) ?? '') && when > t.deleted).map(([trail]) => trail).sort();
        const liveNow = !t.deleted || lastNamed.get(id)! > t.deleted || runs.length > 0;
        return liveNow ? `${id}:${t.name}:${runs.join(',')}` : null;
      })
      .filter(Boolean)
      .sort();
    const got = live(all).map((t) => `${t.id}:${t.name}:${t.runs.map((r) => r.trailId).sort().join(',')}`).sort();
    assert.deepEqual(got, want, `expected result (round ${round})`);
  }
});

// The account's copy, in memory, with a hook to let "another device" save
// between this device's read and its save.
function memoryCopy() {
  let row: { trips: Trip[]; version: number } | null = null;
  let beforeSave: (() => void) | null = null;
  const saved = {
    read: async () => (row ? { trips: row.trips, version: row.version } : null),
    create: async (trips: Trip[]) => {
      beforeSave?.();
      if (row) return false;
      row = { trips, version: 1 };
      return true;
    },
    update: async (trips: Trip[], version: number) => {
      beforeSave?.();
      if (!row || row.version !== version) return false;
      row = { trips, version: version + 1 };
      return true;
    },
  };
  return {
    saved,
    row: () => row,
    otherDeviceSaves: (trips: Trip[]) => {
      beforeSave = () => {
        beforeSave = null;
        row = row ? { trips: mergeTrips(row.trips, trips), version: row.version + 1 } : { trips, version: 1 };
      };
    },
  };
}

test('a sync merges with the saved copy and saves the result', async () => {
  const account = memoryCopy();
  const phone = toggleRun([trip('t')], 't', 'starr', at(1));
  await syncTrips(phone, account.saved);
  const laptop = toggleRun(addTrips([], account.row()!.trips), 't', 'nosedive', at(2));
  const merged = await syncTrips(laptop, account.saved);
  assert.deepEqual(runsOf(merged, 't'), ['nosedive', 'starr']);
  assert.equal(canonical(account.row()!.trips), canonical(merged));
  const again = await syncTrips(merged, account.saved);
  assert.equal(account.row()!.version, 2, 'nothing new: nothing saved');
  assert.equal(canonical(again), canonical(merged));
});

test('another device saving between read and save is merged, not overwritten', async () => {
  const account = memoryCopy();
  await syncTrips([trip('t')], account.saved);
  account.otherDeviceSaves(toggleRun([trip('t')], 't', 'from-laptop', at(3)));
  const merged = await syncTrips(toggleRun([trip('t')], 't', 'from-phone', at(4)), account.saved);
  assert.deepEqual(runsOf(merged, 't'), ['from-laptop', 'from-phone']);
  assert.deepEqual(runsOf(account.row()!.trips, 't'), ['from-laptop', 'from-phone']);
});
