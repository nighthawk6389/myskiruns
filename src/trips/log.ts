// The trip log and how two copies of it merge. Pure functions (no DOM): the
// account sync (src/account/account.ts) merges this device's trips with the
// ones saved in the account, and tests/tripLog.test.ts checks the rules.
//
// Merging never loses a change made on either side:
// - a trip's name, date and resort come from the copy edited last;
// - a run (a trail marked skied on a trip) is kept if it was marked after it
//   was last unmarked anywhere, so runs logged offline on a phone and runs
//   logged on a laptop all survive;
// - a deleted trip stays deleted unless something happened on it after it was
//   deleted (a run logged on a device that hadn't heard yet); then it comes
//   back with only what happened since.
// So that a sync can carry removals, an unmarked run leaves its time in
// `unmarked` and a deleted trip stays in the log, hidden, with `deletedAt`.
// The result is the same whatever order devices merge in.
// Timestamps are ISO strings from toISOString(), which sort as text.

export interface Run {
  trailId: string;
  /** ISO timestamp of when the run was logged */
  at: string;
}

export interface Trip {
  id: string;
  /** resort id (src/resorts.ts); trips from before resorts are Killington */
  resortId?: string;
  name: string;
  /** YYYY-MM-DD */
  startDate: string;
  createdAt: string;
  /** when its name, date or resort last changed (createdAt if never) */
  updatedAt?: string;
  runs: Run[];
  /** trail id -> when its run was unmarked */
  unmarked?: Record<string, string>;
  /** when the trip was deleted; it stays in the log, hidden, without runs */
  deletedAt?: string;
}

const edited = (t: Trip) => t.updatedAt ?? t.createdAt;

/** Not deleted, or brought back by something done after it was deleted. */
export const isLive = (t: Trip) => !t.deletedAt || edited(t) > t.deletedAt || t.runs.length > 0;

const later = (a: string | undefined, b: string | undefined) => (a === undefined ? b : b === undefined || a >= b ? a : b);
const fields = (t: Trip) => JSON.stringify([t.name, t.startDate, t.resortId ?? null]);
const byText = (x: string, y: string) => (x < y ? -1 : x > y ? 1 : 0);

function mergeTrip(versions: Trip[]): Trip {
  // the copy edited last (a tie, which needs the same millisecond on two
  // devices, goes to the larger text so every device picks the same one)
  const base = versions.reduce((x, y) => {
    if (edited(y) !== edited(x)) return edited(y) > edited(x) ? y : x;
    return fields(y) > fields(x) ? y : x;
  });
  const deletedAt = versions.reduce<string | undefined>((m, v) => later(m, v.deletedAt), undefined);
  const unmarked: Record<string, string> = {};
  for (const v of versions) for (const [k, when] of Object.entries(v.unmarked ?? {})) unmarked[k] = later(unmarked[k], when)!;
  const marked = new Map<string, string>();
  for (const r of versions.flatMap((v) => v.runs)) marked.set(r.trailId, later(marked.get(r.trailId), r.at)!);

  const runs: Run[] = [];
  for (const [trailId, at] of marked) {
    // unmarked since, or logged before the trip was deleted
    if ((unmarked[trailId] ?? '') >= at || (deletedAt ?? '') >= at) continue;
    runs.push({ trailId, at });
  }
  for (const [trailId, when] of Object.entries(unmarked)) {
    // moot: marked again since, or older than the deletion (which covers it)
    const run = runs.find((r) => r.trailId === trailId);
    if ((run && run.at > when) || (deletedAt ?? '') >= when) delete unmarked[trailId];
  }
  runs.sort((x, y) => byText(x.at, y.at) || byText(x.trailId, y.trailId));

  const trip: Trip = {
    id: base.id,
    ...(base.resortId !== undefined ? { resortId: base.resortId } : {}),
    name: base.name,
    startDate: base.startDate,
    createdAt: base.createdAt,
    ...(base.updatedAt !== undefined ? { updatedAt: base.updatedAt } : {}),
    runs,
  };
  if (Object.keys(unmarked).length) trip.unmarked = unmarked;
  if (deletedAt) trip.deletedAt = deletedAt;
  return trip;
}

export function mergeTrips(a: Trip[], b: Trip[]): Trip[] {
  const copies = new Map<string, Trip[]>();
  for (const t of [...a, ...b]) copies.set(t.id, [...(copies.get(t.id) ?? []), t]);
  return [...copies.values()].map(mergeTrip).sort((x, y) => byText(x.createdAt, y.createdAt) || byText(x.id, y.id));
}

/** A stable text form: two lists of trips with the same content give the same text. */
export function canonical(trips: Trip[]): string {
  const sorted = (o: Record<string, string> | undefined) => Object.entries(o ?? {}).sort(([x], [y]) => byText(x, y));
  return JSON.stringify(
    [...trips]
      .sort((x, y) => byText(x.id, y.id))
      .map((t) => [
        t.id,
        t.resortId ?? null,
        t.name,
        t.startDate,
        t.createdAt,
        t.updatedAt ?? null,
        [...t.runs].sort((x, y) => byText(x.trailId, y.trailId)).map((r) => [r.trailId, r.at]),
        sorted(t.unmarked),
        t.deletedAt ?? null,
      ]),
  );
}

export const sameTrips = (a: Trip[], b: Trip[]) => canonical(a) === canonical(b);

const isString = (v: unknown): v is string => typeof v === 'string';

/** Trips read from storage or the network, with anything malformed left out. */
export function readTrips(v: unknown): Trip[] {
  const trips: Trip[] = [];
  for (const t of Array.isArray(v) ? (v as Partial<Trip>[]) : []) {
    if (!t || !isString(t.id) || !isString(t.name) || !isString(t.startDate) || !isString(t.createdAt)) continue;
    const runs = (Array.isArray(t.runs) ? t.runs : []).filter((r): r is Run => !!r && isString(r.trailId) && isString(r.at));
    const unmarked = t.unmarked && typeof t.unmarked === 'object' ? Object.entries(t.unmarked).filter(([, w]) => isString(w)) : [];
    trips.push({
      id: t.id,
      ...(isString(t.resortId) ? { resortId: t.resortId } : {}),
      name: t.name,
      startDate: t.startDate,
      createdAt: t.createdAt,
      ...(isString(t.updatedAt) ? { updatedAt: t.updatedAt } : {}),
      runs: runs.map((r) => ({ trailId: r.trailId, at: r.at })),
      ...(unmarked.length ? { unmarked: Object.fromEntries(unmarked) } : {}),
      ...(isString(t.deletedAt) ? { deletedAt: t.deletedAt } : {}),
    });
  }
  return trips;
}

// Changes made on this device. Each records what a merge needs: when a trip
// was edited, when a run was unmarked, when a trip was deleted.

/** Add trips that aren't in the log yet (a trip with the same id, even a
 * deleted one, is kept as it is). */
export function addTrips(trips: Trip[], added: Trip[]): Trip[] {
  const have = new Set(trips.map((t) => t.id));
  const fresh = added.filter((t) => !have.has(t.id));
  return fresh.length ? [...trips, ...fresh] : trips;
}

export function editTrip(trips: Trip[], id: string, patch: Partial<Pick<Trip, 'name' | 'startDate'>>, now: string): Trip[] {
  return trips.map((t) => (t.id === id ? { ...t, ...patch, updatedAt: now } : t));
}

function withUnmarked(t: Trip, unmarked: Record<string, string>): Trip {
  const copy = { ...t };
  if (Object.keys(unmarked).length) copy.unmarked = unmarked;
  else delete copy.unmarked;
  return copy;
}

export function deleteTrip(trips: Trip[], id: string, now: string): Trip[] {
  // its runs and unmarkings are all older than the deletion, which covers them
  return trips.map((t) => (t.id === id ? { ...withUnmarked(t, {}), runs: [], deletedAt: now } : t));
}

/** Mark a trail skied on a trip, or unmark it if it already is. */
export function toggleRun(trips: Trip[], tripId: string, trailId: string, now: string): Trip[] {
  return trips.map((t) => {
    if (t.id !== tripId) return t;
    const unmarked = { ...t.unmarked };
    if (t.runs.some((r) => r.trailId === trailId)) {
      unmarked[trailId] = now;
      return { ...withUnmarked(t, unmarked), runs: t.runs.filter((r) => r.trailId !== trailId) };
    }
    delete unmarked[trailId];
    return { ...withUnmarked(t, unmarked), runs: [...t.runs, { trailId, at: now }] };
  });
}
