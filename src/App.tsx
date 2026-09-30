import { useState, useMemo, useRef } from 'react';
import { RESORTS, getResort, type Resort } from './resorts';
import { useTrips } from './hooks/useTrips';
import { useTrailFilter } from './hooks/useTrailFilter';
import { useConditions } from './hooks/useConditions';
import { FilterBar } from './components/FilterBar/FilterBar';
import { StatsPanel } from './components/StatsPanel/StatsPanel';
import { TrailList } from './components/TrailList/TrailList';
import { ImageMap, type ImageMapHandle } from './components/ImageMap/ImageMap';
import { TripBar } from './components/TripBar/TripBar';
import { TripSummary } from './components/TripSummary/TripSummary';
import styles from './App.module.css';

const RESORT_KEY = 'myskiruns.resort';

/** The resort from ?resort=<id>, else the last one used on this device. */
function initialResort(): Resort {
  const fromUrl = new URLSearchParams(location.search).get('resort');
  try {
    return getResort(fromUrl ?? localStorage.getItem(RESORT_KEY));
  } catch {
    return getResort(fromUrl);
  }
}

function App() {
  const [resort, setResort] = useState(initialResort);
  const chooseResort = (id: string) => {
    const next = getResort(id);
    setResort(next);
    try {
      localStorage.setItem(RESORT_KEY, next.id);
    } catch {
      // private mode: the choice lasts this session
    }
  };
  // everything below is per resort: remounting resets map view, filters,
  // conditions and the trip in view
  return <ResortApp key={resort.id} resort={resort} onChooseResort={chooseResort} />;
}

function ResortApp({ resort, onChooseResort }: { resort: Resort; onChooseResort: (id: string) => void }) {
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

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo}>⛷</span>
          {RESORTS.length > 1 ? (
            <select
              className={styles.resortSelect}
              value={resort.id}
              onChange={(e) => onChooseResort(e.target.value)}
              aria-label="Resort"
            >
              {RESORTS.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          ) : (
            <h1 className={styles.title}>{resort.name} Trail Tracker</h1>
          )}
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
