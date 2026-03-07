// Trail path coordinate data for polyline overlays on the trail map image.
// Each trail is keyed by trail ID and contains an array of segments.
// Each segment is an array of [x, y] percentage coordinate pairs (0-100)
// matching the SVG viewBox="0 0 100 100" used in ImageMap.tsx.
//
// Coordinates are percentages of image width (x) and height (y).
// Image: killington-trail-map.jpg (4572x2704px)
//
// Currently mapped: Bear Mountain (~15 trails)
// Other peaks fall back to dot hotspots until mapped.

export type TrailPathSegment = [number, number][];

export const trailPaths: Record<string, TrailPathSegment[]> = {
  // ============================================================
  // BEAR MOUNTAIN
  // Summit ridge ~(79-82, 15-18), Base lodge ~(88-91, 60-65)
  // ============================================================

  // Outer Limits - Famous steep mogul run, prominent wide trail on the front face
  // Runs straight down the center-left of Bear Mountain
  'outer-limits': [
    [
      [79.5, 16.0],
      [79.8, 20.0],
      [80.0, 25.0],
      [80.2, 30.0],
      [80.5, 35.5],
      [80.8, 41.0],
      [81.0, 46.0],
      [81.2, 51.0],
      [81.5, 55.0],
      [82.0, 59.0],
      [82.8, 62.0],
    ],
  ],

  // Devil's Fiddle - Steep expert trail, runs alongside Outer Limits to the right
  'devils-fiddle': [
    [
      [80.5, 16.5],
      [81.0, 21.0],
      [81.3, 26.0],
      [81.5, 31.0],
      [81.8, 36.0],
      [82.0, 41.0],
      [82.2, 46.0],
      [82.5, 51.0],
      [83.0, 55.5],
      [83.5, 59.0],
      [84.0, 62.0],
    ],
  ],

  // Wildfire - Black diamond, right of Devil's Fiddle
  'wildfire': [
    [
      [81.5, 17.0],
      [82.0, 22.0],
      [82.5, 27.0],
      [83.0, 32.0],
      [83.2, 37.0],
      [83.5, 42.0],
      [83.8, 46.5],
    ],
  ],

  // Lower Wildfire - Continues from Wildfire down to the base, blue
  'lower-wildfire': [
    [
      [83.8, 46.5],
      [84.2, 50.0],
      [84.8, 53.5],
      [85.5, 56.5],
      [86.2, 59.0],
      [87.0, 61.5],
      [87.8, 63.0],
    ],
  ],

  // Bear Claw - Blue trail, sweeps to the right from upper mountain
  'bear-claw': [
    [
      [82.0, 18.0],
      [82.8, 23.0],
      [83.5, 28.0],
      [84.5, 33.0],
      [85.5, 38.0],
      [86.5, 42.5],
      [87.2, 47.0],
      [87.8, 51.0],
      [88.2, 55.0],
      [88.5, 59.0],
      [88.8, 62.5],
    ],
  ],

  // Bear Mountain Liftline - Black, follows the lift line up the center
  'bear-mountain-liftline': [
    [
      [80.8, 16.5],
      [81.5, 22.0],
      [82.2, 28.0],
      [83.0, 34.0],
      [83.8, 40.0],
      [84.5, 45.5],
      [85.0, 50.0],
      [85.5, 54.0],
      [86.0, 57.5],
      [86.5, 60.5],
    ],
  ],

  // Bear Trax - Blue, traverses to the right, more gradual
  'bear-trax': [
    [
      [82.5, 19.0],
      [83.5, 24.0],
      [84.8, 29.0],
      [86.0, 34.0],
      [87.0, 39.0],
      [87.8, 44.0],
      [88.2, 49.0],
      [88.5, 53.5],
      [89.0, 57.5],
      [89.2, 61.0],
    ],
  ],

  // Falls Brook - Blue trail on the right side
  'falls-brook': [
    [
      [83.0, 20.0],
      [84.0, 25.5],
      [85.2, 30.5],
      [86.5, 35.5],
      [87.5, 40.5],
      [88.5, 45.5],
      [89.2, 50.0],
      [89.5, 54.5],
      [89.8, 58.5],
      [90.0, 62.0],
    ],
  ],

  // Skyeburst (Bear) - Blue, connects from Skye Peak side
  'skye-burst-bear': [
    [
      [78.0, 18.0],
      [78.5, 23.0],
      [79.0, 28.5],
      [79.5, 34.0],
      [80.0, 39.5],
      [80.5, 44.5],
      [81.0, 49.0],
      [81.8, 53.5],
      [82.5, 57.5],
      [83.5, 61.0],
    ],
  ],

  // Bear Run - Blue, gentle run curving to the right
  'bear-run': [
    [
      [83.5, 19.5],
      [84.5, 24.5],
      [85.8, 30.0],
      [87.0, 35.5],
      [88.0, 41.0],
      [88.8, 46.5],
      [89.5, 51.5],
      [90.0, 56.0],
      [90.2, 60.0],
      [90.5, 63.0],
    ],
  ],

  // Growler - Glade (double-black), tight trees between main trails
  'growler': [
    [
      [80.0, 20.0],
      [80.2, 25.0],
      [80.5, 30.5],
      [80.8, 36.0],
      [81.0, 41.5],
      [81.2, 46.5],
      [81.5, 51.0],
      [82.0, 55.0],
    ],
  ],

  // Centerpiece - Glade (double-black), between Outer Limits and Devil's Fiddle
  'centerpiece': [
    [
      [80.2, 21.0],
      [80.5, 26.5],
      [80.8, 32.0],
      [81.2, 37.5],
      [81.5, 43.0],
      [81.8, 48.0],
      [82.2, 53.0],
    ],
  ],

  // Spacewalk - Glade (double-black), on the right side of Bear Mountain
  'spacewalk': [
    [
      [82.8, 22.0],
      [83.2, 27.5],
      [83.5, 33.0],
      [83.8, 38.5],
      [84.0, 43.5],
      [84.5, 48.5],
      [85.0, 53.0],
    ],
  ],

  // The Stash - Black terrain park, in the trees
  'the-stash': [
    [
      [84.0, 22.5],
      [84.5, 28.0],
      [85.0, 33.5],
      [85.5, 39.0],
      [86.0, 44.0],
      [86.5, 49.0],
      [87.0, 53.5],
      [87.5, 57.5],
    ],
  ],

  // Lil' Stash - Blue terrain park, smaller version near The Stash
  'lil-stash': [
    [
      [84.5, 35.0],
      [85.0, 39.5],
      [85.5, 44.0],
      [86.0, 48.5],
      [86.5, 52.5],
      [87.0, 56.0],
      [87.5, 59.5],
    ],
  ],
};
