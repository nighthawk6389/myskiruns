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
  const radius = isHovered ? 8 : 6;

  return (
    <g
      onClick={onClick}
      onMouseEnter={() => onHover(trail.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* Hit area */}
      <circle cx={x} cy={y} r={14} fill="transparent" />
      {/* Glow */}
      {isSkied && (
        <circle cx={x} cy={y} r={12} fill={color} opacity={0.25} />
      )}
      {/* Dot */}
      <circle
        cx={x}
        cy={y}
        r={radius}
        fill={color}
        stroke={isHovered ? '#fff' : 'rgba(0,0,0,0.5)'}
        strokeWidth={isHovered ? 2 : 1}
        style={{ transition: 'r 0.15s, fill 0.15s' }}
      />
      {isSkied && (
        <text
          x={x}
          y={y + 1}
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
