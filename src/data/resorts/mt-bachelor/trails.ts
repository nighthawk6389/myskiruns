import type { Trail, PeakData } from '../../../types';

// Mt. Bachelor's 2025-26 trail map (James Niehues's painting; the PDF linked
// from mtbachelor.com's trail map page). Its vector layer draws every trail
// line as a filled outline in the run's colour, read by its centre line
// (tools/trailmap/pdf_outline_lines.py), and every name as outlined capitals
// (tools/trailmap/pdf_glyphs.py, shapes read on contact sheets: letters.json).
// A name is printed in a gap of its own line, its symbol at the name's start;
// each piece is named by the name at its end, or settled on a crop
// (decisions.py). Ten names whose letters the PDF draws grouped by shape
// (Green Flash, Morning Glory, Early Riser and Day Break at Sunrise, Shorty,
// Fish Hawk Wing, Marshmallow, West Boundary, Volcano Adventure Zone, Start
// Park) are placed by hand where printed. Names are spelled as the trail
// report spells them (report.json: the resort's DOR trail list): Bushwacker,
// Northwest Crossover, Halfpipe, Backside Bowls & Glades, West Bowls &
// Glades. The report's runs split into (upper), (middle) and (lower) are one
// trail each, as the map prints them, but Sunrise Getback, whose three parts
// are printed apart with their own symbols. Difficulty is the symbol printed
// with each name; a run printed with two takes the one printed more often, a
// tie the harder (I-5 green; Carnival, Leeway, Avalanche blue; Canyon black).
// Serengeti Plains prints one diamond (the report: double black): the map's
// kept. The Moraine and The Cone print no symbol: black, as the report rates
// them; the adventure zones green. The report's Avalanche West and Cloudchaser
// Access aren't on this map. 36 names have no drawn line (the summit's bowls
// and chutes, tree runs, the Woodward parks): markers at the label; the two
// Bowls & Glades are glades. Areas are the report's sectors, the parks with
// the side they're on. x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'summit', name: 'Summit', elevation: 9065, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'westside', name: 'Westside', elevation: 8065, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'frontside', name: 'Frontside', elevation: 7775, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'eastside', name: 'Eastside', elevation: 7258, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'backside-bowls-glades', name: 'Backside Bowls & Glades', difficulty: 'double-black', peak: 'summit', isGlade: true },
  { id: 'bevs-east', name: "Bev's East", difficulty: 'blue', peak: 'summit' },
  { id: 'beverly-hills', name: 'Beverly Hills', difficulty: 'blue', peak: 'summit' },
  { id: 'cirque-bowl', name: 'Cirque Bowl', difficulty: 'double-black', peak: 'summit' },
  { id: 'cows-face', name: "Cow's Face", difficulty: 'black', peak: 'summit' },
  { id: 'east-healy', name: 'East Healy', difficulty: 'blue', peak: 'summit' },
  { id: 'healy-heights', name: 'Healy Heights', difficulty: 'blue', peak: 'summit' },
  { id: 'hourglass', name: 'Hourglass', difficulty: 'double-black', peak: 'summit' },
  { id: 'pinnacles', name: 'Pinnacles', difficulty: 'double-black', peak: 'summit' },
  { id: 'serengeti-plains', name: 'Serengeti Plains', difficulty: 'black', peak: 'summit' },
  { id: 'sunrise-getback-upper', name: 'Sunrise Getback (upper)', difficulty: 'black', peak: 'summit' },
  { id: 'the-moraine', name: 'The Moraine', difficulty: 'black', peak: 'summit' },
  { id: 'wanoga-way', name: 'Wanoga Way', difficulty: 'blue', peak: 'summit' },
  { id: 'west-ridge', name: 'West Ridge', difficulty: 'black', peak: 'summit' },
  { id: '21-road', name: '21 Road', difficulty: 'blue', peak: 'westside' },
  { id: 'atkesons-zoom', name: "Atkeson's Zoom", difficulty: 'black', peak: 'westside' },
  { id: 'aussie-alley', name: 'Aussie Alley', difficulty: 'blue', peak: 'westside' },
  { id: 'boomerang', name: 'Boomerang', difficulty: 'black', peak: 'westside' },
  { id: 'brookies-run', name: "Brookie's Run", difficulty: 'black', peak: 'westside' },
  { id: 'bushwacker', name: 'Bushwacker', difficulty: 'black', peak: 'westside' },
  { id: 'chadalak', name: 'Chadalak', difficulty: 'blue', peak: 'westside' },
  { id: 'devils-backbone', name: "Devil's Backbone", difficulty: 'black', peak: 'westside' },
  { id: 'devils-east', name: "Devil's East", difficulty: 'black', peak: 'westside' },
  { id: 'devils-west', name: "Devil's West", difficulty: 'black', peak: 'westside' },
  { id: 'downunder', name: 'Downunder', difficulty: 'blue', peak: 'westside' },
  { id: 'downunder-west', name: 'Downunder West', difficulty: 'black', peak: 'westside' },
  { id: 'fish-hawk-wing', name: 'Fish Hawk Wing', difficulty: 'blue', peak: 'westside' },
  { id: 'huckleberry-picker', name: 'Huckleberry Picker', difficulty: 'blue', peak: 'westside' },
  { id: 'kangaroo', name: 'Kangaroo', difficulty: 'blue', peak: 'westside' },
  { id: 'melbourne', name: 'Melbourne', difficulty: 'blue', peak: 'westside' },
  { id: 'northwest-connection', name: 'Northwest Connection', difficulty: 'blue', peak: 'westside' },
  { id: 'northwest-crossover', name: 'Northwest Crossover', difficulty: 'blue', peak: 'westside' },
  { id: 'osprey-way', name: 'Osprey Way', difficulty: 'black', peak: 'westside' },
  { id: 'snapshot-alley', name: 'Snapshot Alley', difficulty: 'black', peak: 'westside' },
  { id: 'snapshot-bowl', name: 'Snapshot Bowl', difficulty: 'black', peak: 'westside' },
  { id: 'sparks-lake-bowl', name: 'Sparks Lake Bowl', difficulty: 'black', peak: 'westside' },
  { id: 'sparks-lake-run', name: 'Sparks Lake Run', difficulty: 'black', peak: 'westside' },
  { id: 'west-bowls-glades', name: 'West Bowls & Glades', difficulty: 'double-black', peak: 'westside', isGlade: true },
  { id: 'west-catchline', name: 'West Catchline', difficulty: 'black', peak: 'westside' },
  { id: 'avalanche', name: 'Avalanche', difficulty: 'blue', peak: 'frontside' },
  { id: 'cannon-beach', name: 'Cannon Beach', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'canyon', name: 'Canyon', difficulty: 'black', peak: 'frontside' },
  { id: 'carys-runway', name: "Cary's Runway", difficulty: 'blue', peak: 'frontside' },
  { id: 'cliffs-run', name: "Cliff's Run", difficulty: 'blue', peak: 'frontside' },
  { id: 'cliffhanger', name: 'Cliffhanger', difficulty: 'blue', peak: 'frontside' },
  { id: 'coffee', name: 'Coffee', difficulty: 'blue', peak: 'frontside' },
  { id: 'coffee-west', name: 'Coffee West', difficulty: 'blue', peak: 'frontside' },
  { id: 'corkscrew', name: 'Corkscrew', difficulty: 'blue', peak: 'frontside' },
  { id: 'dsq', name: 'DSQ', difficulty: 'blue', peak: 'frontside' },
  { id: 'eds-garden', name: "Ed's Garden", difficulty: 'blue', peak: 'frontside' },
  { id: 'grotto', name: 'Grotto', difficulty: 'black', peak: 'frontside' },
  { id: 'halfpipe', name: 'Halfpipe', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'home-run', name: 'Home Run', difficulty: 'green', peak: 'frontside' },
  { id: 'iceberg', name: 'Iceberg', difficulty: 'blue', peak: 'frontside' },
  { id: 'leeway', name: 'Leeway', difficulty: 'blue', peak: 'frontside' },
  { id: 'little-canyon', name: 'Little Canyon', difficulty: 'black', peak: 'frontside' },
  { id: 'old-skyliner', name: 'Old Skyliner', difficulty: 'blue', peak: 'frontside' },
  { id: 'olympian', name: 'Olympian', difficulty: 'blue', peak: 'frontside' },
  { id: 'olympian-shuttle', name: 'Olympian Shuttle', difficulty: 'blue', peak: 'frontside' },
  { id: 'outback-way', name: 'Outback Way', difficulty: 'blue', peak: 'frontside' },
  { id: 'pacific-city', name: 'Pacific City', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'peace-park', name: 'Peace Park', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'progression-park', name: 'Progression Park', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'red-liftline', name: 'Red Liftline', difficulty: 'black', peak: 'frontside' },
  { id: 'red-shuttle', name: 'Red Shuttle', difficulty: 'blue', peak: 'frontside' },
  { id: 'seaside', name: 'Seaside', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'shorty', name: 'Shorty', difficulty: 'black', peak: 'frontside' },
  { id: 'skyliner-liftline', name: 'Skyliner Liftline', difficulty: 'blue', peak: 'frontside' },
  { id: 'summit-crossover', name: 'Summit Crossover', difficulty: 'green', peak: 'frontside' },
  { id: 'sunshine', name: 'Sunshine', difficulty: 'green', peak: 'frontside' },
  { id: 'the-cone', name: 'The Cone', difficulty: 'black', peak: 'frontside' },
  { id: 'the-point', name: 'The Point', difficulty: 'blue', peak: 'frontside', isTerrainPark: true },
  { id: 'thunderbird', name: 'Thunderbird', difficulty: 'blue', peak: 'frontside' },
  { id: 'tippy-toe', name: 'Tippy Toe', difficulty: 'black', peak: 'frontside' },
  { id: 'west-boundary', name: 'West Boundary', difficulty: 'blue', peak: 'frontside' },
  { id: 'west-village-getback', name: 'West Village Getback', difficulty: 'green', peak: 'frontside' },
  { id: 'alpenglow', name: 'Alpenglow', difficulty: 'green', peak: 'eastside' },
  { id: 'bluebird', name: 'Bluebird', difficulty: 'blue', peak: 'eastside' },
  { id: 'carnival', name: 'Carnival', difficulty: 'blue', peak: 'eastside' },
  { id: 'chicken-foot', name: 'Chicken Foot', difficulty: 'blue', peak: 'eastside' },
  { id: 'cirrus', name: 'Cirrus', difficulty: 'blue', peak: 'eastside' },
  { id: 'clarks-jay', name: "Clark's Jay", difficulty: 'blue', peak: 'eastside' },
  { id: 'cloudchaser-crossover', name: 'Cloudchaser Crossover', difficulty: 'blue', peak: 'eastside' },
  { id: 'convergence-zone', name: 'Convergence Zone', difficulty: 'blue', peak: 'eastside' },
  { id: 'day-break', name: 'Day Break', difficulty: 'green', peak: 'eastside' },
  { id: 'dilly-dally-alley', name: 'Dilly Dally Alley', difficulty: 'green', peak: 'eastside' },
  { id: 'early-riser', name: 'Early Riser', difficulty: 'green', peak: 'eastside' },
  { id: 'east-bowls', name: 'East Bowls', difficulty: 'black', peak: 'eastside' },
  { id: 'east-catchline', name: 'East Catchline', difficulty: 'black', peak: 'eastside' },
  { id: 'enchanted-forest', name: 'Enchanted Forest', difficulty: 'green', peak: 'eastside' },
  { id: 'flying-dutchman', name: 'Flying Dutchman', difficulty: 'blue', peak: 'eastside' },
  { id: 'green-flash', name: 'Green Flash', difficulty: 'green', peak: 'eastside' },
  { id: 'hemlock', name: 'Hemlock', difficulty: 'blue', peak: 'eastside' },
  { id: 'high-pressure', name: 'High Pressure', difficulty: 'blue', peak: 'eastside' },
  { id: 'i-5', name: 'I-5', difficulty: 'green', peak: 'eastside' },
  { id: 'jet-stream', name: 'Jet Stream', difficulty: 'blue', peak: 'eastside' },
  { id: 'low-pressure', name: 'Low Pressure', difficulty: 'blue', peak: 'eastside' },
  { id: 'marshmallow', name: 'Marshmallow', difficulty: 'green', peak: 'eastside' },
  { id: 'morning-glory', name: 'Morning Glory', difficulty: 'green', peak: 'eastside' },
  { id: 'pine-cone', name: 'Pine Cone', difficulty: 'blue', peak: 'eastside' },
  { id: 'rainbow-adventure-zone', name: 'Rainbow Adventure Zone', difficulty: 'green', peak: 'eastside' },
  { id: 'roostertail', name: 'Roostertail', difficulty: 'blue', peak: 'eastside' },
  { id: 'short-sands', name: 'Short Sands', difficulty: 'blue', peak: 'eastside', isTerrainPark: true },
  { id: 'start-park', name: 'Start Park', difficulty: 'blue', peak: 'eastside', isTerrainPark: true },
  { id: 'sun-dog', name: 'Sun Dog', difficulty: 'blue', peak: 'eastside' },
  { id: 'sunrise-getback-lower', name: 'Sunrise Getback (lower)', difficulty: 'green', peak: 'eastside' },
  { id: 'sunrise-getback-middle', name: 'Sunrise Getback (middle)', difficulty: 'blue', peak: 'eastside' },
  { id: 'the-low-east', name: 'The Low East', difficulty: 'black', peak: 'eastside' },
  { id: 'volcano-adventure-zone', name: 'Volcano Adventure Zone', difficulty: 'green', peak: 'eastside' },
  { id: 'white-bark', name: 'White Bark', difficulty: 'blue', peak: 'eastside' },
];
