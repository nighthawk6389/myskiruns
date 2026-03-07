import type { PeakData } from '../../types';

interface PeakProps {
  peak: PeakData;
}

export function Peak({ peak }: PeakProps) {
  const { x, y, baseY, width } = peak;
  const halfW = width / 2;

  // Mountain silhouette polygon
  const points = [
    `${x},${y}`,
    `${x + halfW + 30},${baseY}`,
    `${x - halfW - 30},${baseY}`,
  ].join(' ');

  return (
    <g>
      <polygon
        points={points}
        fill="url(#mountainGradient)"
        opacity={0.35}
      />
      {/* Snow cap */}
      <polygon
        points={`${x},${y} ${x + halfW * 0.25},${y + (baseY - y) * 0.12} ${x - halfW * 0.25},${y + (baseY - y) * 0.12}`}
        fill="url(#snowGradient)"
        opacity={0.5}
      />
      {/* Peak label */}
      <text
        x={x}
        y={y - 12}
        textAnchor="middle"
        fill="#e2e8f0"
        fontSize="11"
        fontWeight="600"
        fontFamily="sans-serif"
      >
        {peak.name}
      </text>
      <text
        x={x}
        y={y - 1}
        textAnchor="middle"
        fill="#94a3b8"
        fontSize="9"
        fontFamily="sans-serif"
      >
        {peak.elevation.toLocaleString()}'
      </text>
    </g>
  );
}
