import type { Trail, PeakData } from '../../../types';

// Smugglers' Notch's trail map from smuggs.com's trail-map page (the 2024-25
// artwork, still the map the resort links): one vector PDF page over a
// low-resolution painting (the map image is the vector layer over a smooth
// upscale of the painting). Trail lines are strokes in the difficulty
// colours; names are white outlined glyphs on label boxes in the run's
// colour (each glyph shape read once, then decoded:
// tools/trailmap/resorts/smugglers-notch/), on the line or off it with a
// leader line to the line or to a glade's hollow circle. Each line piece
// takes the name printed on it or the leader that ends on it; one line that
// carries Upper and Lower Drifter was cut between their labels, and the rest
// was settled on zoomed crops (decisions.py). Names are as printed (Express
// is Thomke's Express in the resort's list). Difficulty: the colour of the
// name's box; experts' runs print chains of two or three diamonds on their
// lines (double black). Glades (names with leaders to circles, no line) are
// markers at their circles. Terrain parks are orange lines named in orange
// boxes; Birch Run's own label names its park line. Peaks and elevations are
// the three summits as printed; trails are grouped by mountain as the
// resort's trail report groups them. x/y/baseY/width are unused layout
// fields.
export const peaks: PeakData[] = [
  { id: 'morse', name: 'Morse Mountain', elevation: 2250, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'madonna', name: 'Madonna Mountain', elevation: 3640, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'sterling', name: 'Sterling Mountain', elevation: 3040, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'buds-way', name: "Bud's Way", difficulty: 'green', peak: 'morse' },
  { id: 'burton-treehouse-riglet-park', name: 'Burton Treehouse Riglet Park', difficulty: 'green', peak: 'morse', isTerrainPark: true },
  { id: 'curleys-cutback', name: "Curley's Cutback", difficulty: 'green', peak: 'morse' },
  { id: 'dixies-knoll', name: "Dixie's Knoll", difficulty: 'green', peak: 'morse' },
  { id: 'evaporator', name: 'Evaporator', difficulty: 'blue', peak: 'morse' },
  { id: 'garden-path', name: 'Garden Path', difficulty: 'green', peak: 'morse' },
  { id: 'hibernator', name: 'Hibernator', difficulty: 'green', peak: 'morse' },
  { id: 'howies-wanderer', name: "Howie's Wanderer", difficulty: 'green', peak: 'morse' },
  { id: 'log-jam', name: 'Log Jam', difficulty: 'green', peak: 'morse' },
  { id: 'log-jam-terrain-park', name: 'Log Jam Terrain Park', difficulty: 'blue', peak: 'morse', isTerrainPark: true },
  { id: 'lower-morse-liftline', name: 'Lower Morse Liftline', difficulty: 'green', peak: 'morse' },
  { id: 'magic-learning-trail', name: 'Magic Learning Trail', difficulty: 'green', peak: 'morse' },
  { id: 'meadowlark', name: 'Meadowlark', difficulty: 'green', peak: 'morse' },
  { id: 'midway', name: 'Midway', difficulty: 'green', peak: 'morse' },
  { id: 'sams-run', name: "Sam's Run", difficulty: 'green', peak: 'morse' },
  { id: 'snow-snake', name: 'Snow Snake', difficulty: 'blue', peak: 'morse' },
  { id: 'timberrr', name: 'Timberrr!', difficulty: 'green', peak: 'morse' },
  { id: 'upper-morse-liftline', name: 'Upper Morse Liftline', difficulty: 'black', peak: 'morse' },
  { id: 'bermuda', name: 'Bermuda', difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'catwalk', name: 'Catwalk', difficulty: 'blue', peak: 'madonna' },
  { id: 'dans-ford', name: "Dan's Ford", difficulty: 'blue', peak: 'madonna' },
  { id: 'doc-dempseys-glades', name: "Doc Dempsey's Glades", difficulty: 'black', peak: 'madonna', isGlade: true },
  { id: 'father-bobs', name: "Father Bob's", difficulty: 'blue', peak: 'madonna' },
  { id: 'freefall', name: 'Freefall', difficulty: 'double-black', peak: 'madonna' },
  { id: 'gary-bs-northwest-passage', name: "Gary B's Northwest Passage", difficulty: 'black', peak: 'madonna' },
  { id: 'goat-path', name: 'Goat Path', difficulty: 'blue', peak: 'madonna' },
  { id: 'knights-revenge', name: "Knight's Revenge", difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'knights-revenge-gladed-park', name: "Knight's Revenge Gladed Park", difficulty: 'blue', peak: 'madonna', isGlade: true, isTerrainPark: true },
  { id: 'lower-catwalk', name: 'Lower Catwalk', difficulty: 'blue', peak: 'madonna' },
  { id: 'lower-chilcoot', name: 'Lower Chilcoot', difficulty: 'blue', peak: 'madonna' },
  { id: 'lower-drifter', name: 'Lower Drifter', difficulty: 'blue', peak: 'madonna' },
  { id: 'lower-f-i-s', name: 'Lower F.I.S.', difficulty: 'blue', peak: 'madonna' },
  { id: 'lower-liftline', name: 'Lower Liftline', difficulty: 'blue', peak: 'madonna' },
  { id: 'mcphersons', name: "McPherson's", difficulty: 'blue', peak: 'madonna' },
  { id: 'moonshiners-glades', name: "Moonshiner's Glades", difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'mulcahys-link', name: "Mulcahy's Link", difficulty: 'blue', peak: 'madonna' },
  { id: 'norwegian-woods', name: 'Norwegian Woods', difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'playground', name: 'Playground', difficulty: 'blue', peak: 'madonna' },
  { id: 'red-fox-glades', name: 'Red Fox Glades', difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'robins-run', name: "Robin's Run", difficulty: 'double-black', peak: 'madonna' },
  { id: 'ruthies', name: "Ruthie's", difficulty: 'blue', peak: 'madonna' },
  { id: 'shakedown', name: 'Shakedown', difficulty: 'black', peak: 'madonna', isGlade: true },
  { id: 'shuttle', name: 'Shuttle', difficulty: 'black', peak: 'madonna' },
  { id: 'the-black-hole', name: 'The Black Hole', difficulty: 'double-black', peak: 'madonna' },
  { id: 'the-shire', name: 'The Shire', difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'three-mtn-glades', name: 'Three Mtn. Glades', difficulty: 'blue', peak: 'madonna', isGlade: true },
  { id: 'upper-chilcoot', name: 'Upper Chilcoot', difficulty: 'blue', peak: 'madonna' },
  { id: 'upper-drifter', name: 'Upper Drifter', difficulty: 'blue', peak: 'madonna' },
  { id: 'upper-f-i-s', name: 'Upper F.I.S.', difficulty: 'black', peak: 'madonna' },
  { id: 'upper-liftline', name: 'Upper Liftline', difficulty: 'double-black', peak: 'madonna' },
  { id: 'waterfall', name: 'Waterfall', difficulty: 'blue', peak: 'madonna' },
  { id: 'birch-run', name: 'Birch Run', difficulty: 'blue', peak: 'sterling', isTerrainPark: true },
  { id: 'black-bear', name: 'Black Bear', difficulty: 'black', peak: 'sterling' },
  { id: 'black-snake', name: 'Black Snake', difficulty: 'blue', peak: 'sterling' },
  { id: 'bootlegger', name: 'Bootlegger', difficulty: 'black', peak: 'sterling' },
  { id: 'chute', name: 'Chute', difficulty: 'black', peak: 'sterling' },
  { id: 'crossover', name: 'Crossover', difficulty: 'blue', peak: 'sterling' },
  { id: 'deer-run-glades', name: 'Deer Run Glades', difficulty: 'black', peak: 'sterling', isGlade: true },
  { id: 'full-nelson', name: 'Full Nelson', difficulty: 'black', peak: 'sterling' },
  { id: 'hangmans', name: "Hangman's", difficulty: 'blue', peak: 'sterling' },
  { id: 'hangmans-drop', name: "Hangman's Drop", difficulty: 'black', peak: 'sterling' },
  { id: 'harveys-hideaway', name: "Harvey's Hideaway", difficulty: 'blue', peak: 'sterling' },
  { id: 'highlander-glades', name: 'Highlander Glades', difficulty: 'black', peak: 'sterling', isGlade: true },
  { id: 'jolly-rodger', name: 'Jolly Rodger', difficulty: 'blue', peak: 'sterling' },
  { id: 'lower-exhibition', name: 'Lower Exhibition', difficulty: 'blue', peak: 'sterling' },
  { id: 'lower-pipeline', name: 'Lower Pipeline', difficulty: 'blue', peak: 'sterling' },
  { id: 'lower-rumrunner', name: 'Lower Rumrunner', difficulty: 'blue', peak: 'sterling' },
  { id: 'pipeline-escape', name: 'Pipeline Escape', difficulty: 'black', peak: 'sterling' },
  { id: 'pirates-plank', name: "Pirate's Plank", difficulty: 'black', peak: 'sterling', isGlade: true },
  { id: 'poachers-woods', name: "Poacher's Woods", difficulty: 'blue', peak: 'sterling' },
  { id: 'powder-keg', name: 'Powder Keg', difficulty: 'black', peak: 'sterling', isGlade: true },
  { id: 'practice-slope', name: 'Practice Slope', difficulty: 'blue', peak: 'sterling' },
  { id: 'sherwood-forest', name: 'Sherwood Forest', difficulty: 'blue', peak: 'sterling', isGlade: true },
  { id: 'smugglersalley', name: "Smugglers'Alley", difficulty: 'black', peak: 'sterling' },
  { id: 'snake-bite', name: 'Snake Bite', difficulty: 'black', peak: 'sterling' },
  { id: 'the-zone-terrain-park', name: 'The Zone Terrain Park', difficulty: 'blue', peak: 'sterling', isTerrainPark: true },
  { id: 'thomkes', name: "Thomke's", difficulty: 'blue', peak: 'sterling' },
  { id: 'thomkes-express', name: "Thomke's Express", difficulty: 'blue', peak: 'sterling' },
  { id: 'treasure-run', name: 'Treasure Run', difficulty: 'blue', peak: 'sterling' },
  { id: 'upper-exhibition', name: 'Upper Exhibition', difficulty: 'black', peak: 'sterling' },
  { id: 'upper-pipeline', name: 'Upper Pipeline', difficulty: 'black', peak: 'sterling' },
  { id: 'upper-rumrunner', name: 'Upper Rumrunner', difficulty: 'blue', peak: 'sterling' },
];
