import { useState, useMemo } from 'react';
import { trails } from './data/trails';
import { useTrips } from './hooks/useTrips';
import { useTrailFilter } from './hooks/useTrailFilter';
import { FilterBar } from './components/FilterBar/FilterBar';
import { StatsPanel } from './components/StatsPanel/StatsPanel';
import { TrailList } from './components/TrailList/TrailList';
import { SchematicMap } from './components/SchematicMap/SchematicMap';
import { ImageMap } from './components/ImageMap/ImageMap';
import { MapToggle } from './components/MapToggle/MapToggle';
import { TripBar } from './components/TripBar/TripBar';
import type { MapView } from './components/MapToggle/MapToggle';
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
    setFilterMode,
    setSearchQuery,
  } = useTrailFilter(trails, skiedTrails);

  const [hoveredTrail, setHoveredTrail] = useState<string | null>(null);
  const [mapView, setMapView] = useState<MapView>('image');

  const filteredTrailIds = useMemo(
    () => new Set(filteredTrails.map((t) => t.id)),
    [filteredTrails]
  );

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo}>⛷</span>
          <div>
            <div className={styles.title}>
              Killington Trail Tracker
              <span className={styles.subtitle}> — My Ski Runs</span>
            </div>
          </div>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.viewToggle}>
            <MapToggle view={mapView} onChange={setMapView} />
          </div>
          <TripBar
            trips={trips}
            activeTrip={activeTrip}
            onSelect={selectTrip}
            onCreate={createTrip}
            onUpdate={updateTrip}
            onDelete={deleteTrip}
            onExport={exportJson}
            onImport={importJson}
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
          {mapView === 'schematic' ? (
            <SchematicMap
              filteredTrailIds={filteredTrailIds}
              skiedTrails={skiedTrails}
              hoveredTrail={hoveredTrail}
              onToggleTrail={toggle}
              onHoverTrail={setHoveredTrail}
            />
          ) : (
            <ImageMap
              filteredTrailIds={filteredTrailIds}
              skiedTrails={skiedTrails}
              skiedEver={skiedEver}
              hoveredTrail={hoveredTrail}
              onToggleTrail={toggle}
              onHoverTrail={setHoveredTrail}
            />
          )}
        </div>

        <aside className={styles.sidebar}>
          <StatsPanel
            trails={trails}
            skiedTrails={skiedTrails}
            skiedEver={skiedEver}
            tripName={activeTrip?.name ?? null}
          />
          <TrailList
            trails={filteredTrails}
            skiedTrails={skiedTrails}
            skiedEver={skiedEver}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onToggleTrail={toggle}
            onHoverTrail={setHoveredTrail}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
