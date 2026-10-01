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

/** A trail's overlay: line segments and/or a label marker, in percent of the
 * map image (see scripts/applyTrailProposals.mjs). */
export interface TrailPath {
  segments: number[][][];
  label?: number[];
  source: string;
}

export interface Resort {
  id: string;
  name: string;
  /** trail map image under public/ */
  mapSrc: string;
  /** areas (peaks) in the order the trail list groups them */
  peaks: PeakData[];
  trails: Trail[];
  paths: Record<string, TrailPath>;
}

// To add a resort: put its data in src/data/resorts/<id>/ and its map in
// public/maps/<id>.jpg (docs/trail-map-playbook.md), then list it here.
export const RESORTS: Resort[] = [
  {
    id: 'killington',
    name: 'Killington',
    mapSrc: '/maps/killington.jpg',
    peaks: killington.peaks,
    trails: killington.trails,
    paths: (killingtonPaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'stowe',
    name: 'Stowe',
    mapSrc: '/maps/stowe.jpg',
    peaks: stowe.peaks,
    trails: stowe.trails,
    paths: (stowePaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'okemo',
    name: 'Okemo',
    mapSrc: '/maps/okemo.jpg',
    peaks: okemo.peaks,
    trails: okemo.trails,
    paths: (okemoPaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'sugarbush',
    name: 'Sugarbush',
    mapSrc: '/maps/sugarbush.jpg',
    peaks: sugarbush.peaks,
    trails: sugarbush.trails,
    paths: (sugarbushPaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'jay-peak',
    name: 'Jay Peak',
    mapSrc: '/maps/jay-peak.jpg',
    peaks: jayPeak.peaks,
    trails: jayPeak.trails,
    paths: (jayPeakPaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'whiteface',
    name: 'Whiteface',
    mapSrc: '/maps/whiteface.jpg',
    peaks: whiteface.peaks,
    trails: whiteface.trails,
    paths: (whitefacePaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'winter-park',
    name: 'Winter Park',
    mapSrc: '/maps/winter-park.jpg',
    peaks: winterPark.peaks,
    trails: winterPark.trails,
    paths: (winterParkPaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'breckenridge',
    name: 'Breckenridge',
    mapSrc: '/maps/breckenridge.jpg',
    peaks: breckenridge.peaks,
    trails: breckenridge.trails,
    paths: (breckenridgePaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'copper-mountain',
    name: 'Copper Mountain',
    mapSrc: '/maps/copper-mountain.jpg',
    peaks: copperMountain.peaks,
    trails: copperMountain.trails,
    paths: (copperMountainPaths as { trails: Record<string, TrailPath> }).trails,
  },
  {
    id: 'keystone',
    name: 'Keystone',
    mapSrc: '/maps/keystone.jpg',
    peaks: keystone.peaks,
    trails: keystone.trails,
    paths: (keystonePaths as { trails: Record<string, TrailPath> }).trails,
  },
];

export const DEFAULT_RESORT = RESORTS[0];

export function getResort(id: string | null | undefined): Resort {
  return RESORTS.find((r) => r.id === id) ?? DEFAULT_RESORT;
}
