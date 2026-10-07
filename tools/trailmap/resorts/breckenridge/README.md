# Breckenridge's trail data pipeline

Breckenridge's 2025-26 map is one vector PDF page: every trail line is a
0.99 pt stroke in its difficulty colour, and every name is real (Unicode) text
in its trail's colour with its symbol beside it, so no readers were needed.
Each line piece was matched to the name printed along it, at its end or in a
gap of it, and every unclear piece was settled on zoomed crops. The PDF's
painting is only 1482x962 px, so the map image is the PDF's vector layer matted
over the sharper copy on Vail Resorts' image CDN (scene7).

The scripts here were the scratch scripts of the 2026-10-01 session that built
the committed data (commit `8e4c999`). They are copied with relative paths and
otherwise unchanged; each docstring names its scratch original.

## Source

- **PDF:** `https://www.breckenridge.com/-/aemasset/sitecore/breckenridge/maps/winter-2025-2026/20250926_BR_winter-trail_map_001.pdf`,
  linked from the trail-map page
  `https://www.breckenridge.com/the-mountain/about-the-mountain/trail-map.aspx`.
  It is the 2025-26 edition (dated 2025-09-26 in its name), 1,316,376 bytes,
  SHA-256 `cb6793d2aff7f98bae1049eb6d35ec4d1da898fd8012432cbf9cb1c44cdbe31c`.
  It is one page, 1458 x 1039.5 pt, with no metadata.
  breckenridge.com returns an error page to curl, so `regen.sh` fetches the
  PDF from inside the page in headless Chromium (`tools/trailmap/fetch_pdf.cjs`).
  Behind this sandbox's agent proxy, Chromium also needs the proxy CA's pin
  (`PIN`, which `fetch_pdf.cjs` works out). skimap.org's map 39900
  (`https://skimap.org/skimaps/view/39900`, plain curl) is the same file byte
  for byte. The session first downloaded it there, then confirmed it against
  the resort's own copy.
- **Painting (CDN image):** scene7 `20250926_BR_winter-trail_map_001`. It is
  3037x2166 px (`?req=imageprops`), requested as
  `https://scene7.vailresorts.com/is/image/vailresorts/20250926_BR_winter-trail_map_001?wid=3037&hei=2166&fit=constrain,1&qlt=95`.
  The JPEG is 3,214,831 bytes, SHA-256
  `13bf2b96ce88ffee81b16f99e44a8a72b74757cf75b4d16854e8a31fa999fa5e`, and plain
  curl works. It is the whole flattened map (painting, lines and labels) at
  2.08 px/pt.

`regen.sh` checks both SHA-256 sums. If either file differs (a new edition, or
the CDN re-encoding), it stops and says how to go on (`FORCE=1`). A copy placed
in the work folder by hand is used as it is, after the same check.

## Rebuild

```bash
tools/trailmap/resorts/breckenridge/regen.sh             # rebuild src/data/resorts/breckenridge/ (about 10 s)
IMAGES=1 tools/trailmap/resorts/breckenridge/regen.sh    # also public/maps/breckenridge.jpg (about 20 s)
FORCE=1 tools/trailmap/resorts/breckenridge/regen.sh     # go on although a source's SHA-256 differs
tools/trailmap/resorts/breckenridge/checks/crops.sh      # re-render every crop the decisions cite, and the audit
```

`regen.sh` downloads the sources into `$BRECKENRIDGE_WORK` (default
`work/breckenridge`, git-ignored) and writes every Breckenridge data file. From
an empty work folder the first run takes about 30 s, including the download.
With nothing changed it reproduces the committed files byte for byte, with or
without a filled work folder. It keeps any person's reviews in
`trailReviews.json`, and Claude's unchanged reviews keep their timestamps
(`traces_to_reviews.py --replace-claude`). Needs pymupdf, pillow and numpy,
plus Playwright's Chromium for the download (`PLAYWRIGHT_PATH`, default
`$(npm root -g)/playwright`).

## Pipeline

All coordinates are PDF points unless noted. The map is the clip
0,80 to 1458,925 pt at 3 px/pt: 4374x2535 px. A piece's point (x%, y%) is at
(14.58 x, 80 + 8.45 y) pt.

1. `fetch_pdf.cjs` downloads `breckenridge.pdf` and `curl` downloads
   `scene7.jpg`, both checked by SHA-256.
2. `tools/trailmap/pdf_labels.py` (no options) writes `printed.json`: every
   text object with its characters' centres.
3. `symbols.py` writes `symbols.json`: the fills that are a green circle, blue
   square, black diamond, double diamond or EX.
4. `names.py` takes `printed.json` and `symbols.json` and writes `names.json`:
   200 labels for 197 names, each with its symbol (`names.log` lists what has
   none).
5. `tools/trailmap/extract_pdf_vectors.py` (the flags are in `regen.sh`)
   writes `pieces.json`: 351 pieces (205 black, 89 blue, 57 green).
6. `tools/trailmap/split_pieces.py` cuts piece 250 at (1898.7, 2028.3) px:
   Lower 4 O'Clock above, Gondola Ski Back below (new piece 351). A second
   `extract_pdf_vectors.py` pass (`--min-length 2.5 --max-length 4 --append`)
   then adds the 8 lead-in stubs the first pass drops as under 4 pt, as pieces
   352 to 359, so every earlier id stays put. An inline step sets `_source`
   and `_unnamed` (from `decisions.py`). The result is
   `src/data/resorts/breckenridge/linePolylines.json`, 360 pieces.
7. `matte.py` writes `map.png` (and with `IMAGES=1` also
   `public/maps/breckenridge.jpg`, quality 82, progressive).
8. `match.py` writes `assign.json`: 316 pieces get names, 16 of them several,
   and 44 get none (`match.log`).
9. `reading.py` combines `assign.json` and `decisions.py` into
   `tiles/result_breck.json` (labels with symbols, 343 named pieces) and
   `gaps.json` (92 stretches on 89 trails, 40 markers).
10. `tools/trailmap/seed_roster.py`, then `header.txt`, write `trails.ts`
    (197 trails) and `labels.json`.
11. `tools/trailmap/render_tiles.py` writes `tiles/index.json`, which supplies
    the image size to `aggregate_readings.py`.
12. `tools/trailmap/aggregate_readings.py` writes `trailProposals.json` (157
    trails on pieces) and `review_data.json`.
13. `traces.py` writes `trace_gaps.json`: 89 stretches plus pieces, and 40
    markers.
14. `tools/trailmap/traces_to_reviews.py --replace-claude` writes
    `trailReviews.json` (129 of Claude's reviews).
15. `npm run trails:apply -- --resort breckenridge` writes `trailPaths.json`:
    89 verified, 68 proposed, 40 label markers.

## Files

| file | role |
|---|---|
| `regen.sh` | the whole rebuild: sources (with their SHA-256), extraction, naming, trail list, proposals, reviews, overlays |
| `common.py` | where the repo, the work folder, the PDF and the pieces are |
| `symbols.py` | difficulty symbols from the PDF's fills (scratch: `br_syms.py`) |
| `names.py` | the trail names from the PDF text, deduplicated, two-line names joined, each symbol attached to its name (scratch: `br_names.py`) |
| `match.py` | each name → the pieces it is printed along, ends at or runs on from; names spread along continuations (scratch: `br_build.py`) |
| `decisions.py` | hand-made: pieces settled on crops (`CHECKED`, piece id → name as printed) and lines with no printed name (`UNNAMED`), each with the crop that settled it (scratch: `br_checked.py`) |
| `reading.py` | hand-made rules too: bowl and chute names that take their bowl's symbol (`ZONE`), the four parks (`PARKS`); writes the reading, the label-gap stretches and the markers (scratch: `br_reading.py`) |
| `traces.py` | stretches and markers → the traces `traces_to_reviews.py` takes (scratch: `br_traces.py`) |
| `matte.py` | the map image (an inline script of the session, 2026-10-01T15:08:14) |
| `header.txt` | the comment at the top of `trails.ts` |
| `checks/crops.sh` | re-renders every crop and sheet `decisions.py` cites, then the region audit |
| `checks/zoom.py` | map crops with every piece tagged `id:auto-name` (`reg/*.jpg`; scratch: `br_zoom.py`) |
| `checks/fine.py` | PDF crops with chosen pieces numbered at both ends (`f_*.png`) |
| `checks/crop.py` | a PDF box rendered alone (`c_*.png`) |
| `checks/sheet.py` | label crops by name, or every label with no symbol (`@nosym`) |
| `checks/symsheet.py` | contact sheets of every label of a difficulty with its symbol (scratch: `br_symsheet.py`) |
| `checks/seq.py` | pieces and labels in PDF drawing order: the order does not group them here (scratch: `br_seq.py`) |
| `checks/stubs.py` | a crop of each lead-in stub (pieces 352-359) with the pieces around it and the overlays (`stubs/<id>.png`) |
| `checks/short_strokes.py` | every trail-coloured stroke under 4 pt, with its drawing number and ends: the 8 stubs and two scraps |
| `checks/order.py` | the PDF's drawing order around given pieces (stubs included), with their names (`stubs/seq_of.json`) |
| `checks/net.py` | every piece in a box in its own colour, tagged `id:name` at its middle and dotted at both ends: how pieces connect at a junction |
| `checks/named_syms.py` | the named symbols in map px, for `tools/trailmap/symbol_audit.py` (its header has the commands) |
| `checks/boxes.txt`, `checks/prob_boxes.txt` | the zoom boxes of the first pass over the map (`reg/g_*`) and of the problem windows (`reg/pb_*`) |

Never hand-edit the generated files: `trails.ts`, `linePolylines.json`,
`trailProposals.json`, `trailPaths.json`, or Claude's entries in
`trailReviews.json`. Change the decisions or the scripts here and re-run.

## Nuances of this map

- **Legend:** the trail lines are thin strokes in three colours: green
  (0.02,0.53,0.02), blue (0.01,0.28,0.82) and black (0,0,0), all 0.99 pt.
  They are solid, or dashed (1.505 pt dashes) for catwalks; dashed lines are
  kept. Lifts are thick red lines with white casings. The boundary is yellow
  dashes, and pale yellow bands mark the easiest routes. Terrain parks are
  orange bands, with their names in orange.
- **Symbols:** circle = green, square = blue, diamond = black, double diamond
  = double-black. EX ("Extreme Terrain") is two diamonds that each hold a
  white E and X (12-segment white fills): also double-black. Of the PDF's
  symbol fills, 3 belong to no name. They are lift notes ("■◆ Terrain Only"
  under the Kensho SuperChair, "◆ Terrain Only" by TenMile Station), and
  "Terrain Only" is in `NOT_TRAILS`.
- **Names:** AvenirNextCondensed-Demi, 4.9 to 7 pt, in the trail colours. The
  text holds many copies of each name: curved labels also as one object per
  letter, objects holding several names, and two-line names (bowls, `JOIN`)
  both as two lines and joined. `names.py` keeps one copy per position and
  drops any label whose characters all belong to other, shorter labels.
- **Last drawn wins:** three names are printed twice at one spot in two
  colours, and the later copy is the one that shows: Lower Peerless (black,
  then blue), Lower Sundown (blue, then green) and Freeway Terrain Park (blue,
  then orange). `names.py` sorts copies so that the last drawn is kept.
- **Not trails, ligatures:** subtitles and notes in the trail font are left
  out (`NOT_TRAILS`: "Easiest Way to Peak 9" under Sawmill, "Hike-To",
  "No Lift Access", the bus and coaster notes). The ﬁ/ﬂ ligatures are read as
  fi/fl (Spitfire).
- **Lines run into their names**, as the legend shows ("-◆ Name-"). A piece
  ends at the name's symbol, or at the far end of its text and continues from
  there, and `match.py` uses both. The PDF's drawing order does not group lines
  with names (`checks/seq.py`), unlike Winter Park's, so it is not used.
- **Panels printed on the map:** the legend, the terrain-park list, lift
  stats, the Epic box and the emergency box sit on the map. For the pieces,
  `extract_pdf_vectors.py --exclude` drops strokes wholly inside 4 boxes. For
  the names and symbols, the `PANELS` boxes in `symbols.py` and `names.py`
  (5 boxes, refined later) apply. No trail stroke is treated differently by
  the two sets.
- **No symbol of their own:** chute names inside a bowl print no symbol and
  take their bowl's (`ZONE` in `reading.py`). The chutes of Contest Bowl,
  Horseshoe Bowl, the Peak 7 bowls, Six Senses, Serenity Bowl, South Col,
  Snow White and Lake Chutes / Imperial Bowl are double-black. North Bowl's
  chutes are black, and Alpine Alley takes its black line. The four terrain
  parks print no symbol and get seed_roster's default, blue. An orange label
  matches blue pieces.
- **Two names, one line:** piece 250 carries Lower 4 O'Clock and then Gondola
  Ski Back, so it is cut where Lowest 4 O'Clock leaves it.
- **Stretches and markers:** a name printed in a gap of its own line gets a
  stretch drawn along its characters (two-line names along their midline),
  but only where a piece of its own runs into the name along the text. That
  gives 92 stretches on 89 trails. Three names printed beside their line get
  no stretch: Peak 8 Transfer, Swan City and Pioneer. A name with half its
  characters within 9 pt of one of its pieces counts as printed along it; the
  lead-in stubs don't count for this (they touch a name's end), and Tom's Mom,
  whose second line runs just below its name, is in a gap of its own line
  (`IN_GAP` in `reading.py`).
  The 40 names with no line of their own (bowls, open areas, kids' zones, the
  four parks, Hades and Purgatory by the E-Chair, Windows) are markers at
  their label.
- **Unnamed lines:** 17 real lines carry no printed name: connectors,
  catwalks, park exits, the access path to Windows. They are recorded in
  `UNNAMED` with what each is, and hidden as not trails.
- **The image:** the PDF's painting (xref 150, 1482x962) is placed at
  -14.6,-37.4 to 1468,925.1 pt. `matte.py` renders the page with the painting
  swapped for flat white and then flat black: alpha = 1 - (white - black) /
  255, colour = black / alpha. It composites that layer over the scene7
  raster, cropped to the clip and resized with Lanczos. (The generic
  `tools/trailmap/matte_pdf_layer.py` places the background with a bicubic
  affine transform instead, about 1.6 levels apart on average.)
- **Translucent layers:** the PDF draws 20 form XObjects under a graphics
  state with opacity below 1 or a Multiply blend: a 10% white wash right after
  the painting (Fm0), the yellow easiest-route bands and slow zones (Multiply),
  a 65% and three 60% fills (two of them the legend's Area Closed and Slow
  Zone swatches). scene7's raster is the whole map flattened, so it shows them
  already. `matte.py` therefore takes the layer's coverage from renders with
  those forms emptied (`translucent_forms()` in `matte_pdf_layer.py` finds
  them): opaque content is drawn with any translucent form over it, and the
  raster shows as it is everywhere else. Until 2026-10-07 the full layer's
  alpha was used, which applied them twice: the map was 10, 6 and 5 levels
  (R, G, B) lighter than the PDF's own render where only the painting shows,
  and the bands 27, 25 and 13 levels darker; now both equal scene7's raster
  (within 1 and 4 levels of the PDF's render).
- **Short lead-in stubs:** `extract_pdf_vectors.py`'s default `--min-length 4`
  drops 8 lead-in stubs of 2.8 to 4 pt drawn into a name's symbol or out of
  its last letter: Y-Chute, Deja Vu, Stampede, Tom's Mom, Frosty's Freeway's
  two, Sawmill and King's Way. A second pass appends them (352-359, named in
  `decisions.py` on `checks/stubs.py`'s crops); re-extracting everything at a
  lower minimum would renumber the pieces the decisions are keyed by. With
  them, `match.py` names four pieces it had given two names (75, 172, 199 and
  326: as the crops had settled them) and no longer reaches Frosty's Freeway's
  piece 16, which is now in `CHECKED`.
- **Two lines for one name:** Frosty's Freeway's line runs from the catwalk
  below the 6-Chair top into its label and out of its diamond to the Tunnel
  catwalk, and a second line (16) runs from its diamond up to the catwalk's
  far end beside the label (the PDF draws the three strokes one after another,
  between Snowbirds' and Lobo's pairs). Tom's Mom's runs from the end of the
  closure line beside E Lift Line into its double diamond, the name, then 274
  to the catwalk; its other line (67) comes from an access gate below the name
  to the same catwalk.

## Checks done

- Every piece with no name, several names, or a doubtful one was settled on
  zoomed crops (`checks/crops.sh` re-renders them all). The crops were a
  first pass over the whole map (`reg/g_*`, 30 boxes at 1.4x), the 23 windows
  round the problem pieces (`reg/pb_*`, 2.3x), closer zooms (`reg/z*`, `reg/q_*`,
  `reg/bc`), numbered-piece crops (`f_*`) and plain PDF crops (`c_*`). In
  `decisions.py`, 169 pieces are named and 17 recorded as unnamed, each with
  its crop.
- The labels printed with no symbol were checked on a sheet
  (`checks/sheet.py @nosym`), which gave `ZONE`. Every black and double-black
  trail was checked on symbol contact sheets (`checks/symsheet.py`: sym_blk,
  sym_dbl).
- `region_audit.py` drew every overlay on the map image (`--grid 6x4 --zoom
  1.4 --area 0,330,4374,2535`), with two closer boxes. That audit moved
  piece 240 from Crescendo to the unnamed lines, and piece 3 from Cashier to
  Bonanza.
- The hover check (`tools/trailmap/hover_check.cjs --resort breckenridge`)
  gave 511/511, here and in every later run. It only shows that each overlay
  shows its name, not that the overlay lies on its line.
- The port (2026-10-07): from an empty work folder with `IMAGES=1`, and again
  with the work folder filled, `git status` shows no change to
  `src/data/resorts/breckenridge/` or `public/maps/breckenridge.jpg`. Every
  intermediate file also equals the session's scratch copy. `symbol_audit.py`,
  which came after this resort, flags Tom's Mom's symbol 27 px off its
  overlay (its overlay is piece 67, below its label), and 6 symbols at
  overlay ends (Gold King, King's Way, Deja Vu, Nirvana, Frosty's Freeway,
  Rendezvous), most of them where a short stub was dropped (see above). None
  of these was changed then.
- The fixes (2026-10-07): the 8 stubs on `checks/stubs.py`'s crops and the
  drawing order around them; the 7 trails they belong to on
  `tools/trailmap/overlay_audit.py --resort breckenridge --only ...` cells (no
  other trail's overlay changed); `symbol_audit.py` (`checks/named_syms.py`):
  no symbol off its overlay, and 4 at an overlay end, each the start of its run
  (Gold King, King's Way, Nirvana, Rendezvous). The new image against the
  PDF's own render and scene7's raster, as above, and on crops (the bands, the
  legend's swatches). Hover check 511/511.

## A new season's map

1. Find the new PDF on the trail-map page (a link like
   `.../maps/winter-2026-2027/<date>_BR_winter-trail_map_001.pdf`) and the
   painting's scene7 name in the page's image URLs. Get its size with
   `?req=imageprops`. Put the URLs and the new SHA-256 sums in `regen.sh`,
   and use `FORCE=1` until they are set.
2. Check what the code assumes:
   - the stroke colours and widths, with a tally of `page.get_drawings()`;
   - the name font, sizes and colours;
   - the clip, and the panel boxes (`--exclude` in `regen.sh`, `PANELS` in
     `symbols.py` and `names.py`);
   - the painting's xref and size, and the page width, in `matte.py`;
   - the symbol shapes in `symbols.py`.
3. Rebuild `names.json` and check the two-line names (`JOIN`), `NOT_TRAILS`,
   the labels with no symbol (`checks/sheet.py @nosym`, then `ZONE` and
   `PARKS`), and the symbol sheets.
4. Piece ids change with any new edition, so `decisions.py` and the split in
   `regen.sh` have to be redone. Run `match.py`, then settle every piece with
   no name or several on crops (`checks/zoom.py`, `checks/fine.py`), and
   record `CHECKED` and `UNNAMED` again. Consider moving the resort onto
   `tools/trailmap/pdf_resort.py`, which records decisions as points that
   survive re-extraction.
5. Rebuild, run the region audit, `symbol_audit.py` and the hover check, and
   update `header.txt` and the playbook's Breckenridge entry.
