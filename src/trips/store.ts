// The trip log on this device, in localStorage: every resort's trips, read by
// useTrips and kept in step with the account by src/account/account.ts.
import { readTrips, type Trip } from './log';

export interface TripsState {
  version: 1;
  /** every resort's trips, deleted ones included (hidden: see isLive) */
  trips: Trip[];
  /** the trip being logged on this device (not synced) */
  activeTripId: string | null;
}

const STORAGE_KEY = 'myskiruns.trips';
// the pre-trips app stored a flat list of skied trail ids here
const LEGACY_KEY = 'killington-skied-trails';

export const today = () => new Date().toISOString().slice(0, 10);
export const newTripId = () => `trip-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;

export function isTripsState(v: unknown): v is TripsState {
  const s = v as TripsState;
  return !!s && s.version === 1 && Array.isArray(s.trips);
}

function save(s: TripsState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch {
    // storage full or blocked; the in-memory state still works this session
  }
}

function read(text: string | null): TripsState | null {
  if (!text) return null;
  const parsed = JSON.parse(text);
  if (!isTripsState(parsed)) return null;
  return { version: 1, trips: readTrips(parsed.trips), activeTripId: parsed.activeTripId ?? null };
}

function load(): TripsState {
  try {
    const stored = read(localStorage.getItem(STORAGE_KEY));
    if (stored) return stored;
    const legacy = localStorage.getItem(LEGACY_KEY);
    if (legacy) {
      const ids: string[] = JSON.parse(legacy);
      if (Array.isArray(ids) && ids.length) {
        const now = new Date().toISOString();
        const trip: Trip = {
          id: newTripId(),
          name: 'Earlier runs',
          startDate: today(),
          createdAt: now,
          runs: ids.map((trailId) => ({ trailId, at: now })),
        };
        const s: TripsState = { version: 1, trips: [trip], activeTripId: trip.id };
        save(s);
        return s;
      }
    }
  } catch {
    // unreadable storage: start fresh rather than crash
  }
  return { version: 1, trips: [], activeTripId: null };
}

let state = load();
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((l) => l());

export const getTripsState = () => state;

export function setTripsState(update: (s: TripsState) => TripsState) {
  const next = update(state);
  if (next === state) return;
  state = next;
  save(state);
  notify();
}

export function subscribeTrips(listener: () => void) {
  listeners.add(listener);
  return () => void listeners.delete(listener);
}

// another tab changed the log (this tab keeps its own current trip)
window.addEventListener('storage', (e) => {
  if (e.key !== STORAGE_KEY) return;
  try {
    const other = read(e.newValue);
    if (!other) return;
    state = { ...other, activeTripId: state.activeTripId };
    notify();
  } catch {
    // ignore a half-written value
  }
});
