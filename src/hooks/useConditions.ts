import { useCallback, useEffect, useState } from 'react';

export type Vote = 1 | -1;

export interface Counts {
  up: number;
  down: number;
}

/** 'shared': counts come from everyone via /api/conditions.
 * 'local': the server isn't set up or can't be reached; only this device's
 * own votes are shown. */
export type ConditionsMode = 'loading' | 'shared' | 'local';

const DEVICE_KEY = 'myskiruns.device';
const VOTES_KEY = 'myskiruns.votes';
// matches the server's window: conditions change day to day
const WINDOW_MS = 24 * 60 * 60 * 1000;
const REFRESH_MS = 5 * 60 * 1000;

interface MyVote {
  vote: Vote;
  at: number;
}

function deviceId(): string {
  let id = localStorage.getItem(DEVICE_KEY);
  if (!id) {
    id = crypto.randomUUID?.() ?? `d-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
    localStorage.setItem(DEVICE_KEY, id);
  }
  return id;
}

function loadMine(): Record<string, MyVote> {
  try {
    const all = JSON.parse(localStorage.getItem(VOTES_KEY) ?? '{}') as Record<string, MyVote>;
    const now = Date.now();
    return Object.fromEntries(Object.entries(all).filter(([, v]) => now - v.at < WINDOW_MS));
  } catch {
    return {};
  }
}

async function request(init?: RequestInit): Promise<Record<string, Counts>> {
  const res = await fetch('/api/conditions', init);
  if (!res.ok || !res.headers.get('content-type')?.includes('application/json')) throw new Error(String(res.status));
  return ((await res.json()) as { trails: Record<string, Counts> }).trails;
}

/** Thumbs up / down on today's conditions, per trail. */
export function useConditions() {
  const [mine, setMine] = useState<Record<string, MyVote>>(loadMine);
  const [shared, setShared] = useState<Record<string, Counts> | null>(null);
  const [mode, setMode] = useState<ConditionsMode>('loading');

  useEffect(() => {
    localStorage.setItem(VOTES_KEY, JSON.stringify(mine));
  }, [mine]);

  useEffect(() => {
    let alive = true;
    const refresh = () =>
      request()
        .then((trails) => {
          if (!alive) return;
          setShared(trails);
          setMode('shared');
        })
        .catch(() => alive && setMode((m) => (m === 'shared' ? m : 'local')));
    refresh();
    const t = setInterval(refresh, REFRESH_MS);
    window.addEventListener('online', refresh);
    return () => {
      alive = false;
      clearInterval(t);
      window.removeEventListener('online', refresh);
    };
  }, []);

  /** Vote on a trail; voting the same way again takes the vote back. */
  const vote = useCallback(
    (trailId: string, v: Vote) => {
      const prev = mine[trailId]?.vote;
      const next = prev === v ? 0 : v;
      setMine((m) => {
        const copy = { ...m };
        if (next) copy[trailId] = { vote: next, at: Date.now() };
        else delete copy[trailId];
        return copy;
      });
      // optimistic update of the shared counts
      setShared((s) => {
        if (!s) return s;
        const c = { ...(s[trailId] ?? { up: 0, down: 0 }) };
        if (prev === 1) c.up--;
        if (prev === -1) c.down--;
        if (next === 1) c.up++;
        if (next === -1) c.down++;
        return { ...s, [trailId]: c };
      });
      request({
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ trailId, deviceId: deviceId(), vote: next }),
      })
        .then((trails) => {
          setShared(trails);
          setMode('shared');
        })
        .catch(() => setMode((m) => (m === 'shared' ? m : 'local')));
    },
    [mine],
  );

  /** Counts for a trail: everyone's when shared, else just this device's. */
  const countsFor = useCallback(
    (trailId: string): Counts => {
      if (shared) return shared[trailId] ?? { up: 0, down: 0 };
      const v = mine[trailId]?.vote;
      return { up: v === 1 ? 1 : 0, down: v === -1 ? 1 : 0 };
    },
    [shared, mine],
  );

  const myVote = useCallback((trailId: string): Vote | null => mine[trailId]?.vote ?? null, [mine]);

  return { mode, vote, countsFor, myVote };
}

export type Conditions = ReturnType<typeof useConditions>;
