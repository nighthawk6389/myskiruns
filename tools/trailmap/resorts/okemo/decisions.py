"""Okemo's hand-made decisions: what Claude settled itself while building the 2025-26 map, on top of the
readers' readings (readings/). steps.py applies each group at its place in regen.sh.

These were one-off edits in the scratch session that built Okemo (2026-09-30); they are recorded here with
the exact text they wrote, so a rebuild reproduces the committed files. Change a decision here and re-run
regen.sh; never edit the generated files. The Tomahawk Park pieces are a reading of their own,
readings/result_overrides.json (written by Claude, not by a reader). A person's reviews in
src/data/resorts/okemo/trailReviews.json outrank all of this: the review decisions below are only added for
trails no person has decided.
"""

# --- trails.ts, as seed_roster.py writes it from the six tile readers, changed by hand (08:03 UTC) ----------
# The map prints TOMAHAWK twice: a blue-square trail down to Express Lane (pieces 117, 118) and an orange
# terrain-park section below it (254, 255), here a trail of its own (crop c_239_tomahawk.jpg). Tree Tap is
# printed as an orange park name and pill with no line (spot_other.png). (old, new) text replacements, in order.
TRAILS_TS = [
    ("// glade icon. x/y/baseY/width are unused layout fields.\n",
     "// glade icon. x/y/baseY/width are unused layout fields.\n"
     "// By hand: the map prints TOMAHAWK twice, a blue-square trail down to Express\n"
     "// Lane and an orange terrain-park section below it (Tomahawk Park); Tree Tap\n"
     "// is printed with the orange terrain-park pill and no line. Parks print no\n"
     "// difficulty symbol, so they get seed_roster's default (blue).\n"),
    ("  { id: 'tomahawk', name: 'Tomahawk', difficulty: 'blue', peak: 'okemo-mountain' },\n",
     "  { id: 'tomahawk', name: 'Tomahawk', difficulty: 'blue', peak: 'okemo-mountain' },\n"
     "  { id: 'tomahawk-park', name: 'Tomahawk Park', difficulty: 'blue', peak: 'okemo-mountain', isTerrainPark: true },\n"),
    ("{ id: 'tree-tap', name: 'Tree Tap', difficulty: 'blue', peak: 'jackson-gore' },",
     "{ id: 'tree-tap', name: 'Tree Tap', difficulty: 'blue', peak: 'jackson-gore', isTerrainPark: true },"),
]

# --- linePolylines.json `_unnamed`: pieces the map prints no name for, checked on a crop (08:03) -------------
# aggregate_readings.py gives them no trail and hides them on the review page.
UNNAMED = {
    '239': 'short green spur from Sweet Solitude (137) west to the tops of Upper Sapphire and Tomahawk; no label '
           '(checked on a crop)',
}

# --- pieces cut where a second trail starts (split_pieces.py, 08:48) ---------------------------------------
# The Turkey Shoot trace reader found that its line uses only the lower part of 210, from where 238 joins it
# down to Countdown; 210's upper curve from Buckhorn is Challenger's lead-in (crop c_turkey.jpg). The upper
# part keeps id 210 (CHALLENGER), the lower one becomes 256 (TURKEY SHOOT), named in result_splits.json.
SPLITS = ['210@1599,552=CHALLENGER/TURKEY SHOOT']

# --- trace fixes (08:48): a trace that used part of a piece now uses the cut part ----------------------------
# {trail: (piece that was cut, note put before the reader's note; {new} = the cut part's id)}. Reviews store
# whole pieces (traces_to_reviews.py), so the trace lists the split's new piece and no `partial`.
TRACE_FIXES = {
    'turkey-shoot': (210, 'Piece 210 split at the Challenger/Turkey Shoot junction (~1599,552): the lower part '
                          '({new}) is Turkey Shoot, the upper curve from Buckhorn stays 210 (Challenger). '),
}

# --- Claude's reviews before the person's review (08:49), on top of the traces ------------------------------
# Printed with no line: the trace readers found no distinct run, so a marker at the label (labels.json) instead
# of an invented line. {trail: (label x, label y in source px, what it is)}.
MARKERS = {
    'galaxy-bowl': (1462, 2052, 'a beginner area by carpets 2 and 3 at the Clock Tower base'),
    'bright-star-basin': (4004, 2134, 'a learning area by carpets 6 and 7 at the Jackson Gore base'),
    'tree-tap': (3956, 2088, 'a terrain park printed as an orange name and pill'),
}
MARKER_NOTE = 'Printed with no line: {what}; a marker at the label. The trace reader found no distinct run.'
# Challenger gets the upper part of the cut piece 210 (its proposal was 61, 62 and the whole of 210).
LINES = {
    'challenger': ([61, 62, 210], "Piece 210 was split where Turkey Shoot (238) meets it: its upper curve from "
                                  "Buckhorn is Challenger's lead-in; the lower part is Turkey Shoot."),
}
# Why the review page flags each trail for a recheck ({prior} = the reason traces_to_reviews.py gave, cut to 120
# characters). The markers get MARKER_RECHECK.
MARKER_RECHECK = 'No line printed ({what}): proposed as a marker at the label. Save "No line" to keep it, or draw the run.'
RECHECK = {
    'challenger': 'Piece 210 was split at the Turkey Shoot junction: the upper curve from Buckhorn is now the top of '
                  'Challenger, the lower part goes to Turkey Shoot. Confirm, or move the upper curve.',
    'turkey-shoot': 'Traced: 238 (along the TURKEY SHOOT label) plus the lower part of 210 down to Countdown; the upper '
                    'curve from Buckhorn went to Challenger. {prior}',
    'tomahawk-park': 'Split by Claude: the map prints TOMAHAWK twice; the orange terrain-park section below Express '
                     'Lane (254, 255) is its own trail here. To merge it into Tomahawk instead, mark this one Not on '
                     'this map and add 254/255 to Tomahawk.',
    'tomahawk': 'The blue-square Tomahawk down to Express Lane (117, 118); the orange park section below it is '
                'Tomahawk Park.',
}
# trailReviews.json's own note
REVIEWS_NOTE = 'Human review decisions (tools/trailmap/review). by: claude = proposed by Claude, flagged for recheck.'
