# Archive: the one-off scripts behind the maintained tools

Every script written while building the resorts that isn't part of a resort's pipeline or a maintained tool, kept
as written so nothing used along the way is lost: the analyses that settled hard cases, early versions of tools
now in `tools/` and `tools/trailmap/`, browser checks of the app, and the source surveys. They are a record of the
method, not maintained code: most read the session's scratch folder (`/tmp/claude-0/.../scratchpad`) or a
resort's `work/` folder by absolute path, some use the app's old resort dropdown, and none is run by anything.
To redo one of these jobs, start from the maintained tool named in its group's notes (docs/trail-map-playbook.md
lists them all) and read the script here for what was done.

Nothing here was downloaded: every file was written by Claude in the session that built the resorts.

## app

Browser checks of the app written along the way (offline, the first visit on a slow link, phones, the header, accounts against the mock Supabase, the conditions API against a mock Redis). The maintained ones are `tools/app_check.cjs`, `tools/app_flows.cjs`, `tools/offline_check.cjs` and `tools/accounts_check.cjs`; these used the old resort dropdown and the session's scratch builds.

| file | what it did |
|---|---|
| `accounts/debug_offline.cjs` | Signed in on a phone screen with the network off: prints the console to debug the offline sync |
| `accounts/e2e.cjs` | Accounts end to end against the mock Supabase: sign in with an emailed code on two devices, sync, edit offline, delete the account (superseded by tools/accounts_check.cjs) |
| `accounts/mock-supabase.cjs` | A stand-in for a Supabase project, enough for the app's accounts: GoTrue's email code sign-in, sessions and admin delete, and PostgREST on trip_logs with its row-level security (a user sees only their own row). Codes are readable at GET /__… |
| `accounts/offline_signed_in.cjs` | A signed-in phone that goes offline, marks runs, and syncs them once back online |
| `accounts/start_mock.sh` | Starts scripts/mockSupabase.cjs on port 54321 in the background (PID to mock.pid) |
| `accounts/start_preview.sh` | start vite preview on the accounts test build; its PID goes to preview.pid |
| `conditions/mock_upstash_test.mjs` | api/conditions.ts against a mock Upstash Redis REST server: votes, tags and the 24-hour window |
| `hdr.cjs` | Screenshots of the header on a phone screen (trip bar and resort button) from a build |
| `offline/loaderror_test.cjs` | The load-error screen with the old resort dropdown (superseded by tools/offline_check.cjs) |
| `offline/offline_test.cjs` | Offline behaviour with the old resort dropdown: first visit, offline reload, a deploy (superseded by tools/offline_check.cjs) |
| `offline/serve.cjs` | Static server for dist/ that behaves like Vercel for static files (cache-control: public, max-age=0, must-revalidate + ETag/304) and logs every request. |
| `picker/check.cjs` | node check.cjs <base url> <out dir>: drive the resort picker on desktop (mouse + keyboard) and a phone (touch) |
| `production/double.cjs` | Counts map downloads on a first visit, unthrottled and on a 4 Mbps link: found the map downloaded twice (fixed) |
| `production/header.cjs` | Header layout at 360, 390 and 768 px wide: nothing overlaps |
| `production/mobile.cjs` | Phone flows in Chromium with an iPhone 13 screen and touch: tap a trail on the map, mark it from the sheet, undo, trip summary, switch to Vail and its panels. |
| `production/perf.cjs` | First visit on a slow connection: today's production build vs merged main. The server throttles one shared link (page and service worker alike) and counts every byte sent in the first 60 s. |
| `production/smoke.cjs` | The live site (myskiruns.vercel.app) opens Killington with its overlays |
| `production/tabs_backup.cjs` | Two tabs on one device, and backups: export, import into a fresh browser, import a file from before this release, re-import a deleted trip. |
| `production/upgrade.cjs` | The upgrade production users will go through: the live build (b0ca176, service worker v9, 11 maps precached) to the merged main, on one origin, in one browser profile. Then no signal. |
| `production/who.cjs` | Which requests a first visit makes and who makes them (page or service worker), with and without the worker |
| `shot.cjs` | Desktop and phone screenshots of one resort from a build, with page errors |
| `shot_run.sh` | Serves the scratch build and runs shot.cjs |

## big-sky

Big Sky's checks while its pieces were settled: crops of the PDF sharp around pieces and names, drawing order, junctions, overlaps (now `tools/trailmap/pdf_overlaps.py`), the OpenStreetMap cross-check (now `tools/trailmap/osm_check.py`), and the names against the trail report.

| file | what it did |
|---|---|
| `app/check.cjs` | node check.cjs <base url> <out dir>: Big Sky in the real app: found by search (name, "sky", "montana", "mt"), its three panels load with overlays, a trail on another panel opens that panel; desktop and phone. |
| `binfo.py` | binfo.py RESORT/PANEL [x0,y0,x1,y1]: pieces (crossing the box): id, class, name, why, length, ends. |
| `bpcs.py` | bpcs.py RESORT/PANEL OUT id[,id..] [--m 70] [--w 700]: one cell per piece: the PDF rendered sharp around it (margin m map px), the piece drawn translucent red with its id at both ends, other pieces thin with id:name, names (pdf_resort's rea… |
| `bsc.py` | bsc.py PANEL x0,y0,x1,y1 (map px) ZOOM OUT [--names] [--pieces] [--raw]: Big Sky's panel PDF rendered sharp over the box; --names: each name (pdf_resort's reading, after joins) as a magenta line through its characters with its text, symbols… |
| `bseq.py` | bseq.py RESORT/PANEL id[,id...] [--k 3]: each piece's PDF strokes (seqno) and the strokes drawn k before and after, with the pieces they gave and those pieces' names (one run's strokes are usually drawn one after another). |
| `junc.py` | junc.py RESORT/PANEL id: the pieces whose ends lie on the piece (within 7 px), in order along it, with the point, the arc length there and their names. |
| `namegrid.py` | namegrid.py PANEL OUT name[,name..] [--m 90] [--z 3]: one cell per printed name (every copy): the PDF rendered sharp around it, line pieces thin with id:name, the name magenta. |
| `near.py` | near.py RESORT/PANEL id[,id..] [--r 220]: names printed within r map px of each piece (nearest point), with their symbol and whether a piece already carries them. |
| `osmcheck.py` | osmcheck.py RESORT/PANEL [--radius 320] [--only id,id] [--undecided] [--plot out.png]: cross-check pieces against OpenStreetMap's ski runs (piste:type=downhill ways, fetched with Overpass). Per piece: fit an affine map (OSM metres -> map px… |
| `osmtopo.py` | osmtopo.py OUT name[,name..]: plot OSM runs with these names (and every run within 150 m, grey) in metres, north up, each labelled at both ends with its name and way id; prints where each way starts and ends and which named ways it touches … |
| `overlaps.py` | overlaps.py RESORT/PANEL [--tol 3] [--min 25]: stretches of a named piece lying along another named piece of a different name (within tol map px) for at least min px: two overlays on one drawn line. |
| `pcol.py` | pcol.py PANEL x0,y0,x1,y1 ZOOM OUT id[,id..]: the PDF rendered over the box (map px), the given pieces each in its own colour with its id at its start (S) and end (E), a legend at the top. |
| `pieces_view.py` | pieces_view.py PANEL OUT [zoom] [x0,y0,x1,y1]: the panel's pieces (pieces.json) drawn over its map, ids at mid. |
| `pinfo.py` | pinfo.py RESORT/PANEL id [names...]: a piece's points (every ~20 px, with index) and where the given names' characters run (first/last point), to pick a cut point. |
| `ratecmp.py` | ratecmp.py: Big Sky's trails.ts ratings and mountains vs the trail report (tools/trailmap/resorts/big-sky/report.json). |
| `rostercmp.py` | rostercmp.py [panel ...]: the panels' names vs the resort feed: names not in it, and feed trails no panel prints. |

## deer-valley

Deer Valley's analyses: the October PDF rendered on the November image and diffed (`diff.py`, `clusters.py`,
`pairs.py`), every label side by side in both editions and scored (`labdiff.py`, `labsheet.py`: now
`resorts/deer-valley/checks/editions.py labels`), word-gap settings tried against the interactive map's names
(`spacing.py`), points along pieces for decisions (`pt.py`), crops joined side by side (`hstack.py`), and an edit
that rewrote `vicomap.py check` with a KD-tree (`edit_check.py`).

| file | what it did |
|---|---|
| `deer-valley/diff.py` | The October page rendered on the November image's grid (the registration's affine) and the blurred difference of the two |
| `deer-valley/clusters.py` | Clusters of strong difference in that image, largest first |
| `deer-valley/pairs.py` | pairs.py <out> x,y,w,h ...: each box of the November image beside the October render |
| `deer-valley/labdiff.py` | Each printed label's share of dark text pixels with no match in the other edition, most changed first |
| `deer-valley/labsheet.py` | Contact sheets of the labels (November above, October below), in a given order |
| `deer-valley/spacing.py` | `pdf_glyphs.py labels` with several `--space` values, each scored by the names the interactive map spells the same but for spaces |
| `deer-valley/pt.py` | pt.py id@fraction ...: the map px point that far along a piece (for decisions.py points) |
| `deer-valley/hstack.py` | hstack.py <out> <png> ...: images side by side |
| `deer-valley/edit_check.py` | The edit that replaced `vicomap.py check`'s brute-force distances with a KD-tree |

## general

Wrappers and early versions of tools now in the repo: the hover check runs (`tools/trailmap/hover_all.sh`), the regeneration check (`tools/trailmap/regen_all.sh`), the audit sheets (`tools/trailmap/overlay_audit.py`), piece contact sheets and region audits (`tools/trailmap/piece_sheet.py`, `region_audit.py`).

| file | what it did |
|---|---|
| `along.py` | For a piece: the arc length of each label projected on it and of each junction (another piece's end on it). |
| `audit_sheets.py` | Audit sheets: each trail's overlay (orange) over its crop, other trails thin cyan, 2 per sheet. python3 audit_sheets.py --image src.png --paths trailPaths.json --trails trails.ts --out dir [--only id,id] [--per 2] |
| `hover_all.sh` | Hover check of every resort on the scratch build (superseded by tools/trailmap/hover_all.sh) |
| `hover_bs.sh` | Hover check of Big Sky's three panels |
| `hover_every.sh` | Hover check of every resort and panel then (superseded by tools/trailmap/hover_all.sh) |
| `hover_hv.sh` | Hover check of Heavenly's two panels |
| `hover_one.sh` | hover_one.sh RESORT... : serve dist-hover and run hover_check for the given resorts |
| `hover_pc.sh` | Hover check of Park City |
| `hover_pt.sh` | Hover check of Palisades Tahoe's three panels |
| `hover_some.sh` | hover_some.sh RESORT[:PANEL]... : serve dist-hover on 4199, hover-check each, stop the server by PID |
| `hover_wb.sh` | Hover check of Whistler Blackcomb's three panels |
| `pair.sh` | pair.sh RID x0,y0,x1,y1 zoom out.png : plain crop / crop with pieces and names, side by side |
| `piece_sheet.py` | Contact sheets: each piece alone (magenta) on its own crop, other pieces thin grey, symbols tagged with names. |
| `regen_all.sh` | rerun every other PDF resort's regen.sh (with images) and report whether git sees any change |
| `region_audit.py` | Region audit: every overlay drawn in its own colour with its trail name tagged on it, over zoomed regions of the map, to compare with the printed labels. python3 region_audit.py --image src.png --paths trailPaths.json --trails trails.ts --o… |

## heavenly

Heavenly's analyses: registering the 2022-23 PDF on the 2024-25 image (now `tools/trailmap/register_pages.py`), the side-by-side comparison of the two editions and the ink checks of every label and line piece (`compare.py`, `labelcheck.py`, `linecheck.py`), reading filled outlines and dashes (`ribbon.py`, which became part of `resorts/heavenly/prepare.py`), OpenStreetMap fitted on the lifts' end stations (`osm*.py`), crops for tracing, and the feed parser that built `report.json` (now `tools/trailmap/reports/feed_trails.py`).

| file | what it did |
|---|---|
| `app/picker_hv.cjs` | picker_hv.cjs <url> <out prefix>: the resort picker finds Heavenly by name, second state and lake; picking it opens its two panels, each with its map image and overlays; screenshots on desktop and phone. |
| `py/compare.py` | Side-by-side crops: the 2022 page (warped onto the 2024 image) and the 2024 image, for boxes in main-panel px. |
| `py/dashes.py` | A dashed line fill (by seqno): its subpaths and their centre lines, to chain the dashes |
| `py/info.py` | The 2022-23 PDF's page boxes and a tally of its drawings by type and colour |
| `py/items.py` | The path items of given fills (by seqno): how an outline, an arrowhead or a dash is drawn |
| `py/labelcheck.py` | For each 2022 label (and symbol) of a panel: does the 2024 image still print it there? Draw the label's glyph outlines (glyphs.json, PDF pt) at the image's scale and count how much of them is dark ink in the 2024 image. |
| `py/linecheck.py` | For each line piece of a panel (pieces.json): the share of points along it with the line's ink within 2 px in the 2024 image (blue, green, dark). |
| `py/linesonly.py` | Render only the line-colour fills (blue, green, dark lines) of the 2022 page in a main-map box, over a faded copy of the 2024 image: linesonly.py out x0,y0,x1,y1 zoom |
| `py/names_table.py` | Every name of a panel: printed text, name, centre (map px), symbol, the pieces named after it. |
| `py/noline.py` | Names of a panel with no line of their own: name, symbol, label start/end (first and last glyph, map px). |
| `py/osmfit.py` | Fit OSM (lat/lon) -> main map px from lift end stations; save the fit; report residuals. |
| `py/osmlocal.py` | Draw OSM runs over a crop of the main map, through an affine fitted on nearby lifts' end stations (each lift's direction chosen to fit best). osmlocal.py OUT x0,y0,x1,y1 zoom lift1,lift2,... [extra map=osm pairs] |
| `py/osmnear.py` | OSM runs touching a given way's ends, and their ends (warped into map px). osmnear.py way_id/name ... |
| `py/osmtopo.py` | osmtopo.py OUT name[,name..]: plot OSM runs with these names (and every run within 150 m, grey) in metres, north up, each labelled at both ends with its name and way id; prints where each way starts and ends and which named ways it touches … |
| `py/osmwarp.py` | OSM runs drawn on the main map through a thin-plate-spline warp fitted on the lifts' end stations (each lift's direction picked to agree with a robust affine fit). osmwarp.py OUT x0,y0,x1,y1 zoom [name filter substrings...] |
| `py/pathoverlap.py` | Final overlays (trailPaths.json) lying along another trail's overlay for 40+ px (within 4 px): a route the apply step added along another trail's line, or two trails sharing a line. |
| `py/reg_inset.py` | the inset region of the page, rendered at the image's scale |
| `py/ribbon.py` | Subpaths of a fill and their centre lines (PDF points). |
| `py/seqs.py` | A panel's line outlines in drawing order with their place on the image, to see which outlines belong together |
| `py/show_fill.py` | Draw given fills (by seqno) of a PDF page, zoomed, with their path points: show_fill.py pdf out.png zoom seq... |
| `py/subpaths.py` | List fills of a colour with their subpaths (a subpath starts at a move: an item whose start is not the previous end). |
| `py/trcrop.py` | Crops for tracing: the map with the panel's pieces (thin), every no-line name's label polyline (magenta, its start circled) and candidate traces (traces.json: [[name, [[x, y], ...]], ...], cyan). trcrop.py panel out x0,y0,x1,y1 zoom |
| `scripts/build_feed_trails.py` | Build Heavenly's trail list from the FR.TerrainStatusFeed of an archived terrain-and-lift-status.aspx page. |
| `scripts/warc_to_html.py` | Split one uncompressed WARC response record into its HTTP headers and body. |
| `tools/redraw.py` | redraw.py: redraw selected fills of a PDF page on a blank page (pymupdf Shape) and render it. Used as a module: redraw(page, drawings, scale, clip) -> RGB numpy array. |


## mt-bachelor

Mt. Bachelor's look into a line the extraction missed (I-5's and Carnival's, drawn as one outline at their
junction): the PDF drawings under a map point (`near.py`) and `pdf_outline_lines.py`'s tests run on one drawing
(`dbg_outline.py`). What they found is in `pdf_outline_lines.py` (an outline read by its skeleton when its mean
width is a line's) and `resorts/mt-bachelor/checks/missed.py`.

| file | what it did |
|---|---|
| `mt-bachelor/near.py` | near.py <pdf> x,y ...: the PDF drawings whose box holds each map px point (Mt. Bachelor's clip and scale), with colour, width and drawing order |
| `mt-bachelor/dbg_outline.py` | dbg_outline.py <pdf> <seqno>: one drawing's outlines through `pdf_outline_lines.py`'s centre line, width, length and area |

## okemo

The helpers Okemo's six tile readers and five trace readers wrote for themselves in their work folders (crops, symbol sheets, writing their result files, an OpenStreetMap fit), kept as written. Okemo's pipeline and the readings themselves are in `tools/trailmap/resorts/okemo/`.

| file | what it did |
|---|---|
| `readers/r0/build.py` | id: (name, confidence, note) |
| `readers/r0/check.py` | A box of Okemo's PDF page rendered sharp (map px in, PNG out) |
| `readers/r0/vr.py` | vector render of PDF page 2 for a SOURCE-px box, zoom S relative to source px |
| `readers/r2/build_result.py` | Reader 2 writing its result file: each piece's name with its tiles and note |
| `readers/r2/labsheet.py` | Lettered label boxes drawn on the vector layer, to read the labels one by one |
| `readers/r2/pathmap.py` | The PDF's trail-coloured paths drawn by class, to see which path each piece came from |
| `readers/r2/symsheet.py` | A sheet of symbol crops at given points, captioned |
| `readers/r2/vcrop.py` | Crops of the vector layer with the pieces drawn and numbered |
| `readers/r3/build.py` | Reader 3 writing its result file from its readings |
| `readers/r3/centers.py` | The centres of the labels reader 3 read, from the PDF's glyph fills |
| `readers/r3/symsheet.py` | A sheet of symbol crops by the labels reader 3 read |
| `readers/r4/build_result.py` | Reader 4 writing its result file |
| `readers/r4/groups.py` | The PDF's trail-coloured paths grouped by colour against the pieces |
| `readers/r4/symsheet.py` | A sheet of symbol crops by the labels reader 4 read |
| `readers/r5/pdfcrop.py` | pdfcrop.py x0 y0 x1 y1 zoom out -- render PDF page 1 region given in SOURCE px (3x) at zoom (px per source px). |
| `readers/r5/write_result.py` | Reader 5's result file, written out |
| `readers/trace1_work/bgcrop.py` | bgcrop.py out.png x0 y0 x1 y1 zoom [grid] [pieces/none] [traces json]: background raster only (no vectors), in source px. |
| `readers/trace1_work/osmfit.py` | least squares via normal equations (3 unknowns) |
| `readers/trace1_work/osmplot.py` | map-like frame: X = north (m), Y = east (m) |
| `readers/trace1_work/pcrop.py` | pcrop.py out.png x0 y0 x1 y1 zoom [pieces/all/none] [grid step] [trace json list or {name:list}] Renders the PDF vectors (page 1) at zoom x source px; draws pieces with ids, a source-px grid, traces. |
| `readers/trace4/pdfdump.py` | The PDF's drawings inside a box (map px): type, colour, width, points |
| `readers/trace4/pdfpaths.py` | The PDF's trail-coloured paths listed with their ends, for a trace reader |
| `readers/tw0/joinsim.py` | trails:apply's joining of a trail's pieces simulated (JOIN_NEAR, JOIN_FAR), to see where it would bridge |
| `readers/work/band_one.py` | One glade band (the blue-violet fills round glades) drawn alone over its crop |
| `readers/work/bands.py` | The glade bands' fills listed by colour and box |
| `readers/work/pdfcrop.py` | Render a region of the Okemo PDF map page at high zoom. usage: pdfcrop.py x0 y0 x1 y1 zoom out.png (x/y in SOURCE IMAGE px = PDF pt * 3) optional: --ids 1,2 to overlay pieces (thin magenta) |
| `readers/work/symgrid.py` | Render many small PDF crops (centred on source px) into one captioned grid. usage: symgrid.py out.png zoom half cols name:cx:cy [name:cx:cy ...] |
| `readers/work/write_result.py` | Reader 2's (second) result file, written out |

## palisades-tahoe

Palisades Tahoe's checks: crops, drawing order, the OpenStreetMap cross-check, candidate JOINs of names printed in parts, letter-gap histograms for `--space`, names and symbols against the trail report.

| file | what it did |
|---|---|
| `adddec.py` | adddec.py RESORT[/PANEL] FILE "comment": record FILE's id=NAME / id=-:why / x,y=NAME lines (# comments ignored) in the resort's decisions.py, each id as the point on its piece farthest from every other piece (ids of the last build), so a de… |
| `allstrokes.py` | allstrokes.py PANEL OUT x0,y0,x1,y1 (map px) ZOOM: the PDF region sharp, and beside it every trail-coloured stroke crossing the region redrawn on white with its seqno (d: dashed). |
| `app/check.cjs` | node check.cjs <base url> <out dir>: Palisades Tahoe in the real app: found by search (name, "tahoe", "california", "ca"), its three panels load with overlays, a trail on another panel opens that panel; desktop and phone. |
| `around.py` | around.py PANEL OUT x,y[,label] ... [--r 60] [--z 4]: a sheet of crops (map px centres, radius r map px) with labels and symbols drawn (ptcrop.py's style), each captioned. |
| `classes.py` | classes.py PDF OUT ZOOM: the page rendered faintly with each coloured stroke class drawn on top (label: colour, width, dashed), to see what each class is. |
| `gaphist.py` | gaphist.py PANEL: histogram of letter-to-letter gaps (pt, along each run's end-to-end direction) for a panel's black glyph runs, with the letter pairs: word gaps sit apart from letter gaps. |
| `info.py` | info.py PANEL x0,y0,x1,y1 (map px): pieces crossing the box: id, class, name, why, length, ends. |
| `joins.py` | joins.py PANEL [--gap 14]: pairs and triples of nearby labels (pt) whose words, joined in either order, make a trail report name: candidate JOINs (reading order by position: the upper/left part first). |
| `joinsheet.py` | joinsheet.py PANEL OUT: one cell per candidate JOIN (joins.py): the map around the parts, the first part's glyph centres magenta, the next part's cyan, the third's yellow; caption: the report name. |
| `labmatch.py` | labmatch.py PANEL: each printed label (text, centre in map px, glyph count) with the feed names it could be part of (exact, or the label's words all in the name), to plan JOIN / RENAME. |
| `names.py` | names.py PANEL: the panel's names after JOIN / RENAME / DROP (pdf_resort.py's reading), each with its symbol and position (map px), and whether the trail report has it (by letters and digits only). |
| `nosym.py` | nosym.py PANEL: names with no symbol, each with the nearest unassigned symbols (distance from its nearest glyph, in pt) and the names nearest those symbols. |
| `osmcheck.py` | osmcheck.py [--radius 320] [--only id,id] [--undecided] [--plot out.png]: cross-check Park City's pieces against OpenStreetMap's ski runs (piste:type=downhill ways, fetched with Overpass). Per piece: fit an affine map (OSM metres -> map px)… |
| `ovl.py` | ovl.py PANEL TRAIL_ID x0,y0,x1,y1 ZOOM OUT: one trail's overlay (trailPaths.json) in orange over the map (map px box, zoom vs map px), other overlays thin cyan. |
| `pcs.py` | pcs.py PANEL OUT id[,id..] [--m 70] [--w 700]: one cell per piece: the PDF rendered sharp around it (margin m map px), the piece drawn translucent red with its id at both ends, other pieces thin with id:name, labels magenta. |
| `ptcrop.py` | ptcrop.py PANEL x0,y0,x1,y1 (map px) ZOOM OUT [--labels] [--pieces]: the panel's PDF rendered sharp over the box; --labels: each printed label's glyph centres and text (printed.json) in magenta, symbols as red marks; --pieces: the line piec… |
| `ratecmp.py` | ratecmp.py: trails.ts ratings and sides vs the resort's trail report (truth/feed_trails.json). |
| `rostercmp.py` | rostercmp.py: every panel's names vs the trail report: names not in it, and report trails no panel prints. |
| `seq.py` | seq.py PANEL id[,id...] [--k 4]: each piece's PDF stroke (seqno) and the strokes drawn k before and after it, with the pieces they gave and those pieces' names: one run's strokes are usually drawn one after another. |
| `stretchends.py` | stretchends.py PANEL: each stretch along a name: is a line piece (any) near each of its two ends, and the angle between the name and the trail's own line where it meets the stretch. |
| `symcmp.py` | symcmp.py PANEL: each name's symbol vs the trail report's rating; lists disagreements and names with none. |
| `und.py` | und.py PANEL OUT_DIR [cols rows] [--all]: tiles of the panel's map holding undecided pieces (--all: every piece); each piece drawn in its colour with id (named ones id:name), undecided ones thick red; printed labels magenta; symbols red squ… |

## park-city

Park City's checks: drawing-order checks (`seq*.py`, now `tools/trailmap/pieces.py seq`), crops (`pair.py`, now `pieces.py pair`), the OpenStreetMap cross-check, per-trail audit cells (now `overlay_audit.py`), and `first-pass/`: the stroke tally and the first names-vs-report check.

| file | what it did |
|---|---|
| `adddec.py` | adddec.py FILE "comment": record FILE's id=NAME / id=-:why / x,y=NAME lines (# comments ignored) in Park City's decisions.py, each id as the point on its piece farthest from every other piece (ids of the last build), so a decision never sit… |
| `allstrokes.py` | allstrokes.py OUT x0,y0,x1,y1 (map px) ZOOM: the PDF region sharp, and below it every trail-coloured stroke (green/blue/black/orange, not lifts) crossing the region redrawn thin on white with its seqno and dash flag. |
| `along.py` | along.py ID FRACTION / ID cross OTHER_ID: the point on piece ID (map px) at that fraction of its length, or where it comes closest to piece OTHER_ID (a crossing). |
| `app/check.cjs` | node check.cjs <base url> <out dir>: Park City in the real app: found by search (name, "utah", "ut"), its map and overlays load, a hover shows a name, a click marks a trail, the trail list has its 345 trails; desktop and phone. |
| `app/run.sh` | Serves the scratch build and runs park-city/app/check.cjs |
| `audit.py` | audit4.py PANEL OUT [--per 4] [--max 560] [--only id,id]: per-trail audit cells for a Whistler Blackcomb panel, 2x2 per sheet: the map crop around the trail's overlay and its printed names; the trail's overlay thick orange (red dots at part… |
| `colmis.py` | colmis.py: Park City pieces whose line colour doesn't match their trail's difficulty (green/blue/black/park). |
| `first-pass/crop.py` | crop.py x0 y0 x1 y1 ZOOM OUT [--labels]: render a PDF region of Park City's map (pt); --labels: draw each printed label's glyph centres and text (printed.json) in magenta. |
| `first-pass/drawgroups.py` | drawgroups.py OUT x0,y0,x1,y1 ZOOM spec...: the page region with the strokes of each spec 'r,g,b@w[@dashed]=COLOR' redrawn in COLOR (hex). |
| `first-pass/tally.py` | tally.py PAGE: stroke colours x widths (count, total length) and fill colours (count, median size). |
| `first-pass/unmatched.py` | unmatched.py: Park City's names (after JOIN/RENAME/DROP) not in the archived trail report, and the report's trails no name matches. |
| `info.py` | info.py x0,y0,x1,y1: Park City pieces (id cls name why len ends) and names (symbol, ends) inside the box (map px). |
| `lonely.py` | lonely.py RESORT[/panels/PANEL]: label stretches whose label meets no line end (neither terminal within END_REACH). |
| `look.py` | look.py OUT id[,id...] [--margin 60] [--zoom 3]: one crop around the given pieces (map px), plain on top and with the pieces drawn below: the given ones thick red with ids, the others thin in their colour with id:name. |
| `namecells.py` | namecells.py OUT NAME[,NAME...] [--margin 70] [--zoom 2.2]: one cell per printed label of each name (Park City): the map crop, the label boxed in magenta, every piece drawn thin in its colour with id:name; a contact sheet of 2 columns. |
| `near.py` | near.py [--d 4] [--min 25]: pairs of Park City trails whose overlays run within d map px of each other for at least min px of length (sampled every 2 px) -- two names on one drawn line, or two lines drawn closer than a line's width. |
| `osmcheck.py` | osmcheck.py [--radius 320] [--only id,id] [--undecided] [--plot out.png]: cross-check Park City's pieces against OpenStreetMap's ski runs (piste:type=downhill ways, fetched with Overpass). Per piece: fit an affine map (OSM metres -> map px)… |
| `pair.py` | pair.py x0,y0,x1,y1 zoom out.png: Park City map crop (map px), plain / with pieces (id:name), side by side. |
| `ratecmp.py` | ratecmp.py: Park City's trails.ts difficulty and area vs the archived trail report's (Common Crawl, March 2026). |
| `seq.py` | seq.py id[,id...]: for each Park City piece, the PDF stroke(s) it came from (seqno, colour, dashes), found by its end points: drawing order often groups one run's strokes (a line cut by a label). |
| `seqarea.py` | seqarea.py x0,y0,x1,y1 (map px): every Park City piece in the box with the seqno of its PDF stroke and its name, sorted by seqno (one run's strokes are usually drawn one after another). |
| `seqcheck.py` | seqcheck.py: Park City pieces whose PDF stroke is drawn among another trail's strokes (the strokes just before and after it belong to one other trail) while none of its own trail's strokes are near it in the drawing order. |
| `strokes.py` | strokes.py OUT x0,y0,x1,y1 (map px) ZOOM seq[,seq...]: the PDF region rendered sharp, and below it the same region with only the given strokes redrawn on a white ground, each in its own colour with its seqno. |
| `tp.py` | tp.py name-or-slug[,...]: the pieces each Park City trail got (id, length, ends in map px, how named). |
| `tps.py` | tps.py slug[,...]: each Park City trail's pieces with the drawing order (seqno) of the PDF stroke each came from: one run's strokes are usually drawn one after another, so a piece far off in the order is worth a look. |
| `tz.py` | tz.py OUT tid[,tid...] [--box x0,y0,x1,y1 (map px)] [--zoom Z] [--pieces]: the PDF rendered sharp around the given trails' overlays, plain on top, below with every overlay drawn thin (the given trails red/orange, others cyan, each with its … |
| `und.py` | und.py x0,y0,x1,y1 zoom out: the map crop (map px) with named pieces thin (their colour), undecided ones thick red with their ids, names' labels as in names.json. |
| `und2.py` | und2.py OUT_DIR [cols rows]: tiles of the map (with a margin) holding undecided pieces; in each, every piece drawn thin in its colour with id:name labels for named ones near undecided ones, undecided ones thick red with ids. |

## sources

Finding sources: skimap.org search and probes (now `tools/trailmap/skimap.py`), links inside resort pages (now `tools/trailmap/find_source.cjs`), PDF summaries (now `pdf_inspect.py`, `pdf_classes.py`), and `biggest-resorts/`: the survey of the largest resorts' map sources that chose the five big mountains.

| file | what it did |
|---|---|
| `biggest-resorts/fetch_pdfs.cjs` | Downloads candidate resorts' trail-map PDFs from inside their pages (headless Chromium) |
| `biggest-resorts/maps.py` | skimap.org areas: each one's maps with year and type |
| `biggest-resorts/pdfinfo_tally.py` | For each PDF: metadata, pages, images, drawings and text, to sort candidates by route |
| `biggest-resorts/tally2.py` | Strokes of a PDF page grouped into trail colours (green, blue, black, ...) with counts and lengths |
| `biggest-resorts/vecs.py` | A PDF page's vector drawings rendered alone (no images), to see whether the trail lines are vectors |
| `biggest-resorts/vr_maps.cjs` | Vail Resorts' trail-map pages: lists each page's map PDFs and CDN images |
| `biggest-resorts/vr_maps3.cjs` | vr_maps.cjs again for Wildcat, Crested Butte and Beaver Creek |
| `links.cjs` | node links.cjs <url> : list links and responses mentioning pdf/map/trail |
| `probe/brute.cjs` | node brute.cjs <page url> <url template with {D}> <from YYYYMMDD> <to YYYYMMDD>: fetch each dated URL from inside the page, print hits |
| `probe/classes.py` | classes.py map.pdf page tag [n] [--fills]: contact sheet of the top-n stroke classes (colour, width) drawn alone, each on grey. |
| `probe/inspect_pdf.py` | inspect_pdf.py map.pdf tag [--render 0.5] [--vec PAGE]: summarise a trail-map PDF's images, strokes, fills and text. |
| `probe/links2.cjs` | node links2.cjs <url> [regex]: print responses + img/a/source URLs matching regex (default scene7/pdf/trail/map) |
| `probe/runs.py` | runs.py glyphs.json [join] [exclude x0,y0,x1,y1 ...]: rough count of glyph runs (labels) - consecutive same-colour glyphs within join pt. |
| `probe/tryurls.cjs` | node tryurls.cjs <page url> <url1> <url2> ...: fetch each URL from inside the page (HEAD-like: status, type, length) |
| `probe/veccrop.py` | veccrop.py map.pdf page x0 y0 x1 y1 zoom out.png [--both]: render the vector layer alone (drawings only) for a clip; --both puts the full render beside it. |
| `skarea.py` | A skimap.org area's maps: id and caption (superseded by tools/trailmap/skimap.py maps) |
| `skprobe.py` | skprobe.py AREA_ID [n]: the newest downhill maps of a skimap.org area: year, file type and, for a PDF, its vector content. |
| `sksearch.py` | skimap.org search: area id, name, region, number of maps (superseded by tools/trailmap/skimap.py search) |
| `vail-resorts/fetch_page.cjs` | Opens a Vail Resorts page in a real browser and saves its HTML (the sites refuse curl) |
| `vail-resorts/fetch_status.cjs` | node fetch_status.cjs <terrain-status-url> <out.html>: save the rendered terrain status page (Vail sites). |
| `vail-resorts/fetch_vail.cjs` | node fetch_vail.cjs <page-url> <outprefix>: open the resort's trail-map page in a real browser, list the map PDFs it links, and download the winter trail map PDF with the page as referer. |

## steamboat

Steamboat's look at its interactive map's SVG as a vector source: the SVG's elements and strokes summarised
(`svg_inspect.py`), its lines drawn on the print through a trial affine (`svg_on_map.py`), and each label's best
offset onto the print's ink (`label_offsets.py`: what showed the 2026-27 artwork moved some names). What they found is
in `vicomap.py parse --detail` / `fit-ink` and `resorts/steamboat/prepare.py`.

| file | what it did |
|---|---|
| `steamboat/svg_inspect.py` | svg_inspect.py <map.svg>: element ids by kind, and the fill:none paths' stroke colour, width and dashes, inside or outside the trail groups |
| `steamboat/svg_on_map.py` | svg_on_map.py <image> <trails.json> a,b,c,d,e,f <out> [box ...]: the SVG's trail lines (and names) drawn on the image, cropped |
| `steamboat/label_offsets.py` | Each group's letters' best offset (within 30 px) onto the print's ink in its colour, largest first |

## sugarbush

The helpers Sugarbush's five tile readers wrote for themselves (label drafts, symbol sheets, writing their result files). Sugarbush's pipeline and readings are in `tools/trailmap/resorts/sugarbush/`.

| file | what it did |
|---|---|
| `readers/r1/build.py` | Reader 1 writing its result file |
| `readers/r1/labels_draft.py` | name, symbol, glade, center, note |
| `readers/r2/build.py` | Reader 2 writing its result file |
| `readers/r2/marks.py` | Points from a JSON file marked on a crop of the map |
| `readers/r2/verify.py` | Pieces drawn over crops of the map, to check a reading |
| `readers/r3/labels_check.py` | The labels reader 3 read, marked on a crop by their positions |
| `readers/r3/symsheet.py` | A sheet of symbol crops at given points |
| `readers/r3/write_result.py` | Reader 3's result file, written out |
| `readers/r4/build.py` | Reader 4 writing its result file |
| `readers/r4/labels_draft.py` | Reader 4's draft of the labels it saw, with their symbols |

## trailmap-apply-bridging

The check of a change to `trails:apply`'s bridging rule: which trails' paths changed in every resort, drawn old against new.

| file | what it did |
|---|---|
| `diff.py` | diff.py: per changed resort, the trails whose paths differ between the old bridge rule and the new one, and the end points the old rule added (the bridged-to point and the end it extended), in map px. |
| `viz.py` | viz.py: per changed trail, a crop around where its old and new paths differ: old path red, new green (drawn thin over each other), on the map; a contact sheet of them. |
| `viz2.py` | viz2.py: like viz.py, but one crop per cluster of differing points (within 60 px), about 3x. |

## vail

Vail's development scripts, before its pipeline was cleaned into `tools/trailmap/resorts/vail/` and the detectors into `raster_lines.py` and `raster_symbols.py`: the line and symbol detection, symbol contact sheets and names read off them, review tiles, the gap checks between symbols and overlays.

| file | what it did |
|---|---|
| `fetch_links.cjs` | node fetch_links.cjs <url> <out.html>: save the rendered page and print every link/resource that mentions map/pdf. |
| `regen.sh` | Vail: rebuild reading -> roster -> per-panel proposals -> reviews -> trailPaths from the scratch decisions. |
| `try_pdfs.cjs` | node try_pdfs.cjs <page-url> <url>... : from inside the page, HEAD/GET each candidate and save the PDFs that exist. |
| `ui_check.cjs` | UI check of the Vail panel switcher: desktop and phone screenshots, tab switching, and a trail picked from the list jumping to the panel it is drawn on (zoomed to it, its sheet open). |
| `ui_single.cjs` | Vail in the app on one screen: panel tabs and page errors |
| `vl_add.py` | vl_add.py panel "comment" id=NAME ... id=-:note ... / x,y=NAME : record decisions (by the current piece ids, or a point) as points on the pieces in vl_checked.py, under the panel, with a comment line. |
| `vl_build.py` | Vail: name each line piece from the symbols (Vail draws a trail's symbol on its line, at its top, with the name printed beside it): a piece through a named symbol, or starting at it and running downhill, takes that name; names then spread a… |
| `vl_checked.py` | Vail pieces settled on review tiles (r_<panel>_<n>.jpg) and fine crops: a point on the piece (panel px) and its name. Points, not ids: ids change whenever the extraction changes (vl_pt.resolve finds the current piece there). |
| `vl_diff.py` | vl_diff.py: per trail name, the symbols on its own pieces (named ones and the unnamed '?' ones sitting on them) and the drawn length of each line colour, to settle trails printed with more than one rating. |
| `vl_dsheet.py` | vl_dsheet.py out.png: every diamond / double-diamond symbol on the three panels, cropped around its centre and scaled to one size, tagged with panel, index, detected type and the name read for it. |
| `vl_gapfix.py` | vl_gapfix.py: for each symbol off its trail's overlay (vl_symgap.py), propose the stretch along the printed name from the symbol to the overlay's nearest end; draw the proposals (cyan) over the overlay (magenta) on sheets gapfix_<k>.png, an… |
| `vl_gapsheet.py` | vl_gapsheet.py out.png: for each symbol vl_symgap.py lists, a crop around the symbol and its trail's nearest overlay end, the overlay drawn in magenta and a 25 px grid, to read off the stretch to trace. |
| `vl_grid.py` | vl_grid.py panel out.png x0,y0,x1,y1 [zoom]: the panel with a labelled 100 px grid and every named symbol tagged with its name (from vl_symnames.py), to list the labels that have no symbol and read their positions. |
| `vl_lines.py` | Vail: trail lines from the clean CDN rasters. Per colour class: a strict colour mask, dashes linked along their own direction, small blobs (text glyphs, icon bits) and box outlines dropped, then a 1 px skeleton traced into pieces; at juncti… |
| `vl_pt.py` | Piece ids change whenever the extraction changes, so decisions are kept as a point on the piece (its middle, in panel px): pt(panel, id, lines_file) gives that point; resolve(panel, P, (x, y)) finds the current piece through it. |
| `vl_reading.py` | Vail: the checked decisions -> per-panel inputs for the trail pipeline. |
| `vl_rev.py` | vl_rev.py panel prefix x0,y0,x1,y1 ... [--z 1.25] [--final f.json]: review tiles. Pieces drawn in bright colours with 'id:name' (auto names from assign_<panel>.json, or the final {id: name} map), symbols tagged '#i NAME'. |
| `vl_run.py` | Runs vl_lines.py over each panel with its excluded boxes (legend, logos, inset frames) |
| `vl_show.py` | vl_show.py panel out.png x0,y0,x1,y1 [zoom] [--ids a,b] [--names file]: the panel image (faded) with pieces drawn in bright colours, numbered (or named from an assignment json {id: name}). |
| `vl_snap.py` | vl_snap.py panel cls x,y x,y ... [--r 14] [--show out.png]: snap a rough polyline (read off a zoomed crop) onto the painted line of that colour: resample every 8 px, move each sample to the middle of the nearest run of line pixels within r … |
| `vl_symend.py` | vl_symend.py: named symbols where their trail's overlay ENDS (rather than passing through): either the run starts at its symbol, or the line resumes past the printed name and that stretch is missing. Sheets endsheet_<k>.png show each with t… |
| `vl_symgap.py` | vl_symgap.py: every named symbol whose trail's final overlay (trailPaths.json) does not reach it: a stub between the parent line and the symbol, or the stretch along the printed name, that no piece covers. |
| `vl_symnames.py` | Names printed beside each detected symbol, read on the contact sheets (ss_<panel>_<n>.png). None = not a trail symbol; '?' = a symbol with no name beside it (settled on crops later). |
| `vl_syms.py` | Difficulty symbols on a Vail panel: solid squarish fills in a trail colour (blue square, green circle, black diamond); a black pair of diamonds (two diamonds touching: a 2:1 rotated box with a notch) is a double diamond, and one holding whi… |
| `vl_symsheet.py` | vl_symsheet.py panel start count out.png: contact sheet of symbol crops (symbol circled in red, index on top). |
| `vl_symzoom.py` | vl_symzoom.py panel out.png ids... : larger crops (440x300 source px at 1.5x) around the given symbols. |
| `vl_text.py` | Vail label text: black glyph components (dark ink crowded by other glyph-sized parts), and for each named symbol the chain of glyphs that starts beside it (its printed name). Writes text_<panel>.json: {symbol index: {"pts": [glyph centres i… |
| `vl_textshow.py` | vl_textshow.py panel out.png x0,y0,x1,y1 [zoom]: each label's glyph chain (dots) and its end (circle). |

## whistler-blackcomb

Whistler Blackcomb's checks: its GIS (ArcGIS run layer) against the map's meeting points (`gischeck.py`, `gisfit.py`, `gistopo.py`), the feed and GIS ground truth (`truth/`), per-trail audit cells (`audit4.py`, now `overlay_audit.py`), stroke tallies, and in `readers/` and `audit-readers/` the small helpers that reader sub-agents wrote for themselves while settling pieces and auditing overlays on crops.

| file | what it did |
|---|---|
| `adddec.py` | adddec.py PANEL FILE "comment": record the id=NAME / id=- / id=-:why / x,y=NAME lines of FILE (# comments ignored) with pdf_resort.py's add (ids of the last build). |
| `app/ui_check.cjs` | UI check for Whistler Blackcomb: three panel tabs, a trail on an inset opens its panel, phone size. |
| `app/ui_expr.cjs` | The two Expressways and a park in Whistler Blackcomb's trail list: both listed (one per mountain), each shows its own overlay on the main map; Choker Park's line shows and hovering it names it; no console errors. |
| `audit-readers/scratch_0/look.py` | Crop a map region; draw one trail's overlay thinly (so the drawn line under it stays visible). |
| `audit-readers/scratch_1/focus.py` | Focused crop: plain crop (left/top) and the same crop with ONLY the target trail's overlay drawn thin (magenta, semi-transparent, ends circled) plus other overlays as faint thin cyan lines tagged with names. |
| `audit-readers/scratch_1/pieces_near.py` | Pieces of a panel crossing a box (map px), with their names |
| `audit-readers/scratch_1/pts.py` | A trail's overlay points in map px |
| `audit-readers/scratch_2/along.py` | usage: along.py panel piece_id/x,y;x,y;... [step] |
| `audit-readers/scratch_2/ascii.py` | A box of the map image printed as characters by colour: where exactly a line's ink is |
| `audit-readers/scratch_2/mask.py` | usage: mask.py panel x0,y0,x1,y1 zoom out.png colorclass piece_ids... |
| `audit-readers/scratch_2/near.py` | Printed labels inside a box (map px) |
| `audit-readers/scratch_2/ov.py` | usage: ov.py panel x0,y0,x1,y1 [trail-id to print fully] |
| `audit-readers/scratch_2/pc.py` | usage: pc.py panel x0,y0,x1,y1 -> list pieces (pieces_cut.json) crossing box, with assigned name (names.json) |
| `audit-readers/scratch_3/crop.sh` | usage: crop.sh PANEL NAME x0,y0,x1,y1 ZOOM [paths] [grid] |
| `audit-readers/scratch_3/pair.sh` | usage: pair.sh PANEL NAME x0,y0,x1,y1 ZOOM [grid] -> side-by-side plain / overlays |
| `audit-readers/scratch_4/crop.sh` | usage: crop.sh PANEL x0,y0,x1,y1 ZOOM NAME [paths] [grid] |
| `audit-readers/scratch_4/near.py` | usage: near.py PANEL x0 y0 x1 y1 (map px) |
| `audit-readers/scratch_4/pts.py` | A trail's overlay points in map px |
| `audit4.py` | audit4.py PANEL OUT [--per 4] [--max 560] [--only id,id]: per-trail audit cells for a Whistler Blackcomb panel, 2x2 per sheet: the map crop around the trail's overlay and its printed names; the trail's overlay thick orange (red dots at part… |
| `bestpt.py` | bestpt.py PANEL ID [ID...]: for each piece (ids of the last build), the point on it (map px) farthest from every other piece, and that distance: a safe point to record a decision with. |
| `cls_list.py` | Strokes of one colour and width on a page: index, seqno, length, ends |
| `crop.py` | crop.py PAGE x0 y0 x1 y1 ZOOM OUT [--vec-only]: render a page region of the Whistler PDF. |
| `gischeck.py` | gischeck.py PANEL [--radius 320] [--out flags.json]: cross-check every named piece of a Whistler Blackcomb panel against the resort's ArcGIS run lines. Per piece: fit an affine map (GIS metres -> map px) by ICP on the named pieces around it… |
| `gisfit.py` | gisfit.py PANEL 'GISNAME=id,id;GISNAME=id' 'QUERY,QUERY' [out.png box zoom]: fit a local affine map (GIS lon/lat -> map px) by ICP on the given correspondences (GIS run line -> map pieces), print the residual per run, then project the QUERY… |
| `gisnear.py` | gisnear.py MOUNTAIN NAME [NAME...]: for each GIS run (by base name), its parts' lengths and the runs its two ends touch (nearest runs within 60 m), to read a run's topology. |
| `gistopo.py` | gistopo.py PANEL: where two trails' pieces meet on the map (a piece end on another trail's piece), check that the resort's ArcGIS run lines for the two also come close. Prints the meetings whose GIS runs are far apart: one of the two pieces… |
| `hl.py` | hl.py PAGE x0,y0,x1,y1 ZOOM OUT seqno[,seqno...] : render a region with the given drawings outlined in magenta. |
| `hl2.py` | hl2.py PANEL x0,y0,x1,y1 ZOOM OUT id[,id...]: the crop twice, plain and with the given pieces drawn thin in distinct colours (numbered), to see which drawn line each one lies on. |
| `info.py` | info.py PANEL x0,y0,x1,y1 : pieces (id cls tag why len ends) and names (with symbol) inside the box. |
| `merge_answers.py` | merge_answers.py: compare the two tilings' reader answers with the tool's tags (names.json). Prints: consensus changes (both readers agree, differ from the tag), disagreements, missing answers. |
| `only.py` | only.py PANEL x0,y0,x1,y1 zoom out.png id,id,...: the map crop with only these pieces drawn (thick, distinct colours), each tagged with its id at both ends. |
| `orange.py` | orange.py PAGE: tally stroke colours/widths of orange-ish strokes (r>0.85, 0.3<g<0.75, b<0.3) on the page. |
| `orange_draw.py` | orange_draw.py PAGE x0 y0 x1 y1 ZOOM OUT: crop of the page with each orange stroke (by width) redrawn on top: 1.98 red, 1.07 magenta, 0.85 cyan, 1.6 lime, other blue. |
| `orange_list.py` | orange_list.py PAGE: each orange stroke other than the boundary (1.6) and hatching (0.85): index, width, dashes, rect (pt), length (pt). |
| `overview.py` | overview.py PANEL x0,y0,x1,y1 scale out.png : pieces over the map, red = undecided (with id), green = named, blue = stretch along a name, grey = not a trail. |
| `pair.py` | pair.py PANEL x0,y0,x1,y1 zoom out.png [--names]: plain crop / crop with pieces (id:name) side by side. |
| `prepare_head.py` | Whistler Blackcomb: the map images, line pieces, printed names and symbols of its three panels, from the 2025-26 trail-map PDF (the "Mountain Atlas"), for tools/trailmap/pdf_resort.py. |
| `ratecmp.py` | Each trail's rating against the resort's feed and GIS ratings |
| `readers/scratch_rA_0/c2.py` | usage: c2.py name x0,y0,x1,y1 [zoom] [ids...] -> SCRATCH/name.png: plain on top, pieces below (only ids if given) |
| `readers/scratch_rA_0/dr.py` | dump the PDF page-1 drawings (strokes) to a pickle for quick queries |
| `readers/scratch_rA_0/lab.py` | usage: lab.py x0 y0 x1 y1 (map px) -> printed labels (whole words, not single letters) inside, in map px |
| `readers/scratch_rA_0/near.py` | usage: near.py x y [r] (map px): strokes with a point within r map px (default 6) -> seq, colour, width, bbox (map px) |
| `readers/scratch_rA_0/pp.py` | Pieces by id: points in map px and their names |
| `readers/scratch_rA_1/pc.py` | Crop helper: draw only selected pieces (thin, labelled with id) on a zoomed crop. usage: python3 pc.py --box x0,y0,x1,y1 --zoom 3 --ids 1,2,3 --out out.png [--grid 50] [--width 2] [--dump] --ids all -> every piece touching the box --dump ->… |
| `readers/scratch_rA_1/pdfnear.py` | List PDF drawings (strokes) passing within r map px of a point. usage: pdfnear.py x y [r] [colorfilter] |
| `readers/scratch_rA_1/pdfseq.py` | List PDF drawings with index in [a,b]. usage: pdfseq.py a b |
| `readers/scratch_rA_1/samp.py` | classify |
| `readers/scratch_rA_2/cum.py` | A piece's points with the distance along it |
| `readers/scratch_rA_2/labs.py` | Printed labels inside a box (map px) |
| `readers/scratch_rA_2/pts.py` | Pieces by id: points in map px and their names |
| `readers/scratch_rA_2/show.py` | Render a zoomed crop with only chosen pieces drawn thin, side by side with the plain crop. usage: show.py --box x0,y0,x1,y1 --zoom z --ids 1,2,3 --out out.png [--grid 50] [--width 2] [--stack] |
| `readers/scratch_rA_3/bin/crop.sh` | crop.sh name x0,y0,x1,y1 zoom [ids...] -> crop with only given pieces (or all if 'all', or none if none given) |
| `readers/scratch_rA_3/bin/draws.py` | list PDF drawings (strokes) intersecting a box given in MAP px; print colour, width, dashes, seq, points in map px |
| `readers/scratch_rA_3/bin/names_near.py` | list printed names (from all region txt files) whose centre/first/last lies within R of a point or box |
| `readers/scratch_rA_3/bin/nb.py` | neighbours: for each given piece, list pieces with an endpoint (or any point) near its endpoints |
| `readers/scratch_rA_3/bin/pdfcrop.py` | render the PDF page 2 for a box in MAP px at zoom z (output px per map px), with a 10-map-px grid |
| `readers/scratch_rA_3/bin/pp.py` | Pieces by id: points in map px and their names |
| `readers/scratch_rA_3/bin/seq.py` | list PDF strokes with seqno in a range: colour, width, first/last points in map px |
| `readers/scratch_rA_3/bin/touch.py` | for each given piece, list other pieces whose ENDPOINTS lie within R px of any part of it |
| `readers/scratch_rB_0/tools/crop.sh` | usage: crop.sh name x0,y0,x1,y1 zoom [ids...] (ids empty = all pieces; "none" = no pieces) |
| `readers/scratch_rB_0/tools/labels.py` | Printed labels inside a box (map px) |
| `readers/scratch_rB_0/tools/near.py` | Pieces passing within r px of a point |
| `readers/scratch_rB_0/tools/pinfo.py` | Pieces by id: points in map px and their names |
| `readers/scratch_rB_0/tools/syms.py` | Symbols inside a box (map px) |
| `readers/scratch_rB_1/crop.sh` | usage: crop.sh x0,y0,x1,y1 zoom outname [ids.../all] |
| `readers/scratch_rB_1/pts.py` | Pieces by id: every n-th point in map px |
| `readers/scratch_rB_2/hl.py` | Render a zoomed crop: top/left = plain, other = selected pieces drawn thin (so the map line stays visible). usage: python3 hl.py x0,y0,x1,y1 zoom out.png id1 id2 ... (ids optional; 'all' = every piece in box) |
| `readers/scratch_rB_2/pts.py` | Pieces by id: points in map px and their names |
| `readers/scratch_rB_3/crop.sh` | usage: crop.sh name x0,y0,x1,y1 [zoom] |
| `readers/scratch_rB_3/draw.py` | usage: draw.py x0 y0 x1 y1 (map px) -> list strokes intersecting the box (PDF page 2) |
| `readers/scratch_rB_3/draw2.py` | usage: draw2.py x0 y0 x1 y1 [color-filter] -> full point lists of trail-coloured strokes touching the box |
| `readers/scratch_rB_3/labs.py` | Printed labels inside a box (map px) |
| `readers/scratch_rB_3/pdfclip.py` | usage: pdfclip.py x0 y0 x1 y1 zoom out.png (map px box; zoom = output px per map px) |
| `readers/scratch_rB_3/pp.py` | Pieces by id: points in map px and their names |
| `readers/scratch_rB_3/raw.py` | A piece before and after the cuts (pieces.json vs pieces_cut.json) |
| `readers/scratch_rB_3/sel.py` | usage: sel.py out.json id1 id2 ... |
| `readers/scratch_rB_3/seq.py` | usage: seq.py x0 y0 x1 y1 : list trail-coloured strokes with seqno touching the box, sorted by seqno |
| `readers/scratch_rB_3/strokes.py` | usage: strokes.py x0 y0 x1 y1 zoom out.png [colorfilter r,g,b] draws every trail-coloured PDF stroke touching the box, each in its own colour, numbered, over the map crop |
| `readers/scratch_rB_3/vis.py` | usage: vis.py x0 y0 x1 y1 r,g,b -> for each stroke of that colour touching the box: the visible fraction along its path, printed as a run-length string over the path (V = line colour seen within 1px, . = not) |
| `reg.sh` | reg.sh PANEL x0,y0,x1,y1 ZOOM OUT: current pieces image of a box + the info list (pieces whose midpoint is inside) |
| `regions.py` | regions.py PANEL OUTDIR STEPX STEPY OFFX OFFY ZOOM: reader packages: per region a pair image (plain / pieces with id:name) of the core box plus a margin, and a text file listing the pieces it owns (midpoint inside the core) and the names pr… |
| `tally.py` | Stroke and fill classes of a page of Whistler Blackcomb's PDF (or a clip of it) |
| `truth/arcgis_dump.sh` | Usage: arcgis_dump.sh <outdir> <service>/<layerId>... Downloads all features (all fields, WGS84 geometry) of each layer as GeoJSON, paging by 1000. |
| `truth/arcgis_layers.sh` | Usage: arcgis_layers.sh <outdir> <service>... Saves each FeatureServer's service JSON and each layer's JSON (fields, counts) to outdir. |
| `truth/build_runs.py` | Build wb_truth/runs.json from the official 2025-26 terrain feed + the resort's GIS run layer. |
| `truth/cc_lookup.py` | Look up a URL in a Common Crawl crawl without the (flaky) index server. |
| `truth/cc_query.sh` | Usage: cc_query.sh <url-pattern> <outfile> <collection>... Queries Common Crawl CDX indexes for a URL pattern (with retries), appending JSON lines to outfile. |
| `truth/explore_match.py` | Exploratory: which feed names match GIS names after normalisation, and which don't. |
| `truth/extract_feed.py` | Extract every `<Name> = {json}` assignment for TerrainStatusFeed-like variables from an HTML file. |
| `truth/fetch_page.cjs` | Usage: node fetch_page.cjs <url> <outdir> [waitMs] Opens a page in headless Chromium through the agent proxy, saves the final HTML, every JSON/JS-ish network response body, and a list of all requests. |
| `truth/near.py` | Print the nearest GIS runs to the middle of each named GIS run (for judging ambiguous aliases). |
| `truth/wb_common.py` | Shared loading/normalisation for the Whistler Blackcomb ground-truth build. |
| `truthcmp.py` | The map's trail names against the resort's feed and its GIS runs: names missing on either side |
