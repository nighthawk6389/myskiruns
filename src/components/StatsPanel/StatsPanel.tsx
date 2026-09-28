import type { Trail, Difficulty } from '../../types';
import { DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS } from '../../types';
import styles from './StatsPanel.module.css';

interface StatsPanelProps {
  trails: Trail[];
  skiedTrails: Set<string>;
  skiedEver: Set<string>;
  tripName: string | null;
}

export function StatsPanel({ trails, skiedTrails, skiedEver, tripName }: StatsPanelProps) {
  const total = trails.length;
  const skied = trails.filter((t) => skiedTrails.has(t.id)).length;
  const pct = total > 0 ? Math.round((skied / total) * 100) : 0;
  const ever = trails.filter((t) => skiedEver.has(t.id)).length;

  const byDifficulty = (['green', 'blue', 'black', 'double-black'] as Difficulty[]).map(
    (d) => {
      const ofDifficulty = trails.filter((t) => t.difficulty === d);
      const skiedOfDifficulty = ofDifficulty.filter((t) => skiedTrails.has(t.id));
      return {
        difficulty: d,
        total: ofDifficulty.length,
        skied: skiedOfDifficulty.length,
      };
    }
  );

  return (
    <div className={styles.stats}>
      <div className={styles.statsTitle}>{tripName ?? 'This trip'}</div>
      <div className={styles.totalRow}>
        <span className={styles.totalCount}>{skied}</span>
        <span className={styles.totalLabel}>
          / {total} trails ({pct}%)
        </span>
      </div>
      <div
        className={styles.progressBarOuter}
        role="progressbar"
        aria-label="Trails skied this trip"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={skied}
      >
        <div
          className={styles.progressBarInner}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className={styles.lifetime}>
        All trips: <strong>{ever}</strong> of {total} trails skied
      </div>
      <div className={styles.breakdowns}>
        {byDifficulty.map(({ difficulty, total: t, skied: s }) => (
          <div key={difficulty} className={styles.breakdownItem} title={`${DIFFICULTY_LABELS[difficulty]}: ${s} of ${t} this trip`}>
            <span
              className={styles.breakdownDot}
              style={{ background: DIFFICULTY_UI_COLORS[difficulty] }}
            />
            <span className={styles.breakdownLabel}>
              {DIFFICULTY_LABELS[difficulty]}
            </span>
            <span className={styles.breakdownCount}>
              {s}/{t}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
