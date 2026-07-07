import type { Trail } from '../../types';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailHotspotProps {
  trail: Trail;
  x: number;
  y: number;
  isSkied: boolean;
  isHovered: boolean;
  isVisible: boolean;
  onClick: () => void;
  onHover: (id: string | null) => void;
}

// The overlay viewBox is 1000 units wide (height follows the image's true
// aspect), so 1 unit ≈ 0.1% of the map width. Sizes below are chosen so a
// dot renders ~12px in diameter on a ~1100px-wide map.
const R_DOT = 5.5;
const R_DOT_HOVER = 8;
const R_HIT = 16;
const R_GLOW = 10;

export function TrailHotspot({
  trail,
  x,
  y,
  isSkied,
  isHovered,
  isVisible,
  onClick,
  onHover,
}: TrailHotspotProps) {
  if (!isVisible) return null;

  const baseColor =
    trail.difficulty === 'double-black'
      ? '#ef4444'
      : DIFFICULTY_COLORS[trail.difficulty];
  const color = isSkied ? '#fbbf24' : baseColor;
  const radius = isHovered ? R_DOT_HOVER : R_DOT;

  return (
    <g
      onClick={onClick}
      onMouseEnter={() => onHover(trail.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* Hit area */}
      <circle cx={x} cy={y} r={R_HIT} fill="transparent" />
      {/* Glow */}
      {isSkied && (
        <circle cx={x} cy={y} r={R_GLOW} fill={color} opacity={0.3} />
      )}
      {/* Dot */}
      <circle
        cx={x}
        cy={y}
        r={radius}
        fill={color}
        stroke={isHovered ? '#fff' : 'rgba(255,255,255,0.85)'}
        strokeWidth={isHovered ? 2 : 1.2}
        style={{ transition: 'r 0.15s, fill 0.15s' }}
      />
      {isSkied && (
        <text
          x={x}
          y={y + 0.5}
          textAnchor="middle"
          dominantBaseline="central"
          fill="#000"
          fontSize="8"
          fontWeight="bold"
        >
          ✓
        </text>
      )}
    </g>
  );
}
