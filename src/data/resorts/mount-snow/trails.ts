import type { Trail, PeakData } from '../../../types';

// Mount Snow's 2025-26 trail map: this season's image (Vail Resorts' CDN;
// the resort's own PDF is the same page flattened at 72 dpi), its lines from
// the 2023-24 trail map PDF's run strokes (skimap.org map 24777) and its
// names from the 2024-25 uphill-access map's text (map 36693), two older
// exports of the same artwork registered on this season's image. The
// Sunbrook area behind the summit is drawn only in the map's inset (top
// left): its lines are the inset's own strokes, its names read on crops.
// Names are spelled as the resort's terrain report spells them (report.json:
// the lift-and-terrain-status page's feed in Common Crawl's capture of
// 2025-12-14); ratings are the colour each name is printed in (the map
// prints no symbol by a name), Ripcord's its double diamond. Two differ from
// the report: Low Traverse is printed blue (the report: green), and Ledge,
// listed twice (blue and black), is printed black above and blue below: one
// trail, rated the harder. The parks are rated blue. Lines are named by the
// name printed along them or settled on crops (decisions.py). Printed with
// no line (markers at their names): Shootout, Tramline, Short Fuse and Under
// Pressure (glades and open slopes), and the Grommet, Junkyard and Launch
// Pad parks. Area elevations: the summit as printed (3,600 ft), Carinthia's
// the top of the Nitro Express (OpenStreetMap's lift line on the USGS's 10 m
// elevation model; tools/trailmap/lift_tops.py). x/y/baseY/width are unused
// layout fields.
export const peaks: PeakData[] = [
  { id: 'main-face', name: 'Main Face', elevation: 3600, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'north-face', name: 'North Face', elevation: 3600, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'sunbrook', name: 'Sunbrook', elevation: 3600, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'carinthia', name: 'Carinthia', elevation: 2962, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'beaver-hill', name: 'Beaver Hill', difficulty: 'green', peak: 'main-face' },
  { id: 'canyon', name: 'Canyon', difficulty: 'blue', peak: 'main-face' },
  { id: 'cascade', name: 'Cascade', difficulty: 'blue', peak: 'main-face' },
  { id: 'charlies-chase', name: "Charlie's Chase", difficulty: 'blue', peak: 'main-face' },
  { id: 'choke', name: 'Choke', difficulty: 'blue', peak: 'main-face' },
  { id: 'committed', name: 'Committed', difficulty: 'blue', peak: 'main-face' },
  { id: 'coopers-junction', name: "Cooper's Junction", difficulty: 'green', peak: 'main-face' },
  { id: 'cut-off', name: 'Cut-Off', difficulty: 'blue', peak: 'main-face' },
  { id: 'deer-run', name: 'Deer Run', difficulty: 'green', peak: 'main-face' },
  { id: 'drifter', name: 'Drifter', difficulty: 'blue', peak: 'main-face' },
  { id: 'drop', name: 'Drop', difficulty: 'blue', peak: 'main-face' },
  { id: 'ego-alley', name: 'Ego Alley', difficulty: 'blue', peak: 'main-face' },
  { id: 'high-traverse', name: 'High Traverse', difficulty: 'blue', peak: 'main-face' },
  { id: 'hop', name: 'Hop', difficulty: 'blue', peak: 'main-face' },
  { id: 'illusion', name: 'Illusion', difficulty: 'blue', peak: 'main-face' },
  { id: 'launch-pad', name: 'Launch Pad', difficulty: 'green', peak: 'main-face' },
  { id: 'ledge', name: 'Ledge', difficulty: 'black', peak: 'main-face' },
  { id: 'link', name: 'Link', difficulty: 'blue', peak: 'main-face' },
  { id: 'little-john', name: 'Little John', difficulty: 'blue', peak: 'main-face' },
  { id: 'lodge', name: 'Lodge', difficulty: 'blue', peak: 'main-face' },
  { id: 'long-john', name: 'Long John', difficulty: 'green', peak: 'main-face' },
  { id: 'low-traverse', name: 'Low Traverse', difficulty: 'blue', peak: 'main-face' },
  { id: 'lower-exhibition', name: 'Lower Exhibition', difficulty: 'blue', peak: 'main-face' },
  { id: 'n-e-time', name: 'N.E. Time', difficulty: 'green', peak: 'main-face' },
  { id: 'one-more-time', name: 'One More Time', difficulty: 'blue', peak: 'main-face' },
  { id: 'overbrook', name: 'Overbrook', difficulty: 'blue', peak: 'main-face' },
  { id: 'pats-pitch', name: "Pat's Pitch", difficulty: 'black', peak: 'main-face' },
  { id: 'ridge', name: 'Ridge', difficulty: 'blue', peak: 'main-face' },
  { id: 'roller-coaster', name: 'Roller Coaster', difficulty: 'blue', peak: 'main-face' },
  { id: 'sap-bucket', name: 'Sap Bucket', difficulty: 'blue', peak: 'main-face' },
  { id: 'seasons-pass', name: 'Seasons Pass', difficulty: 'green', peak: 'main-face' },
  { id: 'shootout', name: 'Shootout', difficulty: 'blue', peak: 'main-face' },
  { id: 'short-fuse', name: 'Short Fuse', difficulty: 'blue', peak: 'main-face' },
  { id: 'snowdance', name: 'Snowdance', difficulty: 'green', peak: 'main-face' },
  { id: 'snowdance-pitch', name: 'Snowdance Pitch', difficulty: 'blue', peak: 'main-face' },
  { id: 'somerset-road', name: 'Somerset Road', difficulty: 'green', peak: 'main-face' },
  { id: 'south-bowl', name: 'South Bowl', difficulty: 'blue', peak: 'main-face' },
  { id: 'sweet-sixteen', name: 'Sweet Sixteen', difficulty: 'green', peak: 'main-face' },
  { id: 'switchback', name: 'Switchback', difficulty: 'green', peak: 'main-face' },
  { id: 'tin-lizzy', name: 'Tin Lizzy', difficulty: 'green', peak: 'main-face' },
  { id: 'tramline', name: 'Tramline', difficulty: 'blue', peak: 'main-face' },
  { id: 'uncles', name: 'Uncles', difficulty: 'blue', peak: 'main-face' },
  { id: 'under-pressure', name: 'Under Pressure', difficulty: 'blue', peak: 'main-face' },
  { id: 'upper-exhibition', name: 'Upper Exhibition', difficulty: 'blue', peak: 'main-face' },
  { id: 'yard-sale', name: 'Yard Sale', difficulty: 'black', peak: 'main-face' },
  { id: 'boulder-pile', name: 'Boulder Pile', difficulty: 'black', peak: 'north-face' },
  { id: 'challenger', name: 'Challenger', difficulty: 'black', peak: 'north-face' },
  { id: 'chute', name: 'Chute', difficulty: 'black', peak: 'north-face' },
  { id: 'fallen-timbers', name: 'Fallen Timbers', difficulty: 'black', peak: 'north-face' },
  { id: 'free-fall', name: 'Free Fall', difficulty: 'black', peak: 'north-face' },
  { id: 'jaws', name: 'Jaws', difficulty: 'black', peak: 'north-face' },
  { id: 'little-steep', name: 'Little Steep', difficulty: 'black', peak: 'north-face' },
  { id: 'olympic', name: 'Olympic', difficulty: 'black', peak: 'north-face' },
  { id: 'pdf', name: 'PDF', difficulty: 'black', peak: 'north-face' },
  { id: 'plummet', name: 'Plummet', difficulty: 'black', peak: 'north-face' },
  { id: 'ripcord', name: 'Ripcord', difficulty: 'double-black', peak: 'north-face' },
  { id: 'river-run', name: 'River Run', difficulty: 'blue', peak: 'north-face' },
  { id: 'second-thoughts', name: 'Second Thoughts', difficulty: 'blue', peak: 'north-face' },
  { id: 'skyline', name: 'Skyline', difficulty: 'blue', peak: 'north-face' },
  { id: 'bear-paw', name: 'Bear Paw', difficulty: 'green', peak: 'sunbrook' },
  { id: 'bear-trap', name: 'Bear Trap', difficulty: 'black', peak: 'sunbrook' },
  { id: 'big-dipper', name: 'Big Dipper', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'cloud-nine', name: 'Cloud Nine', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'little-dipper', name: 'Little Dipper', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'milky-way', name: 'Milky Way', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'moonbeam', name: 'Moonbeam', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'moonwalk', name: 'Moonwalk', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'one-small-step', name: 'One Small Step', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'shooting-star', name: 'Shooting Star', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'sunspot', name: 'Sunspot', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'thanks-walt', name: 'Thanks Walt', difficulty: 'blue', peak: 'sunbrook' },
  { id: 'grommet', name: 'Grommet', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'inferno', name: 'Inferno', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'iron-run', name: 'Iron Run', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'junkyard', name: 'Junkyard', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'lower-fools-gold', name: "Lower Fool's Gold", difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'mineshaft', name: 'Mineshaft', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'narrow-gauge', name: 'Narrow Gauge', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'nitro', name: 'Nitro', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'prospector', name: 'Prospector', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'rusty-nail', name: 'Rusty Nail', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'the-farm', name: 'The Farm', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'the-gulch', name: 'The Gulch', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'tunnel-vision', name: 'Tunnel Vision', difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
  { id: 'upper-fools-gold', name: "Upper Fool's Gold", difficulty: 'blue', peak: 'carinthia', isTerrainPark: true },
];
