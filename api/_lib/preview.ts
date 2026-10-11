// Link previews: what iMessage, WhatsApp, Slack and the like show for a link
// to the app. They don't run the app's script, so for a link naming a resort
// (?resort=<id>) or a shared day (&recap=...) the page they get has its own
// title, description and picture (vercel.json sends link-preview bots to
// api/preview.ts; everyone else gets the app as before). The picture
// (api/og.ts) is the resort's map, cropped to the day's runs and drawn with
// them, from the preview data the build writes (dist/preview/<id>.json,
// vite.config.ts).
// Relative imports need their .js extension (Vercel runs api/ as Node ESM).
import { decodeRecap, type Recap } from '../../src/recap/link.js';

export const OG_W = 1200;
export const OG_H = 630;
const SITE_NAME = 'My Ski Runs';

export interface Overlay {
  segments: number[][][];
  label?: number[];
}

export interface PreviewResort {
  id: string;
  name: string;
  region: string;
  /** trail id -> rating */
  trails: Record<string, string>;
  panels: { id: string; name: string; map: string; paths: Record<string, Overlay> }[];
}

/** A resort's preview data from this deployment's static files, or null. */
export async function loadPreview(origin: string, id: string | null): Promise<PreviewResort | null> {
  if (!validResortId(id)) return null;
  try {
    const res = await fetch(new URL(`/preview/${id}.json`, origin));
    if (!res.ok || !(res.headers.get('content-type') ?? '').includes('json')) return null;
    const data = (await res.json()) as PreviewResort;
    return data.id === id && Array.isArray(data.panels) && data.panels.length ? data : null;
  } catch {
    return null;
  }
}

export const validResortId = (id: string | null): id is string => !!id && /^[a-z0-9-]{1,60}$/.test(id);

/** The shared day in a link, if it is one (payloads past a sane length aren't). */
export function recapOf(resort: PreviewResort, payload: string | null): Recap | null {
  if (!payload || payload.length > 6000) return null;
  return decodeRecap(payload, Object.keys(resort.trails));
}

const longDate = (date: string) =>
  new Date(`${date}T12:00:00Z`).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  });

export interface Meta {
  title: string;
  description: string;
  image: string;
  url: string;
}

/** The page's title, description, picture and address for a link. */
export function metaFor(origin: string, resort: PreviewResort, recap: Recap | null, payload: string | null): Meta {
  const url = new URL('/', origin);
  url.searchParams.set('resort', resort.id);
  const image = new URL('/api/og', origin);
  image.searchParams.set('resort', resort.id);
  if (recap && payload) {
    url.searchParams.set('recap', payload);
    image.searchParams.set('recap', payload);
    const n = recap.trailIds.length;
    const parts = [
      `${n} run${n === 1 ? '' : 's'}`,
      recap.newCount ? `${recap.newCount} new` : '',
      recap.days > 1 ? `${recap.days} days` : '',
      longDate(recap.start),
    ].filter(Boolean);
    return {
      title: `${recap.name || 'A ski day'} at ${resort.name}`,
      description: `${parts.join(' · ')}. See the runs on ${resort.name}'s trail map.`,
      image: image.toString(),
      url: url.toString(),
    };
  }
  const total = Object.keys(resort.trails).length;
  return {
    title: `${resort.name} Trail Map · ${SITE_NAME}`,
    description: `Tap the runs you ski on ${resort.name}'s trail map (${total} trails), trip by trip, and see what's left. Free, no app to download, works offline.`,
    image: image.toString(),
    url: url.toString(),
  };
}

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

/** The app's page with a link's own title, description and Open Graph / Twitter tags. */
export function withMeta(html: string, m: Meta): string {
  const tags = [
    `<meta property="og:type" content="website" />`,
    `<meta property="og:site_name" content="${SITE_NAME}" />`,
    `<meta property="og:title" content="${esc(m.title)}" />`,
    `<meta property="og:description" content="${esc(m.description)}" />`,
    `<meta property="og:url" content="${esc(m.url)}" />`,
    `<meta property="og:image" content="${esc(m.image)}" />`,
    `<meta property="og:image:width" content="${OG_W}" />`,
    `<meta property="og:image:height" content="${OG_H}" />`,
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${esc(m.title)}" />`,
    `<meta name="twitter:description" content="${esc(m.description)}" />`,
    `<meta name="twitter:image" content="${esc(m.image)}" />`,
  ].join('\n    ');
  return html
    .replace(/\s*<!-- link preview -->[\s\S]*?<!-- \/link preview -->/, '')
    .replace(/<title>[^<]*<\/title>/, `<title>${esc(m.title)}</title>`)
    .replace(/<meta name="description" content="[^"]*" \/>/, `<meta name="description" content="${esc(m.description)}" />`)
    .replace('</head>', `    ${tags}\n  </head>`);
}

/** The panel showing most of the day's runs (else the resort's first). */
export function panelFor(resort: PreviewResort, trailIds: string[]) {
  let best = resort.panels[0];
  let most = -1;
  for (const p of resort.panels) {
    const n = trailIds.filter((id) => p.paths[id]).length;
    if (n > most) [best, most] = [p, n];
  }
  return best;
}

export interface Crop {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** The part of a map (iw x ih px) to show at the picture's shape: the runs with
 * a margin, at least a third of the map wide, or the whole map's middle. */
export function cropFor(points: number[][], iw: number, ih: number): Crop {
  const aspect = OG_W / OG_H;
  let x0 = 0;
  let x1 = iw;
  let y0 = 0;
  let y1 = ih;
  let w = iw;
  let h = ih;
  if (points.length) {
    const xs = points.map((q) => q[0]);
    const ys = points.map((q) => q[1]);
    [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    const pad = Math.max(x1 - x0, y1 - y0) * 0.12 + iw * 0.02;
    w = Math.max(x1 - x0 + 2 * pad, iw / 3);
    h = y1 - y0 + 2 * pad;
  }
  if (w / h > aspect) h = w / aspect;
  else w = h * aspect;
  const s = Math.min(1, iw / w, ih / h);
  w *= s;
  h *= s;
  const at = (c: number, size: number, max: number) => Math.min(max - size, Math.max(0, c - size / 2));
  return { x: Math.round(at((x0 + x1) / 2, w, iw)), y: Math.round(at((y0 + y1) / 2, h, ih)), w: Math.round(w), h: Math.round(h) };
}

const COLOURS: Record<string, string> = { green: '#22c55e', blue: '#3b82f6', black: '#111827', 'double-black': '#111827' };

/** The runs as an SVG the size of the picture, for the crop of an iw x ih map. */
export function runsSvg(paths: Record<string, Overlay>, ratings: Record<string, string>, trailIds: string[], iw: number, ih: number, crop: Crop): string {
  const k = OG_W / crop.w;
  const pt = (q: number[]) => `${(((q[0] * iw) / 100 - crop.x) * k).toFixed(1)},${(((q[1] * ih) / 100 - crop.y) * k).toFixed(1)}`;
  const casing: string[] = [];
  const colour: string[] = [];
  for (const id of trailIds) {
    const p = paths[id];
    if (!p) continue;
    const c = COLOURS[ratings[id]] ?? COLOURS.blue;
    for (const seg of p.segments) {
      if (seg.length < 2) continue;
      const pts = seg.map(pt).join(' ');
      casing.push(`<polyline points="${pts}" stroke="#fff" stroke-width="14"/>`);
      colour.push(`<polyline points="${pts}" stroke="${c}" stroke-width="8"/>`);
    }
    if (p.label && !p.segments.length) {
      const [x, y] = pt(p.label).split(',');
      casing.push(`<circle cx="${x}" cy="${y}" r="15" fill="#fff"/>`);
      colour.push(`<circle cx="${x}" cy="${y}" r="10" fill="${c}"/>`);
    }
  }
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${OG_W}" height="${OG_H}">` +
    `<rect width="${OG_W}" height="${OG_H}" fill="#0f172a" fill-opacity="${trailIds.length ? 0.25 : 0}"/>` +
    `<g fill="none" stroke-linecap="round" stroke-linejoin="round">${casing.join('')}${colour.join('')}</g></svg>`
  );
}

/** Every point of the day's runs on a panel, in map px. */
export function runPoints(paths: Record<string, Overlay>, trailIds: string[], iw: number, ih: number): number[][] {
  return trailIds
    .map((id) => paths[id])
    .filter(Boolean)
    .flatMap((p) => (p.label && !p.segments.length ? [p.label] : p.segments.flat()))
    .map((q) => [(q[0] * iw) / 100, (q[1] * ih) / 100]);
}
