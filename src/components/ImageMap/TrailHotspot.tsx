import type { Trail } from '../../types';
import { DIFFICULTY_COLORS } from '../../types';

interface TrailHotspotProps {
  trail: Trail;
  /** position in overlay viewBox units */
  x: number;
  y: number;
  /** screen pixels per viewBox unit at the current zoom */
  pxPerUnit: number;
  /** 0.5–1: smaller markers when the map is drawn small (phones) */
  weight: number;
  isSkied: boolean;
  isHovered: boolean;
  isVisible: boolean;
  onHover: (id: string | null) => void;
}

// Sizes in screen pixels; converted to viewBox units so the marker keeps its
// on-screen size at every zoom level.
const R_DOT = 4.5;
const R_DOT_HOVER = 6.5;
const R_HIT = 12;
const R_GLOW = 8;

export function TrailHotspot({ trail, x, y, pxPerUnit, weight, isSkied, isHovered, isVisible, onHover }: TrailHotspotProps) {
  if (!isVisible) return null;

  const u = weight / pxPerUnit;
  const baseColor = trail.difficulty === 'double-black' ? '#ef4444' : DIFFICULTY_COLORS[trail.difficulty];
  const color = isSkied ? '#fbbf24' : baseColor;
  const radius = (isHovered ? R_DOT_HOVER : R_DOT) * u;

  return (
    <g onMouseEnter={() => onHover(trail.id)} onMouseLeave={() => onHover(null)} style={{ cursor: 'pointer' }}>
      <circle cx={x} cy={y} r={R_HIT * u} fill="transparent" />
      {isSkied && <circle cx={x} cy={y} r={R_GLOW * u} fill={color} opacity={0.3} />}
      <circle
        cx={x}
        cy={y}
        r={radius}
        fill={color}
        stroke={isHovered ? '#fff' : 'rgba(255,255,255,0.85)'}
        strokeWidth={(isHovered ? 2 : 1.2) * u}
      />
      {isSkied && (
        <text
          x={x}
          y={y + 0.5 * u}
          textAnchor="middle"
          dominantBaseline="central"
          fill="#000"
          fontSize={7 * u}
          fontWeight="bold"
        >
          ✓
        </text>
      )}
    </g>
  );
}
