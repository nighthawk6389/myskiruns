// Vercel function: the picture for a link's preview (1200 x 630 JPEG): the
// resort's map cropped to a shared day's runs and drawn with them, or the map
// itself for a link to a resort. See api/_lib/preview.ts.
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import sharp, { type OverlayOptions } from 'sharp';
import { cropFor, loadPreview, OG_H, OG_W, panelFor, recapOf, runPoints, runsSvg } from './_lib/preview.js';

const fail = (status: number) => new Response(null, { status });

export async function GET(req: Request) {
  const url = new URL(req.url);
  const resort = await loadPreview(url.origin, url.searchParams.get('resort'));
  if (!resort) return fail(404);
  const recap = recapOf(resort, url.searchParams.get('recap'));
  const runs = recap?.trailIds ?? [];
  const panel = panelFor(resort, runs);

  const map = await fetch(new URL(panel.map, url.origin));
  if (!map.ok) return fail(502);
  const source = Buffer.from(await map.arrayBuffer());
  const { width: iw = 0, height: ih = 0 } = await sharp(source).metadata();
  if (!iw || !ih) return fail(502);
  const crop = cropFor(runPoints(panel.paths, runs, iw, ih), iw, ih);
  const badge = await fetch(new URL('/og/badge.png', url.origin));

  const layers: OverlayOptions[] = [{ input: Buffer.from(runsSvg(panel.paths, resort.trails, runs, iw, ih, crop)) }];
  if (badge.ok) layers.push({ input: Buffer.from(await badge.arrayBuffer()), left: 28, top: OG_H - 28 - 72 });
  const jpeg = await sharp(source)
    .extract({ left: crop.x, top: crop.y, width: crop.w, height: crop.h })
    .resize(OG_W, OG_H, { fit: 'fill' })
    .composite(layers)
    .jpeg({ quality: 82, mozjpeg: true })
    .toBuffer();
  return new Response(new Uint8Array(jpeg), {
    headers: {
      'content-type': 'image/jpeg',
      // the same link always makes the same picture (until a deploy changes the map)
      'cache-control': 'public, max-age=86400, s-maxage=604800',
    },
  });
}
