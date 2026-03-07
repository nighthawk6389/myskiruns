import { useState, useMemo, useCallback } from 'react';
import type { Trail, PeakData } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_COLORS } from '../../types';
import { peaks, getTrailsByPeak } from '../../data/trails';
import { Peak } from './Peak';
import { TrailPath } from './TrailPath';
import styles from './SchematicMap.module.css';

interface SchematicMapProps {
  filteredTrailIds: Set<string>;
  skiedTrails: Set<string>;
  hoveredTrail: string | null;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
}

// Seeded random for consistent trail path generation
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

function generateTrailPath(
  trail: Trail,
  peak: PeakData,
  index: number,
  totalTrails: number
): string {
  const rng = seededRandom(hashString(trail.id));
  const { x, y, baseY, width } = peak;
  const halfW = width / 2;

  // Distribute trails across the peak width
  const spread = (index / Math.max(totalTrails - 1, 1) - 0.5) * 2;
  const startX = x + spread * halfW * 0.3;
  const endX = x + spread * halfW * 0.9;

  // Start point near summit, end at base
  const startY = y + (baseY - y) * (0.05 + rng() * 0.15);
  const endY = baseY - 10 - rng() * 30;

  // Generate 3-4 control points for natural curves
  const segments = 3 + Math.floor(rng() * 2);
  const points: [number, number][] = [[startX, startY]];

  for (let i = 1; i < segments; i++) {
    const t = i / segments;
    const px = startX + (endX - startX) * t + (rng() - 0.5) * halfW * 0.3;
    const py = startY + (endY - startY) * t + (rng() - 0.5) * 20;
    points.push([px, py]);
  }
  points.push([endX, endY]);

  // Build smooth curve
  let d = `M ${points[0][0]} ${points[0][1]}`;
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1];
    const curr = points[i];
    const cpx = (prev[0] + curr[0]) / 2 + (rng() - 0.5) * 15;
    const cpy = (prev[1] + curr[1]) / 2;
    d += ` Q ${cpx} ${cpy} ${curr[0]} ${curr[1]}`;
  }

  return d;
}

export function SchematicMap({
  filteredTrailIds,
  skiedTrails,
  hoveredTrail,
  onToggleTrail,
  onHoverTrail,
}: SchematicMapProps) {
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);

  const trailPaths = useMemo(() => {
    const result: { trail: Trail; path: string }[] = [];
    for (const peak of peaks) {
      const peakTrails = getTrailsByPeak(peak.id);
      peakTrails.forEach((trail, index) => {
        result.push({
          trail,
          path: generateTrailPath(trail, peak, index, peakTrails.length),
        });
      });
    }
    return result;
  }, []);

  const hoveredTrailData = useMemo(() => {
    if (!hoveredTrail) return null;
    return trailPaths.find((tp) => tp.trail.id === hoveredTrail)?.trail ?? null;
  }, [hoveredTrail, trailPaths]);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }, []);

  return (
    <div className={styles.container}>
      <svg
        className={styles.svg}
        viewBox="0 0 1440 750"
        preserveAspectRatio="xMidYMid meet"
        onMouseMove={handleMouseMove}
      >
        <defs>
          <linearGradient id="mountainGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#94a3b8" />
            <stop offset="100%" stopColor="#334155" />
          </linearGradient>
          <linearGradient id="snowGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#cbd5e1" stopOpacity="0" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Base line */}
        <line x1="20" y1="700" x2="1420" y2="700" stroke="#334155" strokeWidth="2" />

        {/* Peak silhouettes */}
        {peaks.map((peak) => (
          <Peak key={peak.id} peak={peak} />
        ))}

        {/* Trail paths */}
        {trailPaths.map(({ trail, path }) => (
          <TrailPath
            key={trail.id}
            trail={trail}
            path={path}
            isSkied={skiedTrails.has(trail.id)}
            isHovered={hoveredTrail === trail.id}
            isVisible={filteredTrailIds.has(trail.id)}
            onClick={() => onToggleTrail(trail.id)}
            onHover={onHoverTrail}
          />
        ))}
      </svg>

      {/* Tooltip */}
      {hoveredTrailData && mousePos && (
        <div
          className={styles.tooltip}
          style={{ left: mousePos.x, top: mousePos.y }}
        >
          <div className={styles.tooltipName}>
            <span
              className={styles.tooltipIcon}
              style={{
                color:
                  hoveredTrailData.difficulty === 'double-black'
                    ? '#ef4444'
                    : DIFFICULTY_COLORS[hoveredTrailData.difficulty],
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
