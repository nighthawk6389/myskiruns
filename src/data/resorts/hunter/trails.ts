import type { Trail, PeakData } from '../../../types';

// Hunter Mountain's 2025-26 trail map is one vector PDF page (huntermtn.com):
// every trail is a thin line in its difficulty colour that runs into its name,
// printed as text in a gap of the line with its symbol at the uphill end. The
// lines and names come straight from the PDF; each line piece was named by
// the name it runs into (tools/trailmap/pdf_resort.py) and checked on zoomed
// crops (tools/trailmap/resorts/hunter/decisions.py). Names are as printed;
// difficulty is the printed symbol (every single and double diamond checked on
// a crop). The three glades print a tree icon and no line, and Learning Zone
// (a beginner area) prints no line: markers at their names. Park Avenue, Park
// Avenue West and Lower 42nd Street carry the freestyle-terrain pill. x/y/
// baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'hunter', name: 'Hunter Mountain', elevation: 4040, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: '7th-avenue', name: '7th Avenue', difficulty: 'blue', peak: 'hunter' },
  { id: 'annapurna', name: 'Annapurna', difficulty: 'double-black', peak: 'hunter' },
  { id: 'b-flat', name: 'B Flat', difficulty: 'green', peak: 'hunter' },
  { id: 'belt-parkway', name: 'Belt Parkway', difficulty: 'blue', peak: 'hunter' },
  { id: 'belt-parkway-bypass', name: 'Belt Parkway Bypass', difficulty: 'blue', peak: 'hunter' },
  { id: 'bleecker-street', name: 'Bleecker Street', difficulty: 'black', peak: 'hunter' },
  { id: 'boston-road', name: 'Boston Road', difficulty: 'green', peak: 'hunter' },
  { id: 'briar-patch', name: 'Briar Patch', difficulty: 'green', peak: 'hunter' },
  { id: 'buckys-run', name: "Bucky's Run", difficulty: 'green', peak: 'hunter' },
  { id: 'central-park', name: 'Central Park', difficulty: 'blue', peak: 'hunter' },
  { id: 'central-park-north', name: 'Central Park North', difficulty: 'green', peak: 'hunter' },
  { id: 'clairs-way', name: "Clair's Way", difficulty: 'double-black', peak: 'hunter' },
  { id: 'drop-off', name: 'Drop Off', difficulty: 'black', peak: 'hunter' },
  { id: 'eisenhower-drive', name: 'Eisenhower Drive', difficulty: 'black', peak: 'hunter' },
  { id: 'empire-trail', name: 'Empire Trail', difficulty: 'blue', peak: 'hunter' },
  { id: 'fifth-avenue', name: 'Fifth Avenue', difficulty: 'green', peak: 'hunter' },
  { id: 'fordham-road', name: 'Fordham Road', difficulty: 'green', peak: 'hunter' },
  { id: 'gateway', name: 'Gateway', difficulty: 'green', peak: 'hunter' },
  { id: 'gramercy-park', name: 'Gramercy Park', difficulty: 'green', peak: 'hunter' },
  { id: 'grand-concourse', name: 'Grand Concourse', difficulty: 'green', peak: 'hunter' },
  { id: 'gun-hill-road', name: 'Gun Hill Road', difficulty: 'blue', peak: 'hunter' },
  { id: 'hellgate', name: 'Hellgate', difficulty: 'black', peak: 'hunter' },
  { id: 'herald-square', name: 'Herald Square', difficulty: 'green', peak: 'hunter' },
  { id: 'jimmy-huega', name: 'Jimmy Huega', difficulty: 'black', peak: 'hunter' },
  { id: 'kmc-drive', name: 'KMC Drive', difficulty: 'green', peak: 'hunter' },
  { id: 'kennedy-drive', name: 'Kennedy Drive', difficulty: 'blue', peak: 'hunter' },
  { id: 'learning-zone', name: 'Learning Zone', difficulty: 'green', peak: 'hunter' },
  { id: 'lower-42nd-street', name: 'Lower 42nd Street', difficulty: 'blue', peak: 'hunter', isTerrainPark: true },
  { id: 'lower-broadway', name: 'Lower Broadway', difficulty: 'black', peak: 'hunter' },
  { id: 'lower-crossover', name: 'Lower Crossover', difficulty: 'black', peak: 'hunter' },
  { id: 'lower-east-side-drive', name: 'Lower East Side Drive', difficulty: 'black', peak: 'hunter' },
  { id: 'lower-highlands', name: 'Lower Highlands', difficulty: 'blue', peak: 'hunter' },
  { id: 'lower-k27', name: 'Lower K27', difficulty: 'double-black', peak: 'hunter' },
  { id: 'lower-sleepy-hollow', name: 'Lower Sleepy Hollow', difficulty: 'blue', peak: 'hunter' },
  { id: 'macombs', name: 'Macombs', difficulty: 'blue', peak: 'hunter' },
  { id: 'mad-box', name: 'Mad Box', difficulty: 'black', peak: 'hunter' },
  { id: 'madison-avenue', name: 'Madison Avenue', difficulty: 'blue', peak: 'hunter' },
  { id: 'madison-square', name: 'Madison Square', difficulty: 'green', peak: 'hunter' },
  { id: 'milky-way', name: 'Milky Way', difficulty: 'black', peak: 'hunter' },
  { id: 'minya-konka', name: 'Minya Konka', difficulty: 'black', peak: 'hunter' },
  { id: 'mossy-brook', name: 'Mossy Brook', difficulty: 'green', peak: 'hunter' },
  { id: 'overlook', name: 'Overlook', difficulty: 'black', peak: 'hunter' },
  { id: 'park-avenue', name: 'Park Avenue', difficulty: 'black', peak: 'hunter', isTerrainPark: true },
  { id: 'park-avenue-west', name: 'Park Avenue West', difficulty: 'black', peak: 'hunter', isTerrainPark: true },
  { id: 'racers-edge', name: "Racer's Edge", difficulty: 'double-black', peak: 'hunter' },
  { id: 'rip-van-winkle', name: 'Rip Van Winkle', difficulty: 'blue', peak: 'hunter' },
  { id: 'rips-return', name: "Rip's Return", difficulty: 'blue', peak: 'hunter' },
  { id: 'rusk-road', name: 'Rusk Road', difficulty: 'green', peak: 'hunter' },
  { id: 'taylors-run', name: "Taylor's Run", difficulty: 'black', peak: 'hunter' },
  { id: 'the-battery', name: 'The Battery', difficulty: 'green', peak: 'hunter' },
  { id: 'the-cliff', name: 'The Cliff', difficulty: 'black', peak: 'hunter' },
  { id: 'the-colonels-alternative', name: "The Colonel's Alternative", difficulty: 'black', peak: 'hunter' },
  { id: 'the-milky-glades', name: 'The Milky Glades', difficulty: 'black', peak: 'hunter', isGlade: true },
  { id: 'times-square', name: 'Times Square', difficulty: 'blue', peak: 'hunter' },
  { id: 'twilight', name: 'Twilight', difficulty: 'black', peak: 'hunter' },
  { id: 'upper-42nd-street', name: 'Upper 42nd Street', difficulty: 'blue', peak: 'hunter' },
  { id: 'upper-crossover', name: 'Upper Crossover', difficulty: 'double-black', peak: 'hunter' },
  { id: 'upper-east-side-drive', name: 'Upper East Side Drive', difficulty: 'black', peak: 'hunter' },
  { id: 'upper-hemlocks', name: 'Upper Hemlocks', difficulty: 'black', peak: 'hunter' },
  { id: 'upper-highlands', name: 'Upper Highlands', difficulty: 'black', peak: 'hunter' },
  { id: 'upper-k27', name: 'Upper K27', difficulty: 'black', peak: 'hunter' },
  { id: 'upper-sleepy-hollow', name: 'Upper Sleepy Hollow', difficulty: 'blue', peak: 'hunter' },
  { id: 'upper-taylors-run', name: "Upper Taylor's Run", difficulty: 'black', peak: 'hunter' },
  { id: 'way-in', name: 'Way In', difficulty: 'black', peak: 'hunter' },
  { id: 'way-out', name: 'Way Out', difficulty: 'blue', peak: 'hunter' },
  { id: 'west-side-glide', name: 'West Side Glide', difficulty: 'blue', peak: 'hunter' },
  { id: 'westway', name: 'Westway', difficulty: 'double-black', peak: 'hunter' },
  { id: 'which-way-glades', name: 'Which Way Glades', difficulty: 'black', peak: 'hunter', isGlade: true },
  { id: 'white-cloud', name: 'White Cloud', difficulty: 'blue', peak: 'hunter' },
  { id: 'woodstock-glades', name: 'Woodstock Glades', difficulty: 'black', peak: 'hunter', isGlade: true },
];
