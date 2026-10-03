// Optional accounts: sign in with a code emailed to you to back up this
// device's trips and sync them with your other devices. Same setup as
// Deconstructed Papers: Supabase Auth's email code (no password), sent through
// Resend as Supabase's mail server. Without a Supabase project configured
// (README, "Accounts") the app has no account features and keeps trips on
// the device only.
//
// Trips sync as one record per account (table trip_logs,
// supabase/migrations/001_trip_logs.sql), merged on the device
// (src/trips/log.ts, src/trips/sync.ts). A sync runs on sign-in, a few seconds
// after a change, when the app comes back online or to the foreground, and
// every few minutes while it's open.
import { useSyncExternalStore } from 'react';
import type { SupabaseClient } from '@supabase/supabase-js';
import { canonical, mergeTrips, readTrips, sameTrips } from '../trips/log';
import { syncTrips, type SavedTrips } from '../trips/sync';
import { getTripsState, setTripsState, subscribeTrips } from '../trips/store';

const env = import.meta.env;
// VITE_ names, or the NEXT_PUBLIC_ ones Vercel's Supabase integration sets
const SUPABASE_URL: string | undefined = env.VITE_SUPABASE_URL || env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY: string | undefined =
  env.VITE_SUPABASE_ANON_KEY ||
  env.VITE_SUPABASE_PUBLISHABLE_KEY ||
  env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

export const accountsEnabled = Boolean(SUPABASE_URL && SUPABASE_KEY);

export interface Account {
  /** 'off': accounts aren't set up for this app */
  status: 'off' | 'loading' | 'signed-out' | 'signed-in';
  email: string | null;
  sync: 'idle' | 'syncing' | 'offline' | 'error';
  /** when this device last synced (ISO) */
  lastSyncedAt: string | null;
  error: string | null;
}

const LAST_SYNC_KEY = 'myskiruns.lastSync';
const SYNC_EVERY_MS = 5 * 60 * 1000;
const TABLE = 'trip_logs';

function storedLastSync(): string | null {
  try {
    return localStorage.getItem(LAST_SYNC_KEY);
  } catch {
    return null;
  }
}

function storeLastSync(at: string | null) {
  try {
    if (at) localStorage.setItem(LAST_SYNC_KEY, at);
    else localStorage.removeItem(LAST_SYNC_KEY);
  } catch {
    // storage blocked: the time shows until the page closes
  }
}

let account: Account = {
  status: accountsEnabled ? 'loading' : 'off',
  email: null,
  sync: 'idle',
  lastSyncedAt: storedLastSync(),
  error: null,
};
const listeners = new Set<() => void>();
const set = (patch: Partial<Account>) => {
  account = { ...account, ...patch };
  listeners.forEach((l) => l());
};

export function useAccount(): Account {
  return useSyncExternalStore(
    (l) => {
      listeners.add(l);
      return () => void listeners.delete(l);
    },
    () => account,
  );
}

// supabase-js loads only when accounts are set up, after the app has rendered.
// Sign-in is by code; a sign-in link (an email template still carrying one)
// also works, in the browser it opens in.
let client: Promise<SupabaseClient> | null = null;
const getClient = () =>
  (client ??= import('@supabase/supabase-js').then(({ createClient }) => createClient(SUPABASE_URL!, SUPABASE_KEY!)));

/** The account's saved copy of the trips: one row, guarded by its version. */
function savedTrips(c: SupabaseClient, userId: string): SavedTrips {
  return {
    async read() {
      const { data, error } = await c.from(TABLE).select('trips, version').eq('user_id', userId).maybeSingle();
      if (error) throw error;
      return data ? { trips: readTrips(data.trips), version: Number(data.version) } : null;
    },
    async create(trips) {
      const { error } = await c.from(TABLE).insert({ user_id: userId, trips, version: 1 });
      // another device created it first
      if (error?.code === '23505') return false;
      if (error) throw error;
      return true;
    },
    async update(trips, version) {
      const { data, error } = await c
        .from(TABLE)
        .update({ trips, version: version + 1, updated_at: new Date().toISOString() })
        .eq('user_id', userId)
        .eq('version', version)
        .select('version');
      if (error) throw error;
      return data.length > 0;
    },
  };
}

const messageOf = (e: unknown) =>
  e && typeof e === 'object' && 'message' in e && typeof e.message === 'string' ? e.message : String(e);

let userId: string | null = null;
// the trips as both sides held them after the last sync (canonical text)
let lastSynced = '';
let running = false;
let again = false;
let timer = 0;

function scheduleSync(delay = 2000) {
  if (!userId) return;
  clearTimeout(timer);
  timer = window.setTimeout(() => void syncNow(), delay);
}

/** Sync now (also the "Sync now" button). */
export async function syncNow() {
  const uid = userId;
  if (!uid) return;
  if (running) {
    again = true;
    return;
  }
  if (!navigator.onLine) {
    set({ sync: 'offline', error: null });
    return;
  }
  running = true;
  set({ sync: 'syncing', error: null });
  try {
    const merged = await syncTrips(getTripsState().trips, savedTrips(await getClient(), uid));
    if (uid !== userId) return;
    lastSynced = canonical(merged);
    // changes made on this device during the sync are kept (and sync next)
    setTripsState((s) => {
      const trips = mergeTrips(s.trips, merged);
      return sameTrips(trips, s.trips) ? s : { ...s, trips };
    });
    const at = new Date().toISOString();
    storeLastSync(at);
    set({ sync: 'idle', lastSyncedAt: at });
  } catch (e) {
    if (navigator.onLine) set({ sync: 'error', error: messageOf(e) });
    else set({ sync: 'offline', error: null });
  } finally {
    running = false;
    if (again) {
      again = false;
      scheduleSync(0);
    }
  }
}

/** Reads the saved session and keeps syncing while signed in. Call once. */
export function startAccounts() {
  if (!accountsEnabled) return;
  getClient()
    .then((c) => {
      c.auth.onAuthStateChange((_event, session) => {
        const id = session?.user.id ?? null;
        const switched = id !== userId;
        userId = id;
        if (!id) {
          lastSynced = '';
          set({ status: 'signed-out', email: null, sync: 'idle', error: null });
          return;
        }
        set({ status: 'signed-in', email: session?.user.email ?? null });
        // supabase-js asks not to call it from inside this callback
        if (switched) setTimeout(() => void syncNow(), 0);
      });
    })
    .catch(() => set({ status: 'signed-out', error: 'Sign-in could not load. Check your connection.' }));

  subscribeTrips(() => {
    if (userId && canonical(getTripsState().trips) !== lastSynced) scheduleSync();
  });
  window.addEventListener('online', () => scheduleSync(0));
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') scheduleSync(0);
  });
  window.setInterval(() => {
    if (document.visibilityState === 'visible') scheduleSync(0);
  }, SYNC_EVERY_MS);
}

function authMessage(e: { message: string; status?: number; code?: string }): string {
  if (e.status === 429 || e.code === 'over_email_send_rate_limit' || /rate limit/i.test(e.message)) {
    return 'Too many tries. Wait a minute, then try again.';
  }
  if (e.code === 'otp_expired' || /expired|invalid/i.test(e.message)) return 'That code is wrong or has expired. Ask for a new one.';
  if (!navigator.onLine || /fetch/i.test(e.message)) return 'No connection. Try again when you’re online.';
  return e.message;
}

/** Email a sign-in code (creates the account on first use). */
export async function sendCode(email: string) {
  const c = await getClient();
  const { error } = await c.auth.signInWithOtp({ email, options: { shouldCreateUser: true } });
  if (error) throw new Error(authMessage(error));
}

export async function verifyCode(email: string, code: string) {
  const c = await getClient();
  const { error } = await c.auth.verifyOtp({ email, token: code, type: 'email' });
  if (error) throw new Error(authMessage(error));
}

/** Sign out on this device. Its trips stay on it. */
export async function signOut() {
  const c = await getClient();
  await c.auth.signOut({ scope: 'local' });
  storeLastSync(null);
  set({ lastSyncedAt: null });
}

/** Delete the account and the trips saved in it (api/account.ts). Trips on
 * this device stay. */
export async function deleteAccount() {
  const c = await getClient();
  const token = (await c.auth.getSession()).data.session?.access_token;
  if (!token) throw new Error('Sign in again first.');
  const res = await fetch('/api/account', { method: 'DELETE', headers: { authorization: `Bearer ${token}` } });
  const body = (await res.json().catch(() => ({}))) as { error?: string };
  if (!res.ok) throw new Error(body.error ?? 'Could not delete the account.');
  await signOut();
}
