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
import { RecapView } from './components/RecapView/RecapView';
import { decodeRecap } from './recap/link';
import { track } from './analytics';
import { reportMark } from './marks';
import styles from './App.module.css';

const RESORT_KEY = 'myskiruns.resort';
// index.html's title: the site's, for the home page (search engines index it as the site, not as a resort)
const SITE_TITLE = document.title;
// the address names a resort (an ad, a search result, a shared link): its tab is titled by it
const RESORT_IN_URL = new URLSearchParams(location.search).has('resort');

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
  // someone's shared day (?recap=), shown read-only until the visitor moves on
  const [recapPayload, setRecapPayload] = useState(() => new URLSearchParams(location.search).get('recap'));
  // a trail to show once its resort is on screen: picked in the search across
  // resorts, or ?trail=<id> in the URL (n: picked again, show it again)
  const [focus, setFocus] = useState<Focus | null>(() => {
    const trailId = new URLSearchParams(location.search).get('trail');
    return trailId ? { resortId: initialResortId(), trailId, n: 0 } : null;
  });
  // the resort on screen: while the next one's data loads, the current one stays
  const shownId = useDeferredValue(resortId);
  const leaveRecap = () => {
    if (!recapPayload) return;
    setRecapPayload(null);
    const url = new URL(location.href);
    url.searchParams.delete('recap');
    history.replaceState(history.state, '', url);
  };
  // the tab is titled by the resort once the address named one or the visitor picked one
  const [titled, setTitled] = useState(RESORT_IN_URL);
  const chooseResort = (id: string, trailId?: string) => {
    leaveRecap();
    setTitled(true);
    const next = resortEntry(id).id;
    setResortId(next);
    if (trailId) {
      track('Trail found', { resort: next });
      setFocus((f) => ({ resortId: next, trailId, n: (f?.n ?? 0) + 1 }));
    }
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
        <LoadedResort
          id={shownId}
          picker={picker}
          recapPayload={recapPayload}
          onLeaveRecap={() => chooseResort(shownId)}
          focus={focus?.resortId === shownId ? focus : null}
          titled={titled}
        />
      </LoadError>
    </Suspense>
  );
}

interface Focus {
  resortId: string;
  trailId: string;
  n: number;
}

function LoadedResort({
  id,
  picker,
  recapPayload,
  onLeaveRecap,
  focus,
  titled,
}: {
  id: string;
  picker: ReactNode;
  recapPayload: string | null;
  onLeaveRecap: () => void;
  focus: Focus | null;
  titled: boolean;
}) {
  const resort = use(loadResort(id));
  const recap = useMemo(
    () => (recapPayload ? decodeRecap(recapPayload, resort.trails.map((t) => t.id)) : null),
    [recapPayload, resort.trails],
  );
  if (recap) return <RecapView key={`recap-${resort.id}`} resort={resort} recap={recap} onExit={onLeaveRecap} />;
  // everything below is per resort: remounting resets map view, filters,
  // conditions and the trip in view
  return <ResortApp key={resort.id} resort={resort} picker={picker} focus={focus} titled={titled} />;
}

function Picker({
  value,
  onChange,
  busy,
}: {
  value: string;
  onChange: (id: string, trailId?: string) => void;
  busy: boolean;
}) {
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

function ResortApp({
  resort,
  picker,
  focus,
  titled,
}: {
  resort: Resort;
  picker: ReactNode;
  focus: Focus | null;
  titled: boolean;
}) {
  const { trails } = resort;
  const {
    trips,
    allTrips,
    activeTrip,
    skiedThisTrip: skiedTrails,
    skiedEver,
    createTrip: newTrip,
    selectTrip,
    updateTrip,
    deleteTrip,
    toggleRun,
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
  const toggle = (id: string) => {
    const marking = !skiedTrails.has(id);
    if (marking) track('Run marked', { resort: resort.id });
    reportMark(resort.id, id, marking);
    toggleRun(id);
  };
  const createTrip: typeof newTrip = (...args) => {
    track('Trip created', { resort: resort.id });
    return newTrip(...args);
  };
  const openSummary = () => {
    track('Summary opened', { resort: resort.id });
    setSummaryOpen(true);
  };

  useEffect(() => track('Resort opened', { resort: resort.id }), [resort.id]);

  // a trail found by the search across resorts: zoom to it and open its sheet
  const focusTrailId = focus?.trailId;
  const focusN = focus?.n;
  useEffect(() => {
    if (focusTrailId) mapRef.current?.focusTrail(focusTrailId);
  }, [focusTrailId, focusN]);

  const filteredTrailIds = useMemo(
    () => new Set(filteredTrails.map((t) => t.id)),
    [filteredTrails]
  );

  // the tab names the resort's map: searches (and ads) for "<resort> trail
  // map" land on ?resort=<id>. The home page keeps the site's title, though
  // it opens on a resort (the last one used, else the first): a search engine
  // indexes it as the site, not as Killington.
  useEffect(() => {
    document.title = titled ? `${resort.name} Trail Map · My Ski Runs` : SITE_TITLE;
  }, [resort.name, titled]);

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
            onSummary={openSummary}
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
            onOpenSummary={activeTrip ? openSummary : undefined}
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
