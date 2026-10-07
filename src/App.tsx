import { Component, Suspense, use, useDeferredValue, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { RESORTS, loadResort, resortEntry, type Resort } from './resorts';
import { useTrips } from './hooks/useTrips';
import { useTrailFilter } from './hooks/useTrailFilter';
import { useConditions } from './hooks/useConditions';
import { FilterBar } from './components/FilterBar/FilterBar';
import { StatsPanel } from './components/StatsPanel/StatsPanel';
import { TrailList } from './components/TrailList/TrailList';
import { ImageMap, type ImageMapHandle } from './components/ImageMap/ImageMap';
import { TripBar } from './components/TripBar/TripBar';
import { TripSummary } from './components/TripSummary/TripSummary';
import { ResortPicker } from './components/ResortPicker/ResortPicker';
import styles from './App.module.css';

const RESORT_KEY = 'myskiruns.resort';

/** The resort from ?resort=<id>, else the last one used on this device. */
function initialResortId(): string {
  const fromUrl = new URLSearchParams(location.search).get('resort');
  let saved: string | null = null;
  try {
    saved = localStorage.getItem(RESORT_KEY);
  } catch {
    // storage blocked: the URL or the default
  }
  return resortEntry(fromUrl ?? saved).id;
}

function App() {
  const [resortId, setResortId] = useState(initialResortId);
  // the resort on screen: while the next one's data loads, the current one stays
  const shownId = useDeferredValue(resortId);
  const chooseResort = (id: string) => {
    const next = resortEntry(id).id;
    setResortId(next);
    try {
      localStorage.setItem(RESORT_KEY, next);
    } catch {
      // private mode: the choice lasts this session
    }
  };
  const picker = <Picker value={resortId} onChange={chooseResort} busy={resortId !== shownId} />;
  return (
    <Suspense fallback={<Splash picker={picker}>Loading {resortEntry(shownId).name}…</Splash>}>
      <LoadError key={shownId} resortId={shownId} picker={picker}>
        <LoadedResort id={shownId} picker={picker} />
      </LoadError>
    </Suspense>
  );
}

function LoadedResort({ id, picker }: { id: string; picker: ReactNode }) {
  const resort = use(loadResort(id));
  // everything below is per resort: remounting resets map view, filters,
  // conditions and the trip in view
  return <ResortApp key={resort.id} resort={resort} picker={picker} />;
}

function Picker({ value, onChange, busy }: { value: string; onChange: (id: string) => void; busy: boolean }) {
  if (RESORTS.length < 2) return <h1 className={styles.title}>{resortEntry(value).name} Trail Tracker</h1>;
  return <ResortPicker resorts={RESORTS} value={value} onChange={onChange} busy={busy} />;
}

/** The header and a message, while a resort loads or when it can't. */
function Splash({ picker, children }: { picker: ReactNode; children: ReactNode }) {
  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo}>⛷</span>
          {picker}
        </div>
      </header>
      <div className={styles.splash}>{children}</div>
    </div>
  );
}

/** Reload the page on a resort: the browser remembers a failed script load for
 * as long as the page is open, so trying again in place would fail again. */
function reopen(resortId: string) {
  const url = new URL(location.href);
  url.searchParams.set('resort', resortId);
  url.searchParams.delete('panel');
  location.assign(url);
}

/** A resort's data that couldn't be loaded: offline, and the resort was never
 * opened on this device (its data is cached once it has been). */
class LoadError extends Component<
  { resortId: string; picker: ReactNode; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <Splash picker={this.props.picker}>
        <p>
          Couldn&apos;t load {resortEntry(this.props.resortId).name}: it needs a connection the first time it&apos;s
          opened.
        </p>
        <button className={styles.retry} onClick={() => reopen(this.props.resortId)}>
          Try again
        </button>
      </Splash>
    );
  }
}

function ResortApp({ resort, picker }: { resort: Resort; picker: ReactNode }) {
  const { trails } = resort;
  const {
    trips,
    allTrips,
    activeTrip,
    skiedThisTrip: skiedTrails,
    skiedEver,
    createTrip,
    selectTrip,
    updateTrip,
    deleteTrip,
    toggleRun: toggle,
    exportJson,
    importJson,
  } = useTrips(resort.id, resort.name);
  const {
    activeDifficulties,
    filterMode,
    searchQuery,
    filteredTrails,
    toggleDifficulty,
    setAllDifficulties,
    setFilterMode,
    setSearchQuery,
  } = useTrailFilter(trails, skiedTrails);

  const [hoveredTrail, setHoveredTrail] = useState<string | null>(null);
  const mapRef = useRef<ImageMapHandle>(null);
  const conditions = useConditions(resort.id);
  const [summaryOpen, setSummaryOpen] = useState(false);

  const filteredTrailIds = useMemo(
    () => new Set(filteredTrails.map((t) => t.id)),
    [filteredTrails]
  );

  // the tab names the resort's map: searches (and ads) for "<resort> trail
  // map" land on ?resort=<id>
  useEffect(() => {
    document.title = `${resort.name} Trail Map · My Ski Runs`;
  }, [resort.name]);

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo}>⛷</span>
          {picker}
        </div>
        <div className={styles.headerRight}>
          <TripBar
            trips={trips}
            activeTrip={activeTrip}
            onSelect={selectTrip}
            onCreate={createTrip}
            onUpdate={updateTrip}
            onDelete={deleteTrip}
            onExport={exportJson}
            onImport={importJson}
            onSummary={() => setSummaryOpen(true)}
          />
        </div>
      </header>

      <FilterBar
        activeDifficulties={activeDifficulties}
        filterMode={filterMode}
        onToggleDifficulty={toggleDifficulty}
        onSetFilterMode={setFilterMode}
      />

      <div className={styles.main}>
        <div className={styles.mapArea}>
          <ImageMap
            ref={mapRef}
            resort={resort}
            filteredTrailIds={filteredTrailIds}
            skiedTrails={skiedTrails}
            skiedEver={skiedEver}
            hoveredTrail={hoveredTrail}
            onToggleTrail={toggle}
            onHoverTrail={setHoveredTrail}
            showHint={skiedTrails.size === 0}
            conditions={conditions}
          />
          <p className={styles.credit}>My Ski Runs is an independent app, not affiliated with {resort.name}.</p>
        </div>

        <aside className={styles.sidebar}>
          <StatsPanel
            trails={trails}
            skiedTrails={skiedTrails}
            skiedEver={skiedEver}
            tripName={activeTrip?.name ?? null}
            onOpenSummary={activeTrip ? () => setSummaryOpen(true) : undefined}
          />
          <TrailList
            trails={filteredTrails}
            peaks={resort.peaks}
            skiedTrails={skiedTrails}
            skiedEver={skiedEver}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onToggleTrail={toggle}
            onLocateTrail={(id) => mapRef.current?.focusTrail(id)}
            onHoverTrail={setHoveredTrail}
            onClearFilters={() => {
              setAllDifficulties();
              setFilterMode('all');
              setSearchQuery('');
            }}
            conditions={conditions}
          />
        </aside>
      </div>

      {summaryOpen && activeTrip && (
        <TripSummary
          trip={activeTrip}
          trips={allTrips}
          resort={resort}
          onClose={() => setSummaryOpen(false)}
          onLocateTrail={(id) => mapRef.current?.focusTrail(id)}
        />
      )}
    </div>
  );
}

export default App;
