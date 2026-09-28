import type { Trail } from '../../types';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailPathProps {
  trail: Trail;
  /** one polyline per drawn line piece, in overlay viewBox units */
  segments: string[];
  isSkied: boolean;
  /** skied on some trip (drawn dashed when not skied on this one) */
  skiedBefore: boolean;
  isHovered: boolean;
  isVisible: boolean;
  /** 0.5–1: thinner lines when the map is drawn small (phones) */
  weight: number;
  /** current zoom; the stage is CSS-scaled, which non-scaling strokes don't undo */
  zoom: number;
  onHover: (id: string | null) => void;
}

// Widths are screen pixels (non-scaling strokes, divided by the CSS zoom), so
// lines keep the same weight at every zoom level. Taps are resolved by the map itself (nearest
// trails within a finger's radius); the hit stroke only drives mouse hover.
const W_HIT = 10;
const W_LINE = 1;
const W_LINE_HOVER = 3.5;

export function TrailPath({ trail, segments, isSkied, skiedBefore, isHovered, isVisible, weight, zoom, onHover }: TrailPathProps) {
  if (!isVisible) return null;

  const baseColor = trail.difficulty === 'double-black' ? '#ef4444' : DIFFICULTY_COLORS[trail.difficulty];
  const color = isSkied ? '#fbbf24' : baseColor;
  // widths in screen px: undo the stage's CSS zoom
  const px = weight / zoom;
  const lineW = (isHovered ? W_LINE_HOVER : W_LINE) * px;
  const line = {
    fill: 'none',
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    vectorEffect: 'non-scaling-stroke' as const,
  };

  return (
    <g onMouseEnter={() => onHover(trail.id)} onMouseLeave={() => onHover(null)} style={{ cursor: 'pointer' }}>
      {segments.map((points, i) => (
        <g key={i}>
          <polyline points={points} {...line} stroke="transparent" strokeWidth={W_HIT / zoom} />
          {/* white casing for contrast against the busy map */}
          <polyline
            points={points}
            {...line}
            stroke="#fff"
            strokeOpacity={isHovered ? 0.95 : isSkied ? 0.8 : 0.45}
            strokeWidth={lineW + (isHovered ? 2.5 : 0.9) * px}
          />
          <polyline
            points={points}
            {...line}
            stroke={color}
            strokeOpacity={isHovered ? 1 : isSkied ? 0.95 : 0.75}
            strokeWidth={lineW}
            strokeDasharray={skiedBefore && !isSkied ? `${4 * px} ${2.5 * px}` : undefined}
            style={{ transition: 'stroke 0.15s, stroke-opacity 0.15s' }}
          />
        </g>
      ))}
    </g>
  );
}
