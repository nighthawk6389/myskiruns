/**
 * Trail overlay coordinates mapped to the actual Killington trail map image.
 * Coordinates are percentages (0-100) of image width (x) and height (y).
 * 0,0 = top-left of the image.
 *
 * These were mapped by analyzing the actual killington-trail-map.jpg image
 * (4572x2704 pixels) and identifying where each trail appears on the map.
 *
 * The Killington trail map shows the resort from a southern viewpoint:
 * - Snowshed/Sunrise: far left, lower elevation
 * - Ramshead: center-left
 * - Snowdon: center
 * - Skye Peak: center-right
 * - Killington Peak: the summit, upper-center-right
 * - Bear Mountain: separate peak, far right
 */

// Define accurate peak regions matching the actual trail map image layout.
// Each region describes the bounding area for that peak's trails on the image.
export const PEAK_REGIONS: Record<string, { xMin: number; xMax: number; yMin: number; yMax: number }> = {
  'snowshed':        { xMin: 2,  xMax: 11, yMin: 38, yMax: 87 },
  'sunrise':         { xMin: 10, xMax: 18, yMin: 30, yMax: 78 },
  'ramshead':        { xMin: 17, xMax: 29, yMin: 20, yMax: 70 },
  'snowdon':         { xMin: 28, xMax: 42, yMin: 10, yMax: 65 },
  'skye-peak':       { xMin: 40, xMax: 56, yMin: 8,  yMax: 58 },
  'killington-peak': { xMin: 50, xMax: 67, yMin: 3,  yMax: 52 },
  'bear-mountain':   { xMin: 65, xMax: 84, yMin: 14, yMax: 62 },
};

// Explicit per-trail coordinates on the actual trail map image.
// Each coordinate is a percentage of image width (x) and height (y).
// Trails are placed at their approximate real location on the map.
export const TRAIL_COORDINATES: Record<string, { x: number; y: number }> = {
  // === SNOWSHED AREA (far left, low elevation) ===
  'snowshed-slope':      { x: 6,  y: 55 },
  'yodeler':             { x: 4,  y: 60 },
  'idler':               { x: 8,  y: 58 },
  'snow-play':           { x: 5,  y: 68 },
  'snowshed-crossover':  { x: 9,  y: 65 },

  // === SUNRISE AREA (left, slightly higher) ===
  'sun-dog':             { x: 12, y: 45 },
  'rendezvous':          { x: 14, y: 50 },
  'bear-cub':            { x: 16, y: 55 },
  'bear-view':           { x: 13, y: 58 },
  'sunrise-connector':   { x: 15, y: 64 },

  // === RAMSHEAD (center-left) ===
  'easy-street':         { x: 20, y: 50 },
  'swirl':               { x: 22, y: 45 },
  'treezy':              { x: 24, y: 42 },
  'squeeze-play':        { x: 19, y: 55 },
  'ramshead-run':        { x: 21, y: 58 },
  'ramshead-liftline':   { x: 23, y: 35 },
  'header':              { x: 26, y: 40 },
  'vagabond':            { x: 25, y: 48 },
  'caper':               { x: 27, y: 52 },
  'timberline':          { x: 22, y: 62 },
  'start-park':          { x: 20, y: 63 },

  // === SNOWDON (center, large area) ===
  'great-northern':      { x: 32, y: 28 },
  'bunny-buster':        { x: 33, y: 45 },
  'chute':               { x: 35, y: 20 },
  'conclusion':          { x: 37, y: 18 },
  'upper-fis':           { x: 33, y: 32 },
  'mountain-run':        { x: 36, y: 52 },
  'mountain-training':   { x: 38, y: 56 },
  'snowdon-liftline':    { x: 34, y: 25 },
  'upper-snowdon':       { x: 36, y: 22 },
  'lower-snowdon':       { x: 38, y: 35 },
  'bittersweet':         { x: 40, y: 38 },
  'sass':                { x: 39, y: 42 },
  'northstar':           { x: 37, y: 15 },
  'royal-flush':         { x: 35, y: 17 },
  'upper-northbrook':    { x: 41, y: 30 },
  'lower-northbrook':    { x: 40, y: 48 },
  'snowdon-glades':      { x: 33, y: 38 },

  // === SKYE PEAK (center-right, major trail area) ===
  'skyelark':            { x: 44, y: 25 },
  'upper-skyelark':      { x: 43, y: 18 },
  'skyeburst':           { x: 46, y: 28 },
  'upper-skyeburst':     { x: 45, y: 20 },
  'skye-hawk':           { x: 48, y: 22 },
  'skyebits':            { x: 42, y: 32 },
  'cruise-control':      { x: 50, y: 30 },
  'mouse-trap':          { x: 47, y: 35 },
  'somewhere':           { x: 49, y: 38 },
  'breakaway':           { x: 44, y: 40 },
  'touch-down':          { x: 51, y: 42 },
  'patsys':              { x: 46, y: 44 },
  'twister':             { x: 48, y: 46 },
  'catwalk':             { x: 53, y: 36 },
  'upper-catwalk':       { x: 52, y: 26 },
  'great-eastern':       { x: 54, y: 48 },
  'home-stretch':        { x: 55, y: 52 },
  'lower-home-stretch':  { x: 54, y: 56 },
  'juggernaut':          { x: 41, y: 50 },
  'vertigo':             { x: 43, y: 12 },
  'upper-vertigo':       { x: 42, y: 10 },
  'ovation':             { x: 45, y: 10 },
  'needles-eye':         { x: 47, y: 16 },
  'panic-button':        { x: 47, y: 18 },
  'dream-maker':         { x: 46, y: 14 },
  'dream-maker-headwall':{ x: 43, y: 15 },
  'highline':            { x: 48, y: 20 },
  'pipe-dream':          { x: 53, y: 32 },
  'valley-plunge':       { x: 52, y: 40 },
  'field-goal':          { x: 50, y: 50 },
  'roundabout':          { x: 46, y: 52 },
  'roundabout-glade':    { x: 44, y: 48 },
  'tin-man':             { x: 48, y: 54 },
  'skye-peak-liftline':  { x: 43, y: 22 },
  'great-bear':          { x: 55, y: 44 },
  'upper-great-bear':    { x: 54, y: 34 },
  'woodward-peace-park': { x: 51, y: 55 },

  // === KILLINGTON PEAK (summit, upper-center-right) ===
  'superstar':           { x: 56, y: 18 },
  'cascade':             { x: 58, y: 10 },
  'downdraft':           { x: 60, y: 8 },
  'double-dipper':       { x: 57, y: 12 },
  'big-dipper-glade':    { x: 59, y: 14 },
  'flume':               { x: 55, y: 15 },
  'escapade':            { x: 61, y: 16 },
  'east-fall':           { x: 63, y: 20 },
  'upper-east-fall':     { x: 62, y: 14 },
  'rime':                { x: 54, y: 12 },
  'reason':              { x: 56, y: 8 },
  'julio':               { x: 53, y: 10 },
  'high-road':           { x: 58, y: 25 },
  'north-way':           { x: 60, y: 28 },
  'great-eastern-kp':    { x: 60, y: 38 },
  'fis':                 { x: 55, y: 22 },
  'lower-fis':           { x: 56, y: 32 },
  'solitude':            { x: 59, y: 35 },
  'k1-gondola-run':      { x: 61, y: 30 },
  'anarchy':             { x: 64, y: 12 },
  'upper-canyon':        { x: 62, y: 22 },
  'lower-canyon':        { x: 63, y: 30 },
  'old-superstar':       { x: 54, y: 25 },
  'killington-liftline': { x: 57, y: 6 },
  'superstar-glade':     { x: 55, y: 20 },
  'header-kp':           { x: 62, y: 35 },
  'mouse-run':           { x: 61, y: 40 },
  'low-road':            { x: 62, y: 45 },
  'the-mall':            { x: 60, y: 44 },

  // === BEAR MOUNTAIN (right side, separate peak) ===
  'outer-limits':        { x: 72, y: 22 },
  'devils-fiddle':       { x: 74, y: 20 },
  'wildfire':            { x: 70, y: 25 },
  'bear-claw':           { x: 76, y: 30 },
  'growler':             { x: 71, y: 28 },
  'centerpiece':         { x: 73, y: 26 },
  'spacewalk':           { x: 75, y: 24 },
  'bear-trax':           { x: 78, y: 35 },
  'falls-brook':         { x: 77, y: 40 },
  'skye-burst-bear':     { x: 68, y: 32 },
  'bear-mountain-liftline': { x: 73, y: 18 },
  'the-stash':           { x: 69, y: 35 },
  'lil-stash':           { x: 70, y: 40 },
  'lower-wildfire':      { x: 71, y: 38 },
  'bear-run':            { x: 76, y: 45 },
};
