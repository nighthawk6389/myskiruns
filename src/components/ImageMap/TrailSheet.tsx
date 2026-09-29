import { useEffect, useRef } from 'react';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS } from '../../types';
import type { Conditions } from '../../hooks/useConditions';
import styles from './ImageMap.module.css';

export interface SheetTrail {
  trail: Trail;
  /** screen px from the tap */
  distance: number;
}

interface TrailSheetProps {
  candidates: SheetTrail[];
  skiedTrails: Set<string>;
  skiedEver: Set<string>;
  onMark: (trail: Trail) => void;
  onHover: (id: string | null) => void;
  onClose: () => void;
  conditions: Conditions;
}

/** Bottom sheet listing the trails under a tap, nearest first, each with a
 * large button to mark or unmark it on the current trip. */
export function TrailSheet({ candidates, skiedTrails, skiedEver, onMark, onHover, onClose, conditions }: TrailSheetProps) {
  // On touch screens the tap that opened the sheet is followed by a synthetic
  // click at the same spot; ignore input briefly so it can't hit a button.
  const armed = useRef(false);
  useEffect(() => {
    const t = setTimeout(() => {
      armed.current = true;
    }, 350);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className={styles.sheet} data-map-ui role="dialog" aria-label="Trails here">
      <div className={styles.sheetHeader}>
        <span>{candidates.length > 1 ? 'Which trail?' : 'Trail'}</span>
        <button className={styles.sheetClose} onClick={() => armed.current && onClose()} aria-label="Close">
          ✕
        </button>
      </div>
      {candidates.map(({ trail }) => {
        const skied = skiedTrails.has(trail.id);
        const color = DIFFICULTY_UI_COLORS[trail.difficulty];
        const counts = conditions.countsFor(trail.id);
        const mine = conditions.myVote(trail.id);
        return (
          <div
            key={trail.id}
            className={styles.sheetRow}
            onPointerEnter={() => onHover(trail.id)}
          >
            <div className={styles.sheetInfo}>
              <div className={styles.sheetName}>
                <span style={{ color, marginRight: 6 }}>{DIFFICULTY_ICONS[trail.difficulty]}</span>
                {trail.name}
              </div>
              <div className={styles.sheetMeta}>
                {DIFFICULTY_LABELS[trail.difficulty]}
                {trail.isGlade && ' · Glade'}
                {trail.isTerrainPark && ' · Park'}
                {skied ? ' · Skied this trip' : skiedEver.has(trail.id) ? ' · Skied on an earlier trip' : ''}
              </div>
              <div className={styles.conditions} role="group" aria-label={`Conditions on ${trail.name} today`}>
                <button
                  className={`${styles.thumb} ${mine === 1 ? styles.thumbUp : ''}`}
                  onClick={() => armed.current && conditions.vote(trail.id, 1)}
                  aria-pressed={mine === 1}
                  aria-label={`Good conditions (${counts.up})`}
                  title="Good conditions today"
                >
                  👍 <span>{counts.up}</span>
                </button>
                <button
                  className={`${styles.thumb} ${mine === -1 ? styles.thumbDown : ''}`}
                  onClick={() => armed.current && conditions.vote(trail.id, -1)}
                  aria-pressed={mine === -1}
                  aria-label={`Poor conditions (${counts.down})`}
                  title="Poor conditions today"
                >
                  👎 <span>{counts.down}</span>
                </button>
                <span className={styles.conditionsNote}>today</span>
              </div>
            </div>
            <button className={skied ? styles.sheetUndo : styles.sheetMark} onClick={() => armed.current && onMark(trail)}>
              {skied ? 'Remove' : 'Skied it'}
            </button>
          </div>
        );
      })}
      {conditions.mode === 'local' && (
        <div className={styles.sheetFootnote}>Condition votes are saved on this device only; sharing isn't set up yet.</div>
      )}
    </div>
  );
}
