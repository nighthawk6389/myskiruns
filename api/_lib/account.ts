// Deleting an account, used by the Vercel function in api/account.ts and by
// the Vite dev server (vite.config.ts). Supabase deletes a user only with the
// project's service key, which must stay on the server; the user's own
// sign-in token says which account. Their saved trips go with them (trip_logs
// rows reference the user with on delete cascade).
import { createClient } from '@supabase/supabase-js';

export interface AccountEnv {
  url?: string;
  /** the public (anon / publishable) key the app uses */
  anonKey?: string;
  /** the service_role / secret key: server only */
  serviceKey?: string;
}

/** The Supabase settings from the environment: the app's own VITE_ names, or
 * the names Vercel's Supabase integration sets. */
export const accountEnv = (e: Record<string, string | undefined>): AccountEnv => ({
  url: e.SUPABASE_URL || e.VITE_SUPABASE_URL || e.NEXT_PUBLIC_SUPABASE_URL,
  anonKey:
    e.SUPABASE_ANON_KEY ||
    e.VITE_SUPABASE_ANON_KEY ||
    e.VITE_SUPABASE_PUBLISHABLE_KEY ||
    e.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    e.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  serviceKey: e.SUPABASE_SERVICE_ROLE_KEY || e.SUPABASE_SECRET_KEY,
});

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  });

/** DELETE with "Authorization: Bearer <the user's access token>". */
export async function handleAccount(req: Request, env: AccountEnv, fetchImpl: typeof fetch = fetch): Promise<Response> {
  if (req.method !== 'DELETE') return json({ error: 'Method not allowed.' }, 405);
  const { url, anonKey, serviceKey } = env;
  if (!url || !anonKey || !serviceKey) return json({ error: 'Accounts are not set up on this server.' }, 503);
  const token = /^Bearer (\S+)$/.exec(req.headers.get('authorization') ?? '')?.[1];
  if (!token) return json({ error: 'Sign in first.' }, 401);

  const options = { auth: { persistSession: false, autoRefreshToken: false }, global: { fetch: fetchImpl } };
  const { data, error } = await createClient(url, anonKey, options).auth.getUser(token);
  if (error || !data.user) return json({ error: 'Your sign-in has expired. Sign in again.' }, 401);
  const removed = await createClient(url, serviceKey, options).auth.admin.deleteUser(data.user.id);
  if (removed.error) return json({ error: 'Could not delete the account. Try again later.' }, 502);
  return json({ deleted: true });
}
