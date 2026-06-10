// Approximate image-space regions (percent of the full trail-map image) where
// each peak's runs appear. Calibrated by reading the peak labels off
// public/killington-trail-map.jpg. cx/cy are the box centre, w/h its full
// width/height — all in [0,100].
//
// NOTE: this map is drawn in perspective, not the usual left-to-right schematic
// (e.g. Bear Mountain is on the skier's left here). Regions overlap and are
// intentionally generous; they exist to anchor each peak's hotspots onto the
// right part of the mountain. Detection then snaps individual hotspots onto
// actual run pixels within the region.
export interface PeakRegion {
  cx: number;
  cy: number;
  w: number;
  h: number;
}

export const PEAK_REGIONS: Record<string, PeakRegion> = {
  'sunrise': { cx: 18, cy: 60, w: 18, h: 36 },
  'bear-mountain': { cx: 25, cy: 38, w: 16, h: 26 },
  'skye-peak': { cx: 41, cy: 44, w: 16, h: 32 },
  'killington-peak': { cx: 55, cy: 30, w: 18, h: 36 },
  'snowdon': { cx: 79, cy: 35, w: 16, h: 30 },
  'ramshead': { cx: 92, cy: 42, w: 11, h: 26 },
  'snowshed': { cx: 63, cy: 61, w: 24, h: 22 },
};
