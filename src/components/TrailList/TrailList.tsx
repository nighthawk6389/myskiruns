import type { Trail } from '../../types';
import { DIFFICULTY_COLORS, DIFFICULTY_ICONS } from '../../types';
import { peaks } from '../../data/trails';
import styles from './TrailList.module.css';

interface TrailListProps {
  trails: Trail[];
  skiedTrails: Set<string>;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onToggleTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
}

export function TrailList({
  trails,
  skiedTrails,
  searchQuery,
  onSearchChange,
  onToggleTrail,
  onHoverTrail,
}: TrailListProps) {
  const trailsByPeak = peaks.map((peak) => ({
    peak,
    trails: trails.filter((t) => t.peak === peak.id),
  })).filter((g) => g.trails.length > 0);

  return (
    <div className={styles.trailList}>
      <div className={styles.searchBox}>
        <input
          className={styles.searchInput}
          type="text"
          placeholder="Search trails..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      {trailsByPeak.length === 0 && (
        <div className={styles.emptyState}>No trails match your filters</div>
      )}
      {trailsByPeak.map(({ peak, trails: peakTrails }) => {
        const skiedCount = peakTrails.filter((t) => skiedTrails.has(t.id)).length;
        return (
          <div key={peak.id} className={styles.peakGroup}>
            <div className={styles.peakHeader}>
              <span className={styles.peakName}>
                {peak.name} ({peak.elevation.toLocaleString()} ft)
              </span>
              <span className={styles.peakCount}>
                {skiedCount}/{peakTrails.length}
              </span>
            </div>
            {peakTrails.map((trail) => {
              const isSkied = skiedTrails.has(trail.id);
              return (
                <div
                  key={trail.id}
                  className={`${styles.trailRow} ${isSkied ? styles.skied : ''}`}
                  onClick={() => onToggleTrail(trail.id)}
                  onMouseEnter={() => onHoverTrail(trail.id)}
                  onMouseLeave={() => onHoverTrail(null)}
                >
                  <span
                    className={styles.difficultyIcon}
                    style={{
                      color:
                        trail.difficulty === 'double-black'
                          ? '#ef4444'
                          : DIFFICULTY_COLORS[trail.difficulty],
                    }}
                  >
                    {DIFFICULTY_ICONS[trail.difficulty]}
                  </span>
                  <span className={styles.trailName}>{trail.name}</span>
                  <div className={styles.trailTags}>
                    {trail.isGlade && <span className={styles.tag}>Glade</span>}
                    {trail.isTerrainPark && <span className={styles.tag}>Park</span>}
                  </div>
                  {isSkied && <span className={styles.checkmark}>✓</span>}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
