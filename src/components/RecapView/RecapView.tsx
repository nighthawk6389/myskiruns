import { useEffect, useMemo, useRef, useState } from 'react';
import type { Resort } from '../../resorts';
import type { Recap } from '../../recap/link';
import { bestPanel } from '../../recap/card';
import { DIFFICULTY_ICONS, DIFFICULTY_LABELS, DIFFICULTY_UI_COLORS, type Difficulty, type Trail } from '../../types';
import { ImageMap, type ImageMapHandle } from '../ImageMap/ImageMap';
import { useConditions } from '../../hooks/useConditions';
import { track } from '../../analytics';
import appStyles from '../../App.module.css';
import styles from './RecapView.module.css';

const ORDER: Difficulty[] = ['green', 'blue', 'black', 'double-black'];
const NONE = new Set<string>();

const dayLabel = (date: string) =>
  new Date(`${date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });

interface RecapViewProps {
  resort: Resort;
  recap: Recap;
  /** leave the shared day for the app itself, at this resort */
  onExit: () => void;
}

/** Someone's shared day (?recap=): their runs on the resort's map, read-only,
 * with the day's numbers and a way into the app. Nothing here touches this
 * device's own trips. */
export function RecapView({ resort, recap, onExit }: RecapViewProps) {
  const mapRef = useRef<ImageMapHandle>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const conditions = useConditions(resort.id);
  const skied = useMemo(() => new Set(recap.trailIds), [recap.trailIds]);
  const trails = useMemo(() => {
    const byId = new Map(resort.trails.map((t) => [t.id, t]));
    return recap.trailIds
      .map((id) => byId.get(id))
      .filter((t): t is Trail => !!t)
      .sort((a, b) => ORDER.indexOf(a.difficulty) - ORDER.indexOf(b.difficulty) || a.name.localeCompare(b.name));
  }, [resort.trails, recap.trailIds]);
  const counts = Object.fromEntries(ORDER.map((d) => [d, trails.filter((t) => t.difficulty === d).length])) as Record<
    Difficulty,
    number
  >;
  const total = resort.trails.length;
  const pct = total ? Math.round((trails.length / total) * 100) : 0;
  const firstPanel = bestPanel(resort, recap.trailIds).id;

  useEffect(() => track('Recap viewed', { resort: resort.id, runs: recap.trailIds.length }), [resort.id, recap.trailIds.length]);

  useEffect(() => {
    document.title = `${recap.name || 'A ski day'} at ${resort.name} · My Ski Runs`;
  }, [recap.name, resort.name]);

  return (
    <div className={appStyles.app}>
      <header className={`${appStyles.header} ${styles.header}`}>
        <div className={styles.brand}>
          <span className={appStyles.logo}>⛷</span>
          <span>My Ski Runs</span>
        </div>
        <button
          className={styles.cta}
          onClick={() => {
            track('Recap: track your own', { resort: resort.id });
            onExit();
          }}
        >
          Track your own runs
        </button>
      </header>

      <div className={appStyles.main}>
        <div className={appStyles.mapArea}>
          <ImageMap
            ref={mapRef}
            resort={resort}
            filteredTrailIds={skied}
            skiedTrails={skied}
            skiedEver={NONE}
            hoveredTrail={hovered}
            onToggleTrail={() => {}}
            onHoverTrail={setHovered}
            showHint={false}
            conditions={conditions}
            readOnly
            firstPanel={firstPanel}
          />
          <p className={appStyles.credit}>My Ski Runs is an independent app, not affiliated with {resort.name}.</p>
        </div>

        <aside className={`${appStyles.sidebar} ${styles.sidebar}`}>
          <section className={styles.summary} aria-labelledby="recap-title">
            <div className={styles.kicker}>A day at {resort.name}</div>
            <h1 id="recap-title" className={styles.title}>
              {recap.name || 'Ski day'}
            </h1>
            <div className={styles.dates}>
              {dayLabel(recap.start)}
              {recap.days > 1 && ` · ${recap.days} days`}
            </div>
            <div className={styles.tiles}>
              <div className={styles.tile}>
                <b>{trails.length}</b>
                <span>run{trails.length === 1 ? '' : 's'}</span>
              </div>
              <div className={styles.tile}>
                <b className={styles.gold}>{recap.newCount}</b>
                <span>new to them</span>
              </div>
              <div className={styles.tile}>
                <b>{pct}%</b>
                <span>of {total} trails</span>
              </div>
            </div>
            <div
              className={styles.mixBar}
              role="img"
              aria-label={ORDER.map((d) => `${DIFFICULTY_LABELS[d]} ${counts[d]}`).join(', ')}
            >
              {ORDER.filter((d) => counts[d]).map((d) => (
                <span key={d} style={{ flex: counts[d], background: DIFFICULTY_UI_COLORS[d] }} />
              ))}
            </div>
            <p className={styles.pitch}>
              Mark the runs you ski on {resort.name}&apos;s trail map, see what&apos;s left, and share your day. Free, no
              app to download.
            </p>
          </section>

          <ol className={styles.runs} aria-label="Runs skied">
            {trails.map((t) => (
              <li key={t.id}>
                <button
                  className={styles.run}
                  onClick={() => mapRef.current?.focusTrail(t.id)}
                  onPointerEnter={() => setHovered(t.id)}
                  onPointerLeave={() => setHovered(null)}
                  title="Show on map"
                >
                  <span style={{ color: DIFFICULTY_UI_COLORS[t.difficulty] }} className={styles.icon}>
                    {DIFFICULTY_ICONS[t.difficulty]}
                  </span>
                  <span className={styles.name}>{t.name}</span>
                </button>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </div>
  );
}
