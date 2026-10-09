# Jay Peak's trail data pipeline

Jay Peak's 2025-26 map is a painting that draws no trail lines at all: each
trail is a painted cut through the trees. But every trail name is real PDF
text with its difficulty symbol drawn just before it, so the trail list comes
straight from the PDF (no tile readers), and every overlay is a trace along
the painted cut, made by trace readers (Claude sub-agents) and checked by
Claude on zoomed crops one trail at a time; where a label sits in trees with
no cut, the trail is a marker at its label. The traces are the record (a
re-run would not trace the same points), so they are kept in `readings/`, and
`regen.sh` rebuilds every Jay Peak file from the PDF, the traces and the
decisions taken on crops, byte for byte.

## Source

- **PDF:** <https://jaypeakresort.com/sites/default/files/2026-02/JPR_TrailMap_Winter_2025%2B2026_ToPRINT.pdf>
  (`JPR_TrailMap_Winter_2025+2026_ToPRINT.pdf`), the 2025-26 winter map:
  18,887,714 bytes, SHA-256
  `005f383ed84a05b05d4e0b381a73b0ad83360c5de071fb9e53b7062076b2f779`, fetched
  2026-09-30 and again 2026-10-07 (unchanged). Plain curl works (`regen.sh`
  sends a browser user agent and `Accept: application/pdf`); the resort's
  trail-maps page (`/skiing-riding/trail-maps`) answered curl with its 404
  page that day, so the URL is the way in.
- One page, 1080 x 666 pt, made in InDesign: a James Niehues painting (two
  stacked CMYK rasters, about 4448x3007) under the names, symbols, lifts,
  boundaries and the Side View inset as vectors and text.
- **Map image:** the page rendered at 4 px/pt inside 9,66,1076,657 pt (the
  painting, without the header band and footer), 4268x2364, saved as JPEG
  quality 88 (`IMAGES=1`). No CDN image is used.

## Rebuild

```bash
tools/trailmap/resorts/jay-peak/regen.sh            # src/data/resorts/jay-peak/ (about 20 s)
IMAGES=1 tools/trailmap/resorts/jay-peak/regen.sh   # also public/maps/jay-peak.jpg
```

Working files go to `$JAY_PEAK_WORK` (default `work/jay-peak`, git-ignored);
the PDF is downloaded there if missing (or put it there by hand). The script
stops if the PDF's SHA-256 is not the one above (`FORCE=1` goes on anyway).
Needs `pip install pymupdf pillow` and the repo's `npm ci`. Afterwards
`work/jay-peak` holds what `tools/trailmap/runs/jay-peak-trace.json` points the
trace workflow at (`jay_source.png`, `tiles/`, `all_labels.txt`).

## Pipeline (regen.sh)

1. `curl` → `$W/jay.pdf`; SHA-256 check.
2. The page at 4x inside the clip → `$W/jay_source.png` (and, with `IMAGES=1`,
   `public/maps/jay-peak.jpg`); `linePolylines.json` with no pieces and a
   `_source` note saying why; `render_tiles.py` over the whole image →
   `$W/tiles/` (42 tiles at 1.7x: what the tracers looked at; its `index.json`
   gives `aggregate_readings.py` the image size).
3. `labels.py` → `$W/jay_label_spans.json` (137 name spans with their symbols);
   `reading.py` → `$W/reading_pdf.json` (114 labels of 88 names, as one
   "certain" reading); `seed_roster.py --areas 'jay-peak=Jay Peak=3862'` →
   `trails.ts` and `$W/labels.json`; `all_labels.py` → `$W/all_labels.txt` (the
   tracers' label list); `aggregate_readings.py --labels` →
   `trailProposals.json` (a marker for each of the 11 named glades, nothing
   else: there are no pieces); then `decisions.py trails`: the five trails
   with no cut flagged as glades, and `header.txt` as the header.
4. `decisions.py traces` copies `readings/` in the order the traces came in
   (rejected traces emptied, a no-op on these files) → `$W/traces/`;
   `traces_to_reviews.py --replace-claude --labels --image` → `trailReviews.json`
   (77 reviews by Claude: 65 traced lines, 12 markers from empty traces);
   `npm run trails:apply` → `trailPaths.json` (65 lines, 23 markers).

`aggregate_readings.py` runs before the glade flags, as it did on 2026-09-30:
run after them it would add proposals for the five no-cut trails, which get
their markers from their reviews instead.

## Files

| file | role |
|---|---|
| `regen.sh` | the whole rebuild |
| `labels.py` | PDF text spans + the symbol fill beside each → label records (was `jay_labels.py`) |
| `reading.py` | label records → one synthetic reading for `seed_roster.py`: non-trail spans dropped, a typo fixed, duplicates merged, glades by name, the inset-only Sis Boom Bah added (was `jay_reading.py`) |
| `all_labels.py` | the label list the trace readers were given (was inline code) |
| `decisions.py` | settled on crops: the five no-cut trails flagged as glades, the two rejected traces, the order the trace files are read in; applies them |
| `header.txt` | the comment at the top of `trails.ts` (written by hand during the trace pass) |
| `readings/trace/trace_0.json` … `trace_2.json` | trace groups 0-2 of `tools/trailmap/runs/jay-peak-trace.json` (first run) |
| `readings/trace/trace_markers.json` | Claude's: the 5 terrain parks and Sis Boom Bah as empty traces (markers at their labels) |
| `readings/trace_b/trace_0.json` | group 6 (run b re-ran groups 6-8; only 6 finished) |
| `readings/trace_c/trace_0.json`, `trace_1.json` | groups 3 and 4 (run c) |
| `readings/trace_d/trace_0.json`, `trace_1.json` | groups 5 and 7 (run d); Deliverance's (in `trace_0`) and Tuckerman's Chute's (in `trace_1`) traces were emptied after the crop check, their notes starting "NO CUT (checked on a crop: …). Tracer: " and keeping the tracer's note |
| `readings/trace_e/trace_0.json` | group 8 (run e) |
| `checks/audit_sheets.py` | each trail's overlay on its crop, the others thin: how every trace was checked |
| `checks/audit_log.json` | the verdict for each of the 88 trails, from its crop |
| `checks/sheet.py` | every printed copy of given labels, rendered from the PDF, with the symbol read |
| `checks/markers.py` | every marker against its printed labels (all at 0 px) |

Generated (never hand-edit): `src/data/resorts/jay-peak/{linePolylines,trailProposals,trailPaths}.json`,
`trails.ts` and Claude's entries in `trailReviews.json`. Every review there
today is Claude's; a person's review added later (no `"by": "claude"`) stays
through a rebuild.

## Nuances of this map

- No trail lines: trails are painted open cuts (white or light-blue snow
  between painted trees); slow zones are green dot-grid shading, terrain parks
  orange pills and orange-dotted areas. Red lines with red text are lifts;
  pink/magenta dashes are uphill travel routes (they often run up a trail's
  cut: a tracer must not follow one past where the trail goes); yellow dashes
  the boundary, orange dashes the area of gravest concern; the red-pink bands
  at the lower right are cross-country and snowshoe trails.
- Names are PDF text (`DIN2014-Bold`, 5.2-6.1 pt), black with a white halo,
  or white on a park's orange pill (that is how a park is told). Some are
  drawn twice in one place (halo and fill): kept once. Lift names are red
  text. Left out: the legend, the Mountain Stats panel, the Side View inset
  and the logos, and the label-font spans that are not trails (the base lodge,
  the hotel, first aid, the moving carpet, the kids', adventure and
  recreation centres, Clips & Reels).
- The symbol is drawn just before the name (sometimes after): green circle,
  blue square, black diamond; no double diamonds, no glade icon. A name
  printed several times takes the majority of its symbols and a tie the
  harder (Ullr's Dream blue with one green label up top; Northway blue with
  one black; Jet, U.N. and Green Mountain Boys one blue and one black: black).
  The 5 parks print no symbol and default to blue.
- "Lower Lift Linee" on the map is Lower Lift Line. Sis Boom Bah is printed
  only in the Side View inset: a marker at its inset label.
- A trail printed more than once runs through all of its labels (the tracers
  were told so): Ullr's Dream is printed 7 times, Northway 5, JFK and Angel's
  Wiggle 3, a dozen others twice.
- Markers (23): the 11 named glades (Glade, Woods), the 5 parks, Sis Boom Bah,
  and 6 trails whose label sits in painted trees with no cut: Timbuktu,
  Valhalla, André's Paradise and Staircase (the tracers' own NO CUT calls),
  Deliverance (its diamond sits in a lightly treed strip beside the Lift Line
  cut; the tracer's low-confidence guess ran parallel to the lift about 30 px
  away and would have overlapped Lift Line) and Tuckerman's Chute (no chute
  is painted on the treed summit face). The first five are flagged as glades;
  Tuckerman's Chute is not.
- 88 trails: 14 green, 39 blue, 35 black; 65 lines and 23 markers.

## Checks done

- Every trace on a zoomed crop as its group came in (`checks/audit_sheets.py
  --only <the group's trails>`), the verdicts in `checks/audit_log.json`: 65
  kept as lines, Deliverance and Tuckerman's Chute rejected (markers).
- Every marker on its printed label (`checks/markers.py`: 0 px, from the PDF
  text).
- The symbols come from the PDF's own fills next to the text; the mixed ones
  were looked at on label crops (`checks/sheet.py`).
- No human review (the owner's call). Hover check
  (`tools/trailmap/hover_check.cjs --resort jay-peak`): 218/218 (65 lines x 3
  points + 23 markers), on 2026-09-30 and since.
- This rebuild (2026-10-07): from an empty work folder, every committed file
  and the map image came out byte for byte, and so did the intermediate files
  of 2026-09-30 (the spans, the reading, `labels.json`, `all_labels.txt`, the
  tiles and their index, `review_data.json`, `recheck.json`, the source PNG).

## A new season's map

1. Put the new PDF's URL and SHA-256 in `regen.sh` and check that the names
   are still text in one font and size range with their symbols beside them
   (`labels.py` prints what it skipped and each name with its symbols; look
   at the doubtful ones with `checks/sheet.py`). Update `reading.py`'s
   non-trail names, typos and inset-only names.
2. Run `regen.sh`'s steps 1-3 (`FORCE=1` for the new file); the traces in
   `readings/` no longer fit (their points are on the old painting). Make the trace groups from the new
   label list (as in `tools/trailmap/runs/jay-peak-trace.json`: every trail
   that is not a named glade or a park, ~8 per group) and run the
   `trailmap-trace` workflow (the playbook's Part 4, "Auto-accept the easy ones, trace the hard ones"), each re-run into its own
   output folder. Put the parks' and inset names' markers in a
   `trace_markers.json`.
3. Check every trace on a crop (`checks/audit_sheets.py`), empty the ones
   with no cut (`REJECTED`), flag the no-cut trails (`NO_CUT`), set
   `TRACE_ORDER` to the new files and rewrite `header.txt`.
4. Hover check.

What carries over: a person's reviews (none so far) for trails whose cut and
label are where they were; nothing else.
