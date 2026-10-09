import type { Trail, PeakData } from '../../../types';

// Snowmass's 2025-26 trail map (aspensnowmass.com: the resort's "layered" PDF,
// one page), drawn as two panels: the whole mountain, and the inset of Hanging
// Valley, drawn larger with the names of runs the main map leaves unnamed. The
// lines are the PDF's own: blue, black and green strokes, and the expert runs,
// a black line in a yellow casing, by the casing's centre line (a few casings
// are a thin yellow stroke over a black one; a few black lines are pure
// black). Every name is white text on a pill in its run's colour, set along
// its own line: the rating is the pill's colour (green, blue, black), a black
// run double black where its own line is cased in yellow or an EX mark
// (extreme terrain) is printed by its name. Cabin's pill is black (the
// report: blue). Names are spelled as the trail report spells them
// (report.json: the resort's grooming feed); a run the report splits into
// upper and lower parts is one trail as the map prints it, but Green Cabin and
// Banzai (printed apart). The inset's names the report doesn't list (Upper
// Ladder, the walls, the glades) are as printed; its boundary traverse, with
// no name printed, is the report's High Pass (Lower BD), double black as its
// casing. On the whole mountain, Hanging Valley's lines take the inset's names
// (Hanging Valley Glades, Weird Woods, Baby Ruth, High Pass (Lower BD)). Where
// one line carries two runs, decisions.py cuts it where they part (Turkey Trot
// and Funnel, Glissade and Garrett Gulch, Wineskin and Monkshood, Banzai Ridge,
// Coney Glade and Blue Grouse, Coyote Hollow and Timberline, Wildcat and
// Campground, East Wall and the Cirque's traverse); Rock Band Chute's line is
// drawn down along Grinder's, its own from where it leaves it. Names with no
// line (most glades, Buckskin Cliffs, West Garrett, Fanny Hill, Strawberry
// Patch, Union): markers at the label. The uphill routes are left out. Areas:
// the printed summits, each with the report's lift areas whose runs come down
// from it.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'cirque', name: 'Cirque', elevation: 12510, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'high-alpine', name: 'High Alpine', elevation: 11880, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'big-burn', name: 'Big Burn', elevation: 11835, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'elk-camp', name: 'Elk Camp', elevation: 11325, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'sams-knob', name: "Sam's Knob", elevation: 10630, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'a-m-f', name: 'A.M.F.', difficulty: 'double-black', peak: 'cirque' },
  { id: 'buckskin', name: 'Buckskin', difficulty: 'double-black', peak: 'cirque' },
  { id: 'buckskin-cliffs', name: 'Buckskin Cliffs', difficulty: 'double-black', peak: 'cirque' },
  { id: 'burn-cliffs', name: 'Burn Cliffs', difficulty: 'double-black', peak: 'cirque' },
  { id: 'cirque-cornice', name: 'Cirque Cornice', difficulty: 'double-black', peak: 'cirque' },
  { id: 'cirque-dikes', name: 'Cirque Dikes', difficulty: 'double-black', peak: 'cirque' },
  { id: 'cirque-headwall', name: 'Cirque Headwall', difficulty: 'double-black', peak: 'cirque' },
  { id: 'east-wall', name: 'East Wall', difficulty: 'double-black', peak: 'cirque' },
  { id: 'gowdys', name: "Gowdy's", difficulty: 'double-black', peak: 'cirque' },
  { id: 'hang-on-halvins', name: "Hang On Halvin's", difficulty: 'double-black', peak: 'cirque' },
  { id: 'high-pass', name: 'High Pass', difficulty: 'black', peak: 'cirque' },
  { id: 'k-t-gully', name: 'K.T. Gully', difficulty: 'double-black', peak: 'cirque' },
  { id: 'little-headwall', name: 'Little Headwall', difficulty: 'double-black', peak: 'cirque' },
  { id: 'ptarmigan', name: 'Ptarmigan', difficulty: 'double-black', peak: 'cirque' },
  { id: 'rock-island', name: 'Rock Island', difficulty: 'double-black', peak: 'cirque' },
  { id: 'sunkiss-glades', name: 'Sunkiss Glades', difficulty: 'double-black', peak: 'cirque', isGlade: true },
  { id: 'baby-ruth', name: 'Baby Ruth', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'cassidys', name: "Cassidy's", difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'coffee-pot', name: 'Coffee Pot', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'cookies', name: 'Cookies', difficulty: 'black', peak: 'high-alpine' },
  { id: 'frog-pond-glades', name: 'Frog Pond Glades', difficulty: 'black', peak: 'high-alpine', isGlade: true },
  { id: 'galavant', name: 'Galavant', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'glade-one', name: 'Glade One', difficulty: 'double-black', peak: 'high-alpine', isGlade: true },
  { id: 'glade-three', name: 'Glade Three', difficulty: 'double-black', peak: 'high-alpine', isGlade: true },
  { id: 'glade-two', name: 'Glade Two', difficulty: 'double-black', peak: 'high-alpine', isGlade: true },
  { id: 'granite', name: 'Granite', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'green-cabin-lower', name: 'Green Cabin (Lower)', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'green-cabin-upper', name: 'Green Cabin (Upper)', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'grinder', name: 'Grinder', difficulty: 'black', peak: 'high-alpine' },
  { id: 'hanging-valley-glades', name: 'Hanging Valley Glades', difficulty: 'double-black', peak: 'high-alpine', isGlade: true },
  { id: 'hanging-valley-headwall', name: 'Hanging Valley Headwall', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'high-pass-lower-bd', name: 'High Pass (Lower BD)', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'lodgepole', name: 'Lodgepole', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'log-deck', name: 'Log Deck', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'lower-ladder', name: 'Lower Ladder', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'lunkerville', name: 'Lunkerville', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'naked-lady', name: 'Naked Lady', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'possible', name: 'Possible', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'reidars', name: "Reidar's", difficulty: 'black', peak: 'high-alpine' },
  { id: 'robertos', name: "Roberto's", difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'rock-band-chute', name: 'Rock Band Chute', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'showcase', name: 'Showcase', difficulty: 'black', peak: 'high-alpine' },
  { id: 'slider', name: 'Slider', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'strawberry-patch', name: 'Strawberry Patch', difficulty: 'black', peak: 'high-alpine' },
  { id: 'the-edge', name: 'The Edge', difficulty: 'black', peak: 'high-alpine' },
  { id: 'toms-trace', name: "Tom's Trace", difficulty: 'black', peak: 'high-alpine' },
  { id: 'turkey-trot', name: 'Turkey Trot', difficulty: 'blue', peak: 'high-alpine' },
  { id: 'union', name: 'Union', difficulty: 'black', peak: 'high-alpine' },
  { id: 'upper-ladder', name: 'Upper Ladder', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'valley-valley', name: 'Valley Valley', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'wall-one', name: 'Wall One', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'wall-two', name: 'Wall Two', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'waters', name: 'Waters', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'weird-woods', name: 'Weird Woods', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'west-1-2', name: 'West 1 & 2', difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'willys', name: "Willy's", difficulty: 'double-black', peak: 'high-alpine' },
  { id: 'banzai-lower', name: 'Banzai (Lower)', difficulty: 'blue', peak: 'big-burn' },
  { id: 'blue-grouse', name: 'Blue Grouse', difficulty: 'blue', peak: 'big-burn' },
  { id: 'cabin', name: 'Cabin', difficulty: 'black', peak: 'big-burn' },
  { id: 'camp-three', name: 'Camp Three', difficulty: 'black', peak: 'big-burn' },
  { id: 'coney-glade', name: 'Coney Glade', difficulty: 'blue', peak: 'big-burn', isGlade: true },
  { id: 'coyote-hollow', name: 'Coyote Hollow', difficulty: 'blue', peak: 'big-burn' },
  { id: 'dallas-freeway', name: 'Dallas Freeway', difficulty: 'blue', peak: 'big-burn' },
  { id: 'dawdler', name: 'Dawdler', difficulty: 'green', peak: 'big-burn' },
  { id: 'fanny-hill', name: 'Fanny Hill', difficulty: 'green', peak: 'big-burn' },
  { id: 'free-fall', name: 'Free Fall', difficulty: 'black', peak: 'big-burn' },
  { id: 'free-fall-glades', name: 'Free Fall Glades', difficulty: 'black', peak: 'big-burn', isGlade: true },
  { id: 'garrett-gulch', name: 'Garrett Gulch', difficulty: 'black', peak: 'big-burn' },
  { id: 'glissade', name: 'Glissade', difficulty: 'black', peak: 'big-burn' },
  { id: 'hals-hollow', name: "Hal's Hollow", difficulty: 'blue', peak: 'big-burn' },
  { id: 'jack-of-hearts', name: 'Jack of Hearts', difficulty: 'blue', peak: 'big-burn' },
  { id: 'lunchline', name: 'Lunchline', difficulty: 'green', peak: 'big-burn' },
  { id: 'max-park', name: 'Max Park', difficulty: 'blue', peak: 'big-burn' },
  { id: 'micks-gully', name: "Mick's Gully", difficulty: 'blue', peak: 'big-burn' },
  { id: 'monkshood', name: 'Monkshood', difficulty: 'blue', peak: 'big-burn' },
  { id: 'nor-way', name: 'Nor Way', difficulty: 'green', peak: 'big-burn' },
  { id: 'powerline', name: 'Powerline', difficulty: 'black', peak: 'big-burn', isGlade: true },
  { id: 'rocky-mountain-high', name: 'Rocky Mountain High', difficulty: 'blue', peak: 'big-burn' },
  { id: 'scooper', name: 'Scooper', difficulty: 'green', peak: 'big-burn' },
  { id: 'sheer-bliss', name: 'Sheer Bliss', difficulty: 'blue', peak: 'big-burn' },
  { id: 'sneakys', name: "Sneaky's", difficulty: 'blue', peak: 'big-burn' },
  { id: 'sneakys-glades', name: "Sneaky's Glades", difficulty: 'black', peak: 'big-burn', isGlade: true },
  { id: 'timberline', name: 'Timberline', difficulty: 'blue', peak: 'big-burn' },
  { id: 'trestle', name: 'Trestle', difficulty: 'blue', peak: 'big-burn' },
  { id: 'velvet-falls', name: 'Velvet Falls', difficulty: 'blue', peak: 'big-burn' },
  { id: 'west-face', name: 'West Face', difficulty: 'black', peak: 'big-burn' },
  { id: 'west-garrett', name: 'West Garrett', difficulty: 'double-black', peak: 'big-burn' },
  { id: 'whispering-jesse', name: 'Whispering Jesse', difficulty: 'blue', peak: 'big-burn' },
  { id: 'wineskin', name: 'Wineskin', difficulty: 'blue', peak: 'big-burn' },
  { id: 'a-line', name: 'A-Line', difficulty: 'black', peak: 'elk-camp' },
  { id: 'adams-avenue', name: "Adam's Avenue", difficulty: 'blue', peak: 'elk-camp' },
  { id: 'assay-hill', name: 'Assay Hill', difficulty: 'green', peak: 'elk-camp' },
  { id: 'bear-bottom', name: 'Bear Bottom', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'bottoms-up', name: 'Bottoms Up', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'bridges', name: 'Bridges', difficulty: 'green', peak: 'elk-camp' },
  { id: 'bull-run', name: 'Bull Run', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'cascade', name: 'Cascade', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'creekside', name: 'Creekside', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'drumstick', name: 'Drumstick', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'east-branch', name: 'East Branch', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'eddy-out', name: 'Eddy Out', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'funnel', name: 'Funnel', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'funnel-bypass', name: 'Funnel Bypass', difficulty: 'green', peak: 'elk-camp' },
  { id: 'grey-wolf', name: 'Grey Wolf', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'gunners-view', name: "Gunner's View", difficulty: 'blue', peak: 'elk-camp' },
  { id: 'long-shot', name: 'Long Shot', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'no-name', name: 'No Name', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'rio', name: 'Rio', difficulty: 'black', peak: 'elk-camp' },
  { id: 'sandy-park', name: 'Sandy Park', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'split-tree', name: 'Split Tree', difficulty: 'black', peak: 'elk-camp' },
  { id: 'west-fork', name: 'West Fork', difficulty: 'blue', peak: 'elk-camp' },
  { id: 'banzai-ridge', name: 'Banzai Ridge', difficulty: 'blue', peak: 'sams-knob' },
  { id: 'bear-claw', name: 'Bear Claw', difficulty: 'black', peak: 'sams-knob' },
  { id: 'campground', name: 'Campground', difficulty: 'black', peak: 'sams-knob' },
  { id: 'fast-draw', name: 'Fast Draw', difficulty: 'black', peak: 'sams-knob' },
  { id: 'howler', name: 'Howler', difficulty: 'black', peak: 'sams-knob' },
  { id: 'moonshine', name: 'Moonshine', difficulty: 'blue', peak: 'sams-knob' },
  { id: 'powderhorn', name: 'Powderhorn', difficulty: 'double-black', peak: 'sams-knob' },
  { id: 'promenade', name: 'Promenade', difficulty: 'black', peak: 'sams-knob' },
  { id: 'slot', name: 'Slot', difficulty: 'black', peak: 'sams-knob' },
  { id: 'sunnyside', name: 'Sunnyside', difficulty: 'blue', peak: 'sams-knob' },
  { id: 'ute-chute', name: 'Ute Chute', difficulty: 'blue', peak: 'sams-knob' },
  { id: 'wildcat', name: 'Wildcat', difficulty: 'black', peak: 'sams-knob' },
  { id: 'zugspitze', name: 'Zugspitze', difficulty: 'black', peak: 'sams-knob' },
];
