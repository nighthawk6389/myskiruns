"""Whistler Blackcomb's 2025-26 trail map (whistlerblackcomb.com, the "Mountain Atlas" PDF): both mountains on
one vector page over a painting, and two insets on the other page that draw terrain the main map leaves out. Read
by tools/trailmap/pdf_resort.py, panel by panel (panels/<panel>/resort.py and decisions.py); prepare.py extracts
them."""

# the map panels, in the order the app's panel switcher shows them (src/resorts.ts names them the same)
PANELS = [('main', 'Both mountains'), ('symphony', 'Symphony'), ('glacier', 'Glacier')]  # (the app's panel tabs)
# the two mountains, each with its summit elevation as printed (Blackcomb Peak 2,440 m / 8,000 ft; Whistler's
# Peak Lookout 2,182 m / 7,160 ft)
AREAS = [('blackcomb', 'Blackcomb Mountain', 8000), ('whistler', 'Whistler Mountain', 7160)]
