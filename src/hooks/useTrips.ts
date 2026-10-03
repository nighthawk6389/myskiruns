import { useCallback, useMemo, useSyncExternalStore } from 'react';
import { addTrips, deleteTrip as deleteFromLog, editTrip, isLive, readTrips, toggleRun as toggleInLog, type Trip } from '../trips/log';
import { getTripsState, isTripsState, newTripId, setTripsState, subscribeTrips, today } from '../trips/store';

export type { Run, Trip } from '../trips/log';

export const LEGACY_RESORT = 'killington';
export const tripResort = (t: Trip) => t.resortId ?? LEGACY_RESORT;

export function defaultTripName(date: string, resortName = 'Killington'): string {
  const d = new Date(`${date}T12:00:00`);
  return `${resortName} · ${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
}

const latest = (trips: Trip[]) =>
  trips.reduce<Trip | null>((best, t) => (!best || t.startDate >= best.startDate ? t : best), null);

/** Trips at one resort. Every resort's trips share one stored list
 * (src/trips/store.ts); the active trip is the selected one if it is at this
 * resort, else this resort's latest. */
export function useTrips(resortId: string = LEGACY_RESORT, resortName = 'Killington') {
  const state = useSyncExternalStore(subscribeTrips, getTripsState);
  // deleted trips stay in the stored log so a sync can carry the deletion
  const liveTrips = useMemo(() => state.trips.filter(isLive), [state.trips]);

  const resortTrips = useMemo(() => liveTrips.filter((t) => tripResort(t) === resortId), [liveTrips, resortId]);
  const activeTrip = resortTrips.find((t) => t.id === state.activeTripId) ?? latest(resortTrips);

  const skiedThisTrip = useMemo(
    () => new Set(activeTrip?.runs.map((r) => r.trailId) ?? []),
    [activeTrip],
  );

  const skiedEver = useMemo(
    () => new Set(resortTrips.flatMap((t) => t.runs.map((r) => r.trailId))),
    [resortTrips],
  );

  const newTrip = useCallback(
    (name: string, startDate: string): Trip => {
      const now = new Date().toISOString();
      return {
        id: newTripId(),
        resortId,
        name: name.trim() || defaultTripName(startDate, resortName),
        startDate,
        createdAt: now,
        updatedAt: now,
        runs: [],
      };
    },
    [resortId, resortName],
  );

  const createTrip = useCallback((name: string, startDate: string) => {
    const trip = newTrip(name, startDate);
    setTripsState((s) => ({ ...s, trips: addTrips(s.trips, [trip]), activeTripId: trip.id }));
  }, [newTrip]);

  const selectTrip = useCallback((id: string) => {
    setTripsState((s) => ({ ...s, activeTripId: id }));
  }, []);

  const updateTrip = useCallback((id: string, patch: Partial<Pick<Trip, 'name' | 'startDate'>>) => {
    setTripsState((s) => ({ ...s, trips: editTrip(s.trips, id, patch, new Date().toISOString()) }));
  }, []);

  const deleteTrip = useCallback((id: string) => {
    // with the active trip gone, this resort's latest trip becomes active
    setTripsState((s) => ({
      ...s,
      trips: deleteFromLog(s.trips, id, new Date().toISOString()),
      activeTripId: s.activeTripId === id ? null : s.activeTripId,
    }));
  }, []);

  /** Mark a trail skied on the active trip, or unmark it if it already is.
   * With no trip yet, starts one for today. */
  const toggleRun = useCallback((trailId: string) => {
    setTripsState((s) => {
      let trips = s.trips;
      const here = trips.filter((t) => isLive(t) && tripResort(t) === resortId);
      let activeTripId = (here.find((t) => t.id === s.activeTripId) ?? latest(here))?.id ?? null;
      if (!activeTripId) {
        const trip = newTrip('', today());
        trips = addTrips(trips, [trip]);
        activeTripId = trip.id;
      }
      return { ...s, trips: toggleInLog(trips, activeTripId, trailId, new Date().toISOString()), activeTripId };
    });
  }, [resortId, newTrip]);

  const exportJson = useCallback(
    () => JSON.stringify({ app: 'myskiruns', exportedAt: new Date().toISOString(), ...state }, null, 2),
    [state],
  );

  /** Merge trips from an exported file; trips already on this device (same id) are kept.
   * A trip deleted here comes back as a copy. Returns the number of trips
   * added, or throws if the file isn't an export. */
  const importJson = useCallback((text: string): number => {
    const parsed = JSON.parse(text);
    if (!isTripsState(parsed)) throw new Error('This file is not a My Ski Runs export.');
    const here = new Map(getTripsState().trips.map((t) => [t.id, t]));
    const incoming = readTrips(parsed.trips)
      .filter((t) => isLive(t) && !(here.has(t.id) && isLive(here.get(t.id)!)))
      .map((t) => (here.has(t.id) ? { ...t, id: newTripId() } : t));
    setTripsState((s) => ({
      ...s,
      trips: addTrips(s.trips, incoming),
      activeTripId: s.activeTripId ?? incoming[0]?.id ?? null,
    }));
    return incoming.length;
  }, []);

  return {
    /** this resort's trips */
    trips: resortTrips,
    /** every resort's trips (the trip summary needs them to tell "new") */
    allTrips: liveTrips,
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
