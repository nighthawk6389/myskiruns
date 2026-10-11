import type { Trail, PeakData } from '../../../types';

// Brighton Resort's 2025-26 trail map (brightonresort.com's trail-maps page:
// one Illustrator page, James Niehues's painting under a vector layer). The
// lines are the PDF's own 0.8 pt strokes in the runs' colours (green, blue,
// black; the parks orange), one stroke often carrying a run and the next:
// cut where the next one's symbol or name starts. Names are outlined glyphs
// in Eurostile Condensed Heavy, read from their shapes (five set as text);
// the rating is the symbol printed by the name. Names are spelled as the
// resort's trail report spells them (report.json): Pick 'Em Up, Racecourse
// (Snake Creek Access) for RACE COURSE. The bowls, chutes and glades printed
// with no line are markers at their names (Snake Bowl, Milly Bowl, Elevator,
// Sawbuck, Short Shot, Diagonal Chute, Boll Weevil, Spaghetti, Captain Hook,
// Wally's World); names printed with no symbol are rated by their line's
// colour (Great Divide, Mary Back), or a bowl's or chute's black where they
// have none (Elevator and Wally's World black, Diagonal Chute double black as
// the chutes beside it; Snake Bowl and Milly Bowl as the report rates them).
// The map also names runs the report doesn't list (Boll Weevil, Boundary
// Chute, Captain Hook, Diagonal Chute, Elevator, Elk Park Access, Great
// Western, Hawkeye Access, Scree Chute, Scree Slope, Slalom Hill, Sol Bright
// Access, Spaghetti, Wally's World), each in the area of the lift it is
// reached from; the report's Explorer Main and Simon's Way (the Explorer
// lift's beginner lines) and Upper Majestic park are not named on it. The
// lines no name is printed by (links, run-outs, the boundary's black line)
// have no overlay. Areas: the report's lifts.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'great-western', name: 'Great Western Express', elevation: 10446, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'snake-creek', name: 'Snake Creek Express', elevation: 10138, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'crest', name: 'Crest 6', elevation: 9969, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'milly', name: 'Milly Express', elevation: 9852, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'majestic', name: 'Majestic', elevation: 9481, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'explorer', name: 'Explorer', elevation: 8888, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'terrain-park', name: 'Terrain Park', elevation: 9481, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'aspen-glo', name: 'Aspen Glo', difficulty: 'black', peak: 'great-western' },
  { id: 'boundary-chute', name: 'Boundary Chute', difficulty: 'black', peak: 'great-western' },
  { id: 'clarks-roost', name: "Clark's Roost", difficulty: 'double-black', peak: 'great-western' },
  { id: 'desperado', name: 'Desperado', difficulty: 'black', peak: 'great-western' },
  { id: 'elk-park', name: 'Elk Park', difficulty: 'blue', peak: 'great-western' },
  { id: 'elk-park-access', name: 'Elk Park Access', difficulty: 'blue', peak: 'great-western' },
  { id: 'elk-park-ridge', name: 'Elk Park Ridge', difficulty: 'black', peak: 'great-western' },
  { id: 'endless-winter', name: 'Endless Winter', difficulty: 'double-black', peak: 'great-western' },
  { id: 'golden-needle', name: 'Golden Needle', difficulty: 'blue', peak: 'great-western' },
  { id: 'great-western', name: 'Great Western', difficulty: 'blue', peak: 'great-western' },
  { id: 'old-western', name: 'Old Western', difficulty: 'blue', peak: 'great-western' },
  { id: 'reins-run', name: "Rein's Run", difficulty: 'double-black', peak: 'great-western' },
  { id: 'rockin-r', name: "Rockin' R", difficulty: 'black', peak: 'great-western' },
  { id: 'silver-spur', name: 'Silver Spur', difficulty: 'black', peak: 'great-western' },
  { id: 'true-grit', name: 'True Grit', difficulty: 'double-black', peak: 'great-western' },
  { id: 'wallys-world', name: "Wally's World", difficulty: 'black', peak: 'great-western' },
  { id: 'western-trail', name: 'Western Trail', difficulty: 'blue', peak: 'great-western' },
  { id: 'wrangler', name: 'Wrangler', difficulty: 'black', peak: 'great-western' },
  { id: 'chicken-out', name: 'Chicken Out', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'doyles-dive', name: "Doyle's Dive", difficulty: 'black', peak: 'snake-creek' },
  { id: 'great-divide', name: 'Great Divide', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'hard-coin', name: 'Hard Coin', difficulty: 'double-black', peak: 'snake-creek' },
  { id: 'lonestar', name: 'Lonestar', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'lower-pioneer', name: 'Lower Pioneer', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'lower-thunder-road', name: 'Lower Thunder Road', difficulty: 'green', peak: 'snake-creek' },
  { id: 'pick-em-up', name: 'Pick Em Up', difficulty: 'green', peak: 'snake-creek' },
  { id: 'pine-martin', name: 'Pine Martin', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'pioneer', name: 'Pioneer', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'sawbuck', name: 'Sawbuck', difficulty: 'double-black', peak: 'snake-creek' },
  { id: 'snake-bowl', name: 'Snake Bowl', difficulty: 'double-black', peak: 'snake-creek' },
  { id: 'sunshine', name: 'Sunshine', difficulty: 'green', peak: 'snake-creek' },
  { id: 'thor', name: 'Thor', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'thunderhead', name: 'Thunderhead', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'ziggy', name: 'Ziggy', difficulty: 'blue', peak: 'snake-creek' },
  { id: 'lower-mary', name: 'Lower Mary', difficulty: 'blue', peak: 'crest' },
  { id: 'mary-main', name: 'Mary Main', difficulty: 'blue', peak: 'crest' },
  { id: 'pacific-highway', name: 'Pacific Highway', difficulty: 'blue', peak: 'crest' },
  { id: 'snow-drift', name: 'Snow Drift', difficulty: 'blue', peak: 'crest' },
  { id: 'tantamount', name: 'Tantamount', difficulty: 'blue', peak: 'crest' },
  { id: 'thunder-road', name: 'Thunder Road', difficulty: 'blue', peak: 'crest' },
  { id: 'wintergreen', name: 'Wintergreen', difficulty: 'blue', peak: 'crest' },
  { id: 'wren-hollow', name: 'Wren Hollow', difficulty: 'black', peak: 'crest' },
  { id: 'backbone', name: 'Backbone', difficulty: 'blue', peak: 'milly' },
  { id: 'backdoor', name: 'Backdoor', difficulty: 'blue', peak: 'milly' },
  { id: 'boll-weevil', name: 'Boll Weevil', difficulty: 'black', peak: 'milly' },
  { id: 'canyon', name: 'Canyon', difficulty: 'green', peak: 'milly' },
  { id: 'captain-hook', name: 'Captain Hook', difficulty: 'double-black', peak: 'milly' },
  { id: 'christy-bowl', name: 'Christy Bowl', difficulty: 'blue', peak: 'milly' },
  { id: 'chute-2', name: 'Chute 2', difficulty: 'black', peak: 'milly' },
  { id: 'devils-dip', name: "Devil's Dip", difficulty: 'black', peak: 'milly' },
  { id: 'diagonal-chute', name: 'Diagonal Chute', difficulty: 'double-black', peak: 'milly' },
  { id: 'easy-out', name: 'Easy Out', difficulty: 'blue', peak: 'milly' },
  { id: 'elevator', name: 'Elevator', difficulty: 'black', peak: 'milly' },
  { id: 'evergreen', name: 'Evergreen', difficulty: 'blue', peak: 'milly' },
  { id: 'exhibition', name: 'Exhibition', difficulty: 'black', peak: 'milly' },
  { id: 'little-milly', name: 'Little Milly', difficulty: 'black', peak: 'milly' },
  { id: 'lone-pine', name: 'Lone Pine', difficulty: 'black', peak: 'milly' },
  { id: 'main-street', name: 'Main Street', difficulty: 'green', peak: 'milly' },
  { id: 'majestic-access', name: 'Majestic Access', difficulty: 'blue', peak: 'milly' },
  { id: 'milly-bowl', name: 'Milly Bowl', difficulty: 'black', peak: 'milly' },
  { id: 'perris-bowl', name: 'Perris Bowl', difficulty: 'blue', peak: 'milly' },
  { id: 'randys-chute', name: "Randy's Chute", difficulty: 'double-black', peak: 'milly' },
  { id: 'scree-chute', name: 'Scree Chute', difficulty: 'double-black', peak: 'milly' },
  { id: 'scree-slope', name: 'Scree Slope', difficulty: 'black', peak: 'milly' },
  { id: 'slalom-hill', name: 'Slalom Hill', difficulty: 'blue', peak: 'milly' },
  { id: 'sol-bright-access', name: 'Sol Bright Access', difficulty: 'black', peak: 'milly' },
  { id: 'spaghetti', name: 'Spaghetti', difficulty: 'black', peak: 'milly' },
  { id: 'state-street', name: 'State Street', difficulty: 'green', peak: 'milly' },
  { id: 'waterfall', name: 'Waterfall', difficulty: 'green', peak: 'milly' },
  { id: 'wee-willow', name: 'Wee Willow', difficulty: 'black', peak: 'milly' },
  { id: '2nd-face', name: '2nd Face', difficulty: 'black', peak: 'majestic' },
  { id: 'cat-track', name: 'Cat Track', difficulty: 'blue', peak: 'majestic' },
  { id: 'face', name: 'Face', difficulty: 'black', peak: 'majestic' },
  { id: 'hawkeye', name: 'Hawkeye', difficulty: 'blue', peak: 'majestic' },
  { id: 'hawkeye-access', name: 'Hawkeye Access', difficulty: 'green', peak: 'majestic' },
  { id: 'jbs', name: 'JBs', difficulty: 'blue', peak: 'majestic' },
  { id: 'lost-maid', name: 'Lost Maid', difficulty: 'green', peak: 'majestic' },
  { id: 'lower-majestic', name: 'Lower Majestic', difficulty: 'green', peak: 'majestic' },
  { id: 'majestic-main', name: 'Majestic Main', difficulty: 'blue', peak: 'majestic' },
  { id: 'mary-back', name: 'Mary Back', difficulty: 'green', peak: 'majestic' },
  { id: 'milly-access', name: 'Milly Access', difficulty: 'blue', peak: 'majestic' },
  { id: 'powder-alley', name: 'Powder Alley', difficulty: 'blue', peak: 'majestic' },
  { id: 'racecourse-snake-creek-access', name: 'Racecourse (Snake Creek Access)', difficulty: 'blue', peak: 'majestic' },
  { id: 'ss-traverse', name: 'SS Traverse', difficulty: 'blue', peak: 'majestic' },
  { id: 'scout', name: 'Scout', difficulty: 'blue', peak: 'majestic' },
  { id: 'short-shot', name: 'Short Shot', difficulty: 'black', peak: 'majestic' },
  { id: 'shoulder', name: 'Shoulder', difficulty: 'blue', peak: 'majestic' },
  { id: 'zanes', name: "Zane's", difficulty: 'black', peak: 'majestic' },
  { id: 'candyland', name: 'Candyland', difficulty: 'blue', peak: 'terrain-park', isTerrainPark: true },
  { id: 'my-o-my', name: 'My-O-My', difficulty: 'blue', peak: 'terrain-park', isTerrainPark: true },
  { id: 'pee-wee', name: 'Pee-Wee', difficulty: 'blue', peak: 'terrain-park', isTerrainPark: true },
];
