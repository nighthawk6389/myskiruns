import type { Trail, PeakData } from '../../../types';

// Snowshoe Mountain's 2025-26 trail map (snowshoemtn.com's maps page: an
// image only, James Niehues's painting of Snowshoe Basin and Silver Creek,
// the Western Territory an inset on the right). The lines and names are its
// interactive map's (resorts-interactive.com map 1814), whose SVG is this
// map's vector layer drawn again, every trail's line, letters and symbol
// grouped under its name; registered on the image in two parts (the main map,
// the Western Territory inset) and each line routed onto the print's own
// (Silver Creek's lie some 5 px off). Names are spelled as the resort's trail
// report spells them (report.json); ratings are the printed symbols (Lower
// Shay's Revenge's two squares double black; Knot Bumper Glades' one diamond
// black, the report has it double black). The terrain parks and the glades,
// in no group of the interactive map, are markers at their printed names
// (the parks blue), as are Shamrock and Grab Hook. Little Spruce runs from its
// square down to Fox Chase's (the interactive map's Fox Chase); Cant Hook,
// Cut-off, Moonshine, Tail Tree, Upper Whistlepunk, Lower Ballhooter and
// Stemwinder, whose interactive-map lines are stubs or none, follow their
// names printed on their lines. Not on this map: the report's Cubb Run Ext.
// Areas: the report's (Snowshoe, Silver Creek).
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'snowshoe', name: 'Snowshoe', elevation: 4768, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'silver-creek', name: 'Silver Creek', elevation: 4820, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'black-bear', name: 'Black Bear', difficulty: 'green', peak: 'snowshoe' },
  { id: 'camp-4', name: 'Camp 4', difficulty: 'green', peak: 'snowshoe' },
  { id: 'camp-99', name: 'Camp 99', difficulty: 'black', peak: 'snowshoe' },
  { id: 'choker', name: 'Choker', difficulty: 'black', peak: 'snowshoe' },
  { id: 'cross-cut', name: 'Cross Cut', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'cut-off', name: 'Cut Off', difficulty: 'green', peak: 'snowshoe' },
  { id: 'evolution-park', name: 'Evolution Park', difficulty: 'blue', peak: 'snowshoe', isTerrainPark: true },
  { id: 'gandy-dancer', name: 'Gandy Dancer', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'gangway', name: 'Gangway', difficulty: 'green', peak: 'snowshoe' },
  { id: 'grab-hook', name: 'Grab Hook', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'grabhammer', name: 'Grabhammer', difficulty: 'black', peak: 'snowshoe' },
  { id: 'heisler-way', name: 'Heisler Way', difficulty: 'green', peak: 'snowshoe' },
  { id: 'j-hook', name: 'J-hook', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'knot-bumper', name: 'Knot Bumper', difficulty: 'black', peak: 'snowshoe' },
  { id: 'knot-bumper-glades', name: 'Knot Bumper Glades', difficulty: 'black', peak: 'snowshoe', isGlade: true },
  { id: 'log-slide', name: 'Log Slide', difficulty: 'green', peak: 'snowshoe' },
  { id: 'lower-ballhooter', name: 'Lower Ballhooter', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'lower-cupp-run', name: 'Lower Cupp Run', difficulty: 'black', peak: 'snowshoe' },
  { id: 'lower-flume', name: 'Lower Flume', difficulty: 'green', peak: 'snowshoe' },
  { id: 'lower-hootenanny', name: 'Lower Hootenanny', difficulty: 'green', peak: 'snowshoe' },
  { id: 'lower-shays-revenge', name: "Lower Shay's Revenge", difficulty: 'double-black', peak: 'snowshoe' },
  { id: 'lower-whistlepunk', name: 'Lower Whistlepunk', difficulty: 'green', peak: 'snowshoe' },
  { id: 'mid-flume', name: 'Mid Flume', difficulty: 'green', peak: 'snowshoe' },
  { id: 'mid-whistlepunk', name: 'Mid Whistlepunk', difficulty: 'green', peak: 'snowshoe' },
  { id: 'moonshine', name: 'Moonshine', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'powder-monkey', name: 'Powder Monkey', difficulty: 'green', peak: 'snowshoe' },
  { id: 'powderidge', name: 'Powderidge', difficulty: 'green', peak: 'snowshoe' },
  { id: 'progression-park', name: 'Progression Park', difficulty: 'blue', peak: 'snowshoe', isTerrainPark: true },
  { id: 'sawmill', name: 'Sawmill', difficulty: 'black', peak: 'snowshoe' },
  { id: 'sawmill-glades', name: 'Sawmill Glades', difficulty: 'black', peak: 'snowshoe', isGlade: true },
  { id: 'shamrock', name: 'Shamrock', difficulty: 'green', peak: 'snowshoe' },
  { id: 'single-tree', name: 'Single Tree', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'skidder', name: 'Skidder', difficulty: 'green', peak: 'snowshoe' },
  { id: 'skip-jack', name: 'Skip Jack', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'spruce', name: 'Spruce', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'stemwinder', name: 'Stemwinder', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'sunset-glades', name: 'Sunset Glades', difficulty: 'black', peak: 'snowshoe', isGlade: true },
  { id: 'tail-tree', name: 'Tail Tree', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'upper-ballhooter', name: 'Upper Ballhooter', difficulty: 'blue', peak: 'snowshoe' },
  { id: 'upper-cupp-run', name: 'Upper Cupp Run', difficulty: 'black', peak: 'snowshoe' },
  { id: 'upper-flume', name: 'Upper Flume', difficulty: 'green', peak: 'snowshoe' },
  { id: 'upper-hootenanny', name: 'Upper Hootenanny', difficulty: 'green', peak: 'snowshoe' },
  { id: 'upper-shays-revenge', name: "Upper Shay's Revenge", difficulty: 'black', peak: 'snowshoe' },
  { id: 'upper-whistlepunk', name: 'Upper Whistlepunk', difficulty: 'green', peak: 'snowshoe' },
  { id: 'whiffletree', name: 'Whiffletree', difficulty: 'green', peak: 'snowshoe' },
  { id: 'widowmaker', name: 'Widowmaker', difficulty: 'black', peak: 'snowshoe' },
  { id: 'bear-claw', name: 'Bear Claw', difficulty: 'black', peak: 'silver-creek' },
  { id: 'bluehorn', name: 'Bluehorn', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'buck-saw', name: 'Buck Saw', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'cant-hook', name: 'Cant Hook', difficulty: 'green', peak: 'silver-creek' },
  { id: 'cascade', name: 'Cascade', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'cubb-run', name: 'Cubb Run', difficulty: 'green', peak: 'silver-creek' },
  { id: 'flying-eagle', name: 'Flying Eagle', difficulty: 'black', peak: 'silver-creek' },
  { id: 'flying-eagle-glades', name: 'Flying Eagle Glades', difficulty: 'black', peak: 'silver-creek', isGlade: true },
  { id: 'fox-chase', name: 'Fox Chase', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'greenhorn', name: 'Greenhorn', difficulty: 'green', peak: 'silver-creek' },
  { id: 'knife-blade', name: 'Knife Blade', difficulty: 'green', peak: 'silver-creek' },
  { id: 'laurel-run', name: 'Laurel Run', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'little-spruce', name: 'Little Spruce', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'mountaineer-park', name: 'Mountaineer Park', difficulty: 'blue', peak: 'silver-creek', isTerrainPark: true },
  { id: 'robertsons-run', name: "Robertson's Run", difficulty: 'green', peak: 'silver-creek' },
  { id: 'slaymaker', name: 'Slaymaker', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'spur', name: 'Spur', difficulty: 'blue', peak: 'silver-creek' },
  { id: 'timberjack-park', name: 'Timberjack Park', difficulty: 'blue', peak: 'silver-creek', isTerrainPark: true },
];
