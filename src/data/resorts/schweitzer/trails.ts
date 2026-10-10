import type { Trail, PeakData } from '../../../types';

// Schweitzer's 2025-26 trail maps (schweitzer.com: images only, James
// Niehues's paintings): Schweitzer Bowl, the front side, and Outback Bowl, the
// back side (skimap.org's 2024-25 image of it, the same artwork at a higher
// resolution). The runs are painted slopes with no line drawn: a name printed
// along each, its symbol by it. Each run's overlay is the stretch along its
// printed name, from its symbol (a run printed twice has a stretch at each);
// the names printed on two lines (South Bowl Chutes, Bunny Hills, Lakeside
// Chutes, Wayne's Woods, Short Cut) and the glades (Chair 4 Glades, J.R.
// Trees) are markers at their names. The cat tracks are navy lines: Gypsy,
// Teakettle Trail, The Great Divide, Down the Hatch and Cat Track to Village
// on the front (the resort's interactive map's lines, resorts-interactive.com
// map 1826, routed onto the print's), and The Great Divide, Down the Hatch,
// Vagabond, Cedar Park and Little Blue Ridge Run on the Outback map (read on
// crops, cut at each run's symbol). Names and symbols are the interactive
// maps' (1826 and 1827: each run's letters and symbol grouped under its name,
// the trail report's), put on the prints, and what they lack was read on
// crops (names.py: most of the Outback map's black runs, the parks, Lower
// Loophole). Names are spelled as the trail report spells them (report.json:
// the mtnpowder feed): JIMMIE'S RUN (J.R.) is Jimmy's Run (upper) and
// (lower), UPPER G-3 G-3 (upper), UPPER KANIKSU Kaniksu (upper), LOWER
// LOOPHOLE Loophole (lower); SOUTHSIDE PARK (the interactive map's Crystal),
// Britt's Bowl and South Bowl Chutes are printed and not on the report. Not
// printed: Dogleg, the E to H Chutes, the R Chutes, Headwall Runout, Pend
// Oreille (lower) and (middle), Kaniksu Woods, No Joke Runout, Phineas'
// Runout, Toomey's Runout, Upper Siberia Road, North Bowl Chutes. Runs printed
// on both maps (Caboose, Skid Row, Trial Run, Loophole Loop, The Great Divide,
// Down the Hatch, Cat Track to Village) have an overlay on each. Areas: the
// report's two bowls.
// x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'schweitzer-bowl', name: 'Schweitzer Bowl', elevation: 6389, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'outback-bowl', name: 'Outback Bowl', elevation: 6389, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'a-chute', name: 'A Chute', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'abracadabra', name: 'Abracadabra', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'basin-trail', name: 'Basin Trail', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'bermuda', name: 'Bermuda', difficulty: 'blue', peak: 'schweitzer-bowl', isTerrainPark: true },
  { id: 'britts-bowl', name: "Britt's Bowl", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'buds-chute-b', name: "Bud's Chute (B)", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'bunny-hills', name: 'Bunny Hills', difficulty: 'blue', peak: 'schweitzer-bowl', isTerrainPark: true },
  { id: 'c-chute', name: 'C Chute', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'caboose', name: 'Caboose', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'cat-track-to-village', name: 'Cat Track to Village', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'chair-4-glades', name: 'Chair 4 Glades', difficulty: 'black', peak: 'schweitzer-bowl', isGlade: true },
  { id: 'charlies', name: "Charlie's", difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'down-the-hatch', name: 'Down the Hatch', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'enchanted-forest', name: 'Enchanted Forest', difficulty: 'green', peak: 'schweitzer-bowl' },
  { id: 'gypsy', name: 'Gypsy', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'happy-trails', name: 'Happy Trails', difficulty: 'green', peak: 'schweitzer-bowl' },
  { id: 'headwall', name: 'Headwall', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'heathers-run', name: "Heather's Run", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'jr-trees', name: 'JR Trees', difficulty: 'black', peak: 'schweitzer-bowl', isGlade: true },
  { id: 'jacks-dream', name: "Jack's Dream", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'jimmys-run-lower', name: "Jimmy's Run (lower)", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'jimmys-run-upper', name: "Jimmy's Run (upper)", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'k-macs-d', name: "K-MAC's (D)", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'loophole-lower', name: 'Loophole (lower)', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'loophole-loop', name: 'Loophole Loop', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'midway', name: 'Midway', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'pend-oreille-upper', name: 'Pend Oreille (upper)', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'primetime', name: 'Primetime', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'quicksilver', name: 'Quicksilver', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'ridge-run-lower', name: 'Ridge Run (lower)', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'ridge-run-upper', name: 'Ridge Run (upper)', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'sams-alley-lower', name: "Sam's Alley (lower)", difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'sams-alley-upper', name: "Sam's Alley (upper)", difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'shenanigans', name: 'Shenanigans', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'skid-row', name: 'Skid Row', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'south-bowl-chutes', name: 'South Bowl Chutes', difficulty: 'double-black', peak: 'schweitzer-bowl' },
  { id: 'south-ridge', name: 'South Ridge', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'southside-park', name: 'Southside Park', difficulty: 'blue', peak: 'schweitzer-bowl', isTerrainPark: true },
  { id: 'starfish', name: 'Starfish', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'stiles-lower', name: 'Stiles (lower)', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'stiles-upper', name: 'Stiles (upper)', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'stomping-grounds-terrain-park', name: 'Stomping Grounds Terrain Park', difficulty: 'blue', peak: 'schweitzer-bowl', isTerrainPark: true },
  { id: 'sundance', name: 'Sundance', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'teakettle-trail', name: 'Teakettle Trail', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'the-face', name: 'The Face', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'the-great-divide', name: 'The Great Divide', difficulty: 'blue', peak: 'schweitzer-bowl' },
  { id: 'trial-run', name: 'Trial Run', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'white-lightning', name: 'White Lightning', difficulty: 'black', peak: 'schweitzer-bowl' },
  { id: 'australia', name: 'Australia', difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'blue-grass', name: 'Blue Grass', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'casper', name: 'Casper', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'cathedral-aisle', name: 'Cathedral Aisle', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'cedar-park', name: 'Cedar Park', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'colburn-school', name: 'Colburn School', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'cut-off', name: 'Cut Off', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'debbie-sue', name: 'Debbie Sue', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'detention', name: 'Detention', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'downhill-run', name: 'Downhill Run', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'g-3-lower', name: 'G-3 (lower)', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'g-3-upper', name: 'G-3 (upper)', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'gitback', name: 'Gitback', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'glade-iator', name: 'Glade-iator', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'hall-pass', name: 'Hall Pass', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'have-fun-lower', name: 'Have Fun (lower)', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'have-fun-upper', name: 'Have Fun (upper)', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'home-school', name: 'Home School', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'kaniksu-lower', name: 'Kaniksu (lower)', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'kaniksu-upper', name: 'Kaniksu (upper)', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'kathys-yard-sale', name: "Kathy's Yard Sale", difficulty: 'black', peak: 'outback-bowl' },
  { id: 'know-fun', name: 'Know Fun', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'kohlis-big-timber', name: "Kohli's Big Timber", difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'lakeside-chutes', name: 'Lakeside Chutes', difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'lakeside-runout', name: 'Lakeside Runout', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'little-blue-ridge-run', name: 'Little Blue Ridge Run', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'misfortune', name: 'Misfortune', difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'no-joke', name: 'No Joke', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'north-ridge', name: 'North Ridge', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'phineas-forest', name: "Phineas' Forest", difficulty: 'black', peak: 'outback-bowl' },
  { id: 'puccis-chute', name: "Pucci's Chute", difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'recess', name: 'Recess', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'revenge', name: 'Revenge', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'right-on', name: 'Right On', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'roller-ghoster', name: 'Roller Ghoster', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'sars-spur', name: 'SARS Spur', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'shoot-the-moon', name: 'Shoot the Moon', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'short-cut', name: 'Short Cut', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'siberia', name: 'Siberia', difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'siberia-runout', name: 'Siberia Runout', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'slapshot', name: 'Slapshot', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'snow-ghost-lower', name: 'Snow Ghost (lower)', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'snow-ghost-upper', name: 'Snow Ghost (upper)', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'spring-board', name: 'Spring Board', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'stellas-run', name: "Stella's Run", difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'study-hall', name: 'Study Hall', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'timber-cruiser', name: 'Timber Cruiser', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'toomeys-trail', name: "Toomey's Trail", difficulty: 'black', peak: 'outback-bowl' },
  { id: 'triple-bypass', name: 'Triple Bypass', difficulty: 'black', peak: 'outback-bowl' },
  { id: 'vagabond', name: 'Vagabond', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'waynes-woods', name: "Wayne's Woods", difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'west-cathedral', name: 'West Cathedral', difficulty: 'blue', peak: 'outback-bowl' },
  { id: 'whiplash', name: 'Whiplash', difficulty: 'double-black', peak: 'outback-bowl' },
  { id: 'wills-runout', name: "Will's Runout", difficulty: 'black', peak: 'outback-bowl' },
  { id: 'zip-down', name: 'Zip Down', difficulty: 'blue', peak: 'outback-bowl' },
];
