# Prompt 0 — first reading of a new map (no trail list yet)

For a resort with no roster: one pass that names every line piece AND builds
the roster from what is printed (names, difficulty symbols, glade icons,
area). Combines prompts 1 and 2 (job A). Run one reader per column of
neighbouring tiles; Stowe: 25 tiles, 6 readers.

Fill in `{{…}}` and send verbatim.

---

You are labeling a ski trail map ({{RESORT}}). Read-only task except for
writing ONE output file.

Tiles: {{TILE_PATHS}}
Each tile is a crop of the trail map at {{ZOOM}}x zoom. The trail lines are
overlaid in thin MAGENTA with magenta end dots, and each piece has a numeric
ID in a yellow box (a thin leader line points from the box to its piece).
The same ID can appear in several tiles (tiles overlap). Tile geometry is in
{{TILES_DIR}}/index.json (box = [x0,y0,x1,y1] in source pixels; tile pixel
(px,py) = source (x0+px/{{ZOOM}}, y0+py/{{ZOOM}})). Full-resolution source
image: {{SOURCE_IMAGE}} — crop and enlarge it with python3 + PIL whenever
text or symbols are small or cut off at a tile edge.

Map legend (verified): {{LEGEND}}

JOB 1 — pieces. For EVERY numeric ID visible in your tiles decide which
trail the underlying drawn line belongs to:
- the NAME as printed on the map (a line belongs to trail X if X's label is
  printed along it, OR it is the continuous continuation of a line carrying
  X's label with no junction/other label in between; labels are often
  inline: the line stops at the label and continues after it);
- or "LIFT", "NOT_A_TRAIL", or "UNKNOWN" (no evidence — do not guess).
If one ID runs through a junction into a differently named trail, say
"SPLIT: A / B" and describe where it switches. A label between two parallel
lines belongs to the line it is aligned with / closer to (check the text
baseline). Give the line color and confidence high/medium/low.

JOB 2 — labels. For EVERY trail-name label printed in your tiles (including
glades and trails with no drawn line), report: the name exactly as printed
(e.g. "LOWER NOSEDIVE"), the difficulty SYMBOL attached to it ("circle" =
easier, "square" = more difficult, "diamond" = most difficult,
"double-diamond" = experts only, "none-visible"), whether a GLADE icon sits
by the label, the AREA it belongs to ({{AREAS}}), and the label's centre in
SOURCE px. Symbols sit at the start or end of the name or where the line
begins; zoom in on the source image for every symbol — one vs two diamonds
is easy to misread. Do not list lift names, lodges, roads or signs.

Write your result as JSON to {{OUT_FILE}}:
{"lines":[{"id":123,"mapName":"NOSEDIVE","color":"blue","confidence":"high","tiles":["t102"],"note":""}],
 "labels":[{"mapName":"NOSEDIVE","symbol":"square","glade":false,"area":"mansfield","labelSrc":[3800,900],"note":""}]}
Then reply with a one-paragraph summary (counts, anything surprising).
