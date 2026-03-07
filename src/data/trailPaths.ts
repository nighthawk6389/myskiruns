// Trail path coordinate data for polyline overlays on the trail map image.
// Each trail is keyed by trail ID and contains an array of segments.
// Each segment is an array of [x, y] percentage coordinate pairs (0-100)
// matching the SVG viewBox="0 0 100 100" used in ImageMap.tsx.
//
// Coordinates are percentages of image width (x) and height (y).
// Image: killington-trail-map.jpg (4572x2704px)
//
// Peak layout on this map (left to right):
//   Snowshed (0-8%) → Sunrise (5-15%) → Bear Mountain (15-35%)
//   → Skye Peak (30-55%) → Killington Peak (45-65%)
//   → Snowdon (65-88%) → Ramshead (85-98%)
//
// All 7 peaks mapped (119 trails).

export type TrailPathSegment = [number, number][];

export const trailPaths: Record<string, TrailPathSegment[]> = {
  // ============================================================
  // SNOWSHED AREA
  // Far left of map, bottom area. Small beginner terrain.
  // Base lodge at ~(4, 72). Top of lifts ~(6, 55).
  // ============================================================

  'snowshed-slope': [
    [[5.5, 55], [5.2, 58], [4.8, 61], [4.5, 64], [4.2, 67], [4.0, 70]]
  ],
  'yodeler': [
    [[6.5, 55], [6.2, 58], [5.8, 61], [5.5, 64], [5.2, 67], [4.8, 70]]
  ],
  'idler': [
    [[4.5, 55], [4.3, 58], [4.0, 61], [3.8, 64], [3.5, 67], [3.3, 70]]
  ],
  'snow-play': [
    [[5.0, 64], [4.8, 66], [4.5, 68], [4.2, 70]]
  ],
  'snowshed-crossover': [
    [[3.5, 60], [4.5, 60], [5.5, 60], [6.5, 60]]
  ],

  // ============================================================
  // SUNRISE AREA
  // Left side of map. Sign at (8.6%, 41.9%).
  // Small area with gentle trails around condos/village.
  // ============================================================

  'sun-dog': [
    [[7.5, 46], [7.3, 48], [7.2, 50], [7.0, 52], [6.8, 54], [6.5, 56]]
  ],
  'rendezvous': [
    [[9.0, 43], [8.0, 44], [7.0, 44.5], [6.0, 45], [5.5, 46]]
  ],
  'bear-cub': [
    [[12.0, 44], [12.0, 46], [11.5, 48], [11.0, 50], [10.5, 52], [10.0, 54]]
  ],
  'bear-view': [
    [[10.5, 42], [11.0, 43], [11.5, 44], [12.0, 45]]
  ],
  'sunrise-connector': [
    [[10.0, 43], [11.0, 43], [12.0, 44], [13.0, 44], [14.0, 45]]
  ],

  // ============================================================
  // BEAR MOUNTAIN
  // Left-center of map. Summit sign at ~(26%, 28%).
  // Base camp at ~(20%, 58%). Major face with mogul runs.
  // ============================================================

  // Outer Limits - the famous wide mogul run, center of Bear face
  'outer-limits': [
    [[25.5, 30], [25.0, 33], [24.5, 36], [24.0, 39], [23.5, 42], [23.0, 45], [22.5, 48], [22.0, 51]]
  ],
  // Devil's Fiddle - steep run left of Outer Limits
  'devils-fiddle': [
    [[24.0, 30], [23.5, 33], [23.0, 36], [22.5, 39], [22.0, 42], [21.5, 45], [21.0, 48]]
  ],
  // Wildfire - right side of Bear face, curves right
  'wildfire': [
    [[27.0, 32], [27.5, 35], [28.0, 38], [28.5, 41], [29.0, 44], [29.0, 47]]
  ],
  // Lower Wildfire - continuation below Wildfire
  'lower-wildfire': [
    [[29.0, 47], [28.5, 49], [28.0, 51], [27.5, 53], [27.0, 55]]
  ],
  // Bear Claw - blue trail on the left side
  'bear-claw': [
    [[21.0, 30], [20.5, 33], [20.0, 36], [19.5, 39], [19.0, 42], [18.5, 45]]
  ],
  // Growler - glade left of Outer Limits
  'growler': [
    [[23.0, 33], [22.5, 36], [22.0, 39], [21.5, 42], [21.0, 45]]
  ],
  // Centerpiece - glade in center of Bear face
  'centerpiece': [
    [[25.0, 34], [24.5, 37], [24.0, 40], [23.5, 43], [23.0, 46]]
  ],
  // Spacewalk - lower left glade area
  'spacewalk': [
    [[21.5, 43], [21.0, 46], [20.5, 49], [20.0, 52], [19.5, 55]]
  ],
  // Bear Trax - blue trail going right from mid-mountain
  'bear-trax': [
    [[26.5, 42], [27.5, 44], [28.5, 46], [29.5, 48], [30.5, 50], [31.5, 52]]
  ],
  // Falls Brook - blue trail on the right side
  'falls-brook': [
    [[29.0, 38], [30.0, 40], [31.0, 42], [32.0, 44], [33.0, 46], [34.0, 48]]
  ],
  // Skyeburst (Bear) - lower connecting trail heading right to Skye area
  'skye-burst-bear': [
    [[27.0, 52], [28.5, 54], [30.0, 55], [31.5, 56], [33.0, 57], [35.0, 58]]
  ],
  // Bear Mountain Liftline - straight line up the center (trail alongside lift)
  'bear-mountain-liftline': [
    [[24.0, 56], [24.5, 52], [25.0, 48], [25.0, 44], [25.5, 40], [25.5, 36], [26.0, 32]]
  ],
  // The Stash - terrain park in trees on right side
  'the-stash': [
    [[32.0, 30], [32.5, 33], [33.0, 36], [33.5, 39], [34.0, 42]]
  ],
  // Lil' Stash - below The Stash
  'lil-stash': [
    [[34.0, 42], [34.0, 44], [33.5, 46], [33.0, 48], [32.5, 50]]
  ],
  // Bear Run - bottom trail from base area
  'bear-run': [
    [[22.0, 56], [23.0, 58], [24.5, 60], [26.0, 61], [28.0, 62]]
  ],

  // ============================================================
  // SKYE PEAK
  // Center-left area. Skye Peak sign at ~(38%, 30%).
  // Large area with many intermediate and expert trails.
  // Trails fan down to base lodge at Ramshead area.
  // ============================================================

  // Skyelark - blue trail going down from Skye Peak area, left side
  'skyelark': [
    [[38.0, 35], [37.0, 38], [36.0, 41], [35.0, 44], [34.5, 47], [34.0, 50]]
  ],
  // Upper Skyelark - upper section
  'upper-skyelark': [
    [[40.0, 28], [39.5, 30], [39.0, 32], [38.5, 34], [38.0, 35]]
  ],
  // Skyeburst - blue trail center of Skye area going down
  'skyeburst': [
    [[39.0, 36], [38.5, 39], [38.0, 42], [37.0, 45], [36.0, 48]]
  ],
  // Upper Skyeburst
  'upper-skyeburst': [
    [[41.0, 28], [40.5, 30], [40.0, 33], [39.5, 35], [39.0, 36]]
  ],
  // Skye Hawk - blue trail
  'skye-hawk': [
    [[42.0, 28], [41.5, 31], [41.0, 34], [40.5, 37], [40.0, 40]]
  ],
  // Skyebits - blue trail
  'skyebits': [
    [[37.0, 32], [36.5, 35], [36.0, 38], [35.5, 41], [35.0, 43]]
  ],
  // Cruise Control - blue trail mid area
  'cruise-control': [
    [[43.0, 30], [42.0, 33], [41.0, 36], [40.0, 39], [39.0, 42]]
  ],
  // Mouse Trap - blue trail
  'mouse-trap': [
    [[44.0, 32], [43.0, 35], [42.5, 38], [42.0, 41], [41.5, 44]]
  ],
  // Somewhere - blue trail
  'somewhere': [
    [[40.0, 20], [39.5, 23], [39.0, 26], [38.5, 28], [38.0, 30]]
  ],
  // Breakaway - blue trail
  'breakaway': [
    [[45.0, 26], [44.0, 29], [43.0, 32], [42.0, 35], [41.0, 38]]
  ],
  // Touch Down - blue trail
  'touch-down': [
    [[44.5, 34], [43.5, 37], [42.5, 40], [41.5, 43], [41.0, 46]]
  ],
  // Patsy's - blue trail
  'patsys': [
    [[43.5, 36], [42.5, 39], [41.5, 42], [40.5, 45], [40.0, 48]]
  ],
  // Twister - blue trail
  'twister': [
    [[42.0, 38], [41.5, 41], [41.0, 44], [40.5, 47], [40.0, 50]]
  ],
  // Catwalk - blue trail going across
  'catwalk': [
    [[45.0, 44], [43.5, 45], [42.0, 46], [40.5, 47], [39.0, 48]]
  ],
  // Upper Catwalk
  'upper-catwalk': [
    [[46.0, 38], [44.5, 39], [43.0, 40], [41.5, 41], [40.0, 42]]
  ],
  // Great Eastern - green trail going right towards Killington
  'great-eastern': [
    [[40.0, 48], [42.0, 49], [44.0, 50], [46.0, 51], [48.0, 52], [50.0, 53]]
  ],
  // Home Stretch - green trail at bottom
  'home-stretch': [
    [[44.0, 56], [45.5, 57], [47.0, 58], [48.5, 59], [50.0, 60]]
  ],
  // Lower Home Stretch
  'lower-home-stretch': [
    [[50.0, 60], [51.0, 61], [52.0, 62], [53.0, 63], [54.0, 64]]
  ],
  // Juggernaut - green trail
  'juggernaut': [
    [[38.0, 50], [39.0, 52], [40.0, 54], [41.0, 56], [42.0, 58], [43.0, 60]]
  ],
  // Vertigo - double-black, steep expert run
  'vertigo': [
    [[44.0, 46], [43.5, 48], [43.0, 50], [42.5, 52], [42.0, 54]]
  ],
  // Upper Vertigo
  'upper-vertigo': [
    [[45.0, 40], [44.5, 42], [44.0, 44], [44.0, 46]]
  ],
  // Ovation - double-black
  'ovation': [
    [[46.0, 42], [45.5, 44], [45.0, 46], [44.5, 48], [44.0, 50], [43.5, 52]]
  ],
  // Needle's Eye - black trail in center-bottom
  'needles-eye': [
    [[45.5, 48], [45.0, 50], [44.5, 52], [44.0, 54], [43.5, 56], [43.0, 58]]
  ],
  // Panic Button - black trail
  'panic-button': [
    [[46.5, 48], [46.0, 50], [45.5, 52], [45.0, 54], [44.5, 56]]
  ],
  // Dream Maker - black trail
  'dream-maker': [
    [[42.0, 22], [41.5, 25], [41.0, 28], [40.5, 31], [40.0, 34]]
  ],
  // Dream Maker Headwall - double-black steep section
  'dream-maker-headwall': [
    [[42.5, 18], [42.0, 20], [42.0, 22]]
  ],
  // Highline - black trail
  'highline': [
    [[43.0, 24], [42.5, 27], [42.0, 30], [41.5, 33], [41.0, 36]]
  ],
  // Pipe Dream - blue trail on the left
  'pipe-dream': [
    [[36.0, 22], [35.5, 25], [35.0, 28], [34.5, 31], [34.0, 34]]
  ],
  // Valley Plunge - blue trail
  'valley-plunge': [
    [[37.0, 34], [36.5, 37], [36.0, 40], [35.5, 43], [35.0, 46]]
  ],
  // Field Goal - blue trail
  'field-goal': [
    [[39.0, 48], [39.5, 50], [40.0, 52], [40.5, 54], [41.0, 56]]
  ],
  // Roundabout - blue trail
  'roundabout': [
    [[35.0, 46], [35.5, 48], [36.0, 50], [37.0, 52], [38.0, 54]]
  ],
  // Roundabout Glade
  'roundabout-glade': [
    [[34.5, 48], [34.5, 50], [35.0, 52], [35.5, 54]]
  ],
  // Tin Man - blue trail
  'tin-man': [
    [[36.5, 44], [36.0, 47], [35.5, 50], [35.0, 53]]
  ],
  // Skye Peak Liftline - black trail along the lift
  'skye-peak-liftline': [
    [[40.0, 50], [40.5, 47], [41.0, 44], [41.0, 41], [41.5, 38], [42.0, 35], [42.0, 32]]
  ],
  // Great Bear - blue trail
  'great-bear': [
    [[35.0, 36], [34.5, 39], [34.0, 42], [33.5, 45], [33.0, 48]]
  ],
  // Upper Great Bear
  'upper-great-bear': [
    [[36.0, 30], [35.5, 33], [35.0, 36]]
  ],
  // Woodward Peace Park - terrain park
  'woodward-peace-park': [
    [[37.0, 42], [37.5, 44], [38.0, 46], [38.5, 48]]
  ],

  // ============================================================
  // KILLINGTON PEAK
  // Center of map. Summit sign at (56.2%, 6.9%).
  // The highest peak with expert terrain radiating down.
  // ============================================================

  // Superstar - the famous mogul run, wide face left of summit
  'superstar': [
    [[53.0, 14], [52.5, 17], [52.0, 20], [51.5, 23], [51.0, 26], [50.5, 29], [50.0, 32], [49.5, 35]]
  ],
  // Cascade - double-black right of Superstar
  'cascade': [
    [[55.0, 14], [54.5, 17], [54.0, 20], [53.5, 23], [53.0, 26], [52.5, 29]]
  ],
  // Downdraft - double-black steep
  'downdraft': [
    [[56.0, 14], [55.5, 17], [55.0, 20], [54.5, 23], [54.0, 26]]
  ],
  // Double Dipper - double-black
  'double-dipper': [
    [[57.0, 14], [56.5, 17], [56.0, 20], [55.5, 23], [55.0, 26], [54.5, 29]]
  ],
  // Big Dipper Glade
  'big-dipper-glade': [
    [[57.5, 18], [57.0, 21], [56.5, 24], [56.0, 27]]
  ],
  // Flume - black trail
  'flume': [
    [[54.0, 14], [53.5, 17], [53.0, 20], [52.5, 23], [52.0, 26]]
  ],
  // Escapade - black trail
  'escapade': [
    [[52.0, 15], [51.5, 18], [51.0, 21], [50.5, 24], [50.0, 27]]
  ],
  // East Fall - black trail on the right side
  'east-fall': [
    [[59.0, 18], [59.0, 21], [58.5, 24], [58.0, 27], [57.5, 30], [57.0, 33]]
  ],
  // Upper East Fall
  'upper-east-fall': [
    [[59.5, 12], [59.0, 14], [59.0, 16], [59.0, 18]]
  ],
  // Rime - black trail center area
  'rime': [
    [[55.0, 20], [54.5, 23], [54.0, 26], [53.5, 29], [53.0, 32]]
  ],
  // Reason - black trail
  'reason': [
    [[54.0, 22], [53.5, 25], [53.0, 28], [52.5, 31], [52.0, 34]]
  ],
  // Julio - black trail
  'julio': [
    [[56.0, 22], [55.5, 25], [55.0, 28], [54.5, 31], [54.0, 34]]
  ],
  // High Road - blue trail
  'high-road': [
    [[50.0, 16], [49.5, 19], [49.0, 22], [48.5, 25], [48.0, 28]]
  ],
  // North Way - blue trail
  'north-way': [
    [[51.0, 18], [50.5, 21], [50.0, 24], [49.5, 27]]
  ],
  // Great Eastern (KP section) - green trail heading left
  'great-eastern-kp': [
    [[52.0, 32], [50.0, 34], [48.0, 36], [46.0, 38], [44.0, 40]]
  ],
  // FIS - black race trail
  'fis': [
    [[56.5, 30], [56.0, 33], [55.5, 36], [55.0, 39], [54.5, 42], [54.0, 45]]
  ],
  // Lower FIS
  'lower-fis': [
    [[54.0, 45], [53.5, 47], [53.0, 49], [52.5, 51], [52.0, 53]]
  ],
  // Solitude - blue trail upper left area
  'solitude': [
    [[48.0, 10], [47.0, 13], [46.0, 16], [45.0, 19], [44.0, 22]]
  ],
  // K-1 Gondola Run - blue trail from summit towards Skye base
  'k1-gondola-run': [
    [[55.0, 10], [53.0, 14], [51.0, 18], [49.0, 22], [47.0, 26], [45.0, 30]]
  ],
  // Anarchy - double-black glade
  'anarchy': [
    [[51.0, 16], [50.5, 19], [50.0, 22], [49.5, 25]]
  ],
  // Upper Canyon - black trail
  'upper-canyon': [
    [[58.0, 26], [57.5, 29], [57.0, 32], [56.5, 35]]
  ],
  // Lower Canyon
  'lower-canyon': [
    [[56.5, 35], [56.0, 38], [55.5, 41], [55.0, 44]]
  ],
  // Old Superstar - black trail
  'old-superstar': [
    [[52.0, 28], [51.5, 31], [51.0, 34], [50.5, 37], [50.0, 40]]
  ],
  // Killington Liftline - black trail along the lift
  'killington-liftline': [
    [[55.5, 42], [55.5, 38], [56.0, 34], [56.0, 30], [56.0, 26], [56.0, 22], [56.0, 18], [56.0, 14]]
  ],
  // Superstar Glade - double-black glade
  'superstar-glade': [
    [[51.5, 22], [51.0, 25], [50.5, 28], [50.0, 31]]
  ],
  // Header (KP) - blue trail
  'header-kp': [
    [[58.5, 28], [58.0, 31], [57.5, 34], [57.0, 37], [56.5, 40]]
  ],
  // Mouse Run - blue trail
  'mouse-run': [
    [[60.0, 30], [59.5, 33], [59.0, 36], [58.5, 39], [58.0, 42]]
  ],
  // Low Road - green trail
  'low-road': [
    [[54.0, 48], [53.0, 50], [52.0, 52], [51.0, 54], [50.0, 56]]
  ],
  // The Mall - green trail at the bottom
  'the-mall': [
    [[52.0, 54], [53.0, 55], [54.0, 56], [55.0, 57], [56.0, 58]]
  ],

  // ============================================================
  // SNOWDON
  // Right side of map. Sign at (81.8%, 21.3%).
  // Mid-size area with mixed terrain.
  // ============================================================

  // Great Northern - blue trail on the left side of Snowdon
  'great-northern': [
    [[74.0, 28], [73.5, 31], [73.0, 34], [72.5, 37], [72.0, 40], [71.5, 43]]
  ],
  // Bunny Buster - green trail
  'bunny-buster': [
    [[76.0, 30], [75.5, 33], [75.0, 36], [74.5, 39], [74.0, 42], [73.5, 45]]
  ],
  // Chute - black trail straight down
  'chute': [
    [[78.0, 26], [77.5, 29], [77.0, 32], [76.5, 35], [76.0, 38]]
  ],
  // Conclusion - double-black
  'conclusion': [
    [[76.5, 26], [76.0, 29], [75.5, 32], [75.0, 35], [74.5, 38]]
  ],
  // Upper FIS - green trail
  'upper-fis': [
    [[79.0, 26], [78.5, 29], [78.0, 32], [77.5, 35], [77.0, 38]]
  ],
  // Mountain Run - green trail
  'mountain-run': [
    [[80.0, 28], [79.5, 31], [79.0, 34], [78.5, 37], [78.0, 40]]
  ],
  // Mountain Training Station - green trail
  'mountain-training': [
    [[80.5, 30], [80.0, 33], [79.5, 36], [79.0, 39]]
  ],
  // Snowdon Liftline - blue trail along lift
  'snowdon-liftline': [
    [[78.0, 44], [78.5, 40], [79.0, 36], [79.5, 32], [80.0, 28], [80.5, 24]]
  ],
  // Upper Snowdon - blue trail
  'upper-snowdon': [
    [[81.0, 24], [80.5, 27], [80.0, 30], [79.5, 33], [79.0, 36]]
  ],
  // Lower Snowdon - blue trail
  'lower-snowdon': [
    [[79.0, 36], [78.5, 39], [78.0, 42], [77.5, 45], [77.0, 48]]
  ],
  // Bittersweet - blue trail
  'bittersweet': [
    [[82.0, 26], [81.5, 29], [81.0, 32], [80.5, 35], [80.0, 38], [79.5, 41]]
  ],
  // Sass - blue trail
  'sass': [
    [[83.0, 28], [82.5, 31], [82.0, 34], [81.5, 37], [81.0, 40]]
  ],
  // Northstar - black trail
  'northstar': [
    [[75.0, 30], [74.5, 33], [74.0, 36], [73.5, 39], [73.0, 42]]
  ],
  // Royal Flush - black trail
  'royal-flush': [
    [[76.0, 32], [75.5, 35], [75.0, 38], [74.5, 41], [74.0, 44]]
  ],
  // Upper Northbrook - blue trail going down
  'upper-northbrook': [
    [[72.0, 44], [72.5, 47], [73.0, 50], [73.5, 53]]
  ],
  // Lower Northbrook - green trail
  'lower-northbrook': [
    [[73.5, 53], [74.0, 55], [74.5, 57], [75.0, 59]]
  ],
  // Snowdon Glades - black glade
  'snowdon-glades': [
    [[77.0, 30], [76.5, 33], [76.0, 36], [75.5, 39]]
  ],

  // ============================================================
  // RAMSHEAD
  // Far right of map. Sign at (92.0%, 26.7%).
  // Beginner/intermediate area with gentle slopes.
  // ============================================================

  // Easy Street - green trail on the right, the main easy way down
  'easy-street': [
    [[94.0, 30], [94.5, 33], [95.0, 36], [95.0, 39], [95.0, 42], [94.5, 45], [94.0, 48]]
  ],
  // Swirl - green trail
  'swirl': [
    [[91.0, 30], [91.0, 33], [91.0, 36], [91.0, 39], [91.0, 42]]
  ],
  // Treezy - green glade
  'treezy': [
    [[90.0, 32], [90.0, 35], [90.0, 38], [90.0, 41]]
  ],
  // Squeeze Play - green glade
  'squeeze-play': [
    [[89.0, 34], [89.0, 37], [89.0, 40], [89.0, 43]]
  ],
  // Ramshead Run - green trail
  'ramshead-run': [
    [[93.0, 30], [93.0, 33], [92.5, 36], [92.5, 39], [92.0, 42], [92.0, 45]]
  ],
  // Ramshead Liftline - blue trail along lift
  'ramshead-liftline': [
    [[92.0, 46], [92.0, 42], [92.0, 38], [92.0, 34], [92.0, 30]]
  ],
  // Header - blue trail
  'header': [
    [[88.0, 28], [88.0, 31], [87.5, 34], [87.5, 37], [87.0, 40]]
  ],
  // Vagabond - blue trail
  'vagabond': [
    [[87.0, 30], [86.5, 33], [86.0, 36], [86.0, 39], [86.0, 42]]
  ],
  // Caper - blue trail
  'caper': [
    [[86.0, 26], [86.0, 29], [86.0, 32], [86.0, 35], [86.0, 38]]
  ],
  // Timberline - blue trail
  'timberline': [
    [[89.0, 28], [89.0, 31], [89.0, 34], [88.5, 37], [88.5, 40]]
  ],
  // Start Park - terrain park
  'start-park': [
    [[90.5, 38], [91.0, 40], [91.5, 42], [92.0, 44]]
  ],
};
