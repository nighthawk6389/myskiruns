// Vercel function: the app's page with a link's own title, description and
// picture, for link-preview bots only (middleware.ts sends them here for links
// with ?resort=; everyone else gets the static page). See api/_lib/preview.ts.
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import { loadPreview, metaFor, recapOf, withMeta } from './_lib/preview.js';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const origin = url.origin;
  const page = await fetch(new URL('/index.html', origin));
  if (!page.ok) return new Response('Not found', { status: 404 });
  let html = await page.text();
  const resort = await loadPreview(origin, url.searchParams.get('resort'));
  if (resort) {
    const payload = url.searchParams.get('recap');
    html = withMeta(html, metaFor(origin, resort, recapOf(resort, payload), payload));
  }
  return new Response(html, {
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'public, max-age=0, s-maxage=86400',
    },
  });
}
