import { useState, useMemo } from 'react';
import { trails } from './data/trails';
import { useSkiedTrails } from './hooks/useSkiedTrails';
import { useTrailFilter } from './hooks/useTrailFilter';
import { FilterBar } from './components/FilterBar/FilterBar';
import { StatsPanel } from './components/StatsPanel/StatsPanel';
import { TrailList } from './components/TrailList/TrailList';
import { SchematicMap } from './components/SchematicMap/SchematicMap';
import { ImageMap } from './components/ImageMap/ImageMap';
import { MapToggle } from './components/MapToggle/MapToggle';
import type { MapView } from './components/MapToggle/MapToggle';
import styles from './App.module.css';

function App() {
  const { skiedTrails, toggle, reset } = useSkiedTrails();
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
  const [mapView, setMapView] = useState<MapView>('schematic');

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
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <MapToggle view={mapView} onChange={setMapView} />
          <button
            onClick={reset}
            style={{
              padding: '5px 14px',
              borderRadius: 6,
              border: '1px solid var(--border)',
              background: 'var(--bg-tertiary)',
              color: 'var(--text-secondary)',
              fontSize: 13,
            }}
          >
            Reset
          </button>
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
              hoveredTrail={hoveredTrail}
              onToggleTrail={toggle}
              onHoverTrail={setHoveredTrail}
            />
          )}
        </div>

        <aside className={styles.sidebar}>
          <StatsPanel trails={trails} skiedTrails={skiedTrails} />
          <TrailList
            trails={filteredTrails}
            skiedTrails={skiedTrails}
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
