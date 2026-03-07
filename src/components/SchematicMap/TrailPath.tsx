import type { Trail } from '../../types';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailPathProps {
  trail: Trail;
  path: string;
  isSkied: boolean;
  isHovered: boolean;
  isVisible: boolean;
  onClick: () => void;
  onHover: (id: string | null) => void;
}

export function TrailPath({
  trail,
  path,
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
  const strokeColor = isSkied ? '#fbbf24' : baseColor;
  const strokeWidth = isHovered ? 5 : isSkied ? 4 : 3;
  const opacity = isSkied ? 1 : 0.8;

  return (
    <g
      onClick={onClick}
      onMouseEnter={() => onHover(trail.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* Wider invisible hit area for easier clicking */}
      <path
        d={path}
        fill="none"
        stroke="transparent"
        strokeWidth={14}
        strokeLinecap="round"
      />
      {/* Glow effect for skied trails */}
      {isSkied && (
        <path
          d={path}
          fill="none"
          stroke="#fbbf24"
          strokeWidth={8}
          strokeLinecap="round"
          opacity={0.3}
          filter="url(#glow)"
        />
      )}
      {/* Trail line */}
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={trail.isGlade ? '6 4' : undefined}
        opacity={opacity}
        style={{ transition: 'stroke-width 0.15s, stroke 0.15s' }}
      />
      {/* Double-black diamond markers */}
      {trail.difficulty === 'double-black' && !isSkied && (
        <path
          d={path}
          fill="none"
          stroke={baseColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray="2 10"
          opacity={0.5}
        />
      )}
    </g>
  );
}
