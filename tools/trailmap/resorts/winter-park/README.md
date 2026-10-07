# Winter Park's trail data pipeline

Winter Park's 2025-26 trail map is one vector PDF page: the painting is one
big raster, and every trail line, name and difficulty symbol is a vector on
top. The lines are strokes in the trail colours, and the names are real text,
but in a font with no Unicode map, so they are decoded from the font's glyph
ids. No readers were needed: every line piece was matched to the name printed
along it or at its end and settled on zoomed crops (`decisions.py`). This
folder holds the scripts that built `src/data/resorts/winter-park/*` and
`public/maps/winter-park.jpg` on 2026-10-01, cleaned up to run from the repo,
and the decisions taken on crops.

## Source

- **URL:** <https://skimap.org/skimaps/view/36019> (skimap.org's Winter Park
  Resort map 36019, "2025-2026 Downhill Ski Map", published 2025, by James
  Niehues). It redirects to
  `https://files.skimap.org/be74hf0apl2iydiexnnzcz095xgm.pdf`. Plain curl
  works (`regen.sh` sends a browser user agent, as the session did).
- **Edition:** PDF title `25-26_WP_Winter-Trail-Map-FINAL`, made with Adobe
  Illustrator 29.8 on 2025-10-30; one page, 1728 x 1206 pt.
- **File:** 34,921,233 bytes, SHA-256
  `2323f3d992472b223f5dd354b0eff72049b514334ffdba8179950e040da08e94`. Fetched
  on 2026-10-01; fetched again on 2026-10-07, same bytes. `regen.sh` checks the
  hash and stops on any other file (`FORCE=1` overrides).
- **The resort's own copy** is a later re-export of the same artwork:
  <https://www.winterparkresort.com/the-mountain/mountain-information/maps>
  links `25-26_wp_winter-trail-map-web.pdf` (title
  `25-26_WP_Winter-Trail-Map-web`, Illustrator 30.0, 2025-12-02, 21,982,368
  bytes, SHA-256 `d16e8fdb0b56de747277956734440196b7b8f27847bc5fc6aeabf30222883bab`).
  Checked on 2026-10-07 and not used. It has the same 232 strokes and the same
  names. Its colours are shifted (black 0,0,0; blue 0.1,0.53,0.79; green
  0.02,0.62,0.29), so these flags extract nothing from it. Its text has 22
  more name pieces (the same names), and four green strokes come in another
  order, so pieces 14-17 would swap ids.
- **No CDN image:** the painting inside the PDF is 9000x6375 px, about
  5.2 px/pt. The map image is the page rendered at 3.2 px/pt, so no sharper
  copy is needed.

## Rebuild

```bash
tools/trailmap/resorts/winter-park/regen.sh             # rebuild src/data/resorts/winter-park/ (~11 s)
IMAGES=1 tools/trailmap/resorts/winter-park/regen.sh    # also public/maps/winter-park.jpg (~17 s)
FORCE=1 tools/trailmap/resorts/winter-park/regen.sh     # on a PDF with another SHA-256 (a new edition: see below)
tools/trailmap/resorts/winter-park/checks/crops.sh      # afterwards: the crops and audit sheets (~1.5 min)
```

It downloads the PDF into `$WINTER_PARK_WORK` (default `work/winter-park`,
git-ignored) and writes every Winter Park data file. From an empty work folder
it takes about 20 s, and it reproduces the committed files byte for byte. A
person's reviews in `trailReviews.json` are kept. Claude's (`"by": "claude"`)
are rebuilt, keeping their timestamps when nothing changed. Needs
`pip install pymupdf pillow fonttools`, and node for `trails:apply`.

Never hand-edit the generated files: `trails.ts`, `linePolylines.json`,
`trailProposals.json`, `trailPaths.json`, or Claude's entries in
`trailReviews.json`. Change the scripts or `decisions.py` here and re-run. To
fix one trail by hand instead, add a person's review (the playbook, "To fix
one trail").

## Pipeline

`regen.sh` runs these in order. They are the session's steps of 2026-10-01
(13:22-14:13 UTC), and the last full chain ran at 14:10. Work files are in
`$WINTER_PARK_WORK`, and `D` is `src/data/resorts/winter-park`.

1. curl → `winterpark.pdf`, then the SHA-256 check.
2. The page inside the map's frame (`--clip 40,165,1360,1150`, without the
   logo band, the legend panel and the sponsor strip) at 3.2 px/pt →
   `wp_source.png` (4224x3152). Rendered only if missing, older than the PDF,
   or with `IMAGES=1`.
   With `IMAGES=1` it is saved as `public/maps/winter-park.jpg` (PIL, quality
   82, optimized, progressive: 3,889,377 bytes).
3. `tools/trailmap/extract_pdf_vectors.py`, twice, writes `pieces.json`. The
   first pass takes the 1.25 pt strokes in blue 0.09,0.54,0.79, green
   0.09,0.63,0.29 and black 0.01,0.02,0.02 (221 pieces). The second
   (`--append`) takes the blue strokes at 1.0 pt (ids 221-231: White Rabbit,
   Lower Parkway, Lonesome Whistle, Jabberwocky). An inline step adds the
   description (`_source`) and the unnamed connectors (`_unnamed`, from
   `decisions.py`) and writes `D/linePolylines.json`.
4. `tools/trailmap/pdf_labels.py --glyph 316=- --glyph '63=‘'` →
   `wp_labels.json`: every text piece (631), with the name font decoded.
5. `symbols.py` → `wp_syms.json`: 38 circles, 42 squares, 31
   advanced-intermediate symbols, 53 diamonds and 14 EX.
6. `names.py` → `wp_names.json`: 195 name labels (173 names), each with its
   colour and symbol.
7. `automatch.py` → `wp_assign.json`: the first-pass auto-match. Only the
   crops' tags use it. `checks/collinear.py` reports how the decisions compare
   with the pieces that run on from a label's own text line. Both steps only
   report.
8. `reading.py` writes `tiles/result_winterpark.json` (the reading: 194
   labels, 172 names, 228 named pieces) and `wp_gaps.json` (128 label-gap
   stretches on 106 trails, and 58 markers).
9. `tools/trailmap/seed_roster.py --areas 'winter-park=Winter Park
   Resort=12060'` → `D/trails.ts` and `labels.json`, with its header swapped
   for `header.txt`. That gives 172 trails: 28 green, 42 blue, 76 black, 26
   double-black. Three are glades and nine are parks.
10. `tools/trailmap/render_tiles.py` → `tiles/` (the tile index gives
    `aggregate_readings.py` the image size; the tiles themselves are not used).
11. `tools/trailmap/aggregate_readings.py` → `D/trailProposals.json` and
    `review_data.json`.
12. `traces.py` → `trace_gaps.json`: a trace for each trail with a stretch,
    and an empty trace for each of the 58 markers.
13. `tools/trailmap/traces_to_reviews.py --replace-claude` →
    `D/trailReviews.json` (164 Claude reviews: 106 confirmed with stretches,
    58 no-line).
14. `npm run -s trails:apply -- --resort winter-park` → `D/trailPaths.json`:
    106 verified, 8 proposed (pieces only, no stretch), 58 label markers.

## Files

| file | role |
|---|---|
| `regen.sh` | the whole pipeline above |
| `decisions.py` | every piece's name as printed (`CHECKED`, 228 pieces) or why it has none (`UNNAMED`, 4 connectors), settled on the crops; was the scratch `wp_checked.py` |
| `header.txt` | the comment at the top of `trails.ts` (the session's edit of 14:13) |
| `symbols.py` | difficulty symbols from the PDF's fills; was `wp_syms.py` |
| `names.py` | the name labels: deduped, two-line names joined, each with its symbol; was `wp_names.py` |
| `automatch.py` | names → pieces, first pass (for the crops' tags; the data don't depend on it); was `wp_build.py` |
| `reading.py` | labels + decisions → the reading for `seed_roster.py`/`aggregate_readings.py`, label-gap stretches and markers; was `wp_reading.py` |
| `traces.py` | stretches and markers → `traces_to_reviews.py`'s input; was `wp_traces.py` |
| `checks/crops.sh` | re-renders every crop, audit sheet and symbol sheet the session checked, with its boxes |
| `checks/zoom.py` | a crop of the map image with every piece drawn and tagged `id:auto-name`; was `wp_zoom.py` |
| `checks/crop.py` | a box rendered straight from the PDF; was `crop.py` |
| `checks/symsheet.py` | contact sheet of every label of a difficulty with its symbol; was `wp_symsheet.py` |
| `checks/collinear.py` | the decisions against the pieces that run on from a label's text line; was `wp_collinear.py` |
| `checks/drawing_order.py` | the PDF's drawing order, pieces and labels interleaved; was `wp_seq.py` |
| `checks/path_groups.py` | which PDF path each piece came from; was `wp_paths.py` |

Not kept from the scratch folder:

- `wp_labels.py`: `tools/trailmap/pdf_labels.py` was made from it in the same
  session. Run with the two `--glyph` flags, it gives the same labels (same
  JSON, keys in another order). This was checked on 2026-10-01 and again on
  2026-10-07.
- `myriad.cff`: the name font, saved with `extract_font(15)` while exploring
  its charset (byte-identical to the PDF's font 15). Nothing reads it, because
  `pdf_labels.py` reads the charset from the PDF itself.

## Nuances of this map

**Lines.** The trails are 1.25 pt strokes in three colours, and four blue
trails are drawn at 1.0 pt. Other stroke classes on the map are left out by
their colour or width:

- the lifts are red 1.0 pt strokes;
- the "Easiest Route to WP Base" bands are wide green strokes (6 pt) under
  the green lines;
- the CLOSED areas are hatched with single-segment yellow and dark
  (0.14,0.12,0.13) strokes at 1.0 and 1.25 pt, clipped to each area;
- the ski-area boundary, and two paths at the Mary Jane base and the tubing
  hill, are near-black 1.0-1.32 pt strokes;
- the names' halos are white 2 pt strokes, and other white strokes are
  dashes and casings.

`extract_pdf_vectors.py` drops runs that lie wholly outside `--clip`: the
legend's line icons. The session added that check for this map. Each piece is
a PDF path of its own (`checks/path_groups.py` found no path cut into several
pieces).

**Legend tiers.** The map has five: Easiest (green circle), More Difficult
(blue square), More Difficult (Advanced Intermediate: a light-blue square
0.11,0.66,0.88 holding a black diamond; its trails are black lines with
black names), Most Difficult (black diamond) and Extreme Terrain (EX). The
app has four ratings, so advanced intermediate is black and EX double-black.

**Symbols** are fills on the names' text lines (`symbols.py`). EX is two
touching black diamonds, each holding a white 12-line glyph (E, X) of at most
4.5 pt. Those letters tell an EX from the black rounded-square service icons.
A fill drawn twice at one spot counts once. Seven symbols sit by no name
(`names.log`):

- four advanced-intermediate symbols: on the dashed connector 0/1, on the
  dashed stretch 2, on the arrow 68 (all three `UNNAMED`), and on Cheshire
  Cat's line where connector 0 leaves it;
- Mock Turtle's circle, off its text line, which `reading.py` gives by hand
  (`EXTRA_SYM` and the symbol point);
- the EX in the Cirque key's title;
- a diamond-shaped fill in a sponsor's logo, below the map.

**Names** are text in a `MyriadVariableConcept-Roman` subset with no
ToUnicode map. `get_text()` gives U+FFFD, but `get_texttrace()` gives each
glyph's index in the subset, and the subset's CFF charset names it
`gidNNNNN`, its index in the full font: space 1, ’ 8, 0-9 17-26, A-Z 34-59,
a-z 66-91. Two glyphs fall outside that order and were read on rendered
labels: 316 is a hyphen (HOLE-IN-THE-WALL) and 63 an opening quote
(OVER ‘N’ UNDERWOOD).

Each text object is one label. `pdf_labels.py`:

- drops a halo copy inside the same object;
- splits an object that holds two names far apart;
- puts back the word spaces the PDF leaves out.

`names.py` then:

- keeps one label per name and spot (fill + overprint), coloured as the last
  copy drawn;
- removes ®;
- joins five names printed on two lines or either side of a lift (`JOIN`:
  Upper Parkway, Sober Englishman, Johnstone Junction, Lonesome Whistle, Race
  Place Recreational Racing);
- gives each symbol to the name whose text line it sits on (within 7 pt of
  the line, at most 16 pt before its first character or after its last). A
  symbol off every line goes to the nearest two-line block with none yet.

**Not trails, or not a trail of their own** (`names.py` `NOT_TRAILS`,
`reading.py` `SKIP`):

- TO VILLAGE WAY is a pointer to Village Way;
- RACE PLACE RECREATIONAL RACING is the race venue;
- the letters A-G2 under ALPHABET CHUTES are one trail, Alphabet Chutes.

**The Cirque.** Its key ("CIRQUE KEY - ALL ◆◆") rates all Cirque terrain EX.
Its nine numbered runs are printed as yellow squares with their names only in
the key box (`KEY`): South Headwall … Heart of Darkness. They become
double-black markers at their squares. G-Face, Go-Joe, JR South and JR North
print no symbol and are double-black too (`CIRQUE_NO_SYMBOL`).

**Parks** print no symbol, so they take `seed_roster.py`'s default, blue
(`PARKS`, nine names). Glades are the names that say GLADE. Display names are
title case, with and/of/the/in/'n' lower case after the first word and
JR/MRC/HCR kept upper case.

**Ratings printed twice.** A trail printed with two ratings takes the
majority, the harder one on a tie (`seed_roster.py`):

- Columbine: square and diamond, black;
- March Hare, White Rabbit: circle and square, blue;
- Mary Jane: two squares and a diamond, blue;
- Lonesome Whistle: two squares and a circle, blue;
- Village Way: six circles and a square, green.

**Lines run into their names.** A trail's line usually stops at its name, and
the line resumes past it, or the name ends the line:

- A name printed along a piece names it.
- A piece ending at a name's symbol, or at the far end of its text and
  pointing along it, continues that trail. 163 of the 232 pieces have an end
  on a label's own text line, just before its first character or after its
  last (`checks/collinear.py`).
- Six of those 163 belong to another trail, settled on crops: 14 is Easy Way
  (its band runs on past the Discovery Park callout to TO VILLAGE WAY), 73
  Rendezvous (it ends at Rendezvous's symbol, below Tweedle Dee's), 133 Mary
  Jane, 168 Cranmer (beside Lower Rail Yard's name), 188 Butch's Breezeway
  (it starts by Vista Dome Cutoff's name), and 204 Key Hole (beside Better
  Not's).
- The PDF's drawing order lists the trails Z to A, each one's labels next to
  its strokes (`checks/drawing_order.py`). That settled most of the rest, but
  it is off by one at group boundaries in places, and the crop decides.

**Label-gap stretches** (`reading.py`). Where a name is printed in a gap of its
own line or at its end, and not along it, the overlay gets a stretch along the
name's characters, from its symbol. Two-line names use their midline. A
stretch is made only where one of the trail's own pieces ends within 18 pt of
the name, pointing along it. That gives 128 stretches on 106 trails.

- Short Haul, Rollover, Forever Eva, Eldorado and 100's get no stretch:
  each is printed away from its line, not along it, and no end of its line
  points along the name.
- `traces.py` orders a trail's stretches so every jump between them is over
  400 px. Otherwise `trails:apply` would join them.

**Markers.** 58 names have no drawn line: the nine Cirque runs and 49 printed
names. Those are painted cuts with no line on them (Sleepy Hollow, Riflesight
Notch, Branch Line, Tweedle Dee …), bowls, glades, chutes and the parks. They
are markers at their labels.

**Piece ids.** `decisions.py` keys every decision by piece id. A vector
extraction is deterministic, so the ids hold for this exact file and these
extraction flags, and only for them: the resort's own re-export already
reorders four strokes. That is why `regen.sh` checks the SHA-256.

## Checks done

All on 2026-10-01, before the commit (`checks/crops.sh` re-renders every one
byte for byte, apart from the first-pass tiles):

- **Every piece settled on crops**, with each piece drawn and tagged
  `id:auto-name`: the whole map in 18 tiles (`reg/r_*`, `reg/s_*`), 12 closer
  crops (`reg/chutes_0`, `reg/z1_0` … `z11_0`) and 11 renders straight from
  the PDF (`c_*.png`, the legend among them). The first-pass tiles `reg/r_*`
  and `reg/chutes_0` were drawn before the auto-match's last change, so their
  tags differ now.
- **The PDF's drawing order** against the decisions (`checks/drawing_order.py`
  and a comparison at 13:52). **The collinear check:** 163 pieces, with the 6
  conflicts above each settled on a crop. Pieces 73, 133, 168 and 188 were
  looked at again on 2026-10-07 and hold up.
- **Region audit** of every overlay: 18 boxes at 1.25x (`audit/`), plus the
  bottom at 1.5x for Village Way (`audz/`).
- **Every double-black and black label with its symbol** on contact sheets,
  captioned with the trail list's difficulty: `sym_dbl.jpg` has the 17
  double-black labels (the other 9 double-blacks are the Cirque key's runs),
  and `sym_blk.jpg` has 79.
- **The hover check** (`tools/trailmap/hover_check.cjs --resort winter-park`):
  400/400 hover points show the right name, at the commit and in every re-run
  through 2026-10-06.
- **This regen** (2026-10-07):
  - From an empty work folder with `IMAGES=1`, `git status` shows no change to
    `src/data/resorts/winter-park` or `public/maps/winter-park.jpg`.
  - It shows none either on second runs, with and without `IMAGES`.
  - Every intermediate equals the session's scratch file byte for byte
    (`wp_labels.json` as JSON).

## A new season's map

1. **Get the new PDF.** Try skimap.org's newest Winter Park Resort map (ski
   area 503) and the resort's maps page. Put its URL and SHA-256 in `regen.sh`.
   Then tally the stroke colours and widths (the playbook, step 1). Colours
   shift even between exports of the same artwork (see Source), so update the
   `--color`/width flags, `names.py`'s `COL` and `symbols.py`'s fill colours
   and sizes. Check the map frame: `CLIP` in `regen.sh`, and the `X0, Y0`
   constants in the scripts (40, 165; 3.2 px/pt). Also check the legend and
   logo bounds in `symbols.py` (x 1405, y 160).
2. **Names.** Run `pdf_labels.py` without the `--glyph` flags. It lists every
   glyph it can't decode. Read each one on a rendered label
   (`checks/crop.py`) and pass `--glyph N=char`. Then check the hand-made
   lists against the new map:
   - in `names.py`: `JOIN`, `NOT_TRAILS`;
   - in `reading.py`: `SKIP`, `PARKS`, `CIRQUE_NO_SYMBOL`, `EXTRA_SYM` and
     its symbol point, `KEY` (the Cirque key), `SMALL`/`KEEP`.
3. **Decisions.** Redo them all: piece ids change with any change to the
   file. With `FORCE=1` the regen still runs, but it names the new pieces by
   the old ids, so start with `CHECKED` and `UNNAMED` empty (every name is
   then a marker). Run `FORCE=1 regen.sh` for the work files, then look at
   `checks/zoom.py` tiles over the whole map, `checks/drawing_order.py` and
   `checks/collinear.py`. Settle every piece into `decisions.py`, then run the
   whole regen. Consider recording the decisions as points this time (as Vail
   and `pdf_resort.py` do), so they survive a re-export.
4. **Update the texts:** `header.txt` (its counts and rating notes), the
   `_source` text in `regen.sh` (step 3), this README and the playbook's
   bullet.
5. **Audit again.** Redo the crops and audit sheets (the boxes in
   `checks/crops.sh` are this edition's), the symbol sheets and the hover
   check.
