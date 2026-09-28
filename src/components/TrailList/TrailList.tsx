import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS } from '../../types';
import { peaks } from '../../data/trails';
import styles from './TrailList.module.css';

interface TrailListProps {
  trails: Trail[];
  skiedTrails: Set<string>;
  skiedEver: Set<string>;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onToggleTrail: (id: string) => void;
  /** show the trail on the map */
  onLocateTrail: (id: string) => void;
  onHoverTrail: (id: string | null) => void;
  /** reset search, difficulty and skied filters */
  onClearFilters: () => void;
}

export function TrailList({
  trails,
  skiedTrails,
  skiedEver,
  searchQuery,
  onSearchChange,
  onToggleTrail,
  onLocateTrail,
  onHoverTrail,
  onClearFilters,
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
          type="search"
          placeholder="Search trails…"
          aria-label="Search trails"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {searchQuery && (
          <button className={styles.clearSearch} onClick={() => onSearchChange('')} aria-label="Clear search">
            ✕
          </button>
        )}
      </div>
      <div className={styles.scroll}>
        {trailsByPeak.length === 0 && (
          <div className={styles.emptyState}>
            No trails match your filters.
            <button className={styles.clearFilters} onClick={onClearFilters}>
              Show all trails
            </button>
          </div>
        )}
        {trailsByPeak.map(({ peak, trails: peakTrails }) => {
          const skiedCount = peakTrails.filter((t) => skiedTrails.has(t.id)).length;
          return (
            <section key={peak.id} className={styles.peakGroup} aria-label={peak.name}>
              <div className={styles.peakHeader}>
                <span className={styles.peakName}>
                  {peak.name} <span className={styles.peakElevation}>{peak.elevation.toLocaleString()} ft</span>
                </span>
                <span className={styles.peakCount}>
                  {skiedCount}/{peakTrails.length}
                </span>
              </div>
              {peakTrails.map((trail) => {
                const isSkied = skiedTrails.has(trail.id);
                const earlier = !isSkied && skiedEver.has(trail.id);
                return (
                  <div
                    key={trail.id}
                    className={`${styles.trailRow} ${isSkied ? styles.skied : ''}`}
                    onMouseEnter={() => onHoverTrail(trail.id)}
                    onMouseLeave={() => onHoverTrail(null)}
                  >
                    <button
                      className={styles.locate}
                      onClick={() => onLocateTrail(trail.id)}
                      title="Show on map"
                    >
                      <span
                        className={styles.difficultyIcon}
                        style={{ color: DIFFICULTY_UI_COLORS[trail.difficulty] }}
                        title={DIFFICULTY_LABELS[trail.difficulty]}
                      >
                        {DIFFICULTY_ICONS[trail.difficulty]}
                      </span>
                      <span className={styles.trailName}>{trail.name}</span>
                      {trail.isGlade && <span className={styles.tag}>Glade</span>}
                      {trail.isTerrainPark && <span className={styles.tag}>Park</span>}
                      {earlier && <span className={styles.earlier}>skied before</span>}
                    </button>
                    <button
                      className={`${styles.check} ${isSkied ? styles.checked : ''}`}
                      onClick={() => onToggleTrail(trail.id)}
                      role="checkbox"
                      aria-checked={isSkied}
                      aria-label={`Skied ${trail.name} this trip`}
                      title={isSkied ? 'Remove from this trip' : 'Mark skied this trip'}
                    >
                      {isSkied ? '✓' : ''}
                    </button>
                  </div>
                );
              })}
            </section>
          );
        })}
      </div>
    </div>
  );
}
