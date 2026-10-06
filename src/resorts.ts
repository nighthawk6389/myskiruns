import type { PeakData, Trail } from './types';

/** A trail's overlay: line segments and/or a label marker, in percent of the
 * map image (see scripts/applyTrailProposals.mjs). */
export interface TrailPath {
  segments: number[][][];
  label?: number[];
  source: string;
}

/** One trail map image and the overlays drawn on it. */
export interface MapPanel {
  id: string;
  /** shown on the panel switcher when a resort has several panels */
  name: string;
  /** trail map image under public/ */
  mapSrc: string;
  paths: Record<string, TrailPath>;
}

export interface Resort {
  id: string;
  name: string;
  /** the trail map: one image, or several panels (Vail: Front Side, Back
   * Bowls, Blue Sky Basin), each with its own overlays; a trail may be drawn
   * on more than one */
  maps: MapPanel[];
  /** areas (peaks) in the order the trail list groups them */
  peaks: PeakData[];
  trails: Trail[];
}

/** A resort in the picker. Its trail list and overlays load when it is
 * opened: each resort's data is its own chunk (vite.config.ts), so a visit
 * downloads the resorts it opens, not all of them. */
export interface ResortEntry {
  id: string;
  name: string;
  load: () => Promise<Resort>;
}

type TrailsModule = { peaks: PeakData[]; trails: Trail[] };
type PathsModule = { default: unknown };

const pathsOf = (doc: PathsModule) => (doc.default as { trails: Record<string, TrailPath> }).trails;

/** A resort drawn on a single map image, public/maps/<id>.jpg. */
function oneMap(
  id: string,
  name: string,
  trails: () => Promise<TrailsModule>,
  paths: () => Promise<PathsModule>,
): ResortEntry {
  return {
    id,
    name,
    load: async () => {
      const [t, p] = await Promise.all([trails(), paths()]);
      const maps = [{ id: 'map', name: 'Trail map', mapSrc: `/maps/${id}.jpg`, paths: pathsOf(p) }];
      return { id, name, maps, peaks: t.peaks, trails: t.trails };
    },
  };
}

// To add a resort: put its data in src/data/resorts/<id>/ and its map in
// public/maps/<id>.jpg (docs/trail-map-playbook.md), then list it here. A
// resort drawn on several panels keeps one trail list and, per panel, its
// overlays in src/data/resorts/<id>/panels/<panel>/ and its map in
// public/maps/<id>-<panel>.jpg.
export const RESORTS: ResortEntry[] = [
  oneMap('killington', 'Killington', () => import('./data/resorts/killington/trails'), () => import('./data/resorts/killington/trailPaths.json')),
  oneMap('stowe', 'Stowe', () => import('./data/resorts/stowe/trails'), () => import('./data/resorts/stowe/trailPaths.json')),
  oneMap('okemo', 'Okemo', () => import('./data/resorts/okemo/trails'), () => import('./data/resorts/okemo/trailPaths.json')),
  oneMap('sugarbush', 'Sugarbush', () => import('./data/resorts/sugarbush/trails'), () => import('./data/resorts/sugarbush/trailPaths.json')),
  oneMap('jay-peak', 'Jay Peak', () => import('./data/resorts/jay-peak/trails'), () => import('./data/resorts/jay-peak/trailPaths.json')),
  oneMap('whiteface', 'Whiteface', () => import('./data/resorts/whiteface/trails'), () => import('./data/resorts/whiteface/trailPaths.json')),
  oneMap('winter-park', 'Winter Park', () => import('./data/resorts/winter-park/trails'), () => import('./data/resorts/winter-park/trailPaths.json')),
  oneMap('breckenridge', 'Breckenridge', () => import('./data/resorts/breckenridge/trails'), () => import('./data/resorts/breckenridge/trailPaths.json')),
  oneMap('copper-mountain', 'Copper Mountain', () => import('./data/resorts/copper-mountain/trails'), () => import('./data/resorts/copper-mountain/trailPaths.json')),
  oneMap('keystone', 'Keystone', () => import('./data/resorts/keystone/trails'), () => import('./data/resorts/keystone/trailPaths.json')),
  {
    id: 'vail',
    name: 'Vail',
    load: async () => {
      const [t, frontSide, backBowls, blueSky] = await Promise.all([
        import('./data/resorts/vail/trails'),
        import('./data/resorts/vail/panels/front-side/trailPaths.json'),
        import('./data/resorts/vail/panels/back-bowls/trailPaths.json'),
        import('./data/resorts/vail/panels/blue-sky/trailPaths.json'),
      ]);
      return {
        id: 'vail',
        name: 'Vail',
        maps: [
          { id: 'front-side', name: 'Front Side', mapSrc: '/maps/vail-front-side.jpg', paths: pathsOf(frontSide) },
          { id: 'back-bowls', name: 'Back Bowls', mapSrc: '/maps/vail-back-bowls.jpg', paths: pathsOf(backBowls) },
          { id: 'blue-sky', name: 'Blue Sky Basin', mapSrc: '/maps/vail-blue-sky.jpg', paths: pathsOf(blueSky) },
        ],
        peaks: t.peaks,
        trails: t.trails,
      };
    },
  },
  oneMap('hunter', 'Hunter Mountain', () => import('./data/resorts/hunter/trails'), () => import('./data/resorts/hunter/trailPaths.json')),
  oneMap('wildcat', 'Wildcat Mountain', () => import('./data/resorts/wildcat/trails'), () => import('./data/resorts/wildcat/trailPaths.json')),
  oneMap('sunday-river', 'Sunday River', () => import('./data/resorts/sunday-river/trails'), () => import('./data/resorts/sunday-river/trailPaths.json')),
  oneMap('sugarloaf', 'Sugarloaf', () => import('./data/resorts/sugarloaf/trails'), () => import('./data/resorts/sugarloaf/trailPaths.json')),
];

export const DEFAULT_RESORT = RESORTS[0];

export function resortEntry(id: string | null | undefined): ResortEntry {
  return RESORTS.find((r) => r.id === id) ?? DEFAULT_RESORT;
}

const loaded = new Map<string, Promise<Resort>>();

/** A resort's data, loaded once (React's use() needs the same promise on
 * every render). */
export function loadResort(id: string): Promise<Resort> {
  let p = loaded.get(id);
  if (!p) {
    p = resortEntry(id).load();
    loaded.set(id, p);
  }
  return p;
}
