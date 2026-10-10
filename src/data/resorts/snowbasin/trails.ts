import type { Trail, PeakData } from '../../../types';

// Snowbasin's 2025-26 trail map (snowbasin.com: the resort's PDF, one page,
// James Niehues's painting under vector lines). The lines are the PDF's own:
// black, blue and green strokes; four blue ones drawn as filled outlines (the
// lines under the Blue Grouse and Orson's pills, Coyote Bowl's lower part,
// Sweet Revenge's top) are taken along their middle. Names are text in the
// run's colour, printed along its line; the rating is the symbol on the line
// by the name, else the name's colour (Gordon's, a blue name and a square on
// its line, is black on the report: the map's blue is kept). Names are
// spelled as the trail report spells them (report.json: the mountain report's
// tables, January 2026): LMM is Lower Moose Mound, Needles Run the report's
// Needles, Rainer's its Rainer's Run, Lower Pyramids its Lower Pyramid;
// Trapper's Bypass, Eas-A-Long, Catastrophe Rocks!, Dry Bowl, Staircase, Pig
// Pen, Porky Cirque and the Blue Grouse park are printed but not on the
// report. The report's Powder Puff and Bear Hollow Woods are not printed.
// Where one line carries two runs, decisions.py cuts it where the second
// starts (Twist & Shout and Gordon's Gully, Trappers Trail and Lower Bear
// Springs, the Main Streets and Elk Ridges, Hollywood and Grizzly Finish,
// Grizzly Start and Wildflower Start, Wildcat Ridge and Centennial, Porcupine
// Traverse, Needles and Showboat, Slo Road, Bear Hollow and Snow Shoe). Penny
// Lane is its whole green line, the "Return to Base Area" route from
// Strawberry included; the ridge from the tram's top to No Name's, and the
// links no name is printed on, have no overlay. The bowls and cirques
// (Sister's Bowl, Middle Bowl Cirque, Needles Cirque, Porky Cirque, Mt. Ogden
// Bowl, Lower Pyramid), printed with no line: markers at their names, double
// black by the two diamonds printed by them (Needles Cirque, printed with
// none, by the report; Porky Cirque, not on it, black). Areas: the report's
// lift areas, Porcupine's runs with the Needles'.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'strawberry', name: 'Strawberry', elevation: 9370, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'needles', name: 'Needles', elevation: 9010, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'john-paul', name: 'John Paul', elevation: 9465, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'carnahans', name: "Carnahan's", difficulty: 'black', peak: 'strawberry' },
  { id: 'coyote-bowl', name: 'Coyote Bowl', difficulty: 'blue', peak: 'strawberry' },
  { id: 'gordons', name: "Gordon's", difficulty: 'blue', peak: 'strawberry' },
  { id: 'gordons-gully', name: "Gordon's Gully", difficulty: 'black', peak: 'strawberry' },
  { id: 'gun-tower', name: 'Gun Tower', difficulty: 'black', peak: 'strawberry' },
  { id: 'hohmanns', name: "Hohmann's", difficulty: 'black', peak: 'strawberry' },
  { id: 'last-chance', name: 'Last Chance', difficulty: 'blue', peak: 'strawberry' },
  { id: 'lone-tree', name: 'Lone Tree', difficulty: 'double-black', peak: 'strawberry' },
  { id: 'lower-bear-springs', name: 'Lower Bear Springs', difficulty: 'blue', peak: 'strawberry' },
  { id: 'lower-elk-ridge', name: 'Lower Elk Ridge', difficulty: 'blue', peak: 'strawberry' },
  { id: 'lower-main-street', name: 'Lower Main Street', difficulty: 'blue', peak: 'strawberry' },
  { id: 'mid-elk-ridge', name: 'Mid Elk Ridge', difficulty: 'blue', peak: 'strawberry' },
  { id: 'mid-main-street', name: 'Mid Main Street', difficulty: 'blue', peak: 'strawberry' },
  { id: 'middle-bowl-cirque', name: 'Middle Bowl Cirque', difficulty: 'double-black', peak: 'strawberry' },
  { id: 'moonshine-bowl', name: 'Moonshine Bowl', difficulty: 'black', peak: 'strawberry' },
  { id: 'needles-cirque', name: 'Needles Cirque', difficulty: 'double-black', peak: 'strawberry' },
  { id: 'sisters-bowl', name: "Sister's Bowl", difficulty: 'double-black', peak: 'strawberry' },
  { id: 'smokeys', name: "Smokey's", difficulty: 'black', peak: 'strawberry' },
  { id: 'sow-back', name: 'Sow Back', difficulty: 'black', peak: 'strawberry' },
  { id: 'strawberry-fields', name: 'Strawberry Fields', difficulty: 'black', peak: 'strawberry' },
  { id: 'sun-king', name: 'Sun King', difficulty: 'blue', peak: 'strawberry' },
  { id: 'the-diamond', name: 'The Diamond', difficulty: 'black', peak: 'strawberry' },
  { id: 'the-walrus', name: 'The Walrus', difficulty: 'black', peak: 'strawberry' },
  { id: 'trappers-bypass', name: "Trapper's Bypass", difficulty: 'blue', peak: 'strawberry' },
  { id: 'trappers-trail', name: 'Trappers Trail', difficulty: 'blue', peak: 'strawberry' },
  { id: 'twist-shout', name: 'Twist & Shout', difficulty: 'black', peak: 'strawberry' },
  { id: 'upper-bear-springs', name: 'Upper Bear Springs', difficulty: 'blue', peak: 'strawberry' },
  { id: 'upper-elk-ridge', name: 'Upper Elk Ridge', difficulty: 'blue', peak: 'strawberry' },
  { id: 'upper-main-street', name: 'Upper Main Street', difficulty: 'black', peak: 'strawberry' },
  { id: 'wfo', name: 'WFO', difficulty: 'black', peak: 'strawberry' },
  { id: 'white-lightning', name: 'White Lightning', difficulty: 'black', peak: 'strawberry' },
  { id: 'white-room', name: 'White Room', difficulty: 'black', peak: 'strawberry' },
  { id: 'wolverine', name: 'Wolverine', difficulty: 'blue', peak: 'strawberry' },
  { id: '119', name: '119', difficulty: 'blue', peak: 'needles' },
  { id: '25th-st', name: '25th St.', difficulty: 'black', peak: 'needles' },
  { id: '3-skis', name: '3 Skis', difficulty: 'black', peak: 'needles' },
  { id: 'bash', name: 'Bash', difficulty: 'black', peak: 'needles' },
  { id: 'bear-hollow', name: 'Bear Hollow', difficulty: 'green', peak: 'needles' },
  { id: 'beaver-slide', name: 'Beaver Slide', difficulty: 'blue', peak: 'needles' },
  { id: 'becker-face', name: 'Becker Face', difficulty: 'blue', peak: 'needles' },
  { id: 'becks', name: 'Becks', difficulty: 'black', peak: 'needles' },
  { id: 'blue-grouse', name: 'Blue Grouse', difficulty: 'blue', peak: 'needles', isTerrainPark: true },
  { id: 'boardwalk', name: 'Boardwalk', difficulty: 'blue', peak: 'needles' },
  { id: 'bobcat-ridge', name: 'Bobcat Ridge', difficulty: 'black', peak: 'needles' },
  { id: 'bullwinkle', name: 'Bullwinkle', difficulty: 'blue', peak: 'needles' },
  { id: 'catastrophe-rocks', name: 'Catastrophe Rocks!', difficulty: 'black', peak: 'needles' },
  { id: 'centennial', name: 'Centennial', difficulty: 'black', peak: 'needles' },
  { id: 'cirque', name: 'Cirque', difficulty: 'black', peak: 'needles' },
  { id: 'city-hill', name: 'City Hill', difficulty: 'blue', peak: 'needles' },
  { id: 'dans-run', name: "Dan's Run", difficulty: 'blue', peak: 'needles' },
  { id: 'dog-leg', name: 'Dog Leg', difficulty: 'blue', peak: 'needles' },
  { id: 'dwaynes', name: "Dwayne's", difficulty: 'black', peak: 'needles' },
  { id: 'eas-a-long', name: 'Eas-A-Long', difficulty: 'green', peak: 'needles' },
  { id: 'fro-zone', name: 'Fro Zone', difficulty: 'black', peak: 'needles' },
  { id: 'grizz', name: 'Grizz', difficulty: 'black', peak: 'needles' },
  { id: 'harolds', name: "Harold's", difficulty: 'blue', peak: 'needles' },
  { id: 'herberts', name: "Herbert's", difficulty: 'blue', peak: 'needles' },
  { id: 'littlecat', name: 'Littlecat', difficulty: 'green', peak: 'needles' },
  { id: 'littlecat-terrain-park', name: 'Littlecat Terrain Park', difficulty: 'green', peak: 'needles', isTerrainPark: true },
  { id: 'lo-fro-zone', name: 'Lo Fro Zone', difficulty: 'blue', peak: 'needles' },
  { id: 'lower-moose-mound', name: 'Lower Moose Mound', difficulty: 'blue', peak: 'needles' },
  { id: 'middle-bowl-traverse', name: 'Middle Bowl Traverse', difficulty: 'blue', peak: 'needles' },
  { id: 'moose-mound', name: 'Moose Mound', difficulty: 'black', peak: 'needles' },
  { id: 'needles', name: 'Needles', difficulty: 'blue', peak: 'needles' },
  { id: 'needles-way', name: 'Needles Way', difficulty: 'green', peak: 'needles' },
  { id: 'orsons', name: "Orson's", difficulty: 'blue', peak: 'needles', isTerrainPark: true },
  { id: 'penny-lane', name: 'Penny Lane', difficulty: 'green', peak: 'needles' },
  { id: 'pfeiffalina', name: 'Pfeiffalina', difficulty: 'black', peak: 'needles' },
  { id: 'philpot-ridge', name: 'Philpot Ridge', difficulty: 'black', peak: 'needles' },
  { id: 'pineview', name: 'Pineview', difficulty: 'black', peak: 'needles' },
  { id: 'porcupine-traverse', name: 'Porcupine Traverse', difficulty: 'blue', peak: 'needles' },
  { id: 'pork-barrel', name: 'Pork Barrel', difficulty: 'black', peak: 'needles' },
  { id: 'porky-cirque', name: 'Porky Cirque', difficulty: 'black', peak: 'needles' },
  { id: 'porky-face', name: 'Porky Face', difficulty: 'blue', peak: 'needles' },
  { id: 'powderhound-bowl', name: 'Powderhound Bowl', difficulty: 'black', peak: 'needles' },
  { id: 'rainers-run', name: "Rainer's Run", difficulty: 'blue', peak: 'needles' },
  { id: 'rocky-j', name: 'Rocky J', difficulty: 'black', peak: 'needles' },
  { id: 'school-hill', name: 'School Hill', difficulty: 'blue', peak: 'needles' },
  { id: 'showboat', name: 'Showboat', difficulty: 'blue', peak: 'needles' },
  { id: 'slo-road', name: 'Slo Road', difficulty: 'green', peak: 'needles' },
  { id: 'snow-shoe', name: 'Snow Shoe', difficulty: 'green', peak: 'needles' },
  { id: 'squirrel', name: 'Squirrel', difficulty: 'green', peak: 'needles' },
  { id: 'steins', name: "Stein's", difficulty: 'blue', peak: 'needles' },
  { id: 'strawberry-traverse', name: 'Strawberry Traverse', difficulty: 'blue', peak: 'needles' },
  { id: 'sunny-side', name: 'Sunny Side', difficulty: 'blue', peak: 'needles' },
  { id: 'sunshine', name: 'Sunshine', difficulty: 'blue', peak: 'needles' },
  { id: 'sunshine-bowl', name: 'Sunshine Bowl', difficulty: 'black', peak: 'needles' },
  { id: 'surprise', name: 'Surprise', difficulty: 'black', peak: 'needles' },
  { id: 'sweet-revenge', name: 'Sweet Revenge', difficulty: 'blue', peak: 'needles' },
  { id: 'the-flank', name: 'The Flank', difficulty: 'double-black', peak: 'needles' },
  { id: 'the-wallow', name: 'The Wallow', difficulty: 'black', peak: 'needles' },
  { id: 'two-bit-street', name: 'Two Bit Street', difficulty: 'blue', peak: 'needles' },
  { id: 'upper-119', name: 'Upper 119', difficulty: 'black', peak: 'needles' },
  { id: 'utah-express', name: 'Utah Express', difficulty: 'black', peak: 'needles' },
  { id: 'wildcat-bowl', name: 'Wildcat Bowl', difficulty: 'blue', peak: 'needles' },
  { id: 'wildcat-ridge', name: 'Wildcat Ridge', difficulty: 'black', peak: 'needles' },
  { id: 'wildcat-traverse', name: 'Wildcat Traverse', difficulty: 'blue', peak: 'needles' },
  { id: 'willow', name: 'Willow', difficulty: 'blue', peak: 'needles' },
  { id: 'womens-gs', name: "Women's GS", difficulty: 'black', peak: 'needles' },
  { id: 'deanes', name: "Deane's", difficulty: 'black', peak: 'john-paul' },
  { id: 'dry-bowl', name: 'Dry Bowl', difficulty: 'black', peak: 'john-paul' },
  { id: 'easter-bowl', name: 'Easter Bowl', difficulty: 'black', peak: 'john-paul' },
  { id: 'ellisons', name: "Ellison's", difficulty: 'black', peak: 'john-paul' },
  { id: 'fts', name: 'FTS', difficulty: 'black', peak: 'john-paul' },
  { id: 'grizzly-downhill', name: 'Grizzly Downhill', difficulty: 'black', peak: 'john-paul' },
  { id: 'grizzly-finish', name: 'Grizzly Finish', difficulty: 'black', peak: 'john-paul' },
  { id: 'grizzly-start', name: 'Grizzly Start', difficulty: 'black', peak: 'john-paul' },
  { id: 'hollywood', name: 'Hollywood', difficulty: 'black', peak: 'john-paul' },
  { id: 'janis', name: "Janis'", difficulty: 'black', peak: 'john-paul' },
  { id: 'john-paul-face', name: 'John Paul Face', difficulty: 'black', peak: 'john-paul' },
  { id: 'lower-pyramid', name: 'Lower Pyramid', difficulty: 'double-black', peak: 'john-paul' },
  { id: 'mt-ogden-bowl', name: 'Mt. Ogden Bowl', difficulty: 'double-black', peak: 'john-paul' },
  { id: 'mt-ogden-bowl-road', name: 'Mt. Ogden Bowl Road', difficulty: 'blue', peak: 'john-paul' },
  { id: 'no-name', name: 'No Name', difficulty: 'black', peak: 'john-paul' },
  { id: 'parsons', name: "Parson's", difficulty: 'black', peak: 'john-paul' },
  { id: 'pig-pen', name: 'Pig Pen', difficulty: 'black', peak: 'john-paul' },
  { id: 'roys', name: "Roy's", difficulty: 'black', peak: 'john-paul' },
  { id: 'shooting-star', name: 'Shooting Star', difficulty: 'black', peak: 'john-paul' },
  { id: 'snow-king', name: 'Snow King', difficulty: 'black', peak: 'john-paul' },
  { id: 'staircase', name: 'Staircase', difficulty: 'black', peak: 'john-paul' },
  { id: 'the-burn', name: 'The Burn', difficulty: 'black', peak: 'john-paul' },
  { id: 'the-jungle', name: 'The Jungle', difficulty: 'black', peak: 'john-paul' },
  { id: 'wildflower-downhill', name: 'Wildflower Downhill', difficulty: 'black', peak: 'john-paul' },
  { id: 'wildflower-finish', name: 'Wildflower Finish', difficulty: 'black', peak: 'john-paul' },
  { id: 'wildflower-start', name: 'Wildflower Start', difficulty: 'black', peak: 'john-paul' },
];
