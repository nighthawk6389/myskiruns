// Trail path coordinate data for polyline overlays on the trail map image.
// Each trail is keyed by trail ID and contains an array of segments.
// Each segment is an array of [x, y] percentage coordinate pairs (0-100)
// matching the SVG viewBox="0 0 100 100" used in ImageMap.tsx.
//
// Coordinates are percentages of image width (x) and height (y).
// Image: killington-trail-map.jpg (4572x2704px)
//
// All 7 peaks mapped (119 trails).

export type TrailPathSegment = [number, number][];

export const trailPaths: Record<string, TrailPathSegment[]> = {
  // ============================================================
  // SNOWSHED AREA
  // Far left of map. Base lodge at ~(5, 73). Top of area ~(8, 44).
  // 5 green/easy trails on gentle terrain.
  // ============================================================

  // Snowshed - Main slope, the wide primary beginner run down the center
  'snowshed-slope': [
    [
      [7.5, 44.0],
      [7.0, 47.5],
      [6.5, 51.0],
      [6.2, 54.5],
      [6.0, 58.0],
      [5.8, 61.5],
      [5.5, 65.0],
      [5.2, 68.5],
      [5.0, 72.0],
      [5.0, 73.5],
    ],
  ],

  // Yodeler - The distinctive winding S-curve trail along the far left edge
  'yodeler': [
    [
      [6.0, 44.5],
      [5.0, 47.0],
      [3.8, 49.5],
      [3.2, 52.0],
      [4.0, 54.5],
      [5.0, 57.0],
      [4.5, 59.5],
      [3.5, 62.0],
      [3.0, 64.5],
      [3.5, 67.0],
      [4.2, 69.5],
      [4.5, 72.0],
      [4.8, 74.0],
    ],
  ],

  // Idler - Green trail, gentle run on the right side of Snowshed
  'idler': [
    [
      [8.5, 44.5],
      [8.8, 48.0],
      [9.0, 51.5],
      [8.8, 55.0],
      [8.2, 58.5],
      [7.5, 62.0],
      [6.8, 65.5],
      [6.0, 69.0],
      [5.5, 72.0],
      [5.2, 73.5],
    ],
  ],

  // Snow Play - Green, short play area near the base
  'snow-play': [
    [
      [6.0, 63.0],
      [5.8, 66.0],
      [5.5, 69.0],
      [5.2, 71.5],
      [5.0, 73.0],
    ],
  ],

  // Crossover - Green connector, traverses horizontally from Snowshed to Sunrise
  'snowshed-crossover': [
    [
      [9.5, 52.0],
      [8.5, 52.2],
      [7.5, 52.5],
      [6.5, 53.0],
      [5.5, 53.5],
      [4.5, 54.0],
    ],
  ],

  // ============================================================
  // SUNRISE AREA
  // Left side, adjacent to Snowshed. Summit ~(15, 38). Base ~(12, 68).
  // 4 green trails + 1 blue.
  // ============================================================

  // Sun Dog - Green, main descent from Sunrise summit
  'sun-dog': [
    [
      [14.5, 38.5],
      [14.0, 42.0],
      [13.5, 45.5],
      [13.0, 49.0],
      [12.5, 52.5],
      [12.0, 56.0],
      [11.5, 59.5],
      [11.2, 63.0],
      [11.0, 66.5],
      [11.0, 68.5],
    ],
  ],

  // Rendezvous - Green, curves left toward Snowshed base
  'rendezvous': [
    [
      [13.5, 39.0],
      [12.8, 42.5],
      [12.0, 46.0],
      [11.2, 49.5],
      [10.5, 53.0],
      [9.8, 56.5],
      [9.2, 60.0],
      [9.0, 63.5],
      [9.2, 66.5],
      [10.0, 69.0],
    ],
  ],

  // Bear Cub - Green, gentle trail on the right side of Sunrise
  'bear-cub': [
    [
      [15.5, 39.0],
      [15.8, 42.5],
      [16.0, 46.0],
      [15.8, 49.5],
      [15.2, 53.0],
      [14.5, 56.5],
      [13.8, 60.0],
      [13.0, 63.5],
      [12.5, 66.5],
      [12.2, 68.5],
    ],
  ],

  // Bear View - Blue (only intermediate at Sunrise), more direct descent
  'bear-view': [
    [
      [15.0, 38.5],
      [15.5, 42.0],
      [16.0, 45.0],
      [16.2, 48.0],
      [16.0, 51.5],
      [15.5, 55.0],
      [14.8, 58.5],
      [14.0, 62.0],
      [13.2, 65.5],
      [12.5, 68.5],
    ],
  ],

  // Sunrise Connector - Green, traverses horizontally connecting areas
  'sunrise-connector': [
    [
      [16.5, 50.0],
      [15.0, 50.3],
      [13.5, 50.8],
      [12.0, 51.2],
      [10.5, 51.8],
      [9.5, 52.2],
    ],
  ],

  // ============================================================
  // RAMSHEAD
  // Center-left. Summit ~(27, 26). Base ~(23, 66).
  // 6 green + 5 blue trails.
  // ============================================================

  // Easy Street - Green, gentle main run down Ramshead
  'easy-street': [
    [
      [26.0, 26.5],
      [25.5, 30.0],
      [25.0, 33.5],
      [24.5, 37.0],
      [24.0, 41.0],
      [23.5, 45.0],
      [23.0, 49.0],
      [22.5, 53.0],
      [22.0, 57.0],
      [21.8, 61.0],
      [22.0, 65.0],
    ],
  ],

  // Swirl - Green, curves to the left with sweeping turns
  'swirl': [
    [
      [25.0, 27.0],
      [24.2, 30.5],
      [23.5, 34.0],
      [23.0, 37.5],
      [22.5, 41.0],
      [22.0, 44.5],
      [21.5, 48.0],
      [21.0, 52.0],
      [20.8, 56.0],
      [21.0, 60.0],
      [21.2, 64.0],
      [21.5, 66.5],
    ],
  ],

  // Treezy - Green glade, through light trees on the center-left
  'treezy': [
    [
      [25.5, 30.0],
      [25.0, 34.0],
      [24.8, 38.0],
      [24.5, 42.0],
      [24.2, 46.0],
      [24.0, 50.0],
      [23.8, 54.0],
      [23.5, 57.5],
    ],
  ],

  // Squeeze Play - Green glade, narrow path through trees
  'squeeze-play': [
    [
      [26.5, 30.5],
      [26.2, 34.5],
      [26.0, 38.5],
      [25.8, 42.5],
      [25.5, 46.5],
      [25.2, 50.5],
      [25.0, 54.5],
      [24.8, 58.0],
    ],
  ],

  // Ramshead Run - Green, long central run
  'ramshead-run': [
    [
      [27.0, 26.5],
      [26.8, 30.5],
      [26.5, 34.5],
      [26.2, 38.5],
      [26.0, 42.5],
      [25.8, 46.5],
      [25.5, 50.5],
      [25.0, 54.5],
      [24.5, 58.5],
      [24.0, 62.5],
      [23.5, 66.0],
    ],
  ],

  // Ramshead Liftline - Blue, follows the lift straight down
  'ramshead-liftline': [
    [
      [27.5, 27.0],
      [27.2, 31.0],
      [27.0, 35.0],
      [26.8, 39.0],
      [26.5, 43.0],
      [26.2, 47.0],
      [26.0, 51.0],
      [25.8, 55.0],
      [25.5, 59.0],
      [25.0, 63.0],
      [24.5, 66.0],
    ],
  ],

  // Header - Blue, steeper run on the right side of Ramshead
  'header': [
    [
      [28.5, 27.5],
      [29.0, 31.0],
      [29.2, 34.5],
      [29.0, 38.0],
      [28.5, 42.0],
      [28.0, 46.0],
      [27.5, 50.0],
      [27.0, 54.0],
      [26.5, 58.0],
      [26.0, 62.0],
      [25.5, 65.5],
    ],
  ],

  // Vagabond - Blue, sweeping run curving right then back center
  'vagabond': [
    [
      [29.5, 28.0],
      [30.0, 31.5],
      [30.5, 35.0],
      [30.5, 38.5],
      [30.0, 42.0],
      [29.5, 46.0],
      [29.0, 50.0],
      [28.2, 54.0],
      [27.5, 58.0],
      [26.8, 62.0],
      [26.2, 65.5],
    ],
  ],

  // Caper - Blue, furthest right Ramshead trail
  'caper': [
    [
      [30.5, 29.0],
      [31.0, 32.5],
      [31.5, 36.0],
      [31.5, 39.5],
      [31.0, 43.0],
      [30.5, 47.0],
      [30.0, 51.0],
      [29.2, 55.0],
      [28.5, 59.0],
      [27.5, 63.0],
      [26.5, 66.0],
    ],
  ],

  // Timberline - Blue, right edge trail bordering Snowdon
  'timberline': [
    [
      [31.5, 29.5],
      [32.0, 33.0],
      [32.5, 36.5],
      [32.5, 40.0],
      [32.2, 44.0],
      [31.8, 48.0],
      [31.2, 52.0],
      [30.5, 56.0],
      [29.5, 60.0],
      [28.5, 63.5],
      [27.5, 66.5],
    ],
  ],

  // Start Park - Green terrain park, short run near the base
  'start-park': [
    [
      [24.0, 55.0],
      [23.5, 58.0],
      [23.0, 61.0],
      [22.5, 64.0],
      [22.2, 66.5],
    ],
  ],

  // ============================================================
  // SNOWDON
  // Center of map. Summit ~(40, 15). Base ~(36, 62).
  // 17 trails: mix of all difficulties.
  // ============================================================

  // Great Northern - Blue, long sweeping run with graceful curves
  'great-northern': [
    [
      [39.5, 15.5],
      [39.0, 19.0],
      [38.5, 22.5],
      [37.8, 26.0],
      [37.2, 30.0],
      [36.8, 34.0],
      [36.5, 38.0],
      [36.2, 42.0],
      [36.0, 46.0],
      [35.8, 50.0],
      [35.5, 54.0],
      [35.2, 58.0],
      [35.5, 61.5],
    ],
  ],

  // Bunny Buster - Green, gentle beginner trail in lower Snowdon
  'bunny-buster': [
    [
      [37.5, 42.0],
      [37.2, 45.5],
      [37.0, 49.0],
      [36.8, 52.5],
      [36.5, 56.0],
      [36.2, 59.5],
    ],
  ],

  // Chute - Black, steep narrow direct descent
  'chute': [
    [
      [41.0, 16.0],
      [41.2, 19.5],
      [41.3, 23.0],
      [41.5, 26.5],
      [41.5, 30.0],
      [41.5, 33.5],
      [41.2, 37.0],
      [41.0, 40.5],
      [40.8, 44.0],
      [40.5, 47.5],
      [40.0, 51.0],
      [39.5, 54.5],
    ],
  ],

  // Conclusion - Double-black, very steep headwall
  'conclusion': [
    [
      [42.0, 16.5],
      [42.5, 20.0],
      [42.8, 23.5],
      [43.0, 27.0],
      [43.0, 30.5],
      [42.8, 34.0],
      [42.5, 37.5],
      [42.0, 41.0],
      [41.5, 44.5],
      [41.0, 48.0],
      [40.5, 52.0],
    ],
  ],

  // Upper FIS - Green, upper gentle section connecting to FIS
  'upper-fis': [
    [
      [43.5, 17.0],
      [44.0, 20.5],
      [44.2, 24.0],
      [44.5, 27.5],
      [44.5, 31.0],
      [44.5, 34.5],
      [44.5, 37.0],
    ],
  ],

  // Mountain Run - Green, long gentle cruiser curving left
  'mountain-run': [
    [
      [38.5, 16.0],
      [38.0, 19.5],
      [37.5, 23.0],
      [37.0, 27.0],
      [36.5, 31.0],
      [36.2, 35.0],
      [36.0, 39.0],
      [35.8, 43.0],
      [35.5, 47.0],
      [35.2, 51.0],
      [35.2, 55.0],
      [35.5, 59.0],
    ],
  ],

  // Mountain Training Station - Green, short training area mid-mountain
  'mountain-training': [
    [
      [37.5, 44.0],
      [37.2, 47.5],
      [37.0, 51.0],
      [36.8, 54.5],
      [36.5, 58.0],
      [36.2, 60.5],
    ],
  ],

  // Snowdon Liftline - Blue, follows the lift line straight down
  'snowdon-liftline': [
    [
      [40.5, 15.5],
      [40.2, 19.5],
      [40.0, 23.5],
      [39.8, 27.5],
      [39.5, 31.5],
      [39.2, 35.5],
      [39.0, 39.5],
      [38.8, 43.5],
      [38.5, 47.5],
      [38.0, 51.5],
      [37.5, 55.5],
      [37.0, 59.0],
      [36.8, 62.0],
    ],
  ],

  // Upper Snowdon - Blue, upper portion with moderate pitch
  'upper-snowdon': [
    [
      [42.5, 16.0],
      [43.0, 19.5],
      [43.2, 23.0],
      [43.2, 26.5],
      [43.0, 30.0],
      [42.5, 33.5],
      [42.0, 37.0],
      [41.5, 40.0],
    ],
  ],

  // Lower Snowdon - Blue, lower section continuing to the base
  'lower-snowdon': [
    [
      [41.5, 40.0],
      [41.0, 43.5],
      [40.5, 47.0],
      [40.0, 50.5],
      [39.5, 54.0],
      [39.0, 57.0],
      [38.5, 60.0],
      [38.0, 62.0],
    ],
  ],

  // Bittersweet - Blue, curving descent on the right side of Snowdon
  'bittersweet': [
    [
      [43.5, 17.5],
      [44.0, 21.0],
      [44.2, 24.5],
      [44.0, 28.0],
      [43.5, 31.5],
      [43.0, 35.0],
      [42.5, 38.5],
      [41.8, 42.0],
      [41.2, 45.5],
      [40.5, 49.0],
      [39.8, 52.5],
      [39.2, 56.0],
      [38.8, 59.5],
    ],
  ],

  // Sass - Blue, runs right-of-center with sweeping turns
  'sass': [
    [
      [44.5, 18.0],
      [45.0, 21.5],
      [45.2, 25.0],
      [45.2, 28.5],
      [45.0, 32.0],
      [44.5, 35.5],
      [44.0, 39.0],
      [43.2, 42.5],
      [42.5, 46.0],
      [41.8, 49.5],
      [41.0, 53.0],
      [40.5, 56.5],
      [40.0, 60.0],
    ],
  ],

  // Northstar - Black, steep trail on the left side of Snowdon
  'northstar': [
    [
      [39.0, 16.0],
      [38.5, 19.5],
      [38.0, 23.0],
      [37.8, 26.5],
      [37.5, 30.0],
      [37.5, 33.5],
      [37.5, 37.0],
      [37.8, 40.5],
      [38.0, 44.0],
      [38.0, 47.5],
      [38.0, 51.0],
      [37.8, 54.5],
    ],
  ],

  // Royal Flush - Black, steep run slightly right of center
  'royal-flush': [
    [
      [40.0, 16.0],
      [40.2, 19.5],
      [40.5, 23.0],
      [40.5, 26.5],
      [40.5, 30.0],
      [40.2, 33.5],
      [40.0, 37.0],
      [39.8, 40.5],
      [39.5, 44.0],
      [39.0, 47.5],
      [38.5, 51.0],
      [38.2, 55.0],
    ],
  ],

  // Upper Northbrook - Blue, upper section heading left
  'upper-northbrook': [
    [
      [36.0, 22.0],
      [35.5, 25.5],
      [35.0, 29.0],
      [34.5, 32.5],
      [34.2, 36.0],
      [34.0, 39.5],
      [34.0, 43.0],
    ],
  ],

  // Lower Northbrook - Green, lower section continuing to base
  'lower-northbrook': [
    [
      [34.0, 43.0],
      [33.8, 46.5],
      [33.8, 50.0],
      [33.8, 53.5],
      [34.0, 57.0],
      [34.2, 60.0],
      [34.5, 63.0],
    ],
  ],

  // Snowdon Glades - Black glade, in the trees on the far left of Snowdon
  'snowdon-glades': [
    [
      [36.5, 20.0],
      [36.0, 23.5],
      [35.5, 27.0],
      [35.2, 30.5],
      [35.0, 34.0],
      [34.8, 37.5],
      [34.5, 41.0],
      [34.2, 44.5],
    ],
  ],

  // ============================================================
  // SKYE PEAK
  // Center-right. Summit ~(56, 9). Base ~(62, 58).
  // 37 trails - the largest peak area. Trails spread wide.
  // ============================================================

  // Skyelark - Blue, main cruiser sweeping left from summit
  'skyelark': [
    [
      [55.0, 10.0],
      [54.5, 13.5],
      [54.0, 17.0],
      [53.5, 20.5],
      [53.0, 24.0],
      [52.5, 28.0],
      [52.0, 32.0],
      [51.5, 36.0],
      [51.0, 40.0],
      [50.8, 44.0],
      [50.5, 48.0],
      [50.5, 52.0],
      [50.5, 56.0],
    ],
  ],

  // Upper Skyelark - Blue, upper section only
  'upper-skyelark': [
    [
      [54.5, 10.0],
      [54.0, 13.5],
      [53.5, 17.0],
      [53.0, 20.5],
      [52.5, 24.0],
      [52.0, 27.0],
    ],
  ],

  // Skyeburst - Blue, sweeping right from summit area
  'skyeburst': [
    [
      [56.5, 10.5],
      [57.0, 14.0],
      [57.5, 17.5],
      [58.0, 21.0],
      [58.2, 24.5],
      [58.2, 28.0],
      [58.0, 32.0],
      [57.5, 36.0],
      [57.0, 40.0],
      [56.5, 44.0],
      [56.0, 48.0],
      [55.8, 52.0],
      [55.5, 56.0],
    ],
  ],

  // Upper Skyeburst - Blue, upper portion only
  'upper-skyeburst': [
    [
      [57.0, 10.5],
      [57.5, 14.0],
      [58.0, 17.5],
      [58.2, 21.0],
      [58.5, 24.5],
    ],
  ],

  // Skye Hawk - Blue, runs right of Skyeburst with sweeping turns
  'skye-hawk': [
    [
      [57.5, 11.0],
      [58.0, 14.5],
      [58.8, 18.0],
      [59.2, 21.5],
      [59.5, 25.0],
      [59.2, 28.5],
      [58.8, 32.0],
      [58.2, 36.0],
      [57.8, 40.0],
      [57.2, 44.0],
      [56.8, 48.0],
      [56.5, 52.0],
    ],
  ],

  // Skyebits - Blue, shorter mid-mountain trail
  'skyebits': [
    [
      [53.5, 27.0],
      [53.0, 30.5],
      [52.5, 34.0],
      [52.0, 37.5],
      [51.8, 41.0],
      [51.5, 44.5],
      [51.2, 48.0],
    ],
  ],

  // Cruise Control - Blue, smooth run right of center with nice flow
  'cruise-control': [
    [
      [58.5, 12.0],
      [59.0, 15.5],
      [59.5, 19.0],
      [60.0, 22.5],
      [60.2, 26.0],
      [60.2, 29.5],
      [60.0, 33.0],
      [59.5, 37.0],
      [59.0, 41.0],
      [58.5, 45.0],
      [58.0, 49.0],
      [57.5, 53.0],
      [57.2, 56.5],
    ],
  ],

  // Mouse Trap - Blue, winding descent with tight turns
  'mouse-trap': [
    [
      [55.5, 14.0],
      [55.0, 17.5],
      [54.5, 21.0],
      [54.2, 24.5],
      [54.0, 28.0],
      [54.2, 31.5],
      [54.5, 35.0],
      [54.2, 38.5],
      [53.8, 42.0],
      [53.5, 45.5],
      [53.0, 49.0],
    ],
  ],

  // Somewhere - Blue, mid-length descent on the left side
  'somewhere': [
    [
      [56.0, 14.5],
      [55.5, 18.0],
      [55.0, 21.5],
      [54.8, 25.0],
      [54.5, 28.5],
      [54.2, 32.0],
      [54.0, 35.5],
      [53.8, 39.0],
      [53.5, 42.5],
      [53.2, 46.0],
      [53.0, 49.5],
    ],
  ],

  // Breakaway - Blue, breaks off to the right from the summit ridge
  'breakaway': [
    [
      [59.0, 13.0],
      [59.5, 16.5],
      [60.2, 20.0],
      [60.8, 23.5],
      [61.0, 27.0],
      [60.8, 30.5],
      [60.2, 34.0],
      [59.8, 37.5],
      [59.2, 41.0],
      [58.8, 44.5],
    ],
  ],

  // Touch Down - Blue, long run toward the base lodge
  'touch-down': [
    [
      [59.5, 14.0],
      [60.0, 17.5],
      [60.5, 21.0],
      [61.0, 24.5],
      [61.2, 28.0],
      [61.2, 31.5],
      [61.0, 35.0],
      [60.5, 39.0],
      [60.0, 43.0],
      [59.5, 47.0],
      [59.0, 51.0],
      [58.8, 55.0],
      [58.5, 58.0],
    ],
  ],

  // Patsy's - Blue, named intermediate with nice pitch
  'patsys': [
    [
      [57.0, 12.0],
      [56.5, 15.5],
      [56.0, 19.0],
      [55.5, 22.5],
      [55.0, 26.0],
      [54.5, 30.0],
      [54.0, 34.0],
      [53.5, 38.0],
      [53.0, 42.0],
      [52.5, 46.0],
      [52.2, 50.0],
    ],
  ],

  // Twister - Blue, winding descent further right
  'twister': [
    [
      [60.0, 13.5],
      [60.5, 17.0],
      [61.0, 20.5],
      [61.5, 24.0],
      [61.8, 27.5],
      [61.5, 31.0],
      [61.0, 34.5],
      [60.5, 38.0],
      [60.0, 41.5],
      [59.5, 45.0],
      [59.0, 48.5],
    ],
  ],

  // Catwalk - Blue, horizontal traverse connecting mid-mountain trails
  'catwalk': [
    [
      [51.0, 48.0],
      [52.5, 48.3],
      [54.0, 48.8],
      [55.5, 49.2],
      [57.0, 49.8],
      [58.5, 50.2],
      [60.0, 50.8],
      [61.0, 51.2],
    ],
  ],

  // Upper Catwalk - Blue, upper horizontal traverse
  'upper-catwalk': [
    [
      [52.0, 35.5],
      [53.5, 35.8],
      [55.0, 36.2],
      [56.5, 36.8],
      [58.0, 37.2],
      [59.0, 37.5],
    ],
  ],

  // Great Eastern - Green, THE longest green trail, winding from top to bottom
  'great-eastern': [
    [
      [54.5, 11.0],
      [53.5, 14.5],
      [52.5, 18.0],
      [51.5, 21.5],
      [50.5, 25.0],
      [49.5, 28.5],
      [49.0, 32.0],
      [48.5, 36.0],
      [48.0, 40.0],
      [47.8, 44.0],
      [47.5, 48.0],
      [47.5, 52.0],
      [47.8, 56.0],
      [48.0, 59.5],
    ],
  ],

  // Home Stretch - Green, lower section heading to the base
  'home-stretch': [
    [
      [60.0, 40.0],
      [60.5, 43.5],
      [61.0, 47.0],
      [61.5, 50.5],
      [62.0, 54.0],
      [62.5, 57.0],
      [62.8, 59.0],
    ],
  ],

  // Lower Home Stretch - Green, final gentle stretch to base lodge
  'lower-home-stretch': [
    [
      [62.8, 59.0],
      [63.2, 61.5],
      [63.8, 64.0],
      [64.2, 66.5],
      [64.5, 68.5],
    ],
  ],

  // Juggernaut - Green, meandering green from mid-mountain to base
  'juggernaut': [
    [
      [58.0, 34.0],
      [58.5, 37.5],
      [59.0, 41.0],
      [59.5, 44.5],
      [60.0, 48.0],
      [60.5, 51.5],
      [61.0, 55.0],
      [61.5, 58.0],
      [61.8, 61.0],
    ],
  ],

  // Vertigo - Double-black, steep expert run on right side of Skye Peak
  'vertigo': [
    [
      [61.0, 15.0],
      [61.5, 18.5],
      [62.0, 22.0],
      [62.2, 25.5],
      [62.5, 29.0],
      [62.5, 32.5],
      [62.2, 36.0],
      [62.0, 39.5],
      [61.5, 43.0],
      [61.0, 46.5],
      [60.5, 50.0],
      [60.0, 54.0],
    ],
  ],

  // Upper Vertigo - Double-black, steep upper section
  'upper-vertigo': [
    [
      [61.5, 11.0],
      [62.0, 14.0],
      [62.2, 17.0],
      [62.5, 20.0],
      [62.5, 23.0],
      [62.5, 26.0],
    ],
  ],

  // Ovation - Double-black, famous steep trail on the far right of Skye Peak
  'ovation': [
    [
      [62.0, 11.5],
      [62.5, 15.0],
      [63.0, 18.5],
      [63.5, 22.0],
      [63.8, 25.5],
      [64.0, 29.0],
      [63.8, 32.5],
      [63.5, 36.0],
      [63.0, 39.5],
      [62.5, 43.0],
      [62.0, 46.5],
      [61.5, 50.0],
    ],
  ],

  // Needle's Eye - Black, narrow challenging trail
  'needles-eye': [
    [
      [59.5, 12.0],
      [60.0, 15.5],
      [60.2, 19.0],
      [60.5, 22.5],
      [60.5, 26.0],
      [60.2, 29.5],
      [59.8, 33.0],
      [59.5, 36.5],
      [59.0, 40.0],
      [58.5, 43.5],
    ],
  ],

  // Panic Button - Black, steep narrow expert trail
  'panic-button': [
    [
      [61.0, 12.5],
      [61.5, 16.0],
      [62.0, 19.5],
      [62.2, 23.0],
      [62.2, 26.5],
      [62.0, 30.0],
      [61.5, 33.5],
      [61.0, 37.0],
      [60.5, 40.5],
    ],
  ],

  // Dream Maker - Black, challenging run on the far right
  'dream-maker': [
    [
      [63.0, 13.0],
      [63.5, 16.5],
      [64.0, 20.0],
      [64.2, 23.5],
      [64.5, 27.0],
      [64.2, 30.5],
      [64.0, 34.0],
      [63.5, 37.5],
      [63.0, 41.0],
      [62.5, 44.5],
      [62.0, 48.0],
    ],
  ],

  // Dream Maker Headwall - Double-black, the steep upper pitch
  'dream-maker-headwall': [
    [
      [63.5, 13.5],
      [64.0, 16.5],
      [64.5, 19.5],
      [64.8, 22.5],
      [64.5, 25.5],
      [64.0, 28.5],
    ],
  ],

  // Highline - Black, rightmost trail on Skye Peak
  'highline': [
    [
      [64.0, 14.0],
      [64.5, 17.5],
      [65.0, 21.0],
      [65.2, 24.5],
      [65.5, 28.0],
      [65.2, 31.5],
      [65.0, 35.0],
      [64.5, 38.5],
      [64.0, 42.0],
      [63.5, 45.5],
      [63.0, 49.0],
    ],
  ],

  // Pipe Dream - Blue, runs to the left from upper Skye
  'pipe-dream': [
    [
      [53.0, 14.0],
      [52.5, 17.5],
      [52.0, 21.0],
      [51.5, 24.5],
      [51.0, 28.0],
      [50.5, 32.0],
      [50.0, 36.0],
      [49.5, 40.0],
      [49.2, 44.0],
    ],
  ],

  // Valley Plunge - Blue, drops into the valley on the left
  'valley-plunge': [
    [
      [54.0, 14.5],
      [53.5, 18.0],
      [53.0, 21.5],
      [52.5, 25.0],
      [52.0, 28.5],
      [51.5, 32.0],
      [51.0, 36.0],
      [50.8, 40.0],
      [50.5, 44.0],
    ],
  ],

  // Field Goal - Blue, mid-mountain descent to the base area
  'field-goal': [
    [
      [60.5, 34.0],
      [60.8, 37.5],
      [61.0, 41.0],
      [61.2, 44.5],
      [61.5, 48.0],
      [61.8, 51.5],
      [62.0, 55.0],
      [62.2, 58.0],
    ],
  ],

  // Roundabout - Blue, wide curving trail on the far right of Skye
  'roundabout': [
    [
      [64.5, 15.0],
      [65.0, 18.5],
      [65.5, 22.0],
      [66.0, 25.5],
      [66.2, 29.0],
      [66.0, 32.5],
      [65.5, 36.0],
      [65.0, 40.0],
      [64.5, 44.0],
      [64.0, 48.0],
      [63.5, 52.0],
      [63.0, 55.5],
    ],
  ],

  // Roundabout Glade - Black glade, in the trees near Roundabout
  'roundabout-glade': [
    [
      [65.0, 20.0],
      [65.5, 23.5],
      [65.8, 27.0],
      [66.0, 30.5],
      [65.8, 34.0],
      [65.5, 37.5],
      [65.0, 41.0],
    ],
  ],

  // Tin Man - Blue, named intermediate on the left of Skye
  'tin-man': [
    [
      [55.5, 13.5],
      [55.0, 17.0],
      [54.5, 20.5],
      [54.0, 24.0],
      [53.5, 28.0],
      [53.0, 32.0],
      [52.5, 36.0],
      [52.2, 40.0],
      [52.0, 44.0],
      [51.8, 48.0],
    ],
  ],

  // Skye Peak Liftline - Black, follows the main Skye Peak lift
  'skye-peak-liftline': [
    [
      [57.5, 10.0],
      [58.0, 13.5],
      [58.2, 17.0],
      [58.5, 20.5],
      [58.8, 24.0],
      [59.0, 27.5],
      [59.0, 31.0],
      [58.8, 34.5],
      [58.5, 38.0],
      [58.0, 42.0],
      [57.5, 46.0],
      [57.0, 50.0],
      [56.5, 54.0],
    ],
  ],

  // Great Bear - Blue, long trail connecting toward Bear Mountain
  'great-bear': [
    [
      [65.0, 16.0],
      [66.0, 19.5],
      [67.0, 23.0],
      [68.0, 27.0],
      [69.0, 31.0],
      [70.0, 35.0],
      [71.0, 39.0],
      [72.0, 43.0],
      [73.0, 47.0],
      [74.0, 51.0],
      [74.5, 55.0],
    ],
  ],

  // Upper Great Bear - Blue, upper section heading east
  'upper-great-bear': [
    [
      [65.5, 14.0],
      [66.5, 17.0],
      [67.5, 20.0],
      [68.5, 23.0],
      [69.5, 26.5],
      [70.0, 30.0],
    ],
  ],

  // Woodward Peace Park - Blue terrain park
  'woodward-peace-park': [
    [
      [59.0, 31.0],
      [59.5, 34.5],
      [60.0, 38.0],
      [60.2, 41.5],
      [60.5, 45.0],
      [60.8, 48.5],
      [61.0, 52.0],
      [61.2, 55.5],
    ],
  ],

  // ============================================================
  // KILLINGTON PEAK
  // Highest summit. Peak ~(45, 4). Base spreads wide.
  // 29 trails including Superstar, Cascade, and other famous runs.
  // ============================================================

  // Superstar - Black, THE most famous trail at Killington, wide direct fall-line
  'superstar': [
    [
      [46.5, 5.0],
      [47.0, 8.5],
      [47.5, 12.0],
      [48.0, 15.5],
      [48.5, 19.0],
      [49.0, 22.5],
      [49.2, 26.0],
      [49.5, 30.0],
      [49.8, 34.0],
      [50.0, 38.0],
      [50.0, 42.0],
      [50.0, 46.0],
      [50.0, 50.0],
      [50.2, 54.0],
      [50.5, 58.0],
    ],
  ],

  // Cascade - Double-black, steep and challenging on the left
  'cascade': [
    [
      [44.5, 5.0],
      [44.0, 8.5],
      [43.5, 12.0],
      [43.0, 15.5],
      [42.8, 19.0],
      [42.5, 22.5],
      [42.2, 26.0],
      [42.0, 30.0],
      [42.0, 34.0],
      [42.0, 37.0],
    ],
  ],

  // Downdraft - Double-black, steep expert trail left of center
  'downdraft': [
    [
      [45.0, 5.0],
      [44.5, 8.5],
      [44.0, 12.0],
      [43.5, 15.5],
      [43.2, 19.0],
      [43.0, 22.5],
      [42.8, 26.0],
      [42.5, 30.0],
      [42.2, 34.0],
      [42.0, 38.0],
      [42.0, 41.0],
    ],
  ],

  // Double Dipper - Double-black, steep mogul run
  'double-dipper': [
    [
      [45.5, 5.5],
      [45.0, 9.0],
      [44.5, 12.5],
      [44.0, 16.0],
      [43.5, 19.5],
      [43.2, 23.0],
      [43.0, 26.5],
      [42.8, 30.0],
      [42.5, 33.5],
    ],
  ],

  // Big Dipper Glade - Double-black glade, in the trees
  'big-dipper-glade': [
    [
      [44.8, 9.5],
      [44.2, 13.0],
      [43.8, 16.5],
      [43.5, 20.0],
      [43.2, 23.5],
      [43.0, 27.0],
      [42.8, 30.5],
    ],
  ],

  // Flume - Black, classic long run heading right
  'flume': [
    [
      [47.0, 5.5],
      [47.5, 9.0],
      [48.0, 12.5],
      [48.5, 16.0],
      [49.0, 19.5],
      [49.5, 23.0],
      [50.0, 26.5],
      [50.2, 30.0],
      [50.5, 34.0],
      [50.8, 38.0],
      [51.0, 42.0],
      [51.0, 46.0],
    ],
  ],

  // Escapade - Black, challenging descent right of Flume
  'escapade': [
    [
      [47.5, 6.0],
      [48.0, 9.5],
      [48.5, 13.0],
      [49.0, 16.5],
      [49.5, 20.0],
      [50.0, 23.5],
      [50.5, 27.0],
      [51.0, 30.5],
      [51.2, 34.0],
      [51.0, 38.0],
      [50.5, 42.0],
    ],
  ],

  // East Fall - Black, runs eastward with moderate curve
  'east-fall': [
    [
      [48.5, 14.5],
      [49.0, 18.0],
      [49.5, 21.5],
      [50.0, 25.0],
      [50.5, 28.5],
      [51.0, 32.0],
      [51.5, 35.5],
      [52.0, 39.0],
      [52.2, 42.5],
      [52.0, 46.0],
      [51.8, 49.5],
    ],
  ],

  // Upper East Fall - Black, short steep upper pitch
  'upper-east-fall': [
    [
      [48.0, 6.5],
      [48.2, 9.5],
      [48.5, 12.0],
      [48.5, 14.5],
    ],
  ],

  // Rime - Black, icy steep trail on the left side
  'rime': [
    [
      [44.0, 5.5],
      [43.5, 9.0],
      [43.0, 12.5],
      [42.5, 16.0],
      [42.0, 19.5],
      [41.8, 23.0],
      [41.5, 26.5],
      [41.2, 30.0],
      [41.0, 33.5],
      [41.0, 37.0],
    ],
  ],

  // Reason - Black, challenging run on the far left
  'reason': [
    [
      [43.5, 6.0],
      [43.0, 9.5],
      [42.5, 13.0],
      [42.0, 16.5],
      [41.5, 20.0],
      [41.2, 23.5],
      [41.0, 27.0],
      [40.8, 30.5],
      [40.8, 34.0],
      [41.0, 37.5],
    ],
  ],

  // Julio - Black, steep trail on the far left of Killington Peak
  'julio': [
    [
      [43.0, 6.5],
      [42.5, 10.0],
      [42.0, 13.5],
      [41.5, 17.0],
      [41.0, 20.5],
      [40.8, 24.0],
      [40.5, 27.5],
      [40.2, 31.0],
      [40.0, 34.0],
    ],
  ],

  // High Road - Blue, intermediate traversing trail heading right
  'high-road': [
    [
      [46.0, 6.0],
      [46.5, 9.5],
      [47.0, 13.0],
      [47.5, 16.5],
      [48.0, 20.0],
      [48.5, 24.0],
      [49.0, 28.0],
      [49.5, 32.0],
      [50.0, 36.0],
      [50.5, 40.0],
      [51.0, 44.0],
    ],
  ],

  // North Way - Blue, traverses left from summit
  'north-way': [
    [
      [45.0, 6.0],
      [44.5, 9.5],
      [44.0, 13.0],
      [43.5, 16.5],
      [43.0, 20.0],
      [42.5, 24.0],
      [42.0, 28.0],
      [41.5, 32.0],
      [41.0, 36.0],
      [40.5, 40.0],
      [40.0, 43.5],
    ],
  ],

  // Great Eastern (K.P.) - Green, long gentle winding trail from the summit
  'great-eastern-kp': [
    [
      [45.5, 5.5],
      [45.0, 9.0],
      [44.5, 12.5],
      [44.0, 16.5],
      [43.5, 20.5],
      [43.0, 25.0],
      [42.5, 29.5],
      [42.0, 34.0],
      [41.5, 38.5],
      [41.0, 43.0],
      [40.5, 47.5],
      [40.0, 52.0],
      [40.0, 56.5],
      [40.5, 60.0],
    ],
  ],

  // FIS - Black, race trail running right from the summit
  'fis': [
    [
      [48.0, 6.0],
      [48.5, 9.5],
      [49.0, 13.0],
      [49.5, 16.5],
      [50.0, 20.0],
      [50.5, 23.5],
      [51.0, 27.0],
      [51.5, 31.0],
      [52.0, 35.0],
      [52.2, 38.0],
    ],
  ],

  // Lower FIS - Blue, lower continuation of FIS
  'lower-fis': [
    [
      [52.2, 38.0],
      [52.2, 41.5],
      [52.0, 45.0],
      [51.8, 48.5],
      [51.5, 52.0],
      [51.2, 55.5],
      [51.0, 59.0],
    ],
  ],

  // Solitude - Blue, quieter trail running right of FIS
  'solitude': [
    [
      [49.0, 7.0],
      [49.5, 10.5],
      [50.0, 14.0],
      [50.5, 17.5],
      [51.0, 21.0],
      [51.5, 24.5],
      [51.5, 28.0],
      [51.2, 32.0],
      [51.0, 36.0],
      [50.5, 40.0],
      [50.0, 44.0],
      [49.5, 48.0],
    ],
  ],

  // K-1 Gondola Run - Blue, follows the K-1 Gondola line down
  'k1-gondola-run': [
    [
      [46.0, 5.0],
      [46.5, 8.5],
      [47.0, 12.0],
      [47.5, 16.0],
      [48.0, 20.0],
      [48.5, 24.0],
      [49.0, 28.0],
      [49.5, 32.0],
      [50.0, 36.0],
      [50.5, 40.5],
      [51.0, 45.0],
      [51.5, 49.5],
      [52.0, 54.0],
      [52.5, 58.0],
    ],
  ],

  // Anarchy - Double-black glade, in the trees on the far left
  'anarchy': [
    [
      [43.5, 8.0],
      [43.0, 11.5],
      [42.5, 15.0],
      [42.0, 18.5],
      [41.5, 22.0],
      [41.2, 25.5],
      [41.0, 29.0],
      [40.8, 32.5],
      [40.5, 36.0],
    ],
  ],

  // Upper Canyon - Black, upper section of the Canyon trail
  'upper-canyon': [
    [
      [47.0, 7.0],
      [47.5, 10.5],
      [48.0, 14.0],
      [48.2, 17.5],
      [48.5, 21.0],
      [48.8, 24.5],
    ],
  ],

  // Lower Canyon - Black, lower section continuing to mid-mountain
  'lower-canyon': [
    [
      [48.8, 24.5],
      [49.0, 28.0],
      [49.2, 31.5],
      [49.5, 35.0],
      [49.8, 38.5],
      [50.0, 42.0],
      [50.2, 45.5],
    ],
  ],

  // Old Superstar - Black, the original Superstar route, slightly left of current
  'old-superstar': [
    [
      [46.0, 8.0],
      [46.5, 11.5],
      [47.0, 15.0],
      [47.5, 18.5],
      [48.0, 22.0],
      [48.2, 25.5],
      [48.5, 29.0],
      [48.8, 33.0],
      [49.0, 37.0],
      [49.2, 41.0],
      [49.5, 45.0],
      [49.8, 49.0],
      [50.0, 53.0],
    ],
  ],

  // Killington Liftline - Black, follows the main K-1 lift straight down
  'killington-liftline': [
    [
      [45.5, 5.0],
      [46.0, 9.0],
      [46.5, 13.0],
      [47.0, 17.0],
      [47.5, 21.0],
      [48.0, 25.0],
      [48.2, 29.0],
      [48.5, 33.0],
      [48.8, 37.0],
      [49.0, 41.0],
      [49.2, 45.0],
      [49.5, 49.0],
      [49.8, 53.0],
      [50.0, 56.5],
    ],
  ],

  // Superstar Glade - Double-black glade adjacent to Superstar
  'superstar-glade': [
    [
      [47.2, 12.0],
      [47.8, 15.5],
      [48.2, 19.0],
      [48.5, 22.5],
      [48.8, 26.0],
      [49.0, 30.0],
      [49.2, 34.0],
      [49.5, 38.0],
    ],
  ],

  // Header (K.P.) - Blue, intermediate trail heading left
  'header-kp': [
    [
      [44.5, 7.0],
      [44.0, 10.5],
      [43.5, 14.0],
      [43.2, 17.5],
      [43.0, 21.0],
      [42.8, 24.5],
      [42.5, 28.0],
      [42.2, 31.5],
      [42.0, 35.0],
      [42.0, 38.5],
    ],
  ],

  // Mouse Run - Blue, winding intermediate with turns
  'mouse-run': [
    [
      [45.0, 7.5],
      [44.5, 11.0],
      [44.0, 14.5],
      [43.5, 18.0],
      [43.2, 21.5],
      [43.0, 25.0],
      [42.8, 28.5],
      [42.5, 32.0],
      [42.2, 35.5],
      [42.0, 39.0],
      [42.0, 42.5],
    ],
  ],

  // Low Road - Green, gentle lower trail
  'low-road': [
    [
      [48.0, 38.0],
      [48.5, 41.5],
      [49.0, 45.0],
      [49.5, 48.5],
      [50.0, 52.0],
      [50.5, 55.5],
      [51.0, 58.5],
      [51.5, 61.5],
    ],
  ],

  // The Mall - Green, wide easy cruiser heading left toward base
  'the-mall': [
    [
      [47.0, 40.0],
      [46.5, 43.5],
      [46.0, 47.0],
      [45.5, 50.5],
      [45.0, 54.0],
      [44.5, 57.5],
      [44.0, 61.0],
      [43.5, 64.0],
    ],
  ],

  // ============================================================
  // BEAR MOUNTAIN
  // Summit ridge ~(79-82, 15-18), Base lodge ~(88-91, 60-65)
  // ============================================================

  // Outer Limits - Famous steep mogul run, straight fall-line down the face
  'outer-limits': [
    [
      [79.5, 16.0],
      [79.6, 19.5],
      [79.8, 23.0],
      [80.0, 26.5],
      [80.2, 30.0],
      [80.4, 33.5],
      [80.5, 37.0],
      [80.7, 40.5],
      [80.8, 44.0],
      [81.0, 48.0],
      [81.2, 52.0],
      [81.5, 56.0],
      [82.0, 59.5],
      [82.8, 62.5],
    ],
  ],

  // Devil's Fiddle - Steep expert trail, parallels Outer Limits slightly right
  'devils-fiddle': [
    [
      [80.5, 16.5],
      [80.8, 20.0],
      [81.0, 23.5],
      [81.2, 27.0],
      [81.5, 30.5],
      [81.8, 34.0],
      [82.0, 37.5],
      [82.2, 41.0],
      [82.5, 44.5],
      [82.8, 48.0],
      [83.0, 52.0],
      [83.5, 56.0],
      [84.0, 59.5],
      [84.5, 62.5],
    ],
  ],

  // Wildfire - Black diamond, runs right of Devil's Fiddle
  'wildfire': [
    [
      [81.5, 17.0],
      [82.0, 20.5],
      [82.5, 24.0],
      [83.0, 27.5],
      [83.2, 31.0],
      [83.5, 34.5],
      [83.8, 38.0],
      [84.0, 41.5],
      [84.0, 45.0],
      [83.8, 47.5],
    ],
  ],

  // Lower Wildfire - Blue, continues from Wildfire curving right to the base
  'lower-wildfire': [
    [
      [83.8, 47.5],
      [84.2, 50.5],
      [84.8, 53.5],
      [85.5, 56.0],
      [86.2, 58.5],
      [87.0, 60.5],
      [87.8, 62.5],
    ],
  ],

  // Bear Claw - Blue, sweeps right from upper mountain with nice curvature
  'bear-claw': [
    [
      [82.0, 18.0],
      [82.8, 21.5],
      [83.5, 25.0],
      [84.2, 28.5],
      [85.0, 32.0],
      [85.8, 36.0],
      [86.5, 40.0],
      [87.0, 44.0],
      [87.5, 48.0],
      [88.0, 52.0],
      [88.2, 56.0],
      [88.5, 59.5],
      [88.8, 62.5],
    ],
  ],

  // Bear Mountain Liftline - Black, follows the lift line up the center
  'bear-mountain-liftline': [
    [
      [80.8, 16.5],
      [81.2, 20.5],
      [81.8, 24.5],
      [82.2, 28.5],
      [82.8, 32.5],
      [83.2, 36.5],
      [83.8, 40.5],
      [84.2, 44.5],
      [84.8, 48.5],
      [85.2, 52.5],
      [85.8, 56.0],
      [86.2, 59.5],
      [86.5, 62.0],
    ],
  ],

  // Bear Trax - Blue, traverses right on a gradual descent
  'bear-trax': [
    [
      [82.5, 19.0],
      [83.5, 22.5],
      [84.5, 26.0],
      [85.5, 30.0],
      [86.5, 34.0],
      [87.2, 38.0],
      [87.8, 42.0],
      [88.2, 46.0],
      [88.5, 50.0],
      [89.0, 54.0],
      [89.2, 58.0],
      [89.2, 61.0],
    ],
  ],

  // Falls Brook - Blue, runs along the right side of Bear Mountain
  'falls-brook': [
    [
      [83.0, 20.0],
      [84.0, 24.0],
      [85.0, 28.0],
      [86.0, 32.0],
      [87.0, 36.0],
      [88.0, 40.0],
      [88.8, 44.0],
      [89.2, 48.0],
      [89.5, 52.0],
      [89.8, 56.0],
      [90.0, 59.5],
      [90.0, 62.0],
    ],
  ],

  // Skyeburst (Bear) - Blue, connects from Skye Peak side on the left
  'skye-burst-bear': [
    [
      [77.5, 18.0],
      [78.0, 22.0],
      [78.5, 26.0],
      [79.0, 30.0],
      [79.5, 34.0],
      [80.0, 38.0],
      [80.2, 42.0],
      [80.5, 46.0],
      [81.0, 50.0],
      [81.5, 54.0],
      [82.2, 58.0],
      [83.0, 61.0],
    ],
  ],

  // Bear Run - Blue, sweeps far right on a gentle arc
  'bear-run': [
    [
      [83.5, 19.5],
      [84.5, 23.5],
      [85.5, 27.5],
      [86.5, 31.5],
      [87.5, 35.5],
      [88.2, 39.5],
      [88.8, 43.5],
      [89.2, 47.5],
      [89.5, 51.5],
      [90.0, 55.5],
      [90.2, 59.5],
      [90.5, 63.0],
    ],
  ],

  // Growler - Glade (double-black), tight trees between Outer Limits and center
  'growler': [
    [
      [80.0, 20.0],
      [80.1, 24.0],
      [80.2, 28.0],
      [80.4, 32.0],
      [80.6, 36.0],
      [80.8, 40.0],
      [81.0, 44.0],
      [81.2, 48.0],
      [81.5, 52.0],
      [82.0, 55.5],
    ],
  ],

  // Centerpiece - Glade (double-black), between Outer Limits and Devil's Fiddle
  'centerpiece': [
    [
      [80.2, 21.0],
      [80.4, 25.0],
      [80.6, 29.0],
      [80.8, 33.0],
      [81.0, 37.0],
      [81.2, 41.0],
      [81.5, 45.0],
      [81.8, 49.0],
      [82.2, 53.0],
    ],
  ],

  // Spacewalk - Glade (double-black), in the trees right of the main trails
  'spacewalk': [
    [
      [82.5, 22.0],
      [82.8, 26.0],
      [83.0, 30.0],
      [83.2, 34.0],
      [83.5, 38.0],
      [83.8, 42.0],
      [84.0, 46.0],
      [84.2, 50.0],
      [84.5, 53.5],
    ],
  ],

  // The Stash - Black terrain park, winding through the trees
  'the-stash': [
    [
      [84.0, 22.5],
      [84.5, 26.5],
      [85.0, 30.5],
      [85.2, 34.5],
      [85.5, 38.5],
      [85.8, 42.5],
      [86.0, 46.5],
      [86.2, 50.5],
      [86.5, 54.5],
      [87.0, 58.0],
    ],
  ],

  // Lil' Stash - Blue terrain park, shorter version near The Stash
  'lil-stash': [
    [
      [84.5, 35.0],
      [85.0, 38.5],
      [85.2, 42.0],
      [85.5, 45.5],
      [86.0, 49.0],
      [86.2, 52.5],
      [86.5, 56.0],
      [87.0, 59.0],
    ],
  ],
};
