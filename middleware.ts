// Vercel Routing Middleware (runs before the static files are served, only for /):
// a link-preview bot (iMessage, WhatsApp, Slack...) fetching a link that names a
// resort gets api/preview.ts, the app's page with that link's own title,
// description and picture (api/_lib/preview.ts). Everyone else, and every
// other path, goes on to the static app as before.
import { next, rewrite } from '@vercel/functions/middleware';

export const config = { matcher: '/', runtime: 'nodejs' };

const PREVIEW_BOT =
  /bot\b|bot\/|facebookexternalhit|facebot|whatsapp|slack|discord|telegram|skype|linkedin|pinterest|embedly|iframely|vkshare|google-inspectiontool|applebot/i;

export default function middleware(req: Request) {
  const url = new URL(req.url);
  if (!url.searchParams.has('resort') || !PREVIEW_BOT.test(req.headers.get('user-agent') ?? '')) return next();
  return rewrite(new URL(`/api/preview${url.search}`, url));
}
