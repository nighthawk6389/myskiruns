import type { Trail, PeakData } from '../../../types';

// Heavenly's trail map: the 2024-25 artwork, still the resort's current map,
// as an image on Vail Resorts' scene7 CDN (skiheavenly.com shows it and links
// no winter PDF): the main painting of the California and Nevada sides and the
// Top of Gondola inset, as two panels. Its lines, names and symbols come from
// the 2022-23 PDF of the same artwork (skimap.org map 23043), registered on
// each painting (tools/trailmap/resorts/heavenly/): every place the two
// editions differ was checked on the image, and what it no longer prints left
// out (Widow Maker, now Lone Wolf; Upper Powderbowl's and Powderbowl Run's
// labels, since moved, are traced where the image prints them); Lakeview Park
// is new. Lines are outlined blue and green routes, solid or dashed, and
// Ellie's dark line; most runs have no line: their names are printed along the
// painted cuts, the symbol before the name, and the overlay is the stretch
// along the name from its symbol. Each line takes the name printed along it or
// at its end; the rest was settled on zoomed crops (decisions.py), with the
// PDF's drawing order and OpenStreetMap's runs: High Five's line forks above
// the Sky Deck to both lifts' feet; California Trail's ends in two arrows into
// the Sky Deck; Comet's starts at Sand Dunes' arrow; Big Dipper's runs on to
// Upper Dipper Return's square; Nova's leaves Big Dipper's; Crossover's forks
// below its lower label to the North Bowl Express top and towards Cloud 9; at
// the top of the gondola, Von Schmidt is the lower label's line round the
// hairpin into the upper label and on to California Trail (an older edition's
// navigation map: Nevada to the Top of Gondola by Comet and the Von Schmidt
// traverse), Silver Spur the line from Easy Street's circle down to it and its
// name on to Bonanza, Bonanza the line from the lower label to its name, and
// Olympic Downhill the line down from the Olympic Express top. Lines the map
// doesn't name have no overlay: a link under the Canyon Express, two green
// arrows from the Sky Deck lodge, the inset's ways to California and Nevada.
// Names are as the resort's trail report spells them (this season's, else
// 2024-25's, the season the map was drawn for); names the report has changed
// since are as printed (Express Line, now Sky Express Line; Canyonland and
// Ridge Run, now each split in two), and a run the report splits into an upper
// and a lower part but the map prints on one line is one trail (California
// Trail, Liz's, Comstock, Mineshaft, Olympic Downhill, Stagecoach, Gunbarrel,
// Von Schmidt). Difficulty: the symbol printed by the name (two diamonds,
// double black); Mott and Killebrew Canyons' 21 named chutes, printed with no
// symbol, take the canyons' double diamond (the report's Extreme); Rim Trail, a
// dark line, black. Every rating agrees with the report but Hogsback's (a
// diamond on the map, double black on this season's report). Bowls, faces,
// woods (glades), the canyons' chutes, the parks and the learning areas are
// markers at their names. The report's learning areas and tubing hill (The
// Meadow, Boulder Carpet Run, Black Bear Hollow, Tubing Run), Groove Trail,
// Pioneer Trail and Red Fir (the map names only their lifts), Ridge Way, Sky
// Chute 2, Galaxy Woods and Pinnacle Glades aren't on the map. Trails are
// grouped by the report's areas (California, Nevada, Top of Gondola);
// elevations: the summits printed above the Sky Express and Milky Way Bowl,
// and the top of the Tamarack Express. x/y/baseY/width are unused layout
// fields.
export const peaks: PeakData[] = [
  { id: 'california', name: 'California', elevation: 10040, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'nevada', name: 'Nevada', elevation: 10067, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'top-of-gondola', name: 'Top of Gondola', elevation: 9725, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'canyonland', name: 'Canyonland', difficulty: 'blue', peak: 'california' },
  { id: 'double-down', name: 'Double Down', difficulty: 'black', peak: 'california' },
  { id: 'east-bowl', name: 'East Bowl', difficulty: 'double-black', peak: 'california' },
  { id: 'east-bowl-woods', name: 'East Bowl Woods', difficulty: 'black', peak: 'california', isGlade: true },
  { id: 'ellies', name: "Ellie's", difficulty: 'black', peak: 'california' },
  { id: 'ellies-swing', name: "Ellie's Swing", difficulty: 'black', peak: 'california' },
  { id: 'enchanted-forest', name: 'Enchanted Forest', difficulty: 'green', peak: 'california' },
  { id: 'express-line', name: 'Express Line', difficulty: 'black', peak: 'california' },
  { id: 'fall-line', name: 'Fall Line', difficulty: 'black', peak: 'california' },
  { id: 'groove-terrain-park', name: 'Groove Terrain Park', difficulty: 'blue', peak: 'california', isTerrainPark: true },
  { id: 'gunbarrel', name: 'Gunbarrel', difficulty: 'double-black', peak: 'california' },
  { id: 'high-five', name: 'High Five', difficulty: 'blue', peak: 'california' },
  { id: 'hogsback', name: 'Hogsback', difficulty: 'black', peak: 'california' },
  { id: 'lakeview-terrain-park', name: 'Lakeview Terrain Park', difficulty: 'blue', peak: 'california', isTerrainPark: true },
  { id: 'lizs', name: "Liz's", difficulty: 'blue', peak: 'california' },
  { id: 'maggies', name: "Maggie's", difficulty: 'green', peak: 'california' },
  { id: 'maggies-canyon', name: "Maggie's Canyon", difficulty: 'black', peak: 'california' },
  { id: 'mombo', name: 'Mombo', difficulty: 'blue', peak: 'california' },
  { id: 'mombo-upper', name: 'Mombo Upper', difficulty: 'blue', peak: 'california' },
  { id: 'patsys', name: "Patsy's", difficulty: 'green', peak: 'california' },
  { id: 'pinnacles', name: 'Pinnacles', difficulty: 'black', peak: 'california' },
  { id: 'pistol', name: 'Pistol', difficulty: 'black', peak: 'california' },
  { id: 'poma-trail', name: 'Poma Trail', difficulty: 'green', peak: 'california' },
  { id: 'powder-line', name: 'Powder Line', difficulty: 'black', peak: 'california' },
  { id: 'powderbowl-run', name: 'Powderbowl Run', difficulty: 'blue', peak: 'california' },
  { id: 'powderbowl-upper', name: 'Powderbowl Upper', difficulty: 'blue', peak: 'california' },
  { id: 'powderbowl-woods', name: 'Powderbowl Woods', difficulty: 'black', peak: 'california', isGlade: true },
  { id: 'ridge-bowl', name: 'Ridge Bowl', difficulty: 'black', peak: 'california' },
  { id: 'ridge-run', name: 'Ridge Run', difficulty: 'blue', peak: 'california' },
  { id: 'round-a-bout', name: 'Round-a-Bout', difficulty: 'blue', peak: 'california' },
  { id: 'ski-way-glades', name: 'Ski Way Glades', difficulty: 'black', peak: 'california', isGlade: true },
  { id: 'sky-canyon', name: 'Sky Canyon', difficulty: 'black', peak: 'california' },
  { id: 'sky-chute', name: 'Sky Chute', difficulty: 'blue', peak: 'california' },
  { id: 'skyline-trail', name: 'Skyline Trail', difficulty: 'blue', peak: 'california' },
  { id: 'steins-way', name: "Stein's Way", difficulty: 'blue', peak: 'california' },
  { id: 'swing-trail', name: 'Swing Trail', difficulty: 'blue', peak: 'california' },
  { id: 'the-face', name: 'The Face', difficulty: 'double-black', peak: 'california' },
  { id: 'waterfall', name: 'Waterfall', difficulty: 'black', peak: 'california' },
  { id: 'west-bowl', name: 'West Bowl', difficulty: 'black', peak: 'california' },
  { id: 'world-cup', name: 'World Cup', difficulty: 'blue', peak: 'california' },
  { id: '100-saddle', name: '$100 Saddle', difficulty: 'blue', peak: 'nevada' },
  { id: 'aries', name: 'Aries', difficulty: 'blue', peak: 'nevada' },
  { id: 'aries-woods', name: 'Aries Woods', difficulty: 'black', peak: 'nevada', isGlade: true },
  { id: 'big-dipper', name: 'Big Dipper', difficulty: 'blue', peak: 'nevada' },
  { id: 'bills', name: "Bill's", difficulty: 'double-black', peak: 'nevada' },
  { id: 'bobs-boulevard', name: "Bob's Boulevard", difficulty: 'double-black', peak: 'nevada' },
  { id: 'bohemian-grove', name: 'Bohemian Grove', difficulty: 'black', peak: 'nevada' },
  { id: 'bonanza', name: 'Bonanza', difficulty: 'blue', peak: 'nevada' },
  { id: 'boulder-bowl', name: 'Boulder Bowl', difficulty: 'green', peak: 'nevada' },
  { id: 'boulder-chute', name: 'Boulder Chute', difficulty: 'blue', peak: 'nevada' },
  { id: 'boundary-chutes', name: 'Boundary Chutes', difficulty: 'double-black', peak: 'nevada' },
  { id: 'cloud-nine', name: 'Cloud Nine', difficulty: 'blue', peak: 'nevada' },
  { id: 'comet', name: 'Comet', difficulty: 'blue', peak: 'nevada' },
  { id: 'comstock', name: 'Comstock', difficulty: 'blue', peak: 'nevada' },
  { id: 'cosmic-wave', name: 'Cosmic Wave', difficulty: 'blue', peak: 'nevada' },
  { id: 'crossover', name: 'Crossover', difficulty: 'blue', peak: 'nevada' },
  { id: 'dipper-bowl', name: 'Dipper Bowl', difficulty: 'black', peak: 'nevada' },
  { id: 'dipper-line', name: 'Dipper Line', difficulty: 'black', peak: 'nevada' },
  { id: 'dipper-return-lower', name: 'Dipper Return Lower', difficulty: 'blue', peak: 'nevada' },
  { id: 'dipper-return-upper', name: 'Dipper Return Upper', difficulty: 'blue', peak: 'nevada' },
  { id: 'dipper-woods', name: 'Dipper Woods', difficulty: 'black', peak: 'nevada', isGlade: true },
  { id: 'emilys-run', name: "Emily's Run", difficulty: 'blue', peak: 'nevada' },
  { id: 'ernies', name: "Ernie's", difficulty: 'double-black', peak: 'nevada' },
  { id: 'galaxy', name: 'Galaxy', difficulty: 'blue', peak: 'nevada' },
  { id: 'galaxy-line', name: 'Galaxy Line', difficulty: 'blue', peak: 'nevada' },
  { id: 'hemlock', name: 'Hemlock', difficulty: 'double-black', peak: 'nevada' },
  { id: 'hully-gully', name: 'Hully Gully', difficulty: 'double-black', peak: 'nevada' },
  { id: 'jacks', name: "Jack's", difficulty: 'blue', peak: 'nevada' },
  { id: 'killebrew-canyon', name: 'Killebrew Canyon', difficulty: 'double-black', peak: 'nevada' },
  { id: 'little-dipper', name: 'Little Dipper', difficulty: 'black', peak: 'nevada' },
  { id: 'lone-wolf', name: 'Lone Wolf', difficulty: 'double-black', peak: 'nevada' },
  { id: 'meteor', name: 'Meteor', difficulty: 'blue', peak: 'nevada' },
  { id: 'milky-way', name: 'Milky Way', difficulty: 'black', peak: 'nevada' },
  { id: 'milky-way-bowl', name: 'Milky Way Bowl', difficulty: 'black', peak: 'nevada' },
  { id: 'mineshaft', name: 'Mineshaft', difficulty: 'blue', peak: 'nevada' },
  { id: 'mott-canyon', name: 'Mott Canyon', difficulty: 'double-black', peak: 'nevada' },
  { id: 'nevada-trail', name: 'Nevada Trail', difficulty: 'blue', peak: 'nevada' },
  { id: 'nevada-woods', name: 'Nevada Woods', difficulty: 'black', peak: 'nevada', isGlade: true },
  { id: 'north-40', name: 'North 40', difficulty: 'double-black', peak: 'nevada' },
  { id: 'north-bowl', name: 'North Bowl', difficulty: 'black', peak: 'nevada' },
  { id: 'north-bowl-upper', name: 'North Bowl Upper', difficulty: 'blue', peak: 'nevada' },
  { id: 'nova', name: 'Nova', difficulty: 'blue', peak: 'nevada' },
  { id: 'olympic-downhill', name: 'Olympic Downhill', difficulty: 'blue', peak: 'nevada' },
  { id: 'on-hold', name: 'On Hold', difficulty: 'double-black', peak: 'nevada' },
  { id: 'orion', name: 'Orion', difficulty: 'blue', peak: 'nevada' },
  { id: 'orions-belt', name: "Orion's Belt", difficulty: 'blue', peak: 'nevada' },
  { id: 'outer-limits', name: 'Outer Limits', difficulty: 'double-black', peak: 'nevada' },
  { id: 'outlaw', name: 'Outlaw', difficulty: 'blue', peak: 'nevada' },
  { id: 'pepis', name: "Pepi's", difficulty: 'blue', peak: 'nevada' },
  { id: 'perimeter', name: 'Perimeter', difficulty: 'blue', peak: 'nevada' },
  { id: 'perimeter-upper', name: 'Perimeter Upper', difficulty: 'blue', peak: 'nevada' },
  { id: 'pinenuts', name: 'Pinenuts', difficulty: 'double-black', peak: 'nevada' },
  { id: 'pipeline', name: 'Pipeline', difficulty: 'double-black', peak: 'nevada' },
  { id: 'ponderosa', name: 'Ponderosa', difficulty: 'blue', peak: 'nevada' },
  { id: 'promise-land', name: 'Promise Land', difficulty: 'double-black', peak: 'nevada' },
  { id: 'ramarrahs', name: "Ramarrah's", difficulty: 'double-black', peak: 'nevada' },
  { id: 'rim-trail', name: 'Rim Trail', difficulty: 'black', peak: 'nevada' },
  { id: 'rocky-point', name: 'Rocky Point', difficulty: 'double-black', peak: 'nevada' },
  { id: 'sand-dunes', name: 'Sand Dunes', difficulty: 'blue', peak: 'nevada' },
  { id: 'snake-eyes', name: 'Snake Eyes', difficulty: 'double-black', peak: 'nevada' },
  { id: 'southern-comfort', name: 'Southern Comfort', difficulty: 'double-black', peak: 'nevada' },
  { id: 'stagecoach', name: 'Stagecoach', difficulty: 'blue', peak: 'nevada' },
  { id: 'stagecoach-lower', name: 'Stagecoach Lower', difficulty: 'blue', peak: 'nevada' },
  { id: 'stagecoach-return', name: 'Stagecoach Return', difficulty: 'blue', peak: 'nevada' },
  { id: 'stagecoach-woods', name: 'Stagecoach Woods', difficulty: 'black', peak: 'nevada', isGlade: true },
  { id: 'stateline-chute', name: 'Stateline Chute', difficulty: 'double-black', peak: 'nevada' },
  { id: 'sweetwater', name: 'Sweetwater', difficulty: 'double-black', peak: 'nevada' },
  { id: 'the-y', name: 'The "Y"', difficulty: 'double-black', peak: 'nevada' },
  { id: 'the-burn', name: 'The Burn', difficulty: 'black', peak: 'nevada' },
  { id: 'the-fingers', name: 'The Fingers', difficulty: 'double-black', peak: 'nevada' },
  { id: 'the-pines', name: 'The Pines', difficulty: 'blue', peak: 'nevada' },
  { id: '49er', name: '49er', difficulty: 'blue', peak: 'top-of-gondola' },
  { id: 'big-easy', name: 'Big Easy', difficulty: 'green', peak: 'top-of-gondola' },
  { id: 'california-trail', name: 'California Trail', difficulty: 'blue', peak: 'top-of-gondola' },
  { id: 'cascade', name: 'Cascade', difficulty: 'blue', peak: 'top-of-gondola' },
  { id: 'easy-street', name: 'Easy Street', difficulty: 'green', peak: 'top-of-gondola' },
  { id: 'sams-dream', name: "Sam's Dream", difficulty: 'blue', peak: 'top-of-gondola' },
  { id: 'silver-spur', name: 'Silver Spur', difficulty: 'blue', peak: 'top-of-gondola' },
  { id: 'tamarack-return', name: 'Tamarack Return', difficulty: 'blue', peak: 'top-of-gondola' },
  { id: 'von-schmidt', name: 'Von Schmidt', difficulty: 'blue', peak: 'top-of-gondola' },
];
