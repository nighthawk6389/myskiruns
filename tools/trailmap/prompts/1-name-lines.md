# Prompt 1 — name every detected line piece

Run one reader (Claude sub-agent) per group of 5–8 **neighbouring** tiles;
neighbours help readers follow lines across tile edges. For a ~4500 px wide
map, 37 tiles in 6 groups took ~25 min wall-clock in parallel.

Fill in `{{…}}` and send verbatim.

---

You are labeling a ski trail map ({{RESORT}}). Read-only task except for
writing ONE output file.

Tiles: {{TILE_PATHS}}
Each tile is a crop of the trail map at {{ZOOM}}x zoom. Detected lines are
drawn as thin MAGENTA overlays with magenta end dots, and each has a numeric
ID in a yellow box (a thin black leader line points from the box to the
line). The same ID can appear in several tiles (tiles overlap). Tile geometry
is in {{TILES_DIR}}/index.json (box = [x0,y0,x1,y1] in source pixels; tile
pixel (px,py) = source (x0+px/{{ZOOM}}, y0+py/{{ZOOM}})).

Map legend (verified): {{LEGEND}}

For EVERY numeric ID visible in your tiles decide what the underlying drawn
line is:
- the NAME of the trail it belongs to, as printed on the map (a line belongs
  to trail X if X's label is printed along it, OR it is the continuous
  continuation of a line that carries X's label with no junction/other label
  in between). Follow lines across tile edges using overlap.
- or "LIFT", "NOT_A_TRAIL" (roads, buildings, sign boxes, text, terrain), or
  "UNKNOWN".
If one ID covers two different trails (runs through a junction into another
named trail), say "SPLIT: A / B" and describe where it switches.
Give the drawn color you see and confidence high/medium/low. Be careful: a
label sitting BETWEEN two parallel lines belongs to the line it is aligned
with / closer to; check the text baseline. Labels are often printed inline:
the line stops at the label and continues after it, so the line leaving a
label's end belongs to that trail. Do not guess — use UNKNOWN when there's no
evidence.

Also list MISSED trails: any trail name label in your tiles whose line has NO
magenta overlay (or only partly), with the tile and approximate tile-pixel
coords of the label and of the undetected line.

Roster of trail names in the app's data (id | name | difficulty | area) is at
{{ROSTER_TXT}} — map names may differ slightly; report the name AS PRINTED ON
THE MAP, plus the best-matching roster id if one exists (else null).

Look at every tile carefully (use Read on each image; crop/zoom with
python3+PIL from {{SOURCE_IMAGE}}, the full-resolution source, if text is
small).

Write your result as JSON to {{OUT_FILE}} with shape:
{"lines":[{"id":123,"mapName":"CAPER","rosterId":"caper","color":"green","confidence":"high","tiles":["t101"],"note":""}],
 "missed":[{"mapName":"TRAIL CREEK","rosterId":null,"color":"green","tile":"t304","labelPx":[600,560],"linePx":[[560,420],[590,700]],"note":""}]}
Then reply with a one-paragraph summary (counts, anything surprising).

---

Killington's `{{LEGEND}}`: "trail difficulty = color of the drawn line
(green / blue / black; black diamond markers on black lines). Maroon lines
with black outline are LIFTS. Yellow dots = boundary. Magenta/pink wide bands
= highlight corridors (not a trail color). Orange pills = terrain-park
features. Red tree icon = glade. Trail names are black capital text on a
white halo, printed along/next to their own line, often rotated."
Write the legend for each new map from its printed legend and a look at a few
zoomed crops — earlier attempts failed by assuming colors (pink/yellow were
highlight bands and boundary dots, not difficulties).
