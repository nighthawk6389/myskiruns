import type { Trail, PeakData } from '../../../types';

// Stevens Pass's winter trail map (stevenspass.com's trail-maps page links
// the 2024-25 edition, 20241115_SV_winter-trail_map_001.pdf; no 2025-26
// file exists under that season's names): two of James Niehues's
// paintings (100 dpi) under one vector layer, the Front Side and Mill
// Valley, each a map panel. Runs are 1.1 to 1.4 pt strokes in their
// colours (dashed: roads and cat tracks; a yellow stroke beside the runs lit
// at night), names outlined black glyphs (pdf_glyphs.py, a font of its own,
// shapes read on contact sheets: letters.json), each printed along its line,
// in a gap of it or beside it, the symbol on the line (two diamonds apart:
// double black). Where one stroke carries two runs it is cut at the second
// one's symbol (Double Diamond / Lower Diamond, Hog Heaven / Hog Wild, Rock
// Garden / Lower Rock Garden, Gemini / Lower Aquarius). Names as printed;
// ratings the printed symbols (Midway, the Mavericks and Training Grounds,
// parks, blue). Thirteen names print no line: the eleven the map calls "for
// reference only, not designated trails or runs" (Big Chief Bowl, Court's
// Meadow, Schim's Meadow, Tye Bowl, Winnie Chutes; Pegasus Gulch, Andromeda
// Face, Waybacks, Orion Chutes, South Park, Polaris), Barrier Bowl and
// Elevator: markers at their names, black. The resort's trail list is empty
// out of season and no capture of it holds a trail: areas are the lifts each
// run is skied from, read on the map, with each lift's top (OpenStreetMap's
// lift on the USGS elevation model). x/y/baseY/width are unused layout
// fields.
export const peaks: PeakData[] = [
  { id: 'seventh-heaven', name: '7th Heaven', elevation: 5659, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'southern-cross', name: 'Southern Cross', elevation: 5601, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'double-diamond', name: 'Double Diamond', elevation: 5595, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'skyline', name: 'Skyline Express', elevation: 5238, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'tye-mill', name: 'Tye Mill', elevation: 5181, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'jupiter', name: 'Jupiter Express', elevation: 5167, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'kehrs-chair', name: "Kehr's Chair", elevation: 4902, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'brooks', name: 'Brooks Express', elevation: 4850, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'hogsback', name: 'Hogsback Express', elevation: 4826, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'daisy', name: 'Daisy', elevation: 4362, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'bobby-chute', name: 'Bobby Chute', difficulty: 'double-black', peak: 'seventh-heaven' },
  { id: 'nancy-chute', name: 'Nancy Chute', difficulty: 'double-black', peak: 'seventh-heaven' },
  { id: 'solitude', name: 'Solitude', difficulty: 'double-black', peak: 'seventh-heaven' },
  { id: 'andromeda-face', name: 'Andromeda Face', difficulty: 'black', peak: 'southern-cross' },
  { id: 'orion', name: 'Orion', difficulty: 'black', peak: 'southern-cross' },
  { id: 'orion-chutes', name: 'Orion Chutes', difficulty: 'black', peak: 'southern-cross' },
  { id: 'pegasus', name: 'Pegasus', difficulty: 'black', peak: 'southern-cross' },
  { id: 'pegasus-gulch', name: 'Pegasus Gulch', difficulty: 'black', peak: 'southern-cross' },
  { id: 'polaris', name: 'Polaris', difficulty: 'black', peak: 'southern-cross' },
  { id: 'south-divide', name: 'South Divide', difficulty: 'blue', peak: 'southern-cross' },
  { id: 'big-chief-bowl', name: 'Big Chief Bowl', difficulty: 'black', peak: 'double-diamond' },
  { id: 'double-diamond', name: 'Double Diamond', difficulty: 'double-black', peak: 'double-diamond' },
  { id: 'lower-diamond', name: 'Lower Diamond', difficulty: 'black', peak: 'double-diamond' },
  { id: 'schims-meadow', name: "Schim's Meadow", difficulty: 'black', peak: 'double-diamond' },
  { id: 'trapper', name: 'Trapper', difficulty: 'black', peak: 'double-diamond' },
  { id: 'wild-katz', name: 'Wild Katz', difficulty: 'double-black', peak: 'double-diamond' },
  { id: 'barrier-bowl', name: 'Barrier Bowl', difficulty: 'black', peak: 'skyline' },
  { id: 'barrier-ridge', name: 'Barrier Ridge', difficulty: 'blue', peak: 'skyline' },
  { id: 'courts-meadow', name: "Court's Meadow", difficulty: 'black', peak: 'skyline' },
  { id: 'exhibition', name: 'Exhibition', difficulty: 'black', peak: 'skyline' },
  { id: 'lower-terminal', name: 'Lower Terminal', difficulty: 'black', peak: 'skyline' },
  { id: 'marmot-meadows', name: 'Marmot Meadows', difficulty: 'blue', peak: 'skyline' },
  { id: 'panorama', name: 'Panorama', difficulty: 'black', peak: 'skyline' },
  { id: 'skyline', name: 'Skyline', difficulty: 'blue', peak: 'skyline' },
  { id: 'winnie-chutes', name: 'Winnie Chutes', difficulty: 'black', peak: 'skyline' },
  { id: 'crest-trail', name: 'Crest Trail', difficulty: 'blue', peak: 'tye-mill' },
  { id: 'promenade', name: 'Promenade', difficulty: 'green', peak: 'tye-mill' },
  { id: 'roller-coaster', name: 'Roller Coaster', difficulty: 'black', peak: 'tye-mill' },
  { id: 'skid-road', name: 'Skid Road', difficulty: 'blue', peak: 'tye-mill' },
  { id: 'tye-bowl', name: 'Tye Bowl', difficulty: 'black', peak: 'tye-mill' },
  { id: 'aquarius', name: 'Aquarius', difficulty: 'blue', peak: 'jupiter' },
  { id: 'aquarius-face', name: 'Aquarius Face', difficulty: 'black', peak: 'jupiter' },
  { id: 'borealis', name: 'Borealis', difficulty: 'black', peak: 'jupiter' },
  { id: 'corona-bowl', name: 'Corona Bowl', difficulty: 'double-black', peak: 'jupiter' },
  { id: 'gemini', name: 'Gemini', difficulty: 'blue', peak: 'jupiter' },
  { id: 'lower-aquarius', name: 'Lower Aquarius', difficulty: 'blue', peak: 'jupiter' },
  { id: 'lower-gemini', name: 'Lower Gemini', difficulty: 'blue', peak: 'jupiter' },
  { id: 'lower-voltage', name: 'Lower Voltage', difficulty: 'black', peak: 'jupiter' },
  { id: 'outer-limits', name: 'Outer Limits', difficulty: 'blue', peak: 'jupiter' },
  { id: 'shooting-star', name: 'Shooting Star', difficulty: 'black', peak: 'jupiter' },
  { id: 'south-park', name: 'South Park', difficulty: 'black', peak: 'jupiter' },
  { id: 'waybacks', name: 'Waybacks', difficulty: 'black', peak: 'jupiter' },
  { id: 'elevator', name: 'Elevator', difficulty: 'black', peak: 'kehrs-chair' },
  { id: 'i-5', name: 'I-5', difficulty: 'black', peak: 'kehrs-chair' },
  { id: 'showcase', name: 'Showcase', difficulty: 'blue', peak: 'kehrs-chair' },
  { id: 'brennans-trail', name: "Brennan's Trail", difficulty: 'blue', peak: 'brooks' },
  { id: 'broadway', name: 'Broadway', difficulty: 'blue', peak: 'brooks' },
  { id: 'lower-mavericks', name: 'Lower Mavericks', difficulty: 'blue', peak: 'brooks', isTerrainPark: true },
  { id: 'midway', name: 'Midway', difficulty: 'blue', peak: 'brooks', isTerrainPark: true },
  { id: 'one-light', name: 'One Light', difficulty: 'blue', peak: 'brooks' },
  { id: 'upper-mavericks', name: 'Upper Mavericks', difficulty: 'blue', peak: 'brooks', isTerrainPark: true },
  { id: 'waterfall', name: 'Waterfall', difficulty: 'blue', peak: 'brooks' },
  { id: 'blue-trail', name: 'Blue Trail', difficulty: 'blue', peak: 'hogsback' },
  { id: 'cloud-9', name: 'Cloud 9', difficulty: 'double-black', peak: 'hogsback' },
  { id: 'hagen-hill', name: 'Hagen Hill', difficulty: 'blue', peak: 'hogsback' },
  { id: 'hog-heaven', name: 'Hog Heaven', difficulty: 'blue', peak: 'hogsback' },
  { id: 'hog-wild', name: 'Hog Wild', difficulty: 'blue', peak: 'hogsback' },
  { id: 'hoot-n-holler', name: "Hoot 'n Holler", difficulty: 'blue', peak: 'hogsback' },
  { id: 'international', name: 'International', difficulty: 'blue', peak: 'hogsback' },
  { id: 'little-tree', name: 'Little Tree', difficulty: 'double-black', peak: 'hogsback' },
  { id: 'lower-rock-garden', name: 'Lower Rock Garden', difficulty: 'black', peak: 'hogsback' },
  { id: 'parachute-1', name: 'Parachute 1', difficulty: 'black', peak: 'hogsback' },
  { id: 'parachute-2', name: 'Parachute 2', difficulty: 'black', peak: 'hogsback' },
  { id: 'rockn-blue', name: "Rock 'n Blue", difficulty: 'blue', peak: 'hogsback' },
  { id: 'rock-garden', name: 'Rock Garden', difficulty: 'double-black', peak: 'hogsback' },
  { id: 'slow-poke', name: 'Slow Poke', difficulty: 'blue', peak: 'hogsback' },
  { id: 'walls-st', name: 'Walls St.', difficulty: 'blue', peak: 'hogsback' },
  { id: '76-road', name: '76 Road', difficulty: 'green', peak: 'daisy' },
  { id: 'easy-street', name: 'Easy Street', difficulty: 'green', peak: 'daisy' },
  { id: 'training-grounds', name: 'Training Grounds', difficulty: 'blue', peak: 'daisy', isTerrainPark: true },
  { id: 'tye-creek', name: 'Tye Creek', difficulty: 'green', peak: 'daisy' },
];
