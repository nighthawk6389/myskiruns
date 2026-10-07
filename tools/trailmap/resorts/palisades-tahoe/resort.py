"""Palisades Tahoe's 2025-26 trail maps (palisadestahoe.com, its trail-maps page): three PDFs, each one vector page
over a painting: the Palisades side, and Alpine's front and back sides. Read by tools/trailmap/pdf_resort.py, panel
by panel (panels/<panel>/resort.py and decisions.py); prepare.py extracts them."""

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('palisades', 'Palisades'), ('alpine-front', 'Alpine front'), ('alpine-back', 'Alpine back')]
# the two mountains, each with its summit elevation as printed (Granite Chief Peak 9,006 ft; Ward Peak 8,637 ft)
AREAS = [('palisades', 'Palisades', 9006), ('alpine', 'Alpine', 8637)]
