import { useCallback, useEffect, useMemo, useState } from 'react';

export interface Run {
  trailId: string;
  /** ISO timestamp of when the run was logged */
  at: string;
}

export interface Trip {
  id: string;
  name: string;
  /** YYYY-MM-DD */
  startDate: string;
  createdAt: string;
  runs: Run[];
}

interface TripsState {
  version: 1;
  trips: Trip[];
  activeTripId: string | null;
}

const STORAGE_KEY = 'myskiruns.trips';
// the pre-trips app stored a flat list of skied trail ids here
const LEGACY_KEY = 'killington-skied-trails';

const today = () => new Date().toISOString().slice(0, 10);
const newId = () => `trip-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;

export function defaultTripName(date: string): string {
  const d = new Date(`${date}T12:00:00`);
  return `Killington · ${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
}

function isTripsState(v: unknown): v is TripsState {
  const s = v as TripsState;
  return !!s && s.version === 1 && Array.isArray(s.trips);
}

function load(): TripsState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (isTripsState(parsed)) return parsed;
    }
    const legacy = localStorage.getItem(LEGACY_KEY);
    if (legacy) {
      const ids: string[] = JSON.parse(legacy);
      if (Array.isArray(ids) && ids.length) {
        const now = new Date().toISOString();
        const trip: Trip = {
          id: newId(),
          name: 'Earlier runs',
          startDate: today(),
          createdAt: now,
          runs: ids.map((trailId) => ({ trailId, at: now })),
        };
        return { version: 1, trips: [trip], activeTripId: trip.id };
      }
    }
  } catch {
    // unreadable storage: start fresh rather than crash
  }
  return { version: 1, trips: [], activeTripId: null };
}

export function useTrips() {
  const [state, setState] = useState<TripsState>(load);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // storage full or blocked; the in-memory state still works this session
    }
  }, [state]);

  const activeTrip = state.trips.find((t) => t.id === state.activeTripId) ?? null;

  const skiedThisTrip = useMemo(
    () => new Set(activeTrip?.runs.map((r) => r.trailId) ?? []),
    [activeTrip],
  );

  const skiedEver = useMemo(
    () => new Set(state.trips.flatMap((t) => t.runs.map((r) => r.trailId))),
    [state.trips],
  );

  const createTrip = useCallback((name: string, startDate: string) => {
    const trip: Trip = {
      id: newId(),
      name: name.trim() || defaultTripName(startDate),
      startDate,
      createdAt: new Date().toISOString(),
      runs: [],
    };
    setState((s) => ({ ...s, trips: [...s.trips, trip], activeTripId: trip.id }));
  }, []);

  const selectTrip = useCallback((id: string) => {
    setState((s) => ({ ...s, activeTripId: id }));
  }, []);

  const updateTrip = useCallback((id: string, patch: Partial<Pick<Trip, 'name' | 'startDate'>>) => {
    setState((s) => ({ ...s, trips: s.trips.map((t) => (t.id === id ? { ...t, ...patch } : t)) }));
  }, []);

  const deleteTrip = useCallback((id: string) => {
    setState((s) => {
      const trips = s.trips.filter((t) => t.id !== id);
      const activeTripId = s.activeTripId === id ? (trips.at(-1)?.id ?? null) : s.activeTripId;
      return { ...s, trips, activeTripId };
    });
  }, []);

  /** Mark a trail skied on the active trip, or unmark it if it already is.
   * With no trip yet, starts one for today. */
  const toggleRun = useCallback((trailId: string) => {
    setState((s) => {
      let trips = s.trips;
      let activeTripId = s.activeTripId;
      if (!trips.some((t) => t.id === activeTripId)) {
        const date = today();
        const trip: Trip = { id: newId(), name: defaultTripName(date), startDate: date, createdAt: new Date().toISOString(), runs: [] };
        trips = [...trips, trip];
        activeTripId = trip.id;
      }
      trips = trips.map((t) => {
        if (t.id !== activeTripId) return t;
        const skied = t.runs.some((r) => r.trailId === trailId);
        return {
          ...t,
          runs: skied
            ? t.runs.filter((r) => r.trailId !== trailId)
            : [...t.runs, { trailId, at: new Date().toISOString() }],
        };
      });
      return { ...s, trips, activeTripId };
    });
  }, []);

  const exportJson = useCallback(
    () => JSON.stringify({ app: 'myskiruns', exportedAt: new Date().toISOString(), ...state }, null, 2),
    [state],
  );

  /** Merge trips from an exported file; trips already on this device (same id) are kept.
   * Returns the number of trips added, or throws if the file isn't an export. */
  const importJson = useCallback((text: string): number => {
    const parsed = JSON.parse(text);
    if (!isTripsState(parsed)) throw new Error('This file is not a My Ski Runs export.');
    const have = new Set(state.trips.map((t) => t.id));
    const incoming = parsed.trips.filter((t) => !have.has(t.id));
    setState((s) => ({
      ...s,
      trips: [...s.trips, ...incoming.filter((t) => !s.trips.some((x) => x.id === t.id))],
      activeTripId: s.activeTripId ?? incoming[0]?.id ?? null,
    }));
    return incoming.length;
  }, [state.trips]);

  return {
    trips: state.trips,
    activeTrip,
    skiedThisTrip,
    skiedEver,
    createTrip,
    selectTrip,
    updateTrip,
    deleteTrip,
    toggleRun,
    exportJson,
    importJson,
  };
}
