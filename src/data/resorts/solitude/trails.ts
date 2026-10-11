import type { Trail, PeakData } from '../../../types';

// Solitude Mountain Resort's 2025-26 trail map (solitudemountain.com's PDF:
// one flattened image of James Niehues's painting, with the Highway to Heaven
// inset top left). The lines and names are its interactive map's
// (resorts-interactive.com map 1811), whose SVG is this map's vector layer
// drawn again, every trail's line, letters and symbol grouped under its name;
// registered on the image (median 0.44 px to the print's own line ink). The
// runs print no symbol: each is rated by the colour of its line and name
// (green, blue, black), the expert areas by the diamond or two printed over
// their names; Tude Dudes, printed green (the interactive map's letters
// blue), green as the report has it. Names are spelled as the resort's trail
// report spells them (report.json); Sundancer, printed once along one line
// (the report's Upper and Lower), is one trail. The bowls, chutes, faces and
// glades printed with no line are markers at their names, and so is the
// Highway to Heaven, printed only in the inset. Not on this map: the Nordic
// area's cross-country and snowshoe trails, and the report's two terrain
// parks (Main Street, Upper Tude Dudes), drawn as features with no name.
// Areas: the report's.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'honeycomb-canyon', name: 'Honeycomb Canyon', elevation: 10488, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'fantasy-ridge', name: 'Fantasy Ridge', elevation: 10479, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'highway-to-heaven', name: 'Highway to Heaven', elevation: 10479, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'solitude-canyon', name: 'Solitude Canyon', elevation: 10035, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'evergreen-peak', name: 'Evergreen Peak', elevation: 9850, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'eagle-ridge', name: 'Eagle Ridge', elevation: 9345, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'moonbeam', name: 'Moonbeam Area', elevation: 8756, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'black-bess', name: 'Black Bess', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'black-forest', name: 'Black Forest', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'boundary-chutes', name: 'Boundary Chutes', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'buckeye-junior', name: 'Buckeye Junior', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'crystal-point', name: 'Crystal Point', difficulty: 'double-black', peak: 'honeycomb-canyon' },
  { id: 'here-be-dragons', name: 'Here Be Dragons', difficulty: 'double-black', peak: 'honeycomb-canyon' },
  { id: 'honeycomb-return', name: 'Honeycomb Return', difficulty: 'blue', peak: 'honeycomb-canyon' },
  { id: 'memorial-chutes', name: 'Memorial Chutes', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'navarone', name: 'Navarone', difficulty: 'double-black', peak: 'honeycomb-canyon' },
  { id: 'no-mans-land', name: "No Man's Land", difficulty: 'double-black', peak: 'honeycomb-canyon' },
  { id: 'prince-of-wales', name: 'Prince of Wales', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'queen-bess', name: 'Queen Bess', difficulty: 'double-black', peak: 'honeycomb-canyon' },
  { id: 'voltaire', name: 'Voltaire', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'woodlawn', name: 'Woodlawn', difficulty: 'black', peak: 'honeycomb-canyon' },
  { id: 'black-bess-chutes', name: 'Black Bess Chutes', difficulty: 'double-black', peak: 'fantasy-ridge' },
  { id: 'honeycomb-chutes', name: 'Honeycomb Chutes', difficulty: 'double-black', peak: 'fantasy-ridge' },
  { id: 'highway-to-heaven', name: 'Highway to Heaven', difficulty: 'double-black', peak: 'highway-to-heaven' },
  { id: 'alta-bird', name: 'Alta Bird', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'back-door', name: 'Back Door', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'broadway', name: 'Broadway', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'cathedral-cirque', name: 'Cathedral Cirque', difficulty: 'double-black', peak: 'solitude-canyon' },
  { id: 'corner-chute', name: 'Corner Chute', difficulty: 'black', peak: 'solitude-canyon' },
  { id: 'dynamite', name: 'Dynamite', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'front-door', name: 'Front Door', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'headwall-forest', name: 'Headwall Forest', difficulty: 'double-black', peak: 'solitude-canyon' },
  { id: 'liberty', name: 'Liberty', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'middle-slope', name: 'Middle Slope', difficulty: 'double-black', peak: 'solitude-canyon' },
  { id: 'milk-run', name: 'Milk Run', difficulty: 'double-black', peak: 'solitude-canyon' },
  { id: 'mine', name: 'Mine', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'north-star', name: 'North Star', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'parachute', name: 'Parachute', difficulty: 'double-black', peak: 'solitude-canyon' },
  { id: 'polaris', name: 'Polaris', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'powderhorn-cirque', name: 'Powderhorn Cirque', difficulty: 'black', peak: 'solitude-canyon' },
  { id: 'roller-coaster', name: 'Roller Coaster', difficulty: 'black', peak: 'solitude-canyon' },
  { id: 'scree-slope', name: 'Scree Slope', difficulty: 'black', peak: 'solitude-canyon' },
  { id: 'sensation', name: 'Sensation', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'shaft', name: 'Shaft', difficulty: 'black', peak: 'solitude-canyon' },
  { id: 'solbright', name: 'SolBright', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'south-star', name: 'South Star', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'summit-access-east', name: 'Summit Access East', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'summit-access-west', name: 'Summit Access West', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'timberline', name: 'Timberline', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'zip-a-dee', name: 'Zip-A-Dee', difficulty: 'blue', peak: 'solitude-canyon' },
  { id: 'barretts-glade', name: "Barrett's Glade", difficulty: 'double-black', peak: 'evergreen-peak', isGlade: true },
  { id: 'dead-tree', name: 'Dead Tree', difficulty: 'double-black', peak: 'evergreen-peak' },
  { id: 'evening-star', name: 'Evening Star', difficulty: 'black', peak: 'evergreen-peak' },
  { id: 'evergreen-chutes', name: 'Evergreen Chutes', difficulty: 'double-black', peak: 'evergreen-peak' },
  { id: 'abbas-alley', name: "Abba's Alley", difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'blue-spruce', name: 'Blue Spruce', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'challenger', name: 'Challenger', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'concord', name: 'Concord', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'diamond-lane', name: 'Diamond Lane', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'eagle-ridge', name: 'Eagle Ridge', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'fleet-street', name: 'Fleet Street', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'fluid-drive', name: 'Fluid Drive', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'garys-glade', name: "Gary's Glade", difficulty: 'blue', peak: 'eagle-ridge', isGlade: true },
  { id: 'grumble-lower', name: 'Grumble Lower', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'grumble-upper', name: 'Grumble Upper', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'hals-hollow', name: "Hal's Hollow", difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'inspiration-lower', name: 'Inspiration Lower', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'inspiration-upper', name: 'Inspiration Upper', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'main-street', name: 'Main Street', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'olympia', name: 'Olympia', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'paradise', name: 'Paradise', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'paradise-lost', name: 'Paradise Lost', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'post-card', name: 'Post Card', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'rhapsody', name: 'Rhapsody', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'rumble-lower', name: 'Rumble Lower', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'rumble-upper', name: 'Rumble Upper', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'serenity-lower', name: 'Serenity Lower', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'serenity-upper', name: 'Serenity Upper', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'shady-lane', name: 'Shady Lane', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'stumble-lower', name: 'Stumble Lower', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'stumble-upper', name: 'Stumble Upper', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'sundancer', name: 'Sundancer', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'sunshine-bowl', name: 'Sunshine Bowl', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'tbd', name: 'TBD', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'vertigo', name: 'Vertigo', difficulty: 'black', peak: 'eagle-ridge' },
  { id: 'wall-street', name: 'Wall Street', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'wanderer', name: 'Wanderer', difficulty: 'blue', peak: 'eagle-ridge' },
  { id: 'deans-dash', name: "Dean's Dash", difficulty: 'green', peak: 'moonbeam' },
  { id: 'easy-street', name: 'Easy Street', difficulty: 'green', peak: 'moonbeam' },
  { id: 'home-run', name: 'Home Run', difficulty: 'blue', peak: 'moonbeam' },
  { id: 'last-run', name: 'Last Run', difficulty: 'blue', peak: 'moonbeam' },
  { id: 'little-dollie', name: 'Little Dollie', difficulty: 'green', peak: 'moonbeam' },
  { id: 'same-street', name: 'Same Street', difficulty: 'green', peak: 'moonbeam' },
  { id: 'tude-dudes', name: 'Tude Dudes', difficulty: 'green', peak: 'moonbeam' },
];
