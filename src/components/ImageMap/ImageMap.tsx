import { useState, useMemo, useCallback } from 'react';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '../../types';
import { peaks, getTrailsByPeak } from '../../data/trails';
import { PEAK_REGIONS } from '../../data/peakRegions';
import trailPositions from '../../data/trailPositions.json';
import trailPathsData from '../../data/trailPaths.json';
import { TrailHotspot } from './TrailHotspot';
import { TrailPath } from './TrailPath';
import { useTrailDetection } from '../../detection/useTrailDetection';
import styles from './ImageMap.module.css';

const MAP_SRC = '/killington-trail-map.jpg';

interface ImageMapProps {
  filteredTrailIds: Set<string>;
  skiedTrails: Set<string>;
  hoveredTrail: string | null;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
}

// Hotspot positions are generated offline by the trail detector
// (scripts/placeTrails.ts -> trailPositions.json), so dots land on actual
// detected runs. Trails missing from the JSON (e.g. added after the last
// `npm run detect:place`) fall back to a grid inside their peak's region.
function generateHotspotPositions(): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>();
  const detected = trailPositions as Record<string, { x: number; y: number }>;

  for (const peak of peaks) {
    const peakTrails = getTrailsByPeak(peak.id);
    const region = PEAK_REGIONS[peak.id];
    peakTrails.forEach((trail, index) => {
      const pos = detected[trail.id];
      if (pos) {
        positions.set(trail.id, pos);
        return;
      }
      if (!region) return;
      const cols = Math.ceil(Math.sqrt(peakTrails.length));
      const rows = Math.ceil(peakTrails.length / cols);
      const col = index % cols;
      const row = Math.floor(index / cols);
      positions.set(trail.id, {
        x: region.cx - region.w / 2 + ((col + 0.5) / cols) * region.w,
        y: region.cy - region.h / 2 + ((row + 0.5) / rows) * region.h,
      });
    });
  }

  return positions;
}

export function ImageMap({
  filteredTrailIds,
  skiedTrails,
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
  const [showDetection, setShowDetection] = useState(false);
  // precomputed trail-LINE overlay (see scripts/generateLineOverlay.mjs)
  const [showLines, setShowLines] = useState(false);

  const detection = useTrailDetection(MAP_SRC, showDetection && imageLoaded);

  const hotspotPositions = useMemo(() => generateHotspotPositions(), []);

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
          {showDetection && detection.overlayUrl && (
            <img
              src={detection.overlayUrl}
              alt="Detected trails"
              className={styles.overlay}
              style={{ pointerEvents: 'none' }}
            />
          )}
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
                .sort((a, b) => {
                  // anchored paths render on top of heuristic ones so hover
                  // resolves to the better-trusted name at overlaps
                  const rank = (t: Trail) => {
                    const e = (
                      trailPathsData as {
                        trails: Record<string, { source?: string }>;
                      }
                    ).trails[t.id];
                    if (!e) return 2; // dots on top
                    return e.source === 'anchor' ? 1 : 0;
                  };
                  return rank(a) - rank(b);
                })
                .map((trail) => {
                const vH = Math.round(1000 / aspect);
                const path = (
                  trailPathsData as {
                    trails: Record<string, { points: number[][] }>;
                  }
                ).trails[trail.id];
                if (path) {
                  // detected line polyline: the whole run is clickable
                  const pts = path.points
                    .map((q) => `${(q[0] * 10).toFixed(1)},${((q[1] * vH) / 100).toFixed(1)}`)
                    .join(' ');
                  return (
                    <TrailPath
                      key={trail.id}
                      trail={trail}
                      points={pts}
                      isSkied={skiedTrails.has(trail.id)}
                      isHovered={hoveredTrail === trail.id}
                      isVisible={filteredTrailIds.has(trail.id)}
                      onClick={() => onToggleTrail(trail.id)}
                      onHover={onHoverTrail}
                    />
                  );
                }
                const pos = hotspotPositions.get(trail.id);
                if (!pos) return null;
                return (
                  <TrailHotspot
                    key={trail.id}
                    trail={trail}
                    x={pos.x * 10}
                    y={(pos.y * vH) / 100}
                    isSkied={skiedTrails.has(trail.id)}
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
        <button
          className={styles.zoomBtn}
          onClick={() => setShowDetection((s) => !s)}
          title="Toggle detected snow-surface overlay"
          style={{
            fontSize: 16,
            background: showDetection ? 'var(--accent, #38f5ff)' : undefined,
            color: showDetection ? '#06283d' : undefined,
          }}
        >
          {detection.loading ? '…' : '⛷'}
        </button>
        <button className={styles.zoomBtn} onClick={() => setZoom((z) => Math.min(z + 0.25, 3))}>+</button>
        <button className={styles.zoomBtn} onClick={() => setZoom((z) => Math.max(z - 0.25, 0.5))}>-</button>
        <button className={styles.zoomBtn} onClick={() => setZoom(1)} style={{ fontSize: 12 }}>1x</button>
      </div>
      {showDetection && detection.overlayUrl && (
        <div
          style={{
            position: 'absolute',
            top: 16,
            left: 16,
            background: 'rgba(15, 23, 42, 0.9)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '6px 12px',
            fontSize: 12,
            color: 'var(--text-secondary)',
          }}
        >
          Detected trail surface · {(detection.coverage * 100).toFixed(1)}% of pixels
        </div>
      )}

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
            {skiedTrails.has(hoveredTrailData.id) && ' • ✓ Skied'}
          </div>
        </div>
      )}
    </div>
  );
}
