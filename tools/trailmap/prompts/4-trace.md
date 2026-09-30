# Prompt 4 — trace the hard trails

For the trails the first pass can't settle on its own: trails printed with
a name but no drawn line (short open-slope runs), traverses that cross many
other trails (Crossover), and trails that share pieces or change name mid-
line (Jake's Ride into Crossover). One reader per ~5 trails. Its output is
pre-filled on the review page (by: claude), so the reviewer only confirms.

Measured on Stowe, blind, against the reviewer's own drawings of 13 such
trails (`score_traces.py`): 8/13 matched within 25 px (short fall-line cuts,
freestyle lines, multi-piece runs). The misses: two traverses traced down
the fall line (an earlier version of this prompt said to default to the
fall line), one trail stopped early, and one Crossover / Jake's Ride
boundary read the other way. Treat traces as pre-fills for review
(`traces_to_reviews.py`), not as final.

Fill in `{{…}}` and send verbatim.

---

You are tracing ski trails on a trail map ({{RESORT}}). Read-only task
except for writing ONE output file.

Full-resolution map: {{SOURCE_IMAGE}} ({{W}}x{{H}} px). Crop and enlarge it
with python3 + PIL; draw on your crops to check your work. Numbered tiles
with the existing line pieces drawn in magenta: {{TILES_DIR}} (index.json
maps tiles to source px; tile px (px,py) = source (x0+px/{{ZOOM}},
y0+py/{{ZOOM}})). The pieces themselves: {{POLYLINES}} (points are PERCENT
of the image: source x = x*{{W}}/100, y = y*{{H}}/100) — draw any piece on a
crop to see exactly where it runs.

Legend: {{LEGEND}}

Trails to trace (name as printed | difficulty | label centre in source px |
what we know): {{TRAILS}}

For EACH trail, work out the whole run from where it starts to where it
ends, following the map:
- Use existing pieces wherever the trail's drawn line exists. A piece may
  belong to two trails (a traverse that continues as another named trail,
  or a shared stretch) — include it for both if so. List every piece the
  trail runs along, even partly; say which piece ends where if it only
  uses part of one.
- Where the trail has NO drawn line (it is printed as a name and symbol on
  an open slope or a cut between trees), trace it yourself as source-px
  points along the open snow the name labels, from its top to its bottom
  (or its start to its end for a traverse), ~every 30-60 px. Follow the
  open snow the label sits in: most runs go down the fall line, but short
  connectors and traverses printed across a slope run ACROSS it, joining
  the trails on either side — decide which from the shape of the opening,
  not from a default. Trace to where the trail visibly ends (a junction,
  a base area), not just past the label.
- Do not guess beyond what the map shows: if you cannot tell where it goes,
  say so and give only the part you can see.

Write JSON to {{OUT_FILE}}:
{"trails":[{"id":"bypass","pieces":[12,34],"partial":{"34":"only north of the Goat crossing"},
  "traced":[[x,y],[x,y]],"confidence":"high|medium|low","note":"how you decided"}]}
Then reply with a short summary.
