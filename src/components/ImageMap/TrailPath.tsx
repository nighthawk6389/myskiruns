import type { Trail } from '../../types';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailPathProps {
  trail: Trail;
  /** polyline in overlay viewBox units */
  points: string;
  isSkied: boolean;
  isHovered: boolean;
  isVisible: boolean;
  onClick: () => void;
  onHover: (id: string | null) => void;
}

// Stroke widths in overlay units (viewBox is 1000 wide → 1 unit ≈ 0.1% of
// the map width). The hit stroke is generous so the whole run is clickable.
const W_HIT = 14;
const W_LINE = 3.2;
const W_LINE_HOVER = 5.5;

export function TrailPath({
  trail,
  points,
  isSkied,
  isHovered,
  isVisible,
  onClick,
  onHover,
}: TrailPathProps) {
  if (!isVisible) return null;

  const baseColor =
    trail.difficulty === 'double-black'
      ? '#ef4444'
      : DIFFICULTY_COLORS[trail.difficulty];
  const color = isSkied ? '#fbbf24' : baseColor;

  return (
    <g
      onClick={onClick}
      onMouseEnter={() => onHover(trail.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* invisible wide hit stroke — makes the whole run clickable */}
      <polyline
        points={points}
        fill="none"
        stroke="transparent"
        strokeWidth={W_HIT}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* white casing for contrast against the busy map */}
      <polyline
        points={points}
        fill="none"
        stroke="#fff"
        strokeOpacity={isHovered ? 0.95 : isSkied ? 0.8 : 0.55}
        strokeWidth={(isHovered ? W_LINE_HOVER : W_LINE) + 2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeOpacity={isHovered ? 1 : isSkied ? 0.95 : 0.8}
        strokeWidth={isHovered ? W_LINE_HOVER : W_LINE}
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ transition: 'stroke 0.15s, stroke-opacity 0.15s' }}
      />
    </g>
  );
}
