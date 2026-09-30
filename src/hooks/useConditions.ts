import { useCallback, useEffect, useState } from 'react';
import { MAX_TAGS } from '../conditionTags';

export type Vote = 1 | -1;

export interface Counts {
  up: number;
  down: number;
  /** condition tag -> how many reports carry it */
  tags: Record<string, number>;
}

const EMPTY: Counts = { up: 0, down: 0, tags: {} };

/** 'shared': counts come from everyone via /api/conditions.
 * 'local': the server isn't set up or can't be reached; only this device's
 * own votes are shown. */
export type ConditionsMode = 'loading' | 'shared' | 'local';

const DEVICE_KEY = 'myskiruns.device';
// Killington keeps the key it had before other resorts were added
const votesKey = (resort: string) => (resort === 'killington' ? 'myskiruns.votes' : `myskiruns.votes.${resort}`);
// matches the server's window: conditions change day to day
const WINDOW_MS = 24 * 60 * 60 * 1000;
const REFRESH_MS = 5 * 60 * 1000;

/** This device's report on a trail: a vote (0 = none) plus condition tags. */
interface MyVote {
  vote: Vote | 0;
  tags?: string[];
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

function loadMine(resort: string): Record<string, MyVote> {
  try {
    const all = JSON.parse(localStorage.getItem(votesKey(resort)) ?? '{}') as Record<string, MyVote>;
    const now = Date.now();
    return Object.fromEntries(Object.entries(all).filter(([, v]) => now - v.at < WINDOW_MS));
  } catch {
    return {};
  }
}

async function request(resort: string, init?: RequestInit): Promise<Record<string, Counts>> {
  const res = await fetch(`/api/conditions?resort=${encodeURIComponent(resort)}`, init);
  if (!res.ok || !res.headers.get('content-type')?.includes('application/json')) throw new Error(String(res.status));
  return ((await res.json()) as { trails: Record<string, Counts> }).trails;
}

/** Thumbs up / down and condition tags on today's conditions, per trail at
 * one resort. Remount (key) to switch resorts. */
export function useConditions(resort = 'killington') {
  const [mine, setMine] = useState<Record<string, MyVote>>(() => loadMine(resort));
  const [shared, setShared] = useState<Record<string, Counts> | null>(null);
  const [mode, setMode] = useState<ConditionsMode>('loading');

  useEffect(() => {
    localStorage.setItem(votesKey(resort), JSON.stringify(mine));
  }, [mine, resort]);

  useEffect(() => {
    let alive = true;
    const refresh = () =>
      request(resort)
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
  }, [resort]);

  /** Replace this device's report on a trail, updating counts optimistically
   * and sending it to the server. */
  const report = useCallback(
    (trailId: string, next: { vote: Vote | 0; tags: string[] }) => {
      const prev = mine[trailId] ?? { vote: 0 as const, tags: [] };
      setMine((m) => {
        const copy = { ...m };
        if (next.vote || next.tags.length) copy[trailId] = { ...next, at: Date.now() };
        else delete copy[trailId];
        return copy;
      });
      setShared((s) => {
        if (!s) return s;
        const old = s[trailId] ?? EMPTY;
        const c: Counts = { up: old.up, down: old.down, tags: { ...old.tags } };
        if (prev.vote === 1) c.up--;
        if (prev.vote === -1) c.down--;
        if (next.vote === 1) c.up++;
        if (next.vote === -1) c.down++;
        for (const t of prev.tags ?? []) c.tags[t] = Math.max(0, (c.tags[t] ?? 0) - 1);
        for (const t of next.tags) c.tags[t] = (c.tags[t] ?? 0) + 1;
        return { ...s, [trailId]: c };
      });
      request(resort, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ trailId, deviceId: deviceId(), ...next }),
      })
        .then((trails) => {
          setShared(trails);
          setMode('shared');
        })
        .catch(() => setMode((m) => (m === 'shared' ? m : 'local')));
    },
    [mine, resort],
  );

  /** Vote on a trail; voting the same way again takes the vote back. */
  const vote = useCallback(
    (trailId: string, v: Vote) => {
      const cur = mine[trailId];
      report(trailId, { vote: cur?.vote === v ? 0 : v, tags: cur?.tags ?? [] });
    },
    [mine, report],
  );

  /** Add or remove a condition tag on this device's report (max MAX_TAGS). */
  const toggleTag = useCallback(
    (trailId: string, tag: string) => {
      const cur = mine[trailId];
      const tags = cur?.tags ?? [];
      const next = tags.includes(tag) ? tags.filter((t) => t !== tag) : [...tags, tag].slice(-MAX_TAGS);
      report(trailId, { vote: cur?.vote ?? 0, tags: next });
    },
    [mine, report],
  );

  /** Counts for a trail: everyone's when shared, else just this device's. */
  const countsFor = useCallback(
    (trailId: string): Counts => {
      if (shared) return shared[trailId] ?? EMPTY;
      const r = mine[trailId];
      if (!r) return EMPTY;
      return {
        up: r.vote === 1 ? 1 : 0,
        down: r.vote === -1 ? 1 : 0,
        tags: Object.fromEntries((r.tags ?? []).map((t) => [t, 1])),
      };
    },
    [shared, mine],
  );

  const myVote = useCallback((trailId: string): Vote | null => mine[trailId]?.vote || null, [mine]);
  const myTags = useCallback((trailId: string): string[] => mine[trailId]?.tags ?? [], [mine]);

  return { mode, vote, toggleTag, countsFor, myVote, myTags };
}

export type Conditions = ReturnType<typeof useConditions>;
