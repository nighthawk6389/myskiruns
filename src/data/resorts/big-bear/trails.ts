import type { Trail, PeakData } from '../../../types';

// Big Bear Mountain Resort's 2025-26 trail maps (bigbearmountainresort.com:
// images only, James Niehues's paintings), one panel per mountain: Snow
// Summit, Bear Mountain and Snow Valley. Names are spelled as the resort's
// mountain report spells them (report.json: the mtnpowder feed). The resort's
// interactive maps (resorts-interactive.com maps 1818, 1808, 1825) draw the
// same paintings with, per run, a group named after it holding its symbols
// and a line. Snow Summit's print draws each run's line: its overlays are the
// print's own lines (colour masks, skeleton pieces), named by the symbol at
// each run's top or settled on crops (decisions.py), its runs in no group
// (Cruiser, Skyline Creek, Sundown, Westridge Park, ZZYZX Park) read on crops
// (names.py). Timber Ridge is one line with one square (the report's Upper
// and Lower), Westridge Park one line with the name printed three times (the
// report's Upper and Lower): one trail each. Comeback Trail and Log Road are
// a square each and no name or line at the summit (named by the interactive
// map's groups; not in the report): markers. Bear Mountain's and Snow Valley's prints paint the
// runs as slopes with no line: their overlays are the interactive map's lines
// as drawn, and for Bear Mountain's runs in no group (Learning Curve, the
// Park Runs, Expressway, The Gulch, the parks' and pipes' runs, Street Scene)
// the stretch along the printed name; Easy Street and Outlaw's Alley traced
// on crops. Snow Valley's interactive map is an older edition: its names and
// symbols were read on the print (names.py), the stretch along the printed
// name added where its line is a stub (Bubble Gum, Lower and Upper Wine Rock,
// Quickie, Thunder Mountain, West Run), and its cat track traced along the
// print's red dashes. Difficulty is the symbol printed by each name; a run
// printed with two ratings takes the report's (Miracle Mile (Upper): squares
// and a diamond, black; Side Chute and Olympic: diamonds and a double
// diamond, double black). Snow Summit's 7 Down is drawn as a green line but
// printed with blue squares: blue. Not on these maps: Snow Valley's The
// Hideout. Backdoors (Bear Mountain) is printed and in the interactive map
// but not in the report. x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'snow-summit', name: 'Snow Summit', elevation: 8200, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'bear-mountain', name: 'Bear Mountain', elevation: 8805, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'snow-valley', name: 'Snow Valley', elevation: 7841, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: '7-down', name: '7 Down', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'bear-bottom-beginner-area', name: 'Bear Bottom Beginner Area', difficulty: 'green', peak: 'snow-summit' },
  { id: 'comeback-trail', name: 'Comeback Trail', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'cruiser', name: 'Cruiser', difficulty: 'green', peak: 'snow-summit' },
  { id: 'dickys', name: "Dicky's", difficulty: 'black', peak: 'snow-summit' },
  { id: 'east-why', name: 'East Why', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'ego-trip', name: 'Ego Trip', difficulty: 'black', peak: 'snow-summit' },
  { id: 'hog-back', name: 'Hog Back', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'jos', name: "Jo's", difficulty: 'blue', peak: 'snow-summit' },
  { id: 'last-chance', name: 'Last Chance', difficulty: 'green', peak: 'snow-summit' },
  { id: 'log-chute-lower', name: 'Log Chute (Lower)', difficulty: 'black', peak: 'snow-summit' },
  { id: 'log-chute-upper', name: 'Log Chute (Upper)', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'log-road', name: 'Log Road', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'mainstream', name: 'Mainstream', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'miracle-mile-lower', name: 'Miracle Mile (Lower)', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'miracle-mile-upper', name: 'Miracle Mile (Upper)', difficulty: 'black', peak: 'snow-summit' },
  { id: 'off-chute', name: 'Off Chute', difficulty: 'black', peak: 'snow-summit' },
  { id: 'olympic', name: 'Olympic', difficulty: 'double-black', peak: 'snow-summit' },
  { id: 'perfect-pitches', name: 'Perfect Pitches', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'pipe-dream', name: 'Pipe Dream', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'side-chute', name: 'Side Chute', difficulty: 'double-black', peak: 'snow-summit' },
  { id: 'side-show', name: 'Side Show', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'skyline-creek', name: 'Skyline Creek', difficulty: 'green', peak: 'snow-summit' },
  { id: 'sugarpine', name: 'Sugarpine', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'summit-connection', name: 'Summit Connection', difficulty: 'green', peak: 'snow-summit' },
  { id: 'summit-run-lower', name: 'Summit Run (Lower)', difficulty: 'green', peak: 'snow-summit' },
  { id: 'summit-run-upper', name: 'Summit Run (Upper)', difficulty: 'green', peak: 'snow-summit' },
  { id: 'sundown', name: 'Sundown', difficulty: 'green', peak: 'snow-summit' },
  { id: 'the-wall', name: 'The Wall', difficulty: 'double-black', peak: 'snow-summit' },
  { id: 'timber-ridge', name: 'Timber Ridge', difficulty: 'blue', peak: 'snow-summit' },
  { id: 'tommis', name: "Tommi's", difficulty: 'black', peak: 'snow-summit' },
  { id: 'westridge-park', name: 'Westridge Park', difficulty: 'blue', peak: 'snow-summit', isTerrainPark: true },
  { id: 'zzyzx-park', name: 'ZZYZX Park', difficulty: 'blue', peak: 'snow-summit', isTerrainPark: true },
  { id: 'accelerator', name: 'Accelerator', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'amusement-park', name: 'Amusement Park', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'backdoors', name: 'Backdoors', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'boneyard', name: 'Boneyard', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'central-park', name: 'Central Park', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'easy-street', name: 'Easy Street', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'exhibition', name: 'Exhibition', difficulty: 'black', peak: 'bear-mountain' },
  { id: 'expressway', name: 'Expressway', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'gambler', name: 'Gambler', difficulty: 'black', peak: 'bear-mountain' },
  { id: 'geronimo', name: 'Geronimo', difficulty: 'double-black', peak: 'bear-mountain' },
  { id: 'grizzly', name: 'Grizzly', difficulty: 'black', peak: 'bear-mountain' },
  { id: 'half-pipe-13ft', name: 'Half Pipe (13ft)', difficulty: 'blue', peak: 'bear-mountain', isTerrainPark: true },
  { id: 'hidden-valley', name: 'Hidden Valley', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'inspiration', name: 'Inspiration', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'learning-curve', name: 'Learning Curve', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'modified-pipe-18ft', name: 'Modified Pipe (18ft)', difficulty: 'blue', peak: 'bear-mountain', isTerrainPark: true },
  { id: 'outlaw', name: 'Outlaw', difficulty: 'black', peak: 'bear-mountain' },
  { id: 'outlaws-alley', name: "Outlaw's Alley", difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'park-run-face', name: 'Park Run (Face)', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'park-run-lower', name: 'Park Run (Lower)', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'park-run-upper', name: 'Park Run (Upper)', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'pipeline-bear-mountain', name: 'Pipeline', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'rips-run', name: "Rip's Run", difficulty: 'black', peak: 'bear-mountain' },
  { id: 'ripcord', name: 'Ripcord', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'showtime', name: 'Showtime', difficulty: 'black', peak: 'bear-mountain' },
  { id: 'silver-connection', name: 'Silver Connection', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'street-scene', name: 'Street Scene', difficulty: 'blue', peak: 'bear-mountain' },
  { id: 'the-gulch', name: 'The Gulch', difficulty: 'green', peak: 'bear-mountain' },
  { id: 'the-wedge', name: 'The Wedge', difficulty: 'double-black', peak: 'bear-mountain' },
  { id: 'big-bowl', name: 'Big Bowl', difficulty: 'black', peak: 'snow-valley' },
  { id: 'bobcat-alley', name: 'Bobcat Alley', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'bubble-gum', name: 'Bubble Gum', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'cat-track', name: 'Cat Track', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'coyote-flats', name: 'Coyote Flats', difficulty: 'green', peak: 'snow-valley' },
  { id: 'eagle-flats', name: 'Eagle Flats', difficulty: 'green', peak: 'snow-valley' },
  { id: 'east-bowl', name: 'East Bowl', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'east-slide', name: 'East Slide', difficulty: 'black', peak: 'snow-valley' },
  { id: 'graduation', name: 'Graduation', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'lake-run', name: 'Lake Run', difficulty: 'black', peak: 'snow-valley' },
  { id: 'little-bowl', name: 'Little Bowl', difficulty: 'black', peak: 'snow-valley' },
  { id: 'lower-wine-rock', name: 'Lower Wine Rock', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'mambo-alley', name: 'Mambo Alley', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'nord-valley', name: 'Nord Valley', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'pipeline-snow-valley', name: 'Pipeline', difficulty: 'black', peak: 'snow-valley' },
  { id: 'quickie', name: 'Quickie', difficulty: 'black', peak: 'snow-valley' },
  { id: 'race-peak', name: 'Race Peak', difficulty: 'black', peak: 'snow-valley' },
  { id: 'richards', name: "Richard's", difficulty: 'blue', peak: 'snow-valley' },
  { id: 'show-me', name: 'Show Me', difficulty: 'double-black', peak: 'snow-valley' },
  { id: 'show-off', name: 'Show Off', difficulty: 'black', peak: 'snow-valley' },
  { id: 'snake-run', name: 'Snake Run', difficulty: 'double-black', peak: 'snow-valley' },
  { id: 'snow-bowl', name: 'Snow Bowl', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'surprise-run', name: 'Surprise Run', difficulty: 'black', peak: 'snow-valley' },
  { id: 'the-chute', name: 'The Chute', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'the-edge', name: 'The EDGE', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'the-face', name: 'The Face', difficulty: 'black', peak: 'snow-valley' },
  { id: 'the-ladder', name: 'The Ladder', difficulty: 'double-black', peak: 'snow-valley' },
  { id: 'thunder-mountain', name: 'Thunder Mountain', difficulty: 'green', peak: 'snow-valley' },
  { id: 'upper-wine-rock', name: 'Upper Wine Rock', difficulty: 'blue', peak: 'snow-valley' },
  { id: 'west-run', name: 'West Run', difficulty: 'black', peak: 'snow-valley' },
  { id: 'west-slide', name: 'West Slide', difficulty: 'blue', peak: 'snow-valley' },
];
