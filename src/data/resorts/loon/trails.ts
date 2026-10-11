import type { Trail, PeakData } from '../../../types';

// Loon Mountain's winter trail map (loonmtn.com's mountain-maps page: one
// image, 2500x1406 px, in a Photoshop PDF; Rob Smith's painting, the Black
// Ridge expansion shaded in). The print draws no trail lines: each run is a
// cut through the trees with its name and symbol printed in it. The lines are
// the resort's interactive map's (resorts-interactive.com map 14), whose SVG
// draws the same painting with every trail's line, letters and symbol grouped
// under its name, registered on the image (median 0.11 px) and kept as they
// are, down each cut. Names and ratings as the trail report (the reportpal
// feed) and the printed symbols, which agree (the interactive map's own
// symbols differ for Undercut, two diamonds as printed, and Lower Walking Boss
// Woods, one). Lil' Stash (its logo in the woods left of Lower Bear Claw)
// and the Air Site (its freestyle pill under the North Peak lift) are park
// markers; the report's other parks print only a pill or a halfpipe icon on a
// run, no name: left out, as are its Nordic trails and uphill routes. Areas:
// the report's (North Peak, Loon Peak, West Basin, South Peak), with the
// summits printed. x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'north-peak', name: 'North Peak', elevation: 3050, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'loon-peak', name: 'Loon Peak', elevation: 2733, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'west-basin', name: 'West Basin', elevation: 2733, x: 0, y: 0, baseY: 0, width: 0 },
  { id: 'south-peak', name: 'South Peak', elevation: 2461, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'air-site', name: 'Air Site', difficulty: 'blue', peak: 'north-peak', isTerrainPark: true },
  { id: 'bucksaw', name: 'Bucksaw', difficulty: 'black', peak: 'north-peak' },
  { id: 'haulback', name: 'Haulback', difficulty: 'blue', peak: 'north-peak' },
  { id: 'lower-flume', name: 'Lower Flume', difficulty: 'black', peak: 'north-peak' },
  { id: 'lower-walking-boss', name: 'Lower Walking Boss', difficulty: 'blue', peak: 'north-peak' },
  { id: 'lower-walking-boss-woods', name: 'Lower Walking Boss Woods', difficulty: 'black', peak: 'north-peak' },
  { id: 'sunset', name: 'Sunset', difficulty: 'blue', peak: 'north-peak' },
  { id: 'upper-flume', name: 'Upper Flume', difficulty: 'black', peak: 'north-peak' },
  { id: 'upper-walking-boss', name: 'Upper Walking Boss', difficulty: 'black', peak: 'north-peak' },
  { id: 'upper-walking-boss-woods', name: 'Upper Walking Boss Woods', difficulty: 'black', peak: 'north-peak' },
  { id: 'angel-street', name: 'Angel Street', difficulty: 'black', peak: 'loon-peak' },
  { id: 'basin-street', name: 'Basin Street', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'bear-claw-extension', name: 'Bear Claw Extension', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'bear-island-bypass', name: 'Bear Island Bypass', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'bear-pause', name: 'Bear Pause', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'big-dipper', name: 'Big Dipper', difficulty: 'black', peak: 'loon-peak' },
  { id: 'brookway', name: 'Brookway', difficulty: 'green', peak: 'loon-peak' },
  { id: 'brookway-extension', name: 'Brookway Extension', difficulty: 'green', peak: 'loon-peak' },
  { id: 'cant-dog', name: 'Cant Dog', difficulty: 'black', peak: 'loon-peak' },
  { id: 'crosscut', name: 'Crosscut', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'dropline', name: 'Dropline', difficulty: 'green', peak: 'loon-peak' },
  { id: 'exodus', name: 'Exodus', difficulty: 'green', peak: 'loon-peak' },
  { id: 'flying-fox', name: 'Flying Fox', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'grand-junction', name: 'Grand Junction', difficulty: 'green', peak: 'loon-peak' },
  { id: 'hannahs-bypass', name: "Hannah's Bypass", difficulty: 'blue', peak: 'loon-peak' },
  { id: 'harder-way', name: 'Harder Way', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'lil-stash', name: "Lil' Stash", difficulty: 'blue', peak: 'loon-peak', isTerrainPark: true },
  { id: 'link', name: 'Link', difficulty: 'green', peak: 'loon-peak' },
  { id: 'little-sister', name: 'Little Sister', difficulty: 'green', peak: 'loon-peak' },
  { id: 'loon-mountain-park', name: 'Loon Mountain Park', difficulty: 'blue', peak: 'loon-peak', isTerrainPark: true },
  { id: 'lower-bear-claw', name: 'Lower Bear Claw', difficulty: 'green', peak: 'loon-peak' },
  { id: 'lower-picked-rock', name: 'Lower Picked Rock', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'mikes-way', name: "Mike's Way", difficulty: 'black', peak: 'loon-peak' },
  { id: 'missing-link', name: 'Missing Link', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'off-the-grid', name: 'Off The Grid', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'picaroon', name: 'Picaroon', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'rolling-bear', name: 'Rolling Bear', difficulty: 'black', peak: 'loon-peak' },
  { id: 'seven-brothers', name: 'Seven Brothers', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'skidder', name: 'Skidder', difficulty: 'black', peak: 'loon-peak' },
  { id: 'springboard', name: 'Springboard', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'summit-loop', name: 'Summit Loop', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'triple-trouble', name: 'Triple Trouble', difficulty: 'black', peak: 'loon-peak' },
  { id: 'upper-bear-claw', name: 'Upper Bear Claw', difficulty: 'green', peak: 'loon-peak' },
  { id: 'upper-picked-rock', name: 'Upper Picked Rock', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'upper-speakeasy', name: 'Upper Speakeasy', difficulty: 'blue', peak: 'loon-peak' },
  { id: 'blue-ox', name: 'Blue Ox', difficulty: 'blue', peak: 'west-basin' },
  { id: 'coolidge-street', name: 'Coolidge Street', difficulty: 'blue', peak: 'west-basin' },
  { id: 'lower-northstar', name: 'Lower Northstar', difficulty: 'blue', peak: 'west-basin' },
  { id: 'lower-rumrunner', name: 'Lower Rumrunner', difficulty: 'blue', peak: 'west-basin' },
  { id: 'lower-speakeasy', name: 'Lower Speakeasy', difficulty: 'blue', peak: 'west-basin' },
  { id: 'rampasture', name: 'Rampasture', difficulty: 'blue', peak: 'west-basin' },
  { id: 'sarsaparilla', name: 'Sarsaparilla', difficulty: 'green', peak: 'west-basin' },
  { id: 'snubber', name: 'Snubber', difficulty: 'green', peak: 'west-basin' },
  { id: 'upper-northstar', name: 'Upper Northstar', difficulty: 'black', peak: 'west-basin' },
  { id: 'upper-rumrunner', name: 'Upper Rumrunner', difficulty: 'black', peak: 'west-basin' },
  { id: 'blazer', name: 'Blazer', difficulty: 'blue', peak: 'south-peak' },
  { id: 'boom-run', name: 'Boom Run', difficulty: 'blue', peak: 'south-peak' },
  { id: 'camp-out', name: 'Camp Out', difficulty: 'blue', peak: 'south-peak' },
  { id: 'chipper', name: 'Chipper', difficulty: 'green', peak: 'south-peak' },
  { id: 'cruiser', name: 'Cruiser', difficulty: 'blue', peak: 'south-peak' },
  { id: 'escape-route', name: 'Escape Route', difficulty: 'green', peak: 'south-peak' },
  { id: 'fox-run', name: 'Fox Run', difficulty: 'green', peak: 'south-peak' },
  { id: 'homeowner-trails', name: 'Homeowner Trails', difficulty: 'green', peak: 'south-peak' },
  { id: 'jack-pot', name: 'Jack Pot', difficulty: 'green', peak: 'south-peak' },
  { id: 'jobber', name: 'Jobber', difficulty: 'black', peak: 'south-peak' },
  { id: 'lincoln-woods', name: 'Lincoln Woods', difficulty: 'green', peak: 'south-peak' },
  { id: 'lower-stinger', name: 'Lower Stinger', difficulty: 'blue', peak: 'south-peak' },
  { id: 'lower-twitcher', name: 'Lower Twitcher', difficulty: 'black', peak: 'south-peak' },
  { id: 'ripsaw', name: 'Ripsaw', difficulty: 'double-black', peak: 'south-peak' },
  { id: 'sidewinder', name: 'Sidewinder', difficulty: 'green', peak: 'south-peak' },
  { id: 'stillwater', name: 'Stillwater', difficulty: 'green', peak: 'south-peak' },
  { id: 'undercut', name: 'Undercut', difficulty: 'double-black', peak: 'south-peak' },
  { id: 'upper-stinger', name: 'Upper Stinger', difficulty: 'blue', peak: 'south-peak' },
  { id: 'upper-twitcher', name: 'Upper Twitcher', difficulty: 'black', peak: 'south-peak' },
  { id: 'wildwood', name: 'Wildwood', difficulty: 'blue', peak: 'south-peak' },
];
