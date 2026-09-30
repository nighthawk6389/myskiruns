import { useState, useMemo, useRef } from 'react';
import { trails } from './data/trails';
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

function App() {
  const {
    trips,
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
  } = useTrips();
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
  const conditions = useConditions();
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
          <h1 className={styles.title}>Killington Trail Tracker</h1>
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
          trips={trips}
          onClose={() => setSummaryOpen(false)}
          onLocateTrail={(id) => mapRef.current?.focusTrail(id)}
        />
      )}
    </div>
  );
}

export default App;
