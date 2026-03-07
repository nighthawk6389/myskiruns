import { useState, useMemo, useCallback } from 'react';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '../../types';
import { peaks, getTrailsByPeak } from '../../data/trails';
import { TrailHotspot } from './TrailHotspot';
import styles from './ImageMap.module.css';

interface ImageMapProps {
  filteredTrailIds: Set<string>;
  skiedTrails: Set<string>;
  hoveredTrail: string | null;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
}

// Seeded random for consistent hotspot placement
function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0;
  }
  return Math.abs(hash);
}

function generateHotspotPositions(): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>();
  // Map peaks to approximate percentage positions on a typical trail map image
  const peakRegions: Record<string, { cx: number; cy: number; w: number; h: number }> = {
    'snowshed': { cx: 8, cy: 55, w: 10, h: 40 },
    'sunrise': { cx: 18, cy: 50, w: 10, h: 40 },
    'ramshead': { cx: 30, cy: 40, w: 12, h: 45 },
    'snowdon': { cx: 44, cy: 35, w: 14, h: 50 },
    'skye-peak': { cx: 62, cy: 28, w: 16, h: 55 },
    'killington-peak': { cx: 78, cy: 20, w: 16, h: 60 },
    'bear-mountain': { cx: 92, cy: 32, w: 12, h: 50 },
  };

  for (const peak of peaks) {
    const region = peakRegions[peak.id];
    if (!region) continue;
    const peakTrails = getTrailsByPeak(peak.id);
    peakTrails.forEach((trail, index) => {
      const rng = seededRandom(hashString(trail.id));
      const cols = Math.ceil(Math.sqrt(peakTrails.length));
      const row = Math.floor(index / cols);
      const col = index % cols;
      const rows = Math.ceil(peakTrails.length / cols);

      const x = region.cx - region.w / 2 + (col / Math.max(cols - 1, 1)) * region.w + (rng() - 0.5) * 2;
      const y = region.cy - region.h / 2 + (row / Math.max(rows - 1, 1)) * region.h + (rng() - 0.5) * 2;

      positions.set(trail.id, { x: Math.max(2, Math.min(98, x)), y: Math.max(5, Math.min(95, y)) });
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
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);

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
            src="/killington-trail-map.jpg"
            alt="Killington Trail Map"
            className={styles.mapImage}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
            style={{ display: imageLoaded ? 'block' : 'none' }}
          />
          {(imageLoaded || imageError) && (
            <svg
              className={styles.overlay}
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
            >
              {allTrails.map((trail) => {
                const pos = hotspotPositions.get(trail.id);
                if (!pos) return null;
                return (
                  <TrailHotspot
                    key={trail.id}
                    trail={trail}
                    x={pos.x}
                    y={pos.y}
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
            {skiedTrails.has(hoveredTrailData.id) && ' • ✓ Skied'}
          </div>
        </div>
      )}
    </div>
  );
}
