import type { PeakData, Trail } from './types';
import * as killington from './data/resorts/killington/trails';
import killingtonPaths from './data/resorts/killington/trailPaths.json';
import * as stowe from './data/resorts/stowe/trails';
import stowePaths from './data/resorts/stowe/trailPaths.json';

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
];

export const DEFAULT_RESORT = RESORTS[0];

export function getResort(id: string | null | undefined): Resort {
  return RESORTS.find((r) => r.id === id) ?? DEFAULT_RESORT;
}
