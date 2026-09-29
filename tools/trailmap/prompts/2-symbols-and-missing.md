# Prompt 2 — difficulty symbols + find unplaced trails

Run after the first review, over the same tile groups. Job A settles
difficulty (and black vs double-black, which line color can't); Job B looks
for roster trails that still have no overlay. Every difficulty change it
proposes must be checked on a zoomed crop of the symbol before applying
(`render_crops.py`, or crops around `labelSrc`) — in our run all 34 held up,
but double vs single diamonds are easy to misread.

Fill in `{{…}}` and send verbatim.

---

You are checking a ski trail map ({{RESORT}}). Read-only except for writing
ONE output file.

Tiles: {{TILE_PATHS}}
Each tile is a crop of the trail map at {{ZOOM}}x zoom. Detected lines are
thin MAGENTA overlays with numeric IDs in yellow boxes. Tile geometry:
{{TILES_DIR}}/index.json (box=[x0,y0,x1,y1] source px; tile px (px,py) ->
source (x0+px/{{ZOOM}}, y0+py/{{ZOOM}})). Full-resolution source image for
zooming: {{SOURCE_IMAGE}} — crop and enlarge it with python3 + PIL whenever
text or symbols are small; do this for every symbol you report.

Legend: {{LEGEND}}
Difficulty SYMBOL printed at the start of a trail next to its name: green
circle = easy, blue square = intermediate, one black diamond = advanced, TWO
black diamonds = expert (double black).

JOB A — difficulty symbols. For EVERY trail-name label in your tiles, report
the symbol attached to that trail (look at both ends of the label and where
the line starts; the symbol is usually right before/after the name or at the
top of the line). Report: name as printed, symbol ("circle", "square",
"diamond", "double-diamond", "none-visible"), glade tree icon nearby
(yes/no), line color, source px of the label.

JOB B — find unplaced trails. These roster trails currently have no overlay:
see {{MISSING_TXT}} (id | name | roster difficulty | area | what the reviewer
marked). Search your tiles for each one, including likely printed variants
(upper/lower pairs where only the base name is printed, shortened names).
For each one you find evidence for, report:
- label text as printed and its source px,
- the line: numeric IDs of the magenta pieces that form it, and/or a list of
  source-px points tracing any stretch that has no magenta overlay,
- if it shares a drawn line with another named trail (e.g. Upper X is the top
  part of X's line), say where it starts/ends in source px and which pieces
  are shared.
Pieces already assigned to trails are listed in {{ASSIGNED_TXT}} (id: trail).
A missing trail may legitimately reuse part of an assigned piece — say so
explicitly. Report only what the map shows; do not guess. If a name is
simply not in your tiles, omit it.

Full roster: {{ROSTER_TXT}}.

Write JSON to {{OUT_FILE}}:
{"symbols":[{"mapName":"CAPER","rosterId":"caper","symbol":"circle","glade":false,"color":"green","labelSrc":[3800,900]}],
 "found":[{"rosterId":"lower-canyon","mapName":"LOWER CANYON","labelSrc":[x,y],"pieces":[12,34],"drawnSrc":[[x,y],[x,y]],"sharesWith":null,"note":"","confidence":"high|medium|low"}]}
Then reply with a short summary.
