import { useEffect, useMemo, useRef, useState } from 'react';
import type { Trip } from '../../hooks/useTrips';
import { trails, peaks } from '../../data/trails';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS } from '../../types';
import { DIFFICULTY_ORDER, summarizeTrip, summaryText } from './summary';
import styles from './TripSummary.module.css';

interface TripSummaryProps {
  trip: Trip;
  trips: Trip[];
  onClose: () => void;
  /** show a trail on the map */
  onLocateTrail: (id: string) => void;
}

const dayLabel = (date: string) =>
  new Date(`${date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
const timeLabel = (d: Date) => d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });

/** Recap of one trip: totals, new trails, difficulty mix, progress by peak
 * and a day-by-day log, with a share/copy button. */
export function TripSummary({ trip, trips, onClose, onLocateTrail }: TripSummaryProps) {
  const s = useMemo(() => summarizeTrip(trip, trips, trails, peaks), [trip, trips]);
  const [shareStatus, setShareStatus] = useState('');
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const share = async () => {
    const text = summaryText(trip, s, trails.length);
    try {
      if (navigator.share) {
        await navigator.share({ title: trip.name, text });
        return;
      }
      await navigator.clipboard.writeText(text);
      setShareStatus('Copied to clipboard');
    } catch (err) {
      // the share sheet was dismissed; nothing to report
      if (err instanceof DOMException && err.name === 'AbortError') return;
      setShareStatus('Could not share');
    }
  };

  const total = s.trails.length;
  const newIds = new Set(s.newTrails.map((t) => t.id));

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="trip-summary-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className={styles.header}>
          <div>
            <h2 id="trip-summary-title" className={styles.title}>{trip.name}</h2>
            <div className={styles.subtitle}>
              {s.days.length
                ? `${dayLabel(s.days[0].date)}${s.days.length > 1 ? ` – ${dayLabel(s.days.at(-1)!.date)}` : ''}`
                : `Starts ${dayLabel(trip.startDate)}`}
            </div>
          </div>
          <button ref={closeRef} className={styles.close} onClick={onClose} aria-label="Close summary">
            ✕
          </button>
        </header>

        {total === 0 ? (
          <p className={styles.empty}>Nothing logged on this trip yet. Tap trails on the map to mark them skied.</p>
        ) : (
          <div className={styles.body}>
            <div className={styles.tiles}>
              <div className={styles.tile}>
                <span className={styles.big}>{total}</span>
                <span>trail{total === 1 ? '' : 's'} of {trails.length}</span>
              </div>
              <div className={styles.tile}>
                <span className={`${styles.big} ${styles.gold}`}>{s.newTrails.length}</span>
                <span>new to you</span>
              </div>
              <div className={styles.tile}>
                <span className={styles.big}>{s.days.length}</span>
                <span>day{s.days.length === 1 ? '' : 's'}</span>
              </div>
            </div>

            <section>
              <h3 className={styles.h3}>Difficulty mix</h3>
              <div className={styles.mixBar} role="img" aria-label={DIFFICULTY_ORDER.map((d) => `${DIFFICULTY_LABELS[d]} ${s.byDifficulty[d]}`).join(', ')}>
                {DIFFICULTY_ORDER.filter((d) => s.byDifficulty[d]).map((d) => (
                  <span key={d} style={{ flex: s.byDifficulty[d], background: DIFFICULTY_UI_COLORS[d] }} />
                ))}
              </div>
              <div className={styles.mixLegend}>
                {DIFFICULTY_ORDER.map((d) => (
                  <span key={d}>
                    <span style={{ color: DIFFICULTY_UI_COLORS[d] }}>{DIFFICULTY_ICONS[d]}</span> {DIFFICULTY_LABELS[d]}{' '}
                    <b>{s.byDifficulty[d]}</b>
                  </span>
                ))}
              </div>
              {s.hardest && (s.hardest.difficulty === 'black' || s.hardest.difficulty === 'double-black') && (
                <div className={styles.note}>
                  Toughest: {s.hardest.trails.map((t) => t.name).join(', ')}
                </div>
              )}
            </section>

            <section>
              <h3 className={styles.h3}>By peak</h3>
              {s.byPeak.map(({ peak, skied, total: t }) => (
                <div key={peak.id} className={styles.peakRow}>
                  <span className={styles.peakName}>{peak.name}</span>
                  <span className={styles.peakBar}>
                    <span style={{ width: `${(skied / t) * 100}%` }} />
                  </span>
                  <span className={styles.peakCount}>
                    {skied}/{t}
                  </span>
                </div>
              ))}
            </section>

            <section>
              <h3 className={styles.h3}>Day by day</h3>
              {s.days.map((day) => (
                <div key={day.date} className={styles.day}>
                  <div className={styles.dayHead}>
                    {dayLabel(day.date)} · {day.runs.length} trail{day.runs.length === 1 ? '' : 's'}
                  </div>
                  <ol className={styles.runs}>
                    {day.runs.map(({ trail, at }) => (
                      <li key={trail.id}>
                        <button
                          className={styles.run}
                          onClick={() => {
                            onClose();
                            onLocateTrail(trail.id);
                          }}
                          title="Show on map"
                        >
                          <span className={styles.time}>{timeLabel(at)}</span>
                          <span style={{ color: DIFFICULTY_UI_COLORS[trail.difficulty] }} className={styles.icon}>
                            {DIFFICULTY_ICONS[trail.difficulty]}
                          </span>
                          <span className={styles.runName}>{trail.name}</span>
                          {newIds.has(trail.id) && <span className={styles.newBadge}>New</span>}
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
              ))}
            </section>
          </div>
        )}

        {total > 0 && (
          <footer className={styles.footer}>
            {shareStatus && <span className={styles.shareStatus} role="status">{shareStatus}</span>}
            <button className={styles.share} onClick={share}>
              Share summary
            </button>
          </footer>
        )}
      </div>
    </div>
  );
}
