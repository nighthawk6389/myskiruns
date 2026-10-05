import type { Trail, PeakData } from '../../../types';

// Wildcat Mountain's 2025-26 trail map (skiwildcat.com). Its PDF outlines the
// names and flattens most lines into the painting, so the lines, names and
// symbols come from an earlier export of the same artwork with live strokes
// and text (skimap.org map 33684): every one of its names lands on the same
// outlined name, in the same colour, on the 2025-26 page (the same page
// shifted by its bleed), and the 2025-26 page prints no other trail name. The
// map image is the 2025-26 page from Vail Resorts' image CDN. Each line piece
// was named on zoomed crops (tools/trailmap/resorts/wildcat/decisions.py):
// this map prints a run's symbol and name along its line, and one drawn line
// often carries several runs (Upper, Middle and Lower Lynx; Cat Track, Middle
// Wildcat and Bobcat), cut where the next run's symbol or name starts. Names
// are as printed; difficulty is the printed symbol (Hairball, Upper Polecat
// and Wildcat Pitch print theirs on the line beside the name). Lower Cat Track
// is the stretch of Wild Kitten's line its label points to. Cat & Mouse (a
// learning area) has no line: a marker. The map's tree-skiing areas print a
// diamond and no name, so they aren't listed; the map counts 48 trails, as
// here. x/y/baseY/width are unused layout fields.
export const peaks: PeakData[] = [
  { id: 'wildcat', name: 'Wildcat Mountain', elevation: 4062, x: 0, y: 0, baseY: 0, width: 0 },
];

export const trails: Trail[] = [
  { id: 'als-folly', name: "Al's Folly", difficulty: 'black', peak: 'wildcat' },
  { id: 'alley-cat', name: 'Alley Cat', difficulty: 'blue', peak: 'wildcat' },
  { id: 'annies-alley', name: "Annie's Alley", difficulty: 'blue', peak: 'wildcat' },
  { id: 'black-cat', name: 'Black Cat', difficulty: 'black', peak: 'wildcat' },
  { id: 'bobcat', name: 'Bobcat', difficulty: 'blue', peak: 'wildcat' },
  { id: 'cat-mouse', name: 'Cat & Mouse', difficulty: 'green', peak: 'wildcat' },
  { id: 'cat-track', name: 'Cat Track', difficulty: 'blue', peak: 'wildcat' },
  { id: 'cat-walk', name: 'Cat Walk', difficulty: 'blue', peak: 'wildcat' },
  { id: 'catenary', name: 'Catenary', difficulty: 'blue', peak: 'wildcat' },
  { id: 'catnap', name: 'Catnap', difficulty: 'blue', peak: 'wildcat' },
  { id: 'cheetah', name: 'Cheetah', difficulty: 'blue', peak: 'wildcat' },
  { id: 'copy-cat', name: 'Copy Cat', difficulty: 'blue', peak: 'wildcat' },
  { id: 'cougar', name: 'Cougar', difficulty: 'blue', peak: 'wildcat' },
  { id: 'feline', name: 'Feline', difficulty: 'black', peak: 'wildcat' },
  { id: 'hainesville-pass', name: 'Hainesville Pass', difficulty: 'blue', peak: 'wildcat' },
  { id: 'hairball', name: 'Hairball', difficulty: 'black', peak: 'wildcat' },
  { id: 'leos-leap', name: "Leo's Leap", difficulty: 'black', peak: 'wildcat' },
  { id: 'lift-lion', name: 'Lift Lion', difficulty: 'black', peak: 'wildcat' },
  { id: 'lower-cat-track', name: 'Lower Cat Track', difficulty: 'blue', peak: 'wildcat' },
  { id: 'lower-catapult', name: 'Lower Catapult', difficulty: 'blue', peak: 'wildcat' },
  { id: 'lower-catenary', name: 'Lower Catenary', difficulty: 'black', peak: 'wildcat' },
  { id: 'lower-lynx', name: 'Lower Lynx', difficulty: 'blue', peak: 'wildcat' },
  { id: 'lower-polecat', name: 'Lower Polecat', difficulty: 'green', peak: 'wildcat' },
  { id: 'lower-wildcat', name: 'Lower Wildcat', difficulty: 'blue', peak: 'wildcat' },
  { id: 'lynx-connection', name: 'Lynx Connection', difficulty: 'blue', peak: 'wildcat' },
  { id: 'lynx-lair', name: 'Lynx Lair', difficulty: 'black', peak: 'wildcat' },
  { id: 'middle-catapult', name: 'Middle Catapult', difficulty: 'black', peak: 'wildcat' },
  { id: 'middle-lynx', name: 'Middle Lynx', difficulty: 'blue', peak: 'wildcat' },
  { id: 'middle-polecat', name: 'Middle Polecat', difficulty: 'green', peak: 'wildcat' },
  { id: 'middle-wildcat', name: 'Middle Wildcat', difficulty: 'blue', peak: 'wildcat' },
  { id: 'midway', name: 'Midway', difficulty: 'blue', peak: 'wildcat' },
  { id: 'ocelot-way', name: 'Ocelot Way', difficulty: 'blue', peak: 'wildcat' },
  { id: 'panther', name: 'Panther', difficulty: 'blue', peak: 'wildcat' },
  { id: 'snowcat-slope', name: 'Snowcat Slope', difficulty: 'green', peak: 'wildcat' },
  { id: 'snowcat-trail', name: 'Snowcat Trail', difficulty: 'green', peak: 'wildcat' },
  { id: 'sphynx', name: 'Sphynx', difficulty: 'black', peak: 'wildcat' },
  { id: 'starr-line', name: 'Starr Line', difficulty: 'black', peak: 'wildcat' },
  { id: 'stray-cat', name: 'Stray Cat', difficulty: 'blue', peak: 'wildcat' },
  { id: 'the-chute', name: 'The Chute', difficulty: 'black', peak: 'wildcat' },
  { id: 'tomcat', name: 'Tomcat', difficulty: 'green', peak: 'wildcat' },
  { id: 'tomcat-schuss', name: 'Tomcat Schuss', difficulty: 'black', peak: 'wildcat' },
  { id: 'top-cat', name: 'Top Cat', difficulty: 'black', peak: 'wildcat' },
  { id: 'upper-catapult', name: 'Upper Catapult', difficulty: 'blue', peak: 'wildcat' },
  { id: 'upper-lynx', name: 'Upper Lynx', difficulty: 'blue', peak: 'wildcat' },
  { id: 'upper-polecat', name: 'Upper Polecat', difficulty: 'green', peak: 'wildcat' },
  { id: 'upper-wildcat', name: 'Upper Wildcat', difficulty: 'black', peak: 'wildcat' },
  { id: 'wild-kitten', name: 'Wild Kitten', difficulty: 'green', peak: 'wildcat' },
  { id: 'wildcat-pitch', name: 'Wildcat Pitch', difficulty: 'black', peak: 'wildcat' },
];
