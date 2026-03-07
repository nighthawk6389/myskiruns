import type { Trail } from '../../types';
import type { TrailPathSegment } from '../../data/trailPaths';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailPolylineProps {
  trail: Trail;
  segments: TrailPathSegment[];
  isSkied: boolean;
  isHovered: boolean;
  isVisible: boolean;
  onClick: () => void;
  onHover: (id: string | null) => void;
}

function segmentToPoints(segment: TrailPathSegment): string {
  return segment.map(([x, y]) => `${x},${y}`).join(' ');
}

export function TrailPolyline({
  trail,
  segments,
  isSkied,
  isHovered,
  isVisible,
  onClick,
  onHover,
}: TrailPolylineProps) {
  if (!isVisible) return null;

  const baseColor =
    trail.difficulty === 'double-black'
      ? '#ef4444'
      : DIFFICULTY_COLORS[trail.difficulty];

  return (
    <g
      onClick={onClick}
      onMouseEnter={() => onHover(trail.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {segments.map((segment, i) => {
        const points = segmentToPoints(segment);
        return (
          <g key={i}>
            {/* Invisible wide hit area for easy clicking/hovering */}
            <polyline
              points={points}
              fill="none"
              stroke="transparent"
              strokeWidth={3}
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Skied state: persistent thin gold line */}
            {isSkied && (
              <polyline
                points={points}
                fill="none"
                stroke="rgba(251, 191, 36, 0.5)"
                strokeWidth={0.8}
                strokeLinecap="round"
                strokeLinejoin="round"
                pointerEvents="none"
                style={{ transition: 'stroke-opacity 0.2s' }}
              />
            )}

            {/* Hover glow (soft wide line beneath the main highlight) */}
            {isHovered && (
              <polyline
                points={points}
                fill="none"
                stroke={baseColor}
                strokeWidth={2.0}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeOpacity={0.3}
                pointerEvents="none"
              />
            )}

            {/* Hover highlight: bold colored line */}
            {isHovered && (
              <polyline
                points={points}
                fill="none"
                stroke={baseColor}
                strokeWidth={1.2}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeOpacity={0.9}
                pointerEvents="none"
              />
            )}
          </g>
        );
      })}
    </g>
  );
}
