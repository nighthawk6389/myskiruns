import { useState, useMemo, useCallback } from 'react';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '../../types';
import { peaks, getTrailsByPeak } from '../../data/trails';
import trailPathsData from '../../data/trailPaths.json';
import { TrailPath } from './TrailPath';
import { TrailHotspot } from './TrailHotspot';
import styles from './ImageMap.module.css';

const MAP_SRC = '/killington-trail-map.jpg';

interface ImageMapProps {
  filteredTrailIds: Set<string>;
  skiedTrails: Set<string>;
  /** trails skied on any trip, shown fainter when not skied on this one */
  skiedEver: Set<string>;
  hoveredTrail: string | null;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
}

// Trails are drawn as clickable paths from trailPaths.json
// (scripts/applyTrailProposals.mjs). A trail with no verified or proposed line
// gets no overlay rather than a guess; it can still be toggled from the list.
// Glades printed only as a label get a marker at the label.
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

export function ImageMap({
  filteredTrailIds,
  skiedTrails,
  skiedEver,
  hoveredTrail,
  onToggleTrail,
  onHoverTrail,
}: ImageMapProps) {
  const [zoom, setZoom] = useState(1);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  // true aspect of the loaded map image; the overlay viewBox follows it so
  // circles render as circles (not stretched ellipses)
  const [aspect, setAspect] = useState(4572 / 2704);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);
  // precomputed trail-LINE overlay (see scripts/generateLineOverlay.mjs)
  const [showLines, setShowLines] = useState(false);

  const allTrails = useMemo(() => {
    const result: Trail[] = [];
    for (const peak of peaks) {
      result.push(...getTrailsByPeak(peak.id));
    }
    return result;
  }, []);

  const hoveredTrailData = useMemo(() => {
    if (!hoveredTrail) return null;
    return allTrails.find((t) => t.id === hoveredTrail) ?? null;
  }, [hoveredTrail, allTrails]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }, []);

  return (
    <div className={styles.container} onMouseMove={handleMouseMove}>
      <div className={styles.scrollArea}>
        {!imageLoaded && !imageError && (
          <div className={styles.placeholder}>
            <div className={styles.placeholderTitle}>Trail Map Image</div>
            <div className={styles.placeholderText}>
              To use the image overlay view, add your Killington trail map image to:
            </div>
            <div className={styles.placeholderCode}>public/killington-trail-map.jpg</div>
            <div className={styles.placeholderText}>
              You can download it from the Killington website or take a screenshot of the trail map.
              The hotspot markers will overlay on top of the image.
            </div>
          </div>
        )}
        <div
          className={styles.imageWrapper}
          style={{ transform: `scale(${zoom})` }}
        >
          <img
            src={MAP_SRC}
            alt="Killington Trail Map"
            className={styles.mapImage}
            onLoad={(e) => {
              const img = e.currentTarget;
              if (img.naturalWidth && img.naturalHeight) {
                setAspect(img.naturalWidth / img.naturalHeight);
              }
              setImageLoaded(true);
            }}
            onError={() => setImageError(true)}
            style={{ display: imageLoaded ? 'block' : 'none' }}
          />
          {showLines && (
            <img
              src="/trail-lines.png"
              alt="Detected trail lines"
              className={styles.overlay}
              style={{ pointerEvents: 'none' }}
            />
          )}
          {(imageLoaded || imageError) && (
            <svg
              className={styles.overlay}
              viewBox={`0 0 1000 ${Math.round(1000 / aspect)}`}
            >
              {[...allTrails]
                // shorter trails render last (on top) so a long run passing
                // nearby doesn't swallow the hover of a short one
                .sort((a, b) => (TRAIL_LENGTH.get(b.id) ?? 0) - (TRAIL_LENGTH.get(a.id) ?? 0))
                .map((trail) => {
                  const path = TRAIL_PATHS[trail.id];
                  if (!path) return null;
                  const vH = Math.round(1000 / aspect);
                  if (path.label) {
                    // trail printed as a label with no drawn line (glades)
                    return (
                      <TrailHotspot
                        key={trail.id}
                        trail={trail}
                        x={path.label[0] * 10}
                        y={(path.label[1] * vH) / 100}
                        isSkied={skiedTrails.has(trail.id)}
                        isHovered={hoveredTrail === trail.id}
                        isVisible={filteredTrailIds.has(trail.id)}
                        onClick={() => onToggleTrail(trail.id)}
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
                      isHovered={hoveredTrail === trail.id}
                      isVisible={filteredTrailIds.has(trail.id)}
                      onClick={() => onToggleTrail(trail.id)}
                      onHover={onHoverTrail}
                    />
                  );
                })}
            </svg>
          )}
        </div>
      </div>

      <div className={styles.zoomControls}>
        <button
          className={styles.zoomBtn}
          onClick={() => setShowLines((s) => !s)}
          title="Toggle detected trail-line overlay"
          style={{
            fontSize: 15,
            background: showLines ? 'var(--accent, #38f5ff)' : undefined,
            color: showLines ? '#06283d' : undefined,
          }}
        >
          〰
        </button>
        <button className={styles.zoomBtn} onClick={() => setZoom((z) => Math.min(z + 0.25, 3))}>+</button>
        <button className={styles.zoomBtn} onClick={() => setZoom((z) => Math.max(z - 0.25, 0.5))}>-</button>
        <button className={styles.zoomBtn} onClick={() => setZoom(1)} style={{ fontSize: 12 }}>1x</button>
      </div>
      {hoveredTrailData && mousePos && (
        <div
          className={styles.tooltip}
          style={{ left: mousePos.x, top: mousePos.y }}
        >
          <div className={styles.tooltipName}>
            <span
              style={{
                color:
                  hoveredTrailData.difficulty === 'double-black'
                    ? '#ef4444'
                    : DIFFICULTY_COLORS[hoveredTrailData.difficulty],
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
    </div>
  );
}
