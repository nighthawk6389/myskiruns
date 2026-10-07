// A stand-in for a Supabase project, enough for the app's accounts: GoTrue's
// email code sign-in, sessions and admin delete, and PostgREST on trip_logs
// with its row-level security (a user sees only their own row). Codes are
// readable at GET /__debug/code?email=..., state at GET /__debug.
const http = require('node:http');
const crypto = require('node:crypto');
const port = Number(process.argv[2] || 54321);
const ANON = 'anon-key';
const SERVICE = 'service-key';

const users = new Map(); // email -> { id, email }
const codes = new Map(); // email -> code
const sessions = new Map(); // access token -> user id
const refreshes = new Map(); // refresh token -> user id
const rows = new Map(); // user id -> { user_id, trips, version, updated_at }
const log = [];

const b64 = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
function session(user) {
  const now = Math.floor(Date.now() / 1000);
  const access = `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64({ sub: user.id, email: user.email, role: 'authenticated', aud: 'authenticated', iat: now, exp: now + 3600, session_id: crypto.randomUUID() })}.sig`;
  const refresh = crypto.randomBytes(12).toString('hex');
  sessions.set(access, user.id);
  refreshes.set(refresh, user.id);
  return { access_token: access, token_type: 'bearer', expires_in: 3600, expires_at: now + 3600, refresh_token: refresh, user: userJson(user) };
}
const userJson = (u) => ({ id: u.id, aud: 'authenticated', role: 'authenticated', email: u.email, email_confirmed_at: new Date().toISOString(), app_metadata: { provider: 'email' }, user_metadata: {}, identities: [], created_at: new Date().toISOString() });
const userById = (id) => [...users.values()].find((u) => u.id === id);
const bearer = (req) => /^Bearer (\S+)$/.exec(req.headers.authorization ?? '')?.[1];

function send(res, status, body, headers = {}) {
  res.writeHead(status, { 'content-type': 'application/json', ...headers });
  res.end(body === undefined ? '' : JSON.stringify(body));
}
const err = (res, status, code, msg) => send(res, status, { code, error_code: code, msg, message: msg });

http.createServer((req, res) => {
  res.setHeader('access-control-allow-origin', '*');
  res.setHeader('access-control-allow-methods', 'GET,POST,PATCH,DELETE,OPTIONS');
  res.setHeader('access-control-allow-headers', req.headers['access-control-request-headers'] ?? '*');
  res.setHeader('access-control-expose-headers', '*');
  if (req.method === 'OPTIONS') return send(res, 204);
  const u = new URL(req.url, 'http://x');
  const chunks = [];
  req.on('data', (c) => chunks.push(c));
  req.on('end', () => {
    const text = Buffer.concat(chunks).toString();
    const body = text ? JSON.parse(text) : {};
    log.push(`${req.method} ${u.pathname}${u.search}`);
    const p = u.pathname;

    if (p === '/__debug') return send(res, 200, { users: [...users.values()], rows: [...rows.values()], log });
    if (p === '/__debug/code') return send(res, 200, { code: codes.get(u.searchParams.get('email')) ?? null });
    if (req.headers.apikey !== ANON && req.headers.apikey !== SERVICE) return err(res, 401, 'no_api_key', 'Invalid API key');

    // ---- auth
    if (p === '/auth/v1/otp' && req.method === 'POST') {
      const email = String(body.email).toLowerCase();
      if (!users.has(email)) {
        if (!body.create_user) return err(res, 422, 'otp_disabled', 'Signups not allowed for otp');
        users.set(email, { id: crypto.randomUUID(), email });
      }
      codes.set(email, String(crypto.randomInt(0, 1e6)).padStart(6, '0'));
      return send(res, 200, {});
    }
    if (p === '/auth/v1/verify' && req.method === 'POST') {
      const email = String(body.email).toLowerCase();
      if (body.type !== 'email' || !codes.has(email) || codes.get(email) !== body.token) return err(res, 403, 'otp_expired', 'Token has expired or is invalid');
      codes.delete(email);
      return send(res, 200, session(users.get(email)));
    }
    if (p === '/auth/v1/token' && u.searchParams.get('grant_type') === 'refresh_token') {
      const id = refreshes.get(body.refresh_token);
      const user = id && userById(id);
      if (!user) return err(res, 400, 'refresh_token_not_found', 'Invalid Refresh Token');
      refreshes.delete(body.refresh_token);
      return send(res, 200, session(user));
    }
    if (p === '/auth/v1/user' && req.method === 'GET') {
      const user = userById(sessions.get(bearer(req)));
      return user ? send(res, 200, userJson(user)) : err(res, 401, 'bad_jwt', 'invalid JWT');
    }
    if (p === '/auth/v1/logout') {
      sessions.delete(bearer(req));
      return send(res, 204);
    }
    const adminDelete = /^\/auth\/v1\/admin\/users\/([^/]+)$/.exec(p);
    if (adminDelete && req.method === 'DELETE') {
      if (req.headers.apikey !== SERVICE || bearer(req) !== SERVICE) return err(res, 403, 'not_admin', 'User not allowed');
      const user = userById(adminDelete[1]);
      if (!user) return err(res, 404, 'user_not_found', 'User not found');
      users.delete(user.email);
      rows.delete(user.id); // on delete cascade
      for (const [t, id] of sessions) if (id === user.id) sessions.delete(t);
      return send(res, 200, userJson(user));
    }

    // ---- PostgREST, trip_logs, row-level security by the caller's token
    if (p === '/rest/v1/trip_logs') {
      const me = sessions.get(bearer(req));
      const filters = [...u.searchParams].filter(([k]) => k !== 'select' && k !== 'columns');
      const match = (row) => row.user_id === me && filters.every(([k, v]) => v.startsWith('eq.') && String(row[k]) === v.slice(3));
      const pick = (row) => {
        const cols = (u.searchParams.get('select') ?? '*').split(',');
        return cols[0] === '*' ? row : Object.fromEntries(cols.map((c) => [c, row[c]]));
      };
      if (req.method === 'GET') return send(res, 200, [...rows.values()].filter(match).map(pick));
      if (req.method === 'POST') {
        const row = Array.isArray(body) ? body[0] : body;
        if (!me || row.user_id !== me) return send(res, 403, { code: '42501', message: 'new row violates row-level security policy for table "trip_logs"' });
        if (rows.has(row.user_id)) return send(res, 409, { code: '23505', message: 'duplicate key value violates unique constraint "trip_logs_pkey"' });
        rows.set(row.user_id, { trips: [], version: 1, updated_at: new Date().toISOString(), ...row });
        return /return=representation/.test(req.headers.prefer ?? '') ? send(res, 201, [pick(rows.get(row.user_id))]) : send(res, 201);
      }
      if (req.method === 'PATCH') {
        const hit = [...rows.values()].filter(match);
        for (const row of hit) Object.assign(row, body);
        return /return=representation/.test(req.headers.prefer ?? '') ? send(res, 200, hit.map(pick)) : send(res, 204);
      }
    }
    return err(res, 404, 'not_found', `${req.method} ${p} not handled`);
  });
}).listen(port, () => console.log(`mock supabase on ${port}`));
