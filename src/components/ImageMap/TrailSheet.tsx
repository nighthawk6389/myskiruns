import { useEffect, useRef, useState } from 'react';
import type { Trail } from '../../types';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS } from '../../types';
import type { Conditions } from '../../hooks/useConditions';
import { CONDITION_TAGS, MAX_TAGS, topTags } from '../../conditionTags';
import type { ReportKind } from '../../reports';
import { ReportForm } from './ReportForm';
import styles from './ImageMap.module.css';

/** the report form for a trail missing from the map, not one in the list */
const MISSING = '\u0000missing';

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
  /** a shared day: the trail's name and rating only */
  readOnly?: boolean;
  /** sends "Something wrong?" for a trail (null: one missing from the map here) */
  onReport?: (trailId: string | null, kind: ReportKind, note: string) => Promise<boolean>;
}

/** Bottom sheet listing the trails under a tap, nearest first, each with a
 * large button to mark or unmark it on the current trip. */
export function TrailSheet({
  candidates,
  skiedTrails,
  skiedEver,
  onMark,
  onHover,
  onClose,
  conditions,
  readOnly = false,
  onReport,
}: TrailSheetProps) {
  // the trail whose report form is open, or MISSING for the sheet's own,
  // until another tap lists other trails
  const shown = candidates.map((c) => c.trail.id).join(' ');
  const [open, setOpen] = useState<{ shown: string; id: string } | null>(null);
  const reporting = open?.shown === shown ? open.id : null;
  const setReporting = (id: string | null) => setOpen(id === null ? null : { shown, id });
  const canReport = !readOnly && !!onReport;

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
        const myTags = conditions.myTags(trail.id);
        const reported = topTags(counts.tags);
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
                {readOnly
                  ? skied && ' · Skied that day'
                  : skied
                    ? ' · Skied this trip'
                    : skiedEver.has(trail.id)
                      ? ' · Skied on an earlier trip'
                      : ''}
              </div>
              {!readOnly && (
                <>
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
                  {reported.length > 0 && (
                    <div className={styles.tagSummary}>
                      {reported.map(({ tag, count }) => (
                        <span key={tag.key}>
                          {tag.emoji} {tag.label}
                          {count > 1 && <b> {count}</b>}
                        </span>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
            {!readOnly && (
              <button className={skied ? styles.sheetUndo : styles.sheetMark} onClick={() => armed.current && onMark(trail)}>
                {skied ? 'Remove' : 'Skied it'}
              </button>
            )}
            {!readOnly && (mine || myTags.length > 0) && (
              <div className={styles.tagPicker} role="group" aria-label={`What's ${trail.name} like? Pick up to ${MAX_TAGS}`}>
                <span className={styles.tagPrompt}>What's it like?</span>
                {CONDITION_TAGS.map((tag) => {
                  const on = myTags.includes(tag.key);
                  return (
                    <button
                      key={tag.key}
                      className={`${styles.tagChip} ${on ? (tag.good === false ? styles.tagBad : tag.good ? styles.tagGood : styles.tagOn) : ''}`}
                      onClick={() => armed.current && conditions.toggleTag(trail.id, tag.key)}
                      aria-pressed={on}
                    >
                      {tag.emoji} {tag.label}
                    </button>
                  );
                })}
              </div>
            )}
            {canReport &&
              (reporting === trail.id ? (
                <ReportForm
                  subject={trail.name}
                  onSend={(kind, note) => onReport(trail.id, kind, note)}
                  onClose={() => setReporting(null)}
                />
              ) : (
                <button className={styles.reportLink} onClick={() => armed.current && setReporting(trail.id)}>
                  Something wrong with {candidates.length > 1 ? 'this trail' : trail.name}?
                </button>
              ))}
          </div>
        );
      })}
      {canReport &&
        (reporting === MISSING ? (
          <ReportForm
            subject="a trail missing from the map"
            missing
            onSend={(kind, note) => onReport(null, kind, note)}
            onClose={() => setReporting(null)}
          />
        ) : (
          <button className={`${styles.reportLink} ${styles.reportMissing}`} onClick={() => armed.current && setReporting(MISSING)}>
            A trail here is missing from the map?
          </button>
        ))}
      {!readOnly && conditions.mode === 'local' && (
        <div className={styles.sheetFootnote}>Condition votes are saved on this device only; sharing isn't set up yet.</div>
      )}
    </div>
  );
}
