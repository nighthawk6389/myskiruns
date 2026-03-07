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
 * - Snowdon: center-left
 * - Skye Peak: center
 * - Killington Peak: the summit, center (the highest point ~x:42 y:4)
 * - Bear Mountain: separate peak, right side (~x:72 y:16)
 *
 * Key reference points on the image:
 * - Killington Peak summit: ~(42, 4)
 * - Bear Mountain summit: ~(72, 16)
 * - Snowshed base lodge: ~(5, 83)
 * - Main mountain mass ends: ~x:56
 * - Forest gap: ~x:56-64
 * - Bear Mountain starts: ~x:64
 */

// Define accurate peak regions matching the actual trail map image layout.
// Each region describes the bounding area for that peak's trails on the image.
// Note: Snowdon, Skye Peak, and Killington Peak overlap because they share
// the same mountain face. The regions reflect the actual trail positions.
export const PEAK_REGIONS: Record<string, { xMin: number; xMax: number; yMin: number; yMax: number }> = {
  'snowshed':        { xMin: 2,  xMax: 11, yMin: 38, yMax: 87 },
  'sunrise':         { xMin: 10, xMax: 18, yMin: 30, yMax: 78 },
  'ramshead':        { xMin: 17, xMax: 29, yMin: 20, yMax: 70 },
  'snowdon':         { xMin: 26, xMax: 40, yMin: 14, yMax: 58 },
  'skye-peak':       { xMin: 33, xMax: 50, yMin: 8,  yMax: 58 },
  'killington-peak': { xMin: 39, xMax: 54, yMin: 3,  yMax: 50 },
  'bear-mountain':   { xMin: 64, xMax: 82, yMin: 14, yMax: 62 },
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
  // Summit area ~(32, 12). Trails run down to ~(36, 56).
  'northstar':           { x: 33, y: 16 },
  'royal-flush':         { x: 31, y: 18 },
  'chute':               { x: 33, y: 20 },
  'conclusion':          { x: 35, y: 18 },
  'snowdon-liftline':    { x: 32, y: 24 },
  'upper-snowdon':       { x: 34, y: 22 },
  'great-northern':      { x: 30, y: 28 },
  'upper-fis':           { x: 31, y: 32 },
  'upper-northbrook':    { x: 36, y: 28 },
  'lower-snowdon':       { x: 36, y: 35 },
  'snowdon-glades':      { x: 29, y: 36 },
  'bittersweet':         { x: 38, y: 38 },
  'sass':                { x: 37, y: 42 },
  'bunny-buster':        { x: 31, y: 44 },
  'lower-northbrook':    { x: 38, y: 48 },
  'mountain-run':        { x: 34, y: 50 },
  'mountain-training':   { x: 36, y: 54 },

  // === SKYE PEAK (center, major trail area) ===
  // Summit area ~(38, 10). Trails run down to ~(48, 56).
  // Expert trails near the top, greens at the bottom.
  'upper-vertigo':       { x: 35, y: 10 },
  'vertigo':             { x: 36, y: 14 },
  'ovation':             { x: 38, y: 12 },
  'dream-maker-headwall':{ x: 34, y: 13 },
  'dream-maker':         { x: 37, y: 16 },
  'needles-eye':         { x: 40, y: 16 },
  'upper-skyelark':      { x: 37, y: 19 },
  'panic-button':        { x: 39, y: 18 },
  'skye-peak-liftline':  { x: 36, y: 22 },
  'highline':            { x: 41, y: 20 },
  'upper-skyeburst':     { x: 39, y: 22 },
  'skyelark':            { x: 38, y: 26 },
  'skye-hawk':           { x: 41, y: 24 },
  'upper-catwalk':       { x: 44, y: 26 },
  'skyeburst':           { x: 40, y: 28 },
  'skyebits':            { x: 36, y: 30 },
  'cruise-control':      { x: 43, y: 30 },
  'pipe-dream':          { x: 45, y: 32 },
  'mouse-trap':          { x: 41, y: 34 },
  'upper-great-bear':    { x: 47, y: 32 },
  'catwalk':             { x: 46, y: 36 },
  'breakaway':           { x: 38, y: 36 },
  'somewhere':           { x: 42, y: 38 },
  'valley-plunge':       { x: 44, y: 40 },
  'touch-down':          { x: 46, y: 42 },
  'patsys':              { x: 40, y: 42 },
  'great-bear':          { x: 48, y: 44 },
  'twister':             { x: 42, y: 44 },
  'roundabout-glade':    { x: 37, y: 46 },
  'roundabout':          { x: 39, y: 50 },
  'great-eastern':       { x: 47, y: 48 },
  'juggernaut':          { x: 35, y: 48 },
  'field-goal':          { x: 43, y: 50 },
  'home-stretch':        { x: 48, y: 52 },
  'tin-man':             { x: 41, y: 52 },
  'woodward-peace-park': { x: 44, y: 54 },
  'lower-home-stretch':  { x: 47, y: 56 },

  // === KILLINGTON PEAK (summit, center of map) ===
  // The summit is at ~(42, 4). Trails radiate down and to the right.
  // Expert trails cluster near the summit; blues/greens extend lower.
  'killington-liftline': { x: 43, y: 5 },
  'reason':              { x: 44, y: 8 },
  'cascade':             { x: 46, y: 8 },
  'downdraft':           { x: 48, y: 7 },
  'julio':               { x: 41, y: 10 },
  'rime':                { x: 43, y: 11 },
  'double-dipper':       { x: 45, y: 11 },
  'flume':               { x: 42, y: 14 },
  'big-dipper-glade':    { x: 47, y: 13 },
  'superstar':           { x: 44, y: 17 },
  'upper-east-fall':     { x: 50, y: 14 },
  'escapade':            { x: 49, y: 16 },
  'anarchy':             { x: 52, y: 12 },
  'superstar-glade':     { x: 43, y: 20 },
  'east-fall':           { x: 51, y: 20 },
  'fis':                 { x: 44, y: 23 },
  'old-superstar':       { x: 42, y: 26 },
  'upper-canyon':        { x: 50, y: 22 },
  'high-road':           { x: 47, y: 25 },
  'north-way':           { x: 49, y: 28 },
  'k1-gondola-run':      { x: 50, y: 30 },
  'lower-canyon':        { x: 51, y: 28 },
  'lower-fis':           { x: 45, y: 30 },
  'solitude':            { x: 48, y: 34 },
  'header-kp':           { x: 50, y: 36 },
  'great-eastern-kp':    { x: 49, y: 40 },
  'mouse-run':           { x: 50, y: 42 },
  'the-mall':            { x: 49, y: 46 },
  'low-road':            { x: 51, y: 44 },

  // === BEAR MOUNTAIN (right side, separate peak) ===
  // Summit ~(72, 16). Separate peak across a forested saddle.
  'bear-mountain-liftline': { x: 73, y: 18 },
  'outer-limits':        { x: 72, y: 22 },
  'devils-fiddle':       { x: 74, y: 20 },
  'spacewalk':           { x: 75, y: 24 },
  'wildfire':            { x: 70, y: 25 },
  'centerpiece':         { x: 73, y: 26 },
  'growler':             { x: 71, y: 28 },
  'bear-claw':           { x: 76, y: 30 },
  'skye-burst-bear':     { x: 68, y: 32 },
  'the-stash':           { x: 69, y: 35 },
  'bear-trax':           { x: 78, y: 35 },
  'lower-wildfire':      { x: 71, y: 38 },
  'lil-stash':           { x: 70, y: 40 },
  'falls-brook':         { x: 77, y: 40 },
  'bear-run':            { x: 76, y: 45 },
};
