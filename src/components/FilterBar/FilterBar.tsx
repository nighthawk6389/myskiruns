import type { Difficulty } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS } from '../../types';
import type { FilterMode } from '../../hooks/useTrailFilter';
import styles from './FilterBar.module.css';

interface FilterBarProps {
  activeDifficulties: Set<Difficulty>;
  filterMode: FilterMode;
  onToggleDifficulty: (d: Difficulty) => void;
  onSetFilterMode: (m: FilterMode) => void;
}

const difficulties: { key: Difficulty; className: string }[] = [
  { key: 'green', className: styles.green },
  { key: 'blue', className: styles.blue },
  { key: 'black', className: styles.black },
  { key: 'double-black', className: styles.doubleBlack },
];

export function FilterBar({
  activeDifficulties,
  filterMode,
  onToggleDifficulty,
  onSetFilterMode,
}: FilterBarProps) {
  return (
    <div className={styles.filterBar}>
      <div className={styles.filterGroup}>
        {difficulties.map(({ key, className }) => (
          <button
            key={key}
            className={`${styles.filterBtn} ${className} ${activeDifficulties.has(key) ? styles.active : ''}`}
            onClick={() => onToggleDifficulty(key)}
          >
            <span className={styles.icon}>{DIFFICULTY_ICONS[key]}</span>
            {DIFFICULTY_LABELS[key]}
          </button>
        ))}
      </div>
      <div className={styles.separator} />
      <div className={styles.filterGroup}>
        <button
          className={`${styles.modeBtn} ${filterMode === 'all' ? styles.active : ''}`}
          onClick={() => onSetFilterMode('all')}
        >
          All
        </button>
        <button
          className={`${styles.modeBtn} ${filterMode === 'skied' ? styles.active : ''}`}
          onClick={() => onSetFilterMode('skied')}
        >
          Skied
        </button>
        <button
          className={`${styles.modeBtn} ${filterMode === 'not-skied' ? styles.active : ''}`}
          onClick={() => onSetFilterMode('not-skied')}
        >
          Not Skied
        </button>
      </div>
    </div>
  );
}
