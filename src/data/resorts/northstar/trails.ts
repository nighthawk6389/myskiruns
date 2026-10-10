import type { Trail, PeakData } from '../../../types';

// Northstar's 2025-26 trail map (northstarcalifornia.com: the resort's PDF,
// page 1; Alex Tait's painting under a vector layer). The lines are the
// PDF's own: every trail line is a filled outline in blue, black or green,
// taken along its middle; the names are white capitals printed on their line,
// each letter haloed in the line's colour, and the rating is the symbol on
// the line by the name, else that colour. Names are spelled as the trail
// report spells them (report.json: the terrain feed, February 2026). One
// outline often carries several runs: decisions.py cuts it where each starts
// (the summits of Mt. Pluto and Lookout Mountain, the Grouse Alleys and The
// Flume, Axe Handle and Stump Alley, the Ridges, Lookout Road and Drifter,
// the Pioneers, Boondocks and Lookout Bypass, Skid Trail, Lumberjack and the
// Main Streets, Gateway and Timber Line, Iron Horse and Why Not), and where a
// run's outline goes on along another's line (Northern Lights' down Christmas
// Tree's, Stump Alley's down Luggi's, Castle Peak's down Drifter's) leaves
// that line to the run printed on it. Lines no name is printed on that go on
// from a run carry its name (Iron Horse from the summit and on to the
// Backside Express, Prosser's summit line, Christmas Tree's two run-outs,
// Timber Line to its lift); the links between runs and the label leader
// lines have no overlay, nor has the line below The Chute's foot, which has a
// square of its own and no name (perhaps the report's Lower Chute). Cowboy
// Pass and Bearly are their labels. The terrain parks (orange pills), the
// glades, the Kids Adventure Zone's four (numbered signs, named in its box)
// and Carpet Bowl (in the Mid-Mountain inset) are markers at their names;
// Sidewinder has its run-out line. The report's Coyote Crossing, Drifter
// Connector and Lower Chute are not printed. Areas: the report's.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'mt-pluto', name: 'Mt. Pluto', elevation: 8610, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'backside', name: 'The Backside', elevation: 8610, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'northwest-territory', name: 'Northwest Territory', elevation: 8120, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'lookout-mountain', name: 'Lookout Mountain', elevation: 8120, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'village', name: 'Village at Northstar', elevation: 6330, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'axe-handle', name: 'Axe Handle', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'bear-crawl', name: 'Bear Crawl', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'cascades', name: 'Cascades', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'cats-face', name: "Cat's Face", difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'crosscut', name: 'Crosscut', difficulty: 'black', peak: 'mt-pluto' },
  { id: 'delight', name: 'Delight', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'drop-off', name: 'Drop Off', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'dutchman', name: 'Dutchman', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'eagle-chute', name: 'Eagle Chute', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'east-ridge', name: 'East Ridge', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'flying-squirrel', name: 'Flying Squirrel', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'forerunner', name: 'Forerunner', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'hornets-nest', name: "Hornet's Nest", difficulty: 'black', peak: 'mt-pluto' },
  { id: 'jibboom', name: 'Jibboom', difficulty: 'black', peak: 'mt-pluto' },
  { id: 'loggers-loop', name: "Logger's Loop", difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'lookout-road', name: 'Lookout Road', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'lower-grouse-alley', name: 'Lower Grouse Alley', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'lower-main-street', name: 'Lower Main Street', difficulty: 'green', peak: 'mt-pluto' },
  { id: 'luggis', name: "Luggi's", difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'lumberjack', name: 'Lumberjack', difficulty: 'green', peak: 'mt-pluto' },
  { id: 'moonshine', name: 'Moonshine', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'pinball', name: 'Pinball', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'pipeline', name: 'Pipeline', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'playground', name: 'Playground', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'powder-bowl', name: 'Powder Bowl', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'sawmill-glade', name: 'Sawmill Glade', difficulty: 'black', peak: 'mt-pluto', isGlade: true },
  { id: 'sidewinder', name: 'Sidewinder', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'skid-trail', name: 'Skid Trail', difficulty: 'green', peak: 'mt-pluto' },
  { id: 'spring-board', name: 'Spring Board', difficulty: 'black', peak: 'mt-pluto' },
  { id: 'stump-alley', name: 'Stump Alley', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'surprise', name: 'Surprise', difficulty: 'black', peak: 'mt-pluto' },
  { id: 'the-chute', name: 'The Chute', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'the-flume', name: 'The Flume', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'the-plunge', name: 'The Plunge', difficulty: 'black', peak: 'mt-pluto' },
  { id: 'the-straits', name: 'The Straits', difficulty: 'blue', peak: 'mt-pluto', isTerrainPark: true },
  { id: 'toninis', name: "Tonini's", difficulty: 'black', peak: 'mt-pluto' },
  { id: 'upper-grouse-alley', name: 'Upper Grouse Alley', difficulty: 'black', peak: 'mt-pluto' },
  { id: 'upper-jibboom', name: 'Upper Jibboom', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'upper-main-street', name: 'Upper Main Street', difficulty: 'green', peak: 'mt-pluto' },
  { id: 'west-ridge', name: 'West Ridge', difficulty: 'blue', peak: 'mt-pluto' },
  { id: 'backdoor', name: 'Backdoor', difficulty: 'blue', peak: 'backside' },
  { id: 'burnout', name: 'Burnout', difficulty: 'black', peak: 'backside' },
  { id: 'castle-peak', name: 'Castle Peak', difficulty: 'blue', peak: 'backside' },
  { id: 'challenger', name: 'Challenger', difficulty: 'black', peak: 'backside' },
  { id: 'down-under', name: 'Down Under', difficulty: 'black', peak: 'backside' },
  { id: 'drifter', name: 'Drifter', difficulty: 'blue', peak: 'backside' },
  { id: 'follow-me', name: 'Follow Me', difficulty: 'black', peak: 'backside' },
  { id: 'iron-horse', name: 'Iron Horse', difficulty: 'black', peak: 'backside' },
  { id: 'lower-burnout', name: 'Lower Burnout', difficulty: 'blue', peak: 'backside' },
  { id: 'monument-glade', name: 'Monument Glade', difficulty: 'black', peak: 'backside', isGlade: true },
  { id: 'polaris', name: 'Polaris', difficulty: 'black', peak: 'backside' },
  { id: 'promised-land', name: 'Promised Land', difficulty: 'black', peak: 'backside' },
  { id: 'rail-splitter', name: 'Rail Splitter', difficulty: 'black', peak: 'backside' },
  { id: 'sierra-grande', name: 'Sierra Grande', difficulty: 'black', peak: 'backside' },
  { id: 'the-islands', name: 'The Islands', difficulty: 'blue', peak: 'backside' },
  { id: 'the-rapids', name: 'The Rapids', difficulty: 'black', peak: 'backside' },
  { id: 'why-not', name: 'Why Not', difficulty: 'black', peak: 'backside' },
  { id: 'bobcat-bowl', name: 'Bobcat Bowl', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'boondocks', name: 'Boondocks', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'carpet-bowl', name: 'Carpet Bowl', difficulty: 'green', peak: 'northwest-territory' },
  { id: 'christmas-tree', name: 'Christmas Tree', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'cowboy-pass', name: 'Cowboy Pass', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'deerskin', name: 'Deerskin', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'easy-street', name: 'Easy Street', difficulty: 'green', peak: 'northwest-territory' },
  { id: 'gateway', name: 'Gateway', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'goldmine', name: 'Goldmine', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'home-run', name: 'Home Run', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'hoot-owl', name: 'Hoot Owl', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'lower-lions-way', name: "Lower Lion's Way", difficulty: 'green', peak: 'northwest-territory' },
  { id: 'lower-pioneer', name: 'Lower Pioneer', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'northern-lights', name: 'Northern Lights', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'overland-trail', name: 'Overland Trail', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'sodergrens', name: "Sodergren's", difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'the-face', name: 'The Face', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'the-glades', name: 'The Glades', difficulty: 'blue', peak: 'northwest-territory', isGlade: true },
  { id: 'the-gulch', name: 'The Gulch', difficulty: 'green', peak: 'northwest-territory' },
  { id: 'the-gully', name: 'The Gully', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'timberline', name: 'Timberline', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'upper-lions-way', name: "Upper Lion's Way", difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'upper-pioneer', name: 'Upper Pioneer', difficulty: 'blue', peak: 'northwest-territory' },
  { id: 'wood-cutter', name: 'Wood Cutter', difficulty: 'green', peak: 'northwest-territory' },
  { id: 'boca', name: 'Boca', difficulty: 'black', peak: 'lookout-mountain' },
  { id: 'gooseneck', name: 'Gooseneck', difficulty: 'black', peak: 'lookout-mountain' },
  { id: 'lookout-bypass', name: 'Lookout Bypass', difficulty: 'blue', peak: 'lookout-mountain' },
  { id: 'lookout-glade', name: 'Lookout Glade', difficulty: 'black', peak: 'lookout-mountain', isGlade: true },
  { id: 'martis', name: 'Martis', difficulty: 'black', peak: 'lookout-mountain' },
  { id: 'prosser', name: 'Prosser', difficulty: 'black', peak: 'lookout-mountain' },
  { id: 'schwarzstrasse', name: 'Schwarzstrasse', difficulty: 'blue', peak: 'lookout-mountain' },
  { id: 'stampede', name: 'Stampede', difficulty: 'black', peak: 'lookout-mountain' },
  { id: 'sugar-pine-glade', name: 'Sugar Pine Glade', difficulty: 'black', peak: 'lookout-mountain', isGlade: true },
  { id: 'the-camp-glade', name: 'The Camp Glade', difficulty: 'black', peak: 'lookout-mountain', isGlade: true },
  { id: 'washoe', name: 'Washoe', difficulty: 'blue', peak: 'lookout-mountain' },
  { id: 'webber', name: 'Webber', difficulty: 'black', peak: 'lookout-mountain' },
  { id: 'bearly', name: 'Bearly', difficulty: 'green', peak: 'village' },
  { id: 'condo-run', name: 'Condo Run', difficulty: 'green', peak: 'village' },
  { id: 'coyote-fork', name: 'Coyote Fork', difficulty: 'blue', peak: 'village' },
  { id: 'lynx-luge', name: 'Lynx Luge', difficulty: 'blue', peak: 'village' },
  { id: 'the-woods', name: 'The Woods', difficulty: 'blue', peak: 'village' },
  { id: 'village-run', name: 'Village Run', difficulty: 'green', peak: 'village' },
];
