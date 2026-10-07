"""Breckenridge pieces settled on zoomed crops (reg/*.jpg): piece id -> name as printed
(scratch: br_checked.py).

CHECKED names a piece where match.py found no name, several, or the wrong one; UNNAMED records the pieces that are
real lines the map prints no name for (connectors, catwalks, exits), with what each is: aggregate_readings.py hides
them (linePolylines.json's _unnamed). reading.py applies both. Ids are extract_pdf_vectors.py's piece ids for the
2025-26 PDF with regen.sh's flags (351 is the part split_pieces.py cut off 250); a new edition renumbers them.

The crops cited (in the work folder) are re-rendered by checks/crops.sh: reg/<name>_<k>.jpg by checks/zoom.py
(every piece tagged id:auto-name on the map image), f_*.png by checks/fine.py (chosen pieces numbered at both
ends), c_*.png by checks/crop.py (the PDF alone).
"""
CHECKED = {
    # Peak 10 west (reg/p10_0.jpg, c_p10.png)
    80: 'Mustang', 81: 'Mustang', 348: 'Mustang', 82: 'Dark Rider', 83: 'Dark Rider', 349: 'Dark Rider',
    84: 'Blackhawk', 85: 'Blackhawk', 86: 'Elan', 87: 'Elan', 89: 'Trinity', 88: 'Trinity', 91: 'Quiver', 90: 'Quiver',
    92: 'Flapjack', 93: 'Flapjack', 94: 'Flapjack', 95: 'Cimarron', 96: 'Cimarron', 97: 'Bronc', 98: 'Bronc',
    100: 'Doublejack', 99: 'Doublejack', 101: 'Centennial', 102: 'Centennial', 104: 'Crystal', 103: 'Crystal',
    105: 'Grits', 106: 'Grits',
    # Peak 10 east / Peak 9 top (reg/z_corsair_0.jpg, reg/z_sizzler_0.jpg)
    108: 'Spitfire', 107: 'Spitfire', 110: 'Corsair', 111: 'Corsair', 109: 'Corsair', 135: 'Sizzler', 134: 'Sizzler',
    131: 'Upper Lehman', 139: 'Cashier',
}
CHECKED.update({
    # Peak 6 chutes (reg/pb_0.jpg): each name's line above and below its text
    308: 'Epiphany', 307: 'Epiphany', 306: 'E.S.P', 305: 'E.S.P', 304: 'Contact', 303: 'Contact', 302: 'Savor', 301: 'Savor',
    300: 'Whiff', 299: 'Whiff', 296: 'Behold', 295: 'Behold', 298: 'Echo', 297: 'Echo', 318: 'Felicity', 319: 'Felicity',
    317: 'Rapture', 316: 'Rapture', 347: 'Yugen', 315: 'Yugen', 313: 'Sublime', 314: 'Sublime', 311: 'Irie', 312: 'Irie',
    309: 'Chi', 310: 'Chi', 294: 'Respite', 198: 'Bliss', 199: 'Bliss',
    # Peak 9 north chutes (reg/zz_chutes9_0.jpg, c_chutes9.png): line into the symbol, the name, line on past it
    11: 'Double Barrel', 346: 'Double Barrel', 19: 'Way Out', 20: 'Way Out', 66: 'Quandary', 65: 'Quandary',
    23: 'Too Much', 24: 'Too Much', 21: 'Solitude', 22: 'Solitude', 18: 'Lobo', 17: 'Lobo', 26: 'Hombre', 25: 'Hombre',
    12: 'Amen', 13: 'Amen', 27: 'No Name', 28: 'No Name', 14: 'Snowbirds', 15: 'Snowbirds',
    # Peak 8 north side (reg/pb_1.jpg)
    56: 'Wacky’s Chute', 55: 'Wacky’s Chute', 58: 'Zoot Chute', 57: 'Zoot Chute', 60: '9 Lives', 59: '9 Lives',
    61: 'Easy Street', 344: 'Alpine Alley', 343: 'Alpine Alley', 345: 'Alpine Alley',
})
CHECKED.update({
    # Peak 7/8 bowls (reg/pb_2.jpg)
    49: 'White Crown', 50: 'White Crown', 52: 'Forget-Me-Not', 48: 'Ptarmigan', 47: 'Ptarmigan', 46: 'Pika', 45: 'Pika',
    # Contest and Horseshoe Bowls (reg/pb_3.jpg)
    337: 'King', 336: 'King', 341: 'Queen', 340: 'Queen', 339: 'Joker', 338: 'Joker', 323: 'Stampede', 327: 'Mule',
    326: 'Mule', 325: 'Rustler', 324: 'Rustler', 322: 'Outlaw', 321: 'Outlaw', 329: 'Brill’s Thrill', 328: 'Brill’s Thrill',
    333: 'Eagle’s Nest', 332: 'Eagle’s Nest', 6: 'Psychopath', 8: 'Upper 4 O’Clock', 7: 'Upper 4 O’Clock', 10: 'Adios',
    63: 'Imperial Ridge',
})
CHECKED.update({
    # E-Chair runs (f_echair.png): labels are drawn in the line ("-symbol name-"); where a name sits beside a
    # line instead, the line belongs to the name it runs into (Hades and Purgatory have no line of their own)
    76: 'E Lift Line', 75: 'E Lift Line', 74: 'E Lift Line', 67: 'Tom’s Mom', 274: 'Tom’s Mom', 78: 'Tom’s Baby',
    77: 'Tom’s Baby', 73: 'Inferno', 72: 'Inferno', 69: 'Devil’s Crotch', 68: 'Devil’s Crotch', 71: 'Mine Shaft',
    70: 'Mine Shaft',
})
CHECKED.update({
    # Peak 6 (reg/pb_5.jpg, reg/pb_6.jpg): Intuition's dashed catwalk on to Barton Breezeway; Delirium's three upper
    # fingers; the stretch below Bliss's symbol is Bliss (Deja Vu's label has its own stub)
    189: 'Intuition', 207: 'Delirium', 208: 'Delirium', 209: 'Delirium', 199: 'Bliss',
})
CHECKED.update({
    # Peak 7 base (f_pb7.png): Claimjumper's upper part branches from Lower Forget-Me-Not and crosses Columbine
    257: 'Claimjumper',
})
CHECKED.update({
    # Peak 8 below the bowls (reg/pb_8.jpg, reg/pb_9.jpg): Little Johnny's two upper branches
    279: 'Little Johnny', 280: 'Little Johnny',
})
CHECKED.update({
    # Peak 9 middle (reg/pb_10.jpg, reg/pb_11.jpg, reg/z_p9mid_0.jpg): Lower Peerless is blue and starts at the
    # Peak 8 Transfer catwalk; Gold King continues to the C-Chair base; American runs on into its park
    123: 'Lower Peerless', 124: 'Lower Peerless', 125: 'Lower Peerless', 118: 'Gold King', 119: 'Gold King',
    128: 'American', 117: 'Peak 8 Transfer', 116: 'Peak 8 Transfer',
})
CHECKED.update({
    # Peak 6 base (reg/pb_12.jpg): Lost Horizon, from Horizon Hut down to the Zendo Chair base
    206: 'Lost Horizon', 205: 'Lost Horizon',
})
CHECKED.update({
    # Peak 8 SuperConnect (reg/pb_13.jpg): Sawmill runs on past its subtitle "Easiest Way to Peak 9" to the mid-load station
    43: 'Sawmill',
})
CHECKED.update({
    # Peak 9 base (f_p9base_a.png, f_p9base_b.png, reg/q_1.jpg): Frontier's upper part; A Chair Line and Eldorado run
    # on to King's Way; Silverthorne is the trunk along the
    # Quicksilver SuperChair; Lower Sundown starts below Sundown; Bonanza runs on across Lower American (c_cashier.png:
    # Cashier is complete without it: 139, label, 138, then green 137, label, 136)
    161: 'Frontier', 167: 'A Chair Line', 151: 'Eldorado', 3: 'Bonanza', 158: 'Silverthorne', 172: 'Lower Sundown',
})
CHECKED.update({
    # Peak 8 base (reg/q_3.jpg, f_p8base.png): Trygve's runs on past its label to the base
    247: 'Trygve’s',
})
CHECKED.update({
    # (f_wire.png, f_rdv.png, f_140.png): Wirepatch crosses the Peak 6 Parkway catwalk and runs on; Southern Cross
    # runs on under the Rendezvous label down to Tunnel; Country Boy's tail past the green line it crosses
    219: 'Wirepatch', 31: 'Southern Cross', 140: 'Country Boy',
})
CHECKED.update({
    # piece 250 cut where Lowest 4 O'Clock leaves it (split_pieces.py): Lower 4 O'Clock above, Gondola Ski Back below
    250: 'Lower 4 O’Clock', 351: 'Gondola Ski Back',
})
UNNAMED = {
    240: 'blue line from under the Vista Haus sign down the right branch of the easiest-route band to the top of Springmeier; no name printed (f_vista.png)',
    230: 'blue feeder from Claimjumper across to Fort Mary B below its label; no name printed',
    79: 'black dashed access path from the gate by Little Burn up toward Windows (a bowl drawn with no line)',
    235: 'green connector from the C-Chair base to the Snowflake lift mid-load station; no name printed',
    254: 'green connector from the Snowflake lift base to Lowest 4 O’Clock; no name printed',
    270: 'blue exit from the bottom of the Freeway Terrain Park to the FIVE SuperChair base (the park itself is an orange band)',
    0: 'green exit from the bottom of the Toyota Banked Slalom course to the FIVE SuperChair base',
    145: 'short green connector from the end of Lower American down toward Lower Sundown; no name printed',
    40: 'green dashed catwalk from beside the Peak 8 SuperConnect mid-load station toward Lower 4 O’Clock; no name printed',
    42: 'the solid green line it becomes, down to Lower 4 O’Clock',
    114: 'short blue connector from Gold King across to Volunteer where Shock begins; no name printed',
    231: 'blue connector from Pioneer down across the Columbine catwalk toward Claimjumper; no name printed',
    232: 'the same connector below the catwalk',
    350: 'black run-out below Cucumber Bowl, from the Columbine catwalk to the top of Duke’s Run; no name printed',
    44: 'black dashed catwalk between the two gates across the top of North Bowl; no name printed',
    342: 'black dashed catwalk along the foot of Contest and Horseshoe Bowls; no name printed',
    4: 'black dashed catwalk from the Peak 9 chutes gate toward the Imperial SuperChair base; no name printed',
}
