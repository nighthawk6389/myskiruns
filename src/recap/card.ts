// The recap card: a picture of the day to share (a story, 1080 x 1920, or a
// square post, 1080 x 1080), drawn on a canvas on the device: the resort's map
// cropped to the runs skied, those runs drawn in their colours, and the
// trip's numbers. It needs no server; the map is the one the app already shows
// (same origin, cached for offline use), so the canvas can be exported.
import type { Difficulty, Trail } from '../types';
import { DIFFICULTY_COLORS, DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS } from '../types';
import type { MapPanel, Resort } from '../resorts';

export type CardSize = 'story' | 'square';

export const CARD_SIZES: Record<CardSize, { w: number; h: number; label: string }> = {
  story: { w: 1080, h: 1920, label: 'Story' },
  square: { w: 1080, h: 1080, label: 'Square' },
};

export interface CardInput {
  resort: Resort;
  trailIds: string[];
  title: string;
  /** "Sat, Feb 14" or "Feb 14 – 16" */
  dates: string;
  newCount: number;
  days: number;
  /** shown in the footer: the app's address */
  site: string;
}

const ORDER: Difficulty[] = ['green', 'blue', 'black', 'double-black'];
const ICON: Record<Difficulty, string> = { green: '●', blue: '■', black: '◆', 'double-black': '◆◆' };
const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
const BG = '#0f172a';
const PANEL = '#1e293b';
const TEXT = '#f1f5f9';
const MUTED = '#94a3b8';
const GOLD = '#fbbf24';

/** The panel showing most of the runs (a resort drawn on several). */
export function bestPanel(resort: Resort, trailIds: string[]): MapPanel {
  let best = resort.maps[0];
  let most = -1;
  for (const p of resort.maps) {
    const n = trailIds.filter((id) => p.paths[id]).length;
    if (n > most) [best, most] = [p, n];
  }
  return best;
}

const imageCache = new Map<string, Promise<HTMLImageElement>>();

function loadImage(src: string): Promise<HTMLImageElement> {
  let p = imageCache.get(src);
  if (!p) {
    p = new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => {
        imageCache.delete(src);
        reject(new Error(`Couldn't load ${src}`));
      };
      img.src = src;
    });
    imageCache.set(src, p);
  }
  return p;
}

interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** The part of the map to show: the runs' extent with a margin, at least a
 * third of the map wide, centred on the runs, at the frame's aspect where the
 * map is big enough for it (else as much of the map as there is that way:
 * the frame then takes the crop's shape). */
function cropOf(points: number[][], iw: number, ih: number, aspect: number): Rect {
  if (!points.length) return { x: 0, y: 0, w: iw, h: ih };
  const xs = points.map((q) => q[0]);
  const ys = points.map((q) => q[1]);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const pad = Math.max(x1 - x0, y1 - y0) * 0.12 + iw * 0.02;
  let w = Math.max(x1 - x0 + 2 * pad, iw / 3);
  let h = Math.max(y1 - y0 + 2 * pad, iw / 3 / aspect);
  if (w / h > aspect) h = w / aspect;
  else w = h * aspect;
  w = Math.min(w, iw);
  h = Math.min(h, ih);
  const at = (c: number, size: number, max: number) => Math.min(max - size, Math.max(0, c - size / 2));
  return { x: at((x0 + x1) / 2, w, iw), y: at((y0 + y1) / 2, h, ih), w, h };
}

function roundRect(ctx: CanvasRenderingContext2D, r: Rect, radius: number) {
  ctx.beginPath();
  ctx.roundRect(r.x, r.y, r.w, r.h, radius);
}

/** Text cut with an ellipsis to fit a width. */
function fitText(ctx: CanvasRenderingContext2D, text: string, maxW: number): string {
  if (ctx.measureText(text).width <= maxW) return text;
  const chars = [...text];
  while (chars.length && ctx.measureText(chars.join('') + '…').width > maxW) chars.pop();
  return chars.join('').trimEnd() + '…';
}

/** The largest font size (down to min) at which the text fits a width. */
function sizeToFit(ctx: CanvasRenderingContext2D, text: string, weight: number, max: number, min: number, maxW: number) {
  let size = max;
  for (; size > min; size -= 2) {
    ctx.font = `${weight} ${size}px ${FONT}`;
    if (ctx.measureText(text).width <= maxW) break;
  }
  ctx.font = `${weight} ${size}px ${FONT}`;
  return size;
}

/** The map cropped to the runs, in a frame as large as fits the box (its
 * top edge, centred across); returns the frame. */
function drawMap(ctx: CanvasRenderingContext2D, img: HTMLImageElement, panel: MapPanel, trails: Trail[], box: Rect): Rect {
  const iw = img.naturalWidth;
  const ih = img.naturalHeight;
  const toPx = (q: number[]) => [(q[0] * iw) / 100, (q[1] * ih) / 100];
  const overlays = trails.map((t) => ({ t, p: panel.paths[t.id] })).filter((o) => o.p);
  const points = overlays.flatMap(({ p }) => (p.label ? [p.label] : p.segments.flat()).map(toPx));
  const crop = cropOf(points, iw, ih, box.w / box.h);
  const k = Math.min(box.w / crop.w, box.h / crop.h);
  const frame = { x: box.x + (box.w - crop.w * k) / 2, y: box.y, w: crop.w * k, h: crop.h * k };

  ctx.save();
  roundRect(ctx, frame, 28);
  ctx.fillStyle = PANEL;
  ctx.fill();
  ctx.clip();
  ctx.translate(frame.x - crop.x * k, frame.y - crop.y * k);
  ctx.scale(k, k);
  ctx.drawImage(img, 0, 0);
  // a veil over the map so the day's runs stand out
  ctx.fillStyle = 'rgba(15, 23, 42, 0.28)';
  ctx.fillRect(0, 0, iw, ih);

  const lw = 9 / k;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  // casing first for every run, then the colours, so crossings read cleanly
  for (const pass of ['casing', 'colour'] as const) {
    for (const { t, p } of overlays) {
      const colour = DIFFICULTY_COLORS[t.difficulty];
      for (const seg of p.segments) {
        if (seg.length < 2) continue;
        ctx.beginPath();
        seg.forEach((q, i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, ...(toPx(q) as [number, number])));
        ctx.strokeStyle = pass === 'casing' ? '#ffffff' : colour;
        ctx.lineWidth = pass === 'casing' ? lw + 7 / k : lw;
        ctx.stroke();
      }
      if (p.label && !p.segments.length) {
        const [x, y] = toPx(p.label);
        ctx.beginPath();
        ctx.arc(x, y, pass === 'casing' ? 17 / k : 12 / k, 0, Math.PI * 2);
        ctx.fillStyle = pass === 'casing' ? '#ffffff' : colour;
        ctx.fill();
      }
    }
  }
  ctx.restore();

  // a thin rim
  ctx.save();
  roundRect(ctx, frame, 28);
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.restore();
  return frame;
}

/** The runs' names in two columns, hardest first, as many as fit, then "+ N more". */
function drawRunList(ctx: CanvasRenderingContext2D, trails: Trail[], r: Rect, fontSize: number) {
  const sorted = [...trails].sort(
    (a, b) => ORDER.indexOf(b.difficulty) - ORDER.indexOf(a.difficulty) || a.name.localeCompare(b.name),
  );
  const rowH = Math.round(fontSize * 1.5);
  const rows = Math.floor(r.h / rowH);
  const cap = rows * 2;
  if (rows < 1 || !sorted.length) return;
  const shown = sorted.length > cap ? sorted.slice(0, cap - 1) : sorted;
  const perCol = Math.ceil((shown.length + (sorted.length > cap ? 1 : 0)) / 2);
  const colW = r.w / 2;
  ctx.textBaseline = 'middle';
  const iconW = fontSize * 1.5;
  shown.forEach((t, i) => {
    const x = r.x + Math.floor(i / perCol) * colW;
    const y = r.y + (i % perCol) * rowH + rowH / 2;
    ctx.fillStyle = DIFFICULTY_UI_COLORS[t.difficulty];
    ctx.font = `700 ${fontSize * 0.8}px ${FONT}`;
    ctx.fillText(ICON[t.difficulty], x, y);
    ctx.fillStyle = TEXT;
    ctx.font = `600 ${fontSize}px ${FONT}`;
    ctx.fillText(fitText(ctx, t.name, colW - iconW - 16), x + iconW, y);
  });
  if (sorted.length > cap) {
    const i = shown.length;
    ctx.fillStyle = MUTED;
    ctx.font = `600 ${fontSize}px ${FONT}`;
    ctx.fillText(`+ ${sorted.length - shown.length} more`, r.x + Math.floor(i / perCol) * colW + iconW, r.y + (i % perCol) * rowH + rowH / 2);
  }
  ctx.textBaseline = 'alphabetic';
}

function drawMix(ctx: CanvasRenderingContext2D, trails: Trail[], r: Rect, fontSize: number) {
  const counts = Object.fromEntries(ORDER.map((d) => [d, trails.filter((t) => t.difficulty === d).length])) as Record<
    Difficulty,
    number
  >;
  const total = trails.length || 1;
  const barH = Math.round(fontSize * 0.75);
  ctx.save();
  roundRect(ctx, { x: r.x, y: r.y, w: r.w, h: barH }, barH / 2);
  ctx.clip();
  let x = r.x;
  for (const d of ORDER) {
    if (!counts[d]) continue;
    const w = (counts[d] / total) * r.w;
    ctx.fillStyle = DIFFICULTY_UI_COLORS[d];
    ctx.fillRect(x, r.y, w + 1, barH);
    x += w;
  }
  ctx.restore();

  // legend: only the levels skied, spread across the width
  const shown = ORDER.filter((d) => counts[d]);
  const colW = r.w / Math.max(shown.length, 1);
  ctx.textBaseline = 'alphabetic';
  shown.forEach((d, i) => {
    const lx = r.x + i * colW;
    const ly = r.y + barH + fontSize * 1.6;
    ctx.fillStyle = DIFFICULTY_UI_COLORS[d];
    const s = fontSize * 0.42;
    const cy = ly - fontSize * 0.33;
    ctx.beginPath();
    if (d === 'green') ctx.arc(lx + s, cy, s, 0, Math.PI * 2);
    else if (d === 'blue') ctx.rect(lx, cy - s, 2 * s, 2 * s);
    else {
      const n = d === 'double-black' ? 2 : 1;
      for (let j = 0; j < n; j++) {
        const dx = lx + s + j * 1.6 * s;
        ctx.moveTo(dx, cy - s * 1.2);
        ctx.lineTo(dx + s * 1.2, cy);
        ctx.lineTo(dx, cy + s * 1.2);
        ctx.lineTo(dx - s * 1.2, cy);
        ctx.closePath();
      }
    }
    ctx.fill();
    const iconW = d === 'double-black' ? 4.4 * s : 2.6 * s;
    ctx.fillStyle = TEXT;
    ctx.font = `700 ${fontSize}px ${FONT}`;
    const n = String(counts[d]);
    ctx.fillText(n, lx + iconW, ly);
    ctx.fillStyle = MUTED;
    ctx.font = `500 ${fontSize * 0.8}px ${FONT}`;
    ctx.fillText(
      fitText(ctx, DIFFICULTY_LABELS[d], colW - iconW - ctx.measureText(n).width - 18),
      lx + iconW + ctx.measureText(n).width + fontSize * 0.55 + 4,
      ly,
    );
  });
}

function drawStats(ctx: CanvasRenderingContext2D, items: { value: string; label: string; colour?: string }[], r: Rect, big: number) {
  const colW = r.w / items.length;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  items.forEach((it, i) => {
    const cx = r.x + colW * (i + 0.5);
    ctx.fillStyle = it.colour ?? TEXT;
    ctx.font = `800 ${big}px ${FONT}`;
    ctx.fillText(it.value, cx, r.y + big);
    ctx.fillStyle = MUTED;
    ctx.font = `600 ${Math.round(big * 0.34)}px ${FONT}`;
    ctx.fillText(it.label, cx, r.y + big + big * 0.52);
  });
  ctx.textAlign = 'left';
}

/** Draws the card; resolves once the map has loaded. */
export async function drawRecapCard(size: CardSize, input: CardInput): Promise<HTMLCanvasElement> {
  const { w: W, h: H } = CARD_SIZES[size];
  const { resort } = input;
  const byId = new Map(resort.trails.map((t) => [t.id, t]));
  const trails = input.trailIds.map((id) => byId.get(id)).filter((t): t is Trail => !!t);
  const panel = bestPanel(resort, input.trailIds);
  const img = await loadImage(panel.mapSrc);

  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d')!;
  const story = size === 'story';
  const M = story ? 64 : 52;
  const inner = W - 2 * M;

  // background: the app's night blue, lighter at the top
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#1e293b');
  g.addColorStop(0.55, BG);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);

  // header: the brand, the resort, the trip and its dates
  let y = story ? 120 : 76;
  ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = GOLD;
  ctx.font = `800 ${story ? 30 : 26}px ${FONT}`;
  ctx.fillText('⛷  MY SKI RUNS', M, y);
  y += story ? 92 : 70;
  const resortName = resort.name;
  const rs = sizeToFit(ctx, resortName, 800, story ? 84 : 64, 40, inner);
  ctx.fillStyle = TEXT;
  ctx.fillText(resortName, M, y);
  y += Math.round(rs * 0.62) + (story ? 26 : 18);
  ctx.font = `600 ${story ? 38 : 30}px ${FONT}`;
  ctx.fillStyle = MUTED;
  const sub = [input.title, input.dates].filter(Boolean).join('  ·  ');
  ctx.fillText(fitText(ctx, sub, inner), M, y);
  y += story ? 48 : 32;

  // from the bottom up: the footer, the difficulty mix, the numbers; the map
  // takes what is left, in the crop's shape, and on a story the room it leaves
  // lists the runs
  const L = story
    ? { site: 36, tag: 28, footGap: 44, mixFont: 34, big: 104, statsGap: 44, mapGap: 56 }
    : { site: 26, tag: 20, footGap: 30, mixFont: 26, big: 72, statsGap: 30, mapGap: 30 };
  const fy = H - (story ? 92 : 50);
  const footTop = fy - L.site;
  const legendBase = footTop - (story ? 64 : 40);
  const barTop = legendBase - L.mixFont * 1.6 - Math.round(L.mixFont * 0.75);
  const statsTop = barTop - L.statsGap - L.big * 1.55;
  const mapBox = { x: M, y, w: inner, h: statsTop - L.mapGap - y };
  const frame = drawMap(ctx, img, panel, trails, mapBox);
  const spare = mapBox.h - frame.h;
  if (story && spare >= 120) {
    drawRunList(ctx, trails, { x: M + 8, y: frame.y + frame.h + 40, w: inner - 8, h: spare - 60 }, 30);
  }

  // the numbers
  const total = resort.trails.length;
  const pct = total ? Math.max(trails.length ? 1 : 0, Math.round((trails.length / total) * 100)) : 0;
  const stats = [
    { value: String(trails.length), label: trails.length === 1 ? 'run' : 'runs' },
    { value: String(input.newCount), label: 'new to me', colour: GOLD },
    input.days > 1 ? { value: String(input.days), label: 'days' } : { value: `${pct}%`, label: 'of the mountain' },
  ];
  drawStats(ctx, stats, { x: M, y: statsTop, w: inner, h: L.big * 1.55 }, L.big);
  drawMix(ctx, trails, { x: M, y: barTop, w: inner, h: legendBase - barTop }, L.mixFont);

  // footer: where to get it
  ctx.textAlign = 'center';
  ctx.fillStyle = TEXT;
  ctx.font = `700 ${L.site}px ${FONT}`;
  ctx.fillText(input.site, W / 2, fy);
  ctx.fillStyle = MUTED;
  ctx.font = `500 ${L.tag}px ${FONT}`;
  ctx.fillText('Tap the runs you ski on the trail map', W / 2, fy + L.footGap);
  ctx.textAlign = 'left';
  return canvas;
}

export function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) =>
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('Could not make the image'))), 'image/jpeg', 0.9),
  );
}
