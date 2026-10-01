import type { PeakData, Trail } from './types';
import * as killington from './data/resorts/killington/trails';
import killingtonPaths from './data/resorts/killington/trailPaths.json';
import * as stowe from './data/resorts/stowe/trails';
import stowePaths from './data/resorts/stowe/trailPaths.json';
import * as okemo from './data/resorts/okemo/trails';
import okemoPaths from './data/resorts/okemo/trailPaths.json';
import * as sugarbush from './data/resorts/sugarbush/trails';
import sugarbushPaths from './data/resorts/sugarbush/trailPaths.json';
import * as jayPeak from './data/resorts/jay-peak/trails';
import jayPeakPaths from './data/resorts/jay-peak/trailPaths.json';
import * as whiteface from './data/resorts/whiteface/trails';
import whitefacePaths from './data/resorts/whiteface/trailPaths.json';
import * as winterPark from './data/resorts/winter-park/trails';
import winterParkPaths from './data/resorts/winter-park/trailPaths.json';
import * as breckenridge from './data/resorts/breckenridge/trails';
import breckenridgePaths from './data/resorts/breckenridge/trailPaths.json';
import * as copperMountain from './data/resorts/copper-mountain/trails';
import copperMountainPaths from './data/resorts/copper-mountain/trailPaths.json';
import * as keystone from './data/resorts/keystone/trails';
import keystonePaths from './data/resorts/keystone/trailPaths.json';
import * as vail from './data/resorts/vail/trails';
import vailFrontSidePaths from './data/resorts/vail/panels/front-side/trailPaths.json';
import vailBackBowlsPaths from './data/resorts/vail/panels/back-bowls/trailPaths.json';
import vailBlueSkyPaths from './data/resorts/vail/panels/blue-sky/trailPaths.json';

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

const pathsOf = (doc: unknown) => (doc as { trails: Record<string, TrailPath> }).trails;

/** A resort drawn on a single map image. */
const oneMap = (mapSrc: string, paths: unknown): MapPanel[] => [{ id: 'map', name: 'Trail map', mapSrc, paths: pathsOf(paths) }];

// To add a resort: put its data in src/data/resorts/<id>/ and its map in
// public/maps/<id>.jpg (docs/trail-map-playbook.md), then list it here. A
// resort drawn on several panels keeps one trail list and, per panel, its
// overlays in src/data/resorts/<id>/panels/<panel>/ and its map in
// public/maps/<id>-<panel>.jpg.
export const RESORTS: Resort[] = [
  {
    id: 'killington',
    name: 'Killington',
    maps: oneMap('/maps/killington.jpg', killingtonPaths),
    peaks: killington.peaks,
    trails: killington.trails,
  },
  {
    id: 'stowe',
    name: 'Stowe',
    maps: oneMap('/maps/stowe.jpg', stowePaths),
    peaks: stowe.peaks,
    trails: stowe.trails,
  },
  {
    id: 'okemo',
    name: 'Okemo',
    maps: oneMap('/maps/okemo.jpg', okemoPaths),
    peaks: okemo.peaks,
    trails: okemo.trails,
  },
  {
    id: 'sugarbush',
    name: 'Sugarbush',
    maps: oneMap('/maps/sugarbush.jpg', sugarbushPaths),
    peaks: sugarbush.peaks,
    trails: sugarbush.trails,
  },
  {
    id: 'jay-peak',
    name: 'Jay Peak',
    maps: oneMap('/maps/jay-peak.jpg', jayPeakPaths),
    peaks: jayPeak.peaks,
    trails: jayPeak.trails,
  },
  {
    id: 'whiteface',
    name: 'Whiteface',
    maps: oneMap('/maps/whiteface.jpg', whitefacePaths),
    peaks: whiteface.peaks,
    trails: whiteface.trails,
  },
  {
    id: 'winter-park',
    name: 'Winter Park',
    maps: oneMap('/maps/winter-park.jpg', winterParkPaths),
    peaks: winterPark.peaks,
    trails: winterPark.trails,
  },
  {
    id: 'breckenridge',
    name: 'Breckenridge',
    maps: oneMap('/maps/breckenridge.jpg', breckenridgePaths),
    peaks: breckenridge.peaks,
    trails: breckenridge.trails,
  },
  {
    id: 'copper-mountain',
    name: 'Copper Mountain',
    maps: oneMap('/maps/copper-mountain.jpg', copperMountainPaths),
    peaks: copperMountain.peaks,
    trails: copperMountain.trails,
  },
  {
    id: 'keystone',
    name: 'Keystone',
    maps: oneMap('/maps/keystone.jpg', keystonePaths),
    peaks: keystone.peaks,
    trails: keystone.trails,
  },
  {
    id: 'vail',
    name: 'Vail',
    maps: [
      { id: 'front-side', name: 'Front Side', mapSrc: '/maps/vail-front-side.jpg', paths: pathsOf(vailFrontSidePaths) },
      { id: 'back-bowls', name: 'Back Bowls', mapSrc: '/maps/vail-back-bowls.jpg', paths: pathsOf(vailBackBowlsPaths) },
      { id: 'blue-sky', name: 'Blue Sky Basin', mapSrc: '/maps/vail-blue-sky.jpg', paths: pathsOf(vailBlueSkyPaths) },
    ],
    peaks: vail.peaks,
    trails: vail.trails,
  },
];

export const DEFAULT_RESORT = RESORTS[0];

export function getResort(id: string | null | undefined): Resort {
  return RESORTS.find((r) => r.id === id) ?? DEFAULT_RESORT;
}
