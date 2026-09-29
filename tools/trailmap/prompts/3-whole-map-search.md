# Prompt 3 — independent whole-map search for names

Use before removing roster trails that nobody could find. It is deliberately
a *different* method from prompts 1–2 (which split the map by area): each
reader gets ~8 names and scans the entire map at its own zoom, so a label
missed at a tile edge or by one reader gets a second, independent look. In
our run it confirmed 29 of 32 removals and recovered 3 trails printed as a
second, unprefixed label (HOME STRETCH → Lower Home Stretch, etc.).

Fill in `{{…}}` and send verbatim.

---

You are verifying a ski trail map of {{RESORT}}. Read-only, except for
writing ONE output file.

Source image: {{SOURCE_IMAGE}} (full resolution). Search the WHOLE map
systematically: cut it into a grid of overlapping crops (for example 700x500
source px with 100 px overlap), enlarge each crop 2x with python3 + PIL, and
look at every one. {{TEXT_STYLES}} Also check the legend and any inset or
corner text.

Your task: decide, for each of these names, whether it is printed anywhere
on this map:
{{NAMES}}

Count as found: the exact name or an obvious printed variant (a shortened
name; "UPPER"/"LOWER" prefixes may be omitted on the map if the base name is
printed on a clearly separate section that starts at its own difficulty
symbol). A lift name (e.g. "{{EXAMPLE_LIFT}}") is not a trail; neither is a
name printed for a building, lodge or area box.

For each name report: found yes/no; if yes, the text as printed, its
source-pixel position, the difficulty symbol next to it
(circle/square/diamond/double-diamond/none), whether a trail line runs along
it, and a crop you saved as evidence ({{EVIDENCE_DIR}}/<slug>.png). Be
careful and skeptical: a wrong "yes" is worse than a wrong "no", so zoom in to
confirm every candidate.

Also, while scanning, list every trail-name label you see that is NOT in
{{CURRENT_NAMES_TXT}} (the app's current trail list) and not in your names —
give text and source px. Ignore lift names, lodges and area boxes.

Write JSON to {{OUT_FILE}}:
{"names":[{"name":"Lower Canyon","found":false,"printed":null,"src":null,"symbol":null,"line":null,"evidence":null,"note":""}],"otherUnlisted":[{"text":"...","src":[x,y]}]}
Reply with a short summary.
