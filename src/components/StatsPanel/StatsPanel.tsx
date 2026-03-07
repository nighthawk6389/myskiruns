import type { Trail, Difficulty } from '../../types';
import { DIFFICULTY_COLORS, DIFFICULTY_LABELS } from '../../types';
import styles from './StatsPanel.module.css';

interface StatsPanelProps {
  trails: Trail[];
  skiedTrails: Set<string>;
}

export function StatsPanel({ trails, skiedTrails }: StatsPanelProps) {
  const total = trails.length;
  const skied = trails.filter((t) => skiedTrails.has(t.id)).length;
  const pct = total > 0 ? Math.round((skied / total) * 100) : 0;

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
      <div className={styles.statsTitle}>Your Progress</div>
      <div className={styles.totalRow}>
        <span className={styles.totalCount}>{skied}</span>
        <span className={styles.totalLabel}>
          / {total} trails ({pct}%)
        </span>
      </div>
      <div className={styles.progressBarOuter}>
        <div
          className={styles.progressBarInner}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className={styles.breakdowns}>
        {byDifficulty.map(({ difficulty, total: t, skied: s }) => (
          <div key={difficulty} className={styles.breakdownItem}>
            <span
              className={styles.breakdownDot}
              style={{
                background:
                  difficulty === 'double-black'
                    ? '#ef4444'
                    : DIFFICULTY_COLORS[difficulty],
              }}
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
