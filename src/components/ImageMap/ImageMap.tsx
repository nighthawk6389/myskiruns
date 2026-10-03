import { useState, useMemo, useCallback, useEffect, useImperativeHandle, useRef } from 'react';
import { keepForOffline, startOffline } from '../../offline';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_COLORS, DIFFICULTY_UI_COLORS } from '../../types';
import type { Resort, TrailPath as Overlay } from '../../resorts';
import { TrailPath } from './TrailPath';
import { TrailHotspot } from './TrailHotspot';
import { TrailSheet, type SheetTrail } from './TrailSheet';
import type { Conditions } from '../../hooks/useConditions';
import { topTags } from '../../conditionTags';
import styles from './ImageMap.module.css';

const MAX_ZOOM = 6;
// how far from a tap a trail still counts as "tapped", in screen px
const PICK_RADIUS_TOUCH = 24;
const PICK_RADIUS_MOUSE = 12;
// movement beyond this turns a press into a pan instead of a tap
const TAP_SLOP = 8;
// below this width the map opens zoomed to fill the (tall) map area
const PHONE_MAX_W = 760;
// the detected-lines debug overlay is only offered with ?lines in the URL
const SHOW_LINES_TOGGLE = typeof location !== 'undefined' && new URLSearchParams(location.search).has('lines');

export interface ImageMapHandle {
  /** zoom to a trail, highlight it and open its sheet */
  focusTrail: (id: string) => void;
}

interface ImageMapProps {
  filteredTrailIds: Set<string>;
  skiedTrails: Set<string>;
  /** trails skied on any trip, shown fainter when not skied on this one */
  skiedEver: Set<string>;
  hoveredTrail: string | null;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
  /** show the "tap a trail" hint (nothing marked on this trip yet) */
  showHint: boolean;
  conditions: Conditions;
  /** whose map, trails and overlays to show; remount (key) when it changes */
  resort: Resort;
  ref?: React.Ref<ImageMapHandle>;
}

// Trails are drawn from the resort's trailPaths.json
// (scripts/applyTrailProposals.mjs), one per map panel. A trail with no
// verified or proposed line gets no overlay; it can still be toggled from the
// list. Glades printed only as a label get a marker there.
function pathLengths(paths: Record<string, Overlay>) {
  return new Map(
    Object.entries(paths).map(([id, p]) => [
      id,
      p.segments.reduce(
        (sum, seg) =>
          sum + seg.slice(1).reduce((s, q, i) => s + Math.hypot(q[0] - seg[i][0], q[1] - seg[i][1]), 0),
        0,
      ),
    ]),
  );
}

interface NameAnchor {
  x: number;
  y: number;
  /** degrees, kept within ±90 so text never reads upside down */
  angle: number;
  /** length of the stretch the name sits on, viewBox units */
  length: number;
}

/** Where to print a trail's name: the middle of its longest stretch, turned
 * to follow the line there. Coordinates are overlay viewBox units. */
function nameAnchor(segments: number[][][], vH: number): NameAnchor | null {
  let best: { pts: number[][]; cum: number[] } | null = null;
  for (const seg of segments) {
    const pts = seg.map((q) => [q[0] * 10, (q[1] * vH) / 100]);
    const cum = [0];
    for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    if (!best || cum.at(-1)! > best.cum.at(-1)!) best = { pts, cum };
  }
  if (!best || best.cum.at(-1)! === 0) return null;
  const { pts, cum } = best;
  const total = cum.at(-1)!;
  const at = (t: number) => {
    const i = Math.max(1, cum.findIndex((c) => c >= t));
    const u = (t - cum[i - 1]) / Math.max(1e-9, cum[i] - cum[i - 1]);
    return [pts[i - 1][0] + u * (pts[i][0] - pts[i - 1][0]), pts[i - 1][1] + u * (pts[i][1] - pts[i - 1][1])];
  };
  const mid = at(total / 2);
  // direction over a stretch either side of the middle smooths out kinks
  const a = at(Math.max(0, total / 2 - 15));
  const b = at(Math.min(total, total / 2 + 15));
  let angle = (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI;
  if (angle > 90) angle -= 180;
  if (angle < -90) angle += 180;
  return { x: mid[0], y: mid[1], angle, length: total };
}

const NAME_PX = 11;
const NAME_CHAR_PX = 6.2;

function distToSegment(px: number, py: number, ax: number, ay: number, bx: number, by: number) {
  const dx = bx - ax;
  const dy = by - ay;
  const len = dx * dx + dy * dy;
  const t = len === 0 ? 0 : Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / len));
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
}

interface View {
  k: number;
  tx: number;
  ty: number;
}

/** The view kept on the map: never smaller than the whole map, never panned
 * off it. fitW/fitH: the map's size at zoom 1; w/h: the map area's. */
function clampView(v: View, fitW: number, fitH: number, w: number, h: number): View {
  const k = Math.min(MAX_ZOOM, Math.max(1, v.k));
  const mw = fitW * k;
  const mh = fitH * k;
  const tx = mw <= w ? (w - mw) / 2 : Math.min(0, Math.max(w - mw, v.tx));
  const ty = mh <= h ? (h - mh) / 2 : Math.min(0, Math.max(h - mh, v.ty));
  return { k, tx, ty };
}

/** The view that shows a trail's overlay: in the middle ~60% of the map
 * area, never closer than 4x. */
function viewOfTrail(path: Overlay, fitW: number, fitH: number, w: number, h: number): View {
  const pts = path.label ? [path.label] : path.segments.flat();
  const xs = pts.map((q) => (q[0] * fitW) / 100);
  const ys = pts.map((q) => (q[1] * fitH) / 100);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const k = Math.min(4, Math.max(1.5, Math.min((w * 0.6) / (x1 - x0 || 1), (h * 0.5) / (y1 - y0 || 1))));
  // on phones the sheet covers the bottom of the screen, so aim higher
  const cy = w <= PHONE_MAX_W ? h * 0.4 : h / 2;
  return { k, tx: w / 2 - ((x0 + x1) / 2) * k, ty: cy - ((y0 + y1) / 2) * k };
}

/** The panel to open first: ?panel=<id> when the resort has it, else its first. */
function initialPanel(resort: Resort): string {
  const want = typeof location !== 'undefined' ? new URLSearchParams(location.search).get('panel') : null;
  return (resort.maps.find((m) => m.id === want) ?? resort.maps[0]).id;
}

export function ImageMap({
  filteredTrailIds,
  skiedTrails,
  skiedEver,
  hoveredTrail,
  onToggleTrail,
  onHoverTrail,
  showHint,
  conditions,
  resort,
  ref,
}: ImageMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [box, setBox] = useState({ w: 0, h: 0 });
  const [imageLoaded, setImageLoaded] = useState(false);
  // 'offline': no connection and this map isn't cached yet; it loads once the
  // connection is back. 'missing': the file isn't there.
  const [imageError, setImageError] = useState<'offline' | 'missing' | null>(null);
  const [imageTry, setImageTry] = useState(0);
  // the first panel on screen has loaded: time to cache the others
  const [firstMapLoaded, setFirstMapLoaded] = useState(false);
  // true aspect of the loaded map image; the overlay viewBox follows it
  const [aspect, setAspect] = useState(4572 / 2704);
  // null until the user moves the map: the default view for the screen size
  const [view, setView] = useState<View | null>(null);
  // animate programmatic moves (buttons, locate), not direct manipulation
  const [smooth, setSmooth] = useState(false);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);
  const [showLines, setShowLines] = useState(false);
  const [sheet, setSheet] = useState<SheetTrail[] | null>(null);
  const [toast, setToast] = useState<{ trail: Trail; skied: boolean } | null>(null);

  // a resort drawn on several panels (Vail) shows one at a time
  const panels = resort.maps;
  const [panelId, setPanelId] = useState(() => initialPanel(resort));
  const panel = panels.find((p) => p.id === panelId) ?? panels[0];
  // a trail picked on another panel, to zoom to once that panel has loaded
  const pendingFocus = useRef<string | null>(null);

  const TRAIL_PATHS = panel.paths;
  const TRAIL_LENGTH = useMemo(() => pathLengths(panel.paths), [panel.paths]);
  const allTrails = useMemo(
    () => resort.peaks.flatMap((peak) => resort.trails.filter((t) => t.peak === peak.id)),
    [resort],
  );
  const trailById = useMemo(() => new Map(allTrails.map((t) => [t.id, t])), [allTrails]);

  // the map is laid out at "fit" size; zoom and pan are a transform on top
  const fitW = box.w && box.h ? Math.min(box.w, box.h * aspect) : 0;
  const fitH = fitW / aspect;
  const vH = Math.round(1000 / aspect);

  const clamp = useCallback((v: View): View => clampView(v, fitW, fitH, box.w, box.h), [fitW, fitH, box.w, box.h]);

  // phones: the map area is taller than the fitted map, so start zoomed in
  // to fill its height (centered) instead of showing empty bands
  const defaultView = useMemo((): View => {
    if (!fitH || box.w > PHONE_MAX_W || box.h < fitH * 1.2) return { k: 1, tx: 0, ty: 0 };
    const k = Math.min(MAX_ZOOM, box.h / fitH);
    return { k, tx: (box.w - fitW * k) / 2, ty: 0 };
  }, [box.w, box.h, fitW, fitH]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setBox({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // every panel of this resort's map, cached for use without signal
  useEffect(() => (firstMapLoaded ? keepForOffline(panels.map((p) => p.mapSrc)) : undefined), [firstMapLoaded, panels]);

  useEffect(() => {
    if (imageError !== 'offline') return;
    const retry = () => {
      setImageError(null);
      setImageTry((n) => n + 1);
    };
    window.addEventListener('online', retry);
    return () => window.removeEventListener('online', retry);
  }, [imageError]);

  const zoomAt = useCallback(
    (factor: number, cx: number, cy: number) => {
      setView((prev) => {
        const v = prev ?? defaultView;
        const k = Math.min(MAX_ZOOM, Math.max(1, v.k * factor));
        return clamp({ k, tx: cx - ((cx - v.tx) * k) / v.k, ty: cy - ((cy - v.ty) * k) / v.k });
      });
    },
    [clamp, defaultView],
  );

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      setSmooth(false);
      const r = el.getBoundingClientRect();
      zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX - r.left, e.clientY - r.top);
    };
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWheel);
  }, [zoomAt]);

  // clamp at render time so resizes and image loads re-fit without an effect
  const cv = clamp(view ?? defaultView);
  // lines and markers are designed for a ~1100px-wide map; thin them when the
  // map is drawn smaller so they don't swamp it on a phone
  const weight = Math.min(1, Math.max(0.5, (fitW * cv.k) / 1100));
  const pxPerUnit = (fitW * cv.k) / 1000 || 1;
  const namePx = NAME_PX * Math.max(0.8, weight);

  const anchors = useMemo(
    () =>
      new Map(
        Object.entries(TRAIL_PATHS)
          .map(([id, p]) => [id, nameAnchor(p.segments, vH)] as const)
          .filter((e): e is readonly [string, NameAnchor] => !!e[1]),
      ),
    [vH, TRAIL_PATHS],
  );

  // Names go where the line is long enough on screen to hold them and they
  // don't collide with a name already placed; longer trails get first pick,
  // so zooming in reveals more names.
  const names = useMemo(() => {
    const placed: { x: number; y: number; r: number }[] = [];
    const out: { trail: Trail; a: NameAnchor; width: number }[] = [];
    const order = [...anchors.entries()].sort((p, q) => q[1].length - p[1].length);
    for (const [id, a] of order) {
      const trail = trailById.get(id);
      if (!trail || !filteredTrailIds.has(id)) continue;
      const width = (trail.name.length * NAME_CHAR_PX * namePx) / NAME_PX + 8;
      if (a.length * pxPerUnit < width * 1.2) continue;
      const x = a.x * pxPerUnit;
      const y = a.y * pxPerUnit;
      const r = width / 2;
      if (placed.some((o) => Math.hypot(o.x - x, o.y - y) < (o.r + r) * 0.8)) continue;
      placed.push({ x, y, r });
      out.push({ trail, a, width });
    }
    return out;
  }, [anchors, pxPerUnit, namePx, trailById, filteredTrailIds]);

  /** Trails near a point on screen, nearest first. */
  const pick = useCallback(
    (sx: number, sy: number, radius: number): SheetTrail[] => {
      const toScreen = (q: number[]): [number, number] => [
        cv.tx + (cv.k * q[0] * fitW) / 100,
        cv.ty + (cv.k * q[1] * fitH) / 100,
      ];
      const hits: SheetTrail[] = [];
      for (const [id, p] of Object.entries(TRAIL_PATHS)) {
        const trail = trailById.get(id);
        if (!trail || !filteredTrailIds.has(id)) continue;
        let d = Infinity;
        if (p.label) {
          const [x, y] = toScreen(p.label);
          d = Math.hypot(sx - x, sy - y);
        }
        for (const seg of p.segments) {
          for (let i = 1; i < seg.length; i++) {
            const [ax, ay] = toScreen(seg[i - 1]);
            const [bx, by] = toScreen(seg[i]);
            d = Math.min(d, distToSegment(sx, sy, ax, ay, bx, by));
          }
        }
        if (d <= radius) hits.push({ trail, distance: d });
      }
      return hits.sort((a, b) => a.distance - b.distance).slice(0, 4);
    },
    [cv.k, cv.tx, cv.ty, fitW, fitH, trailById, filteredTrailIds, TRAIL_PATHS],
  );

  // one finger or the mouse pans, two fingers pinch, a still press is a tap
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const gesture = useRef({ moved: 0, pinch: 0 });

  const local = (e: React.PointerEvent) => {
    const r = containerRef.current!.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  const onPointerDown = (e: React.PointerEvent) => {
    if ((e.target as HTMLElement).closest('[data-map-ui]')) return;
    containerRef.current?.setPointerCapture(e.pointerId);
    setSmooth(false);
    pointers.current.set(e.pointerId, local(e));
    if (pointers.current.size === 1) gesture.current = { moved: 0, pinch: 0 };
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      gesture.current.pinch = Math.hypot(a.x - b.x, a.y - b.y);
      gesture.current.moved = TAP_SLOP + 1;
    }
  };

  // Mouse hover names the NEAREST trail within reach, like a tap does, so at
  // a crossing the line under the pointer wins rather than whichever trail
  // happens to be drawn on top (and markers never cover lines).
  const mouseHover = useRef<string | null>(null);
  const setMouseHover = (id: string | null) => {
    if (mouseHover.current === id) return;
    mouseHover.current = id;
    onHoverTrail(id);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const p = local(e);
    const prev = pointers.current.get(e.pointerId);
    if (e.pointerType === 'mouse') {
      setMousePos(p);
      const overUi = (e.target as HTMLElement).closest('[data-map-ui]');
      if (!prev && !sheet) setMouseHover(overUi ? null : (pick(p.x, p.y, PICK_RADIUS_MOUSE)[0]?.trail.id ?? null));
    }
    if (!prev) return;
    pointers.current.set(e.pointerId, p);
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      if (gesture.current.pinch) zoomAt(d / gesture.current.pinch, (a.x + b.x) / 2, (a.y + b.y) / 2);
      gesture.current.pinch = d;
      return;
    }
    const dx = p.x - prev.x;
    const dy = p.y - prev.y;
    gesture.current.moved += Math.abs(dx) + Math.abs(dy);
    if (gesture.current.moved > TAP_SLOP) {
      setView((prev) => {
        const v = clamp(prev ?? defaultView);
        return clamp({ ...v, tx: v.tx + dx, ty: v.ty + dy });
      });
    }
  };

  const onPointerUp = (e: React.PointerEvent) => {
    if (!pointers.current.has(e.pointerId)) return;
    pointers.current.delete(e.pointerId);
    if (pointers.current.size > 0 || gesture.current.moved > TAP_SLOP) return;
    const p = local(e);
    const hits = pick(p.x, p.y, e.pointerType === 'mouse' ? PICK_RADIUS_MOUSE : PICK_RADIUS_TOUCH);
    setSheet(hits.length ? hits : null);
    onHoverTrail(hits[0]?.trail.id ?? null);
  };

  const onPointerCancel = (e: React.PointerEvent) => {
    pointers.current.delete(e.pointerId);
  };

  const mark = (trail: Trail) => {
    const willBeSkied = !skiedTrails.has(trail.id);
    onToggleTrail(trail.id);
    setSheet(null);
    onHoverTrail(null);
    setToast({ trail, skied: willBeSkied });
  };

  /** Show another panel; its view starts over once its image has loaded. */
  const switchPanel = (id: string) => {
    setPanelId(id);
    setImageLoaded(false);
    setImageError(null);
    setView(null);
    setSmooth(false);
  };

  const focusTrail = (id: string) => {
    const trail = trailById.get(id);
    if (!trail) return;
    onHoverTrail(id);
    setSheet([{ trail, distance: 0 }]);
    // several panels: show the trail where it is drawn (this panel if it is,
    // else the panel of its area, else any), zooming once that one has loaded
    const there = TRAIL_PATHS[id]
      ? panel
      : (panels.find((p) => p.id === trail.peak && p.paths[id]) ?? panels.find((p) => p.paths[id]));
    if (there && there !== panel) {
      pendingFocus.current = id;
      switchPanel(there.id);
      return;
    }
    const path = TRAIL_PATHS[id];
    if (!path) return;
    if (!imageLoaded) {
      pendingFocus.current = id; // its size isn't known yet: zoom once it loads
      return;
    }
    if (!fitW) return;
    setSmooth(true);
    setView(clamp(viewOfTrail(path, fitW, fitH, box.w, box.h)));
  };
  useImperativeHandle(ref, () => ({ focusTrail }));

  // Escape closes the sheet
  useEffect(() => {
    if (!sheet) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSheet(null);
        onHoverTrail(null);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [sheet, onHoverTrail]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 5000);
    return () => clearTimeout(t);
  }, [toast]);

  const hoveredTrailData = hoveredTrail ? (trailById.get(hoveredTrail) ?? null) : null;
  const stageStyle = {
    width: fitW,
    height: fitH,
    transform: `translate(${cv.tx}px, ${cv.ty}px) scale(${cv.k})`,
  };

  return (
    <div
      ref={containerRef}
      className={styles.container}
      style={{ cursor: hoveredTrail && mousePos && !sheet ? 'pointer' : undefined }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerCancel}
      onPointerLeave={() => {
        setMousePos(null);
        setMouseHover(null);
      }}
    >
      {imageError === 'offline' && (
        <div className={styles.placeholder}>
          <div className={styles.placeholderTitle}>No connection</div>
          <div className={styles.placeholderText}>
            This map isn&apos;t saved on this device yet. It loads when you&apos;re back online, and stays
            available offline after that. The trail list works now.
          </div>
        </div>
      )}
      {imageError === 'missing' && (
        <div className={styles.placeholder}>
          <div className={styles.placeholderTitle}>Trail map image missing</div>
          <div className={styles.placeholderCode}>public{panel.mapSrc}</div>
        </div>
      )}
      <div className={`${styles.stage} ${smooth ? styles.smooth : ''}`} style={stageStyle}>
        <img
          key={`${panel.id}-${imageTry}`}
          src={panel.mapSrc}
          alt={`${resort.name} trail map${panels.length > 1 ? `, ${panel.name}` : ''}`}
          className={styles.mapImage}
          draggable={false}
          onLoad={(e) => {
            const img = e.currentTarget;
            const a = img.naturalWidth && img.naturalHeight ? img.naturalWidth / img.naturalHeight : aspect;
            setAspect(a);
            setImageLoaded(true);
            setFirstMapLoaded(true);
            startOffline();
            // a trail picked from the list before this map had loaded (or on
            // another panel): zoom to it now that the map's size is known
            const id = pendingFocus.current;
            pendingFocus.current = null;
            const path = id ? panel.paths[id] : undefined;
            if (path && box.w && box.h) {
              const fw = Math.min(box.w, box.h * a);
              setView(clampView(viewOfTrail(path, fw, fw / a, box.w, box.h), fw, fw / a, box.w, box.h));
            }
          }}
          onError={() => setImageError(navigator.onLine ? 'missing' : 'offline')}
          style={{ visibility: imageLoaded ? 'visible' : 'hidden' }}
        />
        {showLines && <img src={panel.mapSrc.replace(/\.jpg$/, '-lines.png')} alt="" className={styles.overlay} draggable={false} />}
        {imageLoaded && (
          <svg className={styles.overlay} viewBox={`0 0 1000 ${vH}`}>
            {[...allTrails]
              // shorter trails render last (on top) so their hover isn't swallowed
              .sort((a, b) => (TRAIL_LENGTH.get(b.id) ?? 0) - (TRAIL_LENGTH.get(a.id) ?? 0))
              .map((trail) => {
                const path = TRAIL_PATHS[trail.id];
                if (!path) return null;
                const highlighted = hoveredTrail === trail.id || !!sheet?.some((s) => s.trail.id === trail.id);
                if (path.label) {
                  return (
                    <TrailHotspot
                      key={trail.id}
                      trail={trail}
                      x={path.label[0] * 10}
                      y={(path.label[1] * vH) / 100}
                      pxPerUnit={pxPerUnit}
                      weight={weight}
                      isSkied={skiedTrails.has(trail.id)}
                      isHovered={highlighted}
                      isVisible={filteredTrailIds.has(trail.id)}
                    />
                  );
                }
                const segments = path.segments.map((seg) =>
                  seg.map((q) => `${(q[0] * 10).toFixed(1)},${((q[1] * vH) / 100).toFixed(1)}`).join(' '),
                );
                return (
                  <TrailPath
                    key={trail.id}
                    trail={trail}
                    segments={segments}
                    isSkied={skiedTrails.has(trail.id)}
                    skiedBefore={skiedEver.has(trail.id)}
                    isHovered={highlighted}
                    isVisible={filteredTrailIds.has(trail.id)}
                    weight={weight}
                    zoom={cv.k}
                  />
                );
              })}
            <g className={styles.trailNames} aria-hidden="true">
              {names.map(({ trail, a }) => (
                <text
                  key={trail.id}
                  x={a.x}
                  y={a.y}
                  transform={`rotate(${a.angle.toFixed(1)} ${a.x.toFixed(1)} ${a.y.toFixed(1)})`}
                  fontSize={namePx / pxPerUnit}
                  strokeWidth={3 / pxPerUnit}
                  fill={
                    skiedTrails.has(trail.id)
                      ? '#92400e'
                      : trail.difficulty === 'double-black'
                        ? '#b91c1c'
                        : trail.difficulty === 'black'
                          ? '#111827'
                          : DIFFICULTY_COLORS[trail.difficulty]
                  }
                >
                  {trail.name}
                </text>
              ))}
            </g>
          </svg>
        )}
      </div>

      {panels.length > 1 && (
        <div className={styles.panelTabs} role="group" aria-label="Trail map" data-map-ui>
          {panels.map((p) => (
            <button
              key={p.id}
              className={`${styles.panelTab} ${p === panel ? styles.panelTabOn : ''}`}
              aria-pressed={p === panel}
              onClick={() => {
                if (p === panel) return;
                pendingFocus.current = null;
                switchPanel(p.id);
                setSheet(null);
                onHoverTrail(null);
              }}
            >
              {p.name}
            </button>
          ))}
        </div>
      )}

      <div className={styles.zoomControls} data-map-ui>
        {SHOW_LINES_TOGGLE && (
          <button
            className={styles.zoomBtn}
            onClick={() => setShowLines((s) => !s)}
            title="Show detected trail lines"
            aria-pressed={showLines}
            style={{ fontSize: 15 }}
          >
            〰
          </button>
        )}
        <button
          className={styles.zoomBtn}
          onClick={() => {
            setSmooth(true);
            zoomAt(1.5, box.w / 2, box.h / 2);
          }}
          aria-label="Zoom in"
          title="Zoom in"
        >
          +
        </button>
        <button
          className={styles.zoomBtn}
          onClick={() => {
            setSmooth(true);
            zoomAt(1 / 1.5, box.w / 2, box.h / 2);
          }}
          aria-label="Zoom out"
          title="Zoom out"
        >
          −
        </button>
        <button
          className={styles.zoomBtn}
          onClick={() => {
            setSmooth(true);
            setView({ k: 1, tx: 0, ty: 0 });
          }}
          aria-label="Show the whole map"
          title="Show the whole map"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
            <path d="M1.5 5.5v-4h4M10.5 1.5h4v4M14.5 10.5v4h-4M5.5 14.5h-4v-4" />
          </svg>
        </button>
      </div>

      {showHint && imageLoaded && !sheet && !toast && (
        <div className={`${styles.hint} ${panels.length > 1 ? styles.hintLow : ''}`} aria-hidden="true">
          Tap a trail on the map to mark it skied
        </div>
      )}

      {hoveredTrailData && mousePos && !sheet && (
        <div className={styles.tooltip} style={{ left: mousePos.x, top: mousePos.y }}>
          <div className={styles.tooltipName}>
            <span
              style={{
                color: DIFFICULTY_UI_COLORS[hoveredTrailData.difficulty],
                marginRight: 4,
              }}
            >
              {DIFFICULTY_ICONS[hoveredTrailData.difficulty]}
            </span>
            {hoveredTrailData.name}
          </div>
          <div className={styles.tooltipDetail}>
            {DIFFICULTY_LABELS[hoveredTrailData.difficulty]}
            {hoveredTrailData.isGlade && ' • Glade'}
            {hoveredTrailData.isTerrainPark && ' • Terrain Park'}
            {skiedTrails.has(hoveredTrailData.id)
              ? ' • ✓ Skied this trip'
              : skiedEver.has(hoveredTrailData.id) && ' • Skied on an earlier trip'}
          </div>
          {(() => {
            const c = conditions.countsFor(hoveredTrailData.id);
            const tags = topTags(c.tags)
              .map(({ tag, count }) => `${tag.emoji} ${tag.label}${count > 1 ? ` ${count}` : ''}`)
              .join(' · ');
            return c.up + c.down > 0 || tags ? (
              <div className={styles.tooltipDetail}>
                Today: 👍 {c.up} · 👎 {c.down}
                {tags && <> · {tags}</>}
              </div>
            ) : null;
          })()}
        </div>
      )}

      {sheet && (
        <TrailSheet
          candidates={sheet}
          skiedTrails={skiedTrails}
          skiedEver={skiedEver}
          onMark={mark}
          onHover={onHoverTrail}
          conditions={conditions}
          onClose={() => {
            setSheet(null);
            onHoverTrail(null);
          }}
        />
      )}

      {toast && !sheet && (
        <div className={styles.toast} role="status" data-map-ui>
          <span>
            {toast.skied ? '✓ Marked' : 'Removed'} <strong>{toast.trail.name}</strong>
          </span>
          <button
            onClick={() => {
              onToggleTrail(toast.trail.id);
              setToast(null);
            }}
          >
            Undo
          </button>
        </div>
      )}
    </div>
  );
}
