import type { Trail } from '../../types';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailPolylineProps {
  trail: Trail;
  svgPath: string;
  isSkied: boolean;
  isHovered: boolean;
  isVisible: boolean;
  onClick: () => void;
  onHover: (id: string | null) => void;
}

export function TrailPolyline({
  trail,
  svgPath,
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
  const strokeColor = isSkied ? '#fbbf24' : baseColor;
  const strokeWidth = isHovered ? 0.8 : isSkied ? 0.6 : 0.4;
  const opacity = isSkied ? 1 : 0.85;

  return (
    <g
      onClick={onClick}
      onMouseEnter={() => onHover(trail.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* Wider invisible hit area for easier clicking */}
      <path
        d={svgPath}
        fill="none"
        stroke="transparent"
        strokeWidth={2}
        strokeLinecap="round"
      />
      {/* Glow effect for skied trails */}
      {isSkied && (
        <path
          d={svgPath}
          fill="none"
          stroke="#fbbf24"
          strokeWidth={1.2}
          strokeLinecap="round"
          opacity={0.3}
        />
      )}
      {/* Trail line */}
      <path
        d={svgPath}
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={trail.isGlade ? '1 0.8' : undefined}
        opacity={opacity}
        style={{ transition: 'stroke-width 0.15s, stroke 0.15s' }}
      />
      {/* Double-black diamond markers */}
      {trail.difficulty === 'double-black' && !isSkied && (
        <path
          d={svgPath}
          fill="none"
          stroke={baseColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray="0.3 1.5"
          opacity={0.5}
        />
      )}
    </g>
  );
}
