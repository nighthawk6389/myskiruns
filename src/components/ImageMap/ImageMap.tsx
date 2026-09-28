import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '../../types';
import { peaks, getTrailsByPeak } from '../../data/trails';
import trailPathsData from '../../data/trailPaths.json';
import { TrailPath } from './TrailPath';
import { TrailHotspot } from './TrailHotspot';
import { TrailSheet, type SheetTrail } from './TrailSheet';
import styles from './ImageMap.module.css';

const MAP_SRC = '/killington-trail-map.jpg';
const MAX_ZOOM = 6;
// how far from a tap a trail still counts as "tapped", in screen px
const PICK_RADIUS_TOUCH = 24;
const PICK_RADIUS_MOUSE = 12;
// movement beyond this turns a press into a pan instead of a tap
const TAP_SLOP = 8;

interface ImageMapProps {
  filteredTrailIds: Set<string>;
  skiedTrails: Set<string>;
  /** trails skied on any trip, shown fainter when not skied on this one */
  skiedEver: Set<string>;
  hoveredTrail: string | null;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
}

// Trails are drawn from trailPaths.json (scripts/applyTrailProposals.mjs).
// A trail with no verified or proposed line gets no overlay; it can still be
// toggled from the list. Glades printed only as a label get a marker there.
const TRAIL_PATHS = (
  trailPathsData as {
    trails: Record<string, { segments: number[][][]; label?: number[]; source: string }>;
  }
).trails;

const TRAIL_LENGTH = new Map(
  Object.entries(TRAIL_PATHS).map(([id, p]) => [
    id,
    p.segments.reduce(
      (sum, seg) =>
        sum + seg.slice(1).reduce((s, q, i) => s + Math.hypot(q[0] - seg[i][0], q[1] - seg[i][1]), 0),
      0,
    ),
  ]),
);

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

export function ImageMap({
  filteredTrailIds,
  skiedTrails,
  skiedEver,
  hoveredTrail,
  onToggleTrail,
  onHoverTrail,
}: ImageMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [box, setBox] = useState({ w: 0, h: 0 });
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  // true aspect of the loaded map image; the overlay viewBox follows it
  const [aspect, setAspect] = useState(4572 / 2704);
  const [view, setView] = useState<View>({ k: 1, tx: 0, ty: 0 });
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);
  const [showLines, setShowLines] = useState(false);
  const [sheet, setSheet] = useState<SheetTrail[] | null>(null);
  const [toast, setToast] = useState<{ trail: Trail; skied: boolean } | null>(null);

  const allTrails = useMemo(() => {
    const result: Trail[] = [];
    for (const peak of peaks) result.push(...getTrailsByPeak(peak.id));
    return result;
  }, []);
  const trailById = useMemo(() => new Map(allTrails.map((t) => [t.id, t])), [allTrails]);

  // the map is laid out at "fit" size; zoom and pan are a transform on top
  const fitW = box.w && box.h ? Math.min(box.w, box.h * aspect) : 0;
  const fitH = fitW / aspect;
  const vH = Math.round(1000 / aspect);

  const clamp = useCallback(
    (v: View): View => {
      const k = Math.min(MAX_ZOOM, Math.max(1, v.k));
      const w = fitW * k;
      const h = fitH * k;
      const tx = w <= box.w ? (box.w - w) / 2 : Math.min(0, Math.max(box.w - w, v.tx));
      const ty = h <= box.h ? (box.h - h) / 2 : Math.min(0, Math.max(box.h - h, v.ty));
      return { k, tx, ty };
    },
    [fitW, fitH, box.w, box.h],
  );

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setBox({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const zoomAt = useCallback(
    (factor: number, cx: number, cy: number) => {
      setView((v) => {
        const k = Math.min(MAX_ZOOM, Math.max(1, v.k * factor));
        return clamp({ k, tx: cx - ((cx - v.tx) * k) / v.k, ty: cy - ((cy - v.ty) * k) / v.k });
      });
    },
    [clamp],
  );

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const r = el.getBoundingClientRect();
      zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX - r.left, e.clientY - r.top);
    };
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWheel);
  }, [zoomAt]);

  // clamp at render time so resizes and image loads re-fit without an effect
  const cv = clamp(view);
  // lines and markers are designed for a ~1100px-wide map; thin them when the
  // map is drawn smaller so they don't swamp it on a phone
  const weight = Math.min(1, Math.max(0.5, (fitW * cv.k) / 1100));

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
    [cv.k, cv.tx, cv.ty, fitW, fitH, trailById, filteredTrailIds],
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
    pointers.current.set(e.pointerId, local(e));
    if (pointers.current.size === 1) gesture.current = { moved: 0, pinch: 0 };
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      gesture.current.pinch = Math.hypot(a.x - b.x, a.y - b.y);
      gesture.current.moved = TAP_SLOP + 1;
    }
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const p = local(e);
    if (e.pointerType === 'mouse') setMousePos(p);
    const prev = pointers.current.get(e.pointerId);
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
    if (gesture.current.moved > TAP_SLOP) setView((v) => clamp({ ...v, tx: v.tx + dx, ty: v.ty + dy }));
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
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerCancel}
      onPointerLeave={() => setMousePos(null)}
    >
      {imageError && (
        <div className={styles.placeholder}>
          <div className={styles.placeholderTitle}>Trail map image missing</div>
          <div className={styles.placeholderCode}>public/killington-trail-map.jpg</div>
        </div>
      )}
      <div className={styles.stage} style={stageStyle}>
        <img
          src={MAP_SRC}
          alt="Killington trail map"
          className={styles.mapImage}
          draggable={false}
          onLoad={(e) => {
            const img = e.currentTarget;
            if (img.naturalWidth && img.naturalHeight) setAspect(img.naturalWidth / img.naturalHeight);
            setImageLoaded(true);
          }}
          onError={() => setImageError(true)}
          style={{ visibility: imageLoaded ? 'visible' : 'hidden' }}
        />
        {showLines && <img src="/trail-lines.png" alt="" className={styles.overlay} draggable={false} />}
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
                      pxPerUnit={(fitW * cv.k) / 1000 || 1}
                      weight={weight}
                      isSkied={skiedTrails.has(trail.id)}
                      isHovered={highlighted}
                      isVisible={filteredTrailIds.has(trail.id)}
                      onHover={onHoverTrail}
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
                    onHover={onHoverTrail}
                  />
                );
              })}
          </svg>
        )}
      </div>

      <div className={styles.zoomControls} data-map-ui>
        <button
          className={styles.zoomBtn}
          onClick={() => setShowLines((s) => !s)}
          title="Show detected trail lines"
          aria-pressed={showLines}
          style={{ fontSize: 15 }}
        >
          〰
        </button>
        <button className={styles.zoomBtn} onClick={() => zoomAt(1.5, box.w / 2, box.h / 2)} aria-label="Zoom in">
          +
        </button>
        <button className={styles.zoomBtn} onClick={() => zoomAt(1 / 1.5, box.w / 2, box.h / 2)} aria-label="Zoom out">
          −
        </button>
        <button className={styles.zoomBtn} onClick={() => setView(clamp({ k: 1, tx: 0, ty: 0 }))} style={{ fontSize: 12 }}>
          Fit
        </button>
      </div>

      {hoveredTrailData && mousePos && !sheet && (
        <div className={styles.tooltip} style={{ left: mousePos.x, top: mousePos.y }}>
          <div className={styles.tooltipName}>
            <span
              style={{
                color:
                  hoveredTrailData.difficulty === 'double-black' ? '#ef4444' : DIFFICULTY_COLORS[hoveredTrailData.difficulty],
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
        </div>
      )}

      {sheet && (
        <TrailSheet
          candidates={sheet}
          skiedTrails={skiedTrails}
          skiedEver={skiedEver}
          onMark={mark}
          onHover={onHoverTrail}
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
