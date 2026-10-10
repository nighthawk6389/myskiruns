import type { Trail, PeakData } from '../../../types';

// Buttermilk's 2025-26 trail map (aspensnowmass.com: the resort's "layered"
// PDF, one page, drawn like Snowmass's). The lines are the PDF's own: blue,
// black and green strokes, and the green dots of the "least difficult way
// down" (Homestead Road from the top to the base, and Bear's lower part).
// Every name is white text on a pill in its run's colour, set along its own
// line: the rating is the pill's colour (green, blue, black); the map has no
// expert terrain. Names are spelled as the trail report spells them
// (report.json: the resort's grooming feed); RIDGE and TRAIL, printed on
// Ridge Trail's green upper line and its blue lower one, are the report's two
// Ridge Trails; Ptarmigan Glade is printed but not on the report. The uphill
// routes and the parks the map doesn't print (Panda Park, Teaser Park, Family
// Cross, the Mini Pipe, the Snow Cross, Alex's Alley) are left out. Where one
// line carries two runs, decisions.py cuts it where they part (Klaus' Way and
// Racer's Edge, Buckskin and Rabbit Run, Spruce and the Super Pipe, Blue
// Grouse and Westward Ho, Savio and its cut-across). Panda Hill, printed with
// no line (the beginner area at the base): a marker at its name. Areas: the
// three printed bases with the report's lift areas.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'west-buttermilk', name: 'West Buttermilk', elevation: 8693, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'tiehack', name: 'Tiehack', elevation: 8037, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'main', name: 'Main Buttermilk', elevation: 7870, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'big-face-hollow', name: 'Big Face Hollow', difficulty: 'blue', peak: 'west-buttermilk' },
  { id: 'blue-grouse', name: 'Blue Grouse', difficulty: 'green', peak: 'west-buttermilk' },
  { id: 'camp-bird', name: 'Camp Bird', difficulty: 'blue', peak: 'west-buttermilk' },
  { id: 'larkspur', name: 'Larkspur', difficulty: 'green', peak: 'west-buttermilk' },
  { id: 'little-teaser', name: 'Little Teaser', difficulty: 'black', peak: 'west-buttermilk' },
  { id: 'lower-larkspur', name: 'Lower Larkspur', difficulty: 'black', peak: 'west-buttermilk' },
  { id: 'reds-rover', name: "Red's Rover", difficulty: 'green', peak: 'west-buttermilk', isTerrainPark: true },
  { id: 'teaser', name: 'Teaser', difficulty: 'blue', peak: 'west-buttermilk' },
  { id: 'toms-thumb', name: "Tom's Thumb", difficulty: 'green', peak: 'west-buttermilk' },
  { id: 'westward-ho', name: 'Westward Ho', difficulty: 'green', peak: 'west-buttermilk' },
  { id: 'buckskin', name: 'Buckskin', difficulty: 'blue', peak: 'tiehack' },
  { id: 'eagle-hill', name: 'Eagle Hill', difficulty: 'blue', peak: 'tiehack' },
  { id: 'javelin', name: 'Javelin', difficulty: 'black', peak: 'tiehack' },
  { id: 'klaus-way', name: "Klaus' Way", difficulty: 'black', peak: 'tiehack' },
  { id: 'magic-carpet', name: 'Magic Carpet', difficulty: 'blue', peak: 'tiehack' },
  { id: 'oregon-trail', name: 'Oregon Trail', difficulty: 'green', peak: 'tiehack' },
  { id: 'ptarmigan', name: 'Ptarmigan', difficulty: 'blue', peak: 'tiehack' },
  { id: 'ptarmigan-glade', name: 'Ptarmigan Glade', difficulty: 'black', peak: 'tiehack', isGlade: true },
  { id: 'rabbit-run', name: 'Rabbit Run', difficulty: 'blue', peak: 'tiehack' },
  { id: 'racers-edge', name: "Racer's Edge", difficulty: 'black', peak: 'tiehack' },
  { id: 'sterner', name: 'Sterner', difficulty: 'black', peak: 'tiehack' },
  { id: 'sterner-gulch', name: 'Sterner Gulch', difficulty: 'blue', peak: 'tiehack' },
  { id: 'tiehack-trail', name: 'Tiehack Trail', difficulty: 'black', peak: 'tiehack' },
  { id: 'timberdoodle-glade', name: 'Timberdoodle Glade', difficulty: 'black', peak: 'tiehack', isGlade: true },
  { id: 'baby-doe', name: 'Baby Doe', difficulty: 'blue', peak: 'main' },
  { id: 'bear', name: 'Bear', difficulty: 'blue', peak: 'main' },
  { id: 'columbine', name: 'Columbine', difficulty: 'blue', peak: 'main' },
  { id: 'friedls', name: "Friedl's", difficulty: 'blue', peak: 'main' },
  { id: 'government', name: 'Government', difficulty: 'black', peak: 'main', isTerrainPark: true },
  { id: 'homestead-road', name: 'Homestead Road', difficulty: 'green', peak: 'main' },
  { id: 'jacobs-ladder', name: "Jacob's Ladder", difficulty: 'black', peak: 'main', isTerrainPark: true },
  { id: 'lovers-lane', name: "Lover's Lane", difficulty: 'blue', peak: 'main' },
  { id: 'lower-savio', name: 'Lower Savio', difficulty: 'blue', peak: 'main' },
  { id: 'midway-avenue', name: 'Midway Avenue', difficulty: 'blue', peak: 'main' },
  { id: 'no-problem', name: 'No Problem', difficulty: 'blue', peak: 'main' },
  { id: 'panda-hill', name: 'Panda Hill', difficulty: 'green', peak: 'main' },
  { id: 'ridge-trail-lower', name: 'Ridge Trail (Lower)', difficulty: 'blue', peak: 'main' },
  { id: 'ridge-trail-upper', name: 'Ridge Trail (Upper)', difficulty: 'green', peak: 'main' },
  { id: 'savio-upper', name: 'Savio (Upper)', difficulty: 'blue', peak: 'main' },
  { id: 'spruce-upper', name: 'Spruce (Upper)', difficulty: 'black', peak: 'main' },
  { id: 'spruce-face', name: 'Spruce Face', difficulty: 'black', peak: 'main', isTerrainPark: true },
  { id: 'sterner-catwalk', name: 'Sterner Catwalk', difficulty: 'green', peak: 'main' },
  { id: 'super-pipe', name: 'Super Pipe', difficulty: 'black', peak: 'main', isTerrainPark: true },
  { id: 'uncle-chucks-glades', name: "Uncle Chuck's Glades", difficulty: 'black', peak: 'main', isGlade: true, isTerrainPark: true },
];
