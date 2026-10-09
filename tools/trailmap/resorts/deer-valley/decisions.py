"""Naming decisions settled on crops, keyed by points in map px (work/deer-valley/map.png), so they survive a
re-extraction: pdf_resort.py finds the piece through each point. `pdf_resort.py deer-valley add` records new ones.

The crops: piece sheets (tools/trailmap/piece_sheet.py, each piece alone in magenta with the names around it, tagged
with the interactive map's trail covering it: `vicomap.py check`), the interactive map's own lines drawn over the
map (`vicomap.py show`), and zoomed grid crops (grid_crop.py). The interactive map (resorts-interactive.com map 1815)
draws this map's strokes again, grouped by trail name: where it names a piece, the crop was read for the name printed
along or at the end of that line.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
"""
CHECKED = [
    # Flagstaff (sheets s_0, s_1, v1.png: the interactive map's Bluebell, Lily, Silver Buck and Mountain Daisy over
    # the map): the blue line from the summit down the lift to Bluebell's first label; the line from Bluebell's square
    # on past Lower Lily's junction to the lift base (the interactive map's Bluebell; Lower Lily's line joins it);
    # the blue line from the Quincy Express base to Hidden Treasure's label (the green one beside it is Mountain
    # Daisy's), twice; Peeler's, Star Gazer's and Three Ply's lines from the Mountain Daisy junction down to their
    # symbols, Square Deal's from the lift base to its diamond
    ((3633, 659), 'Bluebell'),
    ((3941, 1209), 'Bluebell'),
    ((3546, 882), 'Hidden Treasure'),
    ((3461, 832), 'Hidden Treasure'),
    ((3577, 978), 'Peeler'),
    ((3678, 969), 'Star Gazer'),
    ((3467, 1031), 'Three Ply'),
    ((3500, 909), 'Square Deal'),
    # Empire Canyon and Lady Morgan (s_0-s_3, v2.png, v5.png): Magnet's line from its diamond up to the lift, and on
    # from its name's start to Lower Magnet's diamond; Lucky Jack's from its circle to the lift base; the line from
    # the Empire Canyon base east to Nugget's (the interactive map's Walker, which runs on down the slow road past
    # Walker's name); Pearl's from its name's start up to Solace's line, and the hairpin from there down to Webster's
    # name (the interactive map's Webster); Dakota's blue line from the lift to Pearl's; Custer's from the road to its
    # circle; Buckeye's, Conviction's, Domingo's and Orion's from their symbols to the lift and the summit
    ((4660, 952), 'Magnet'),
    ((4398, 1018), 'Magnet'),
    ((4099, 926), 'Lucky Jack'),
    ((4244, 929), 'Walker'),
    ((4512, 824), 'Pearl'),
    ((4435, 936), 'Webster'),
    ((4443, 841), 'Dakota'),
    ((4084, 1164), 'Custer'),
    ((4555, 707), 'Buckeye'),
    ((4968, 498), 'Conviction'),
    ((4920, 528), 'Domingo'),
    ((4965, 481), 'Orion'),
    # Silver Lake and Bald Eagle (s_2, s_5-s_8, v_sunrise.png, c6.png): Trainer's line by its name; Wizard's and
    # Ottobahn's from their squares down to the lift base; Sunrise's line from Silver Lake across the lifts to the
    # junction by Silver Link's square, the stub from there to the road, down across the Bald Eagle summit and on
    # past Rising Star's name (the interactive map's Sunrise, all of it; Silver Link's line leaves the junction down
    # along its own name); Rising Star's from the road to its name, Roamer's from Rising Star's square to its own, Big
    # Stick's from the road by Roamer's square to its own; Solid Muldoon's two lines (the blue one under the Bald Eagle
    # summit, the green one from the junction above Wide West down to its circle, then on to Little Stick's junction)
    ((3182, 1309), 'Trainer'),
    ((2714, 1220), 'Wizard'),
    ((3038, 1258), 'Ottobahn'),
    ((3131, 1357), 'Sunrise'),
    ((3029, 1403), 'Sunrise'),
    ((2804, 1465), 'Sunrise'),
    ((2733, 1530), 'Sunrise'),
    ((2756, 1542), 'Rising Star'),
    ((2796, 1599), 'Roamer'),
    ((2910, 1633), 'Big Stick'),
    ((3007, 1507), 'Solid Muldoon'),
    ((2911, 2250), 'Solid Muldoon'),
    ((2903, 2168), 'Solid Muldoon'),
    # Bald Eagle's lower slopes and Snow Park (s_2, s_3, s_7, s_10): Deer Hollow's long line from Gnat's Eye down to
    # the base; the stub between Success's name and Little Bell's; White Owl's black line past its two-line name;
    # Last Chance's from the road down to the boundary; Dew Drop's from under its name down to Last Chance's; Crescent's
    # and Cascade's from their symbols to the lift base and to Deer Hollow
    ((2658, 2416), 'Deer Hollow'),
    ((3104, 1638), 'Little Bell'),
    ((2984, 2040), 'White Owl'),
    ((3274, 1987), 'Last Chance'),
    ((3160, 2093), 'Dew Drop'),
    ((2144, 2853), 'Crescent'),
    ((2418, 2646), 'Cascade'),
    # Bald Mountain (s_3, s_4, s_8, s_9): Evergreen's, Ruins of Pompeii's, Tycoon's, Blue Ledge's and Grizzly's lines
    # from the summit to their symbols; Edgar's Alley's from Stein's Way's diamond down past Perseverance's line to
    # its square, and its link from Stein's Way lower down (the interactive map's Edgar's Alley, four pieces);
    # Perseverance's from its bowl to its square; Rattler's from its diamond to the lift base; Morning Star's,
    # Paradise's and Free Thinker's from their diamonds up to the Mayflower Bowl traverse; Finis's from its diamond
    # down to Tycoon's square
    ((2478, 856), 'Evergreen'),
    ((2537, 655), 'Ruins of Pompeii'),
    ((2548, 788), 'Tycoon'),
    ((2495, 634), 'Blue Ledge'),
    ((2502, 662), 'Grizzly'),
    ((2299, 745), "Edgar's Alley"),
    ((2336, 769), "Edgar's Alley"),
    ((2337, 700), "Edgar's Alley"),
    ((2164, 1040), "Edgar's Alley"),
    ((2373, 705), 'Perseverance'),
    ((2657, 1242), 'Rattler'),
    ((2160, 725), 'Morning Star'),
    ((1938, 971), 'Paradise'),
    ((2068, 941), 'Free Thinker'),
    ((2101, 1187), 'Finis'),
    # Park Peak, Big Dutch and Keetley (s_10-s_13, v3.png, v6.png): Spitfire's and Rebellion's lines down to their
    # diamonds; Nemesis's and Deep Enuf's from Redemption's line to theirs; Free Will's from its square to the lift,
    # Redemption's from its square round to the Reliance junction; Mountain Monarch's from Matchless's square to its
    # own (the interactive map's Mountain Monarch); Mayflower Link's from the Keetley base past its two-line name;
    # Lady of the Lake's long line from the Star junction down to its name (the auto-match gave it to Stein's Way,
    # whose name ends at its top); McHenry's from Sultan Connection's name to its own, and from its name to the East
    # Village base; Exchange's two stubs either side of its name
    ((1275, 1008), 'Spitfire'),
    ((955, 1019), 'Rebellion'),
    ((2041, 354), 'Nemesis'),
    ((2447, 274), 'Deep Enuf'),
    ((2697, 266), 'Free Will'),
    ((2672, 281), 'Redemption'),
    ((1404, 1038), 'Mountain Monarch'),
    ((1682, 1267), 'Mayflower Link'),
    ((1626, 1370), 'Lady of the Lake'),
    ((2267, 1477), 'McHenry'),
    ((859, 1906), 'McHenry'),
    ((1779, 654), 'Exchange'),
    ((1846, 598), 'Exchange'),
    # Jordanelle (s_7): its line from the gondola's base down to its first name, and from Mountaineer's down to its
    # third name's square
    ((1225, 2703), 'Jordanelle'),
    ((2254, 2304), 'Jordanelle'),
    # Pioche (v3.png): Minnow's line from the end of Viola's second name down the east side (the interactive map's
    # Minnow: Viola's own line runs under the lift to that name); Dispute's black stub from Niagara's line to its
    # diamond (1.68 pt)
    ((1657, 2054), 'Minnow'),
    ((1645, 2100), 'Dispute'),
    # the four strokes cut in two (CUTS below), a point on each part
    ((3285, 616), 'Trump'),
    ((3097, 855), 'Ontario'),
    ((2860, 1899), 'Champion'),
    ((2879, 1853), "Know You Don't"),
    ((3063, 479), 'Clipper'),
    ((3010, 585), 'Golden Age'),
    ((1152, 1703), 'Lady of the Lake'),
    ((1072, 1783), 'All Right'),
    ((1956, 619), 'Carbenite'),
    ((1666, 636), 'Persistance'),
]
UNNAMED = [
    # v1.png: a blue link from the Mountain Daisy junction down to where Lily and Silver Buck meet, no name printed
    # along it; the interactive map draws no trail on it
    ((3695, 992), 'a link between Mountain Daisy and Silver Buck: no name printed along it'),
    # v5.png: a blue line along the Empire Express, under its lift line, from Solace's line to the Empire Canyon base:
    # no name printed along it, and the interactive map draws no trail there
    ((4356, 847), 'the line along the Empire Express lift: no name printed along it'),
]
CUTS = [
    # s_0 (and `vicomap.py check --along`): one stroke from Trump's name down through the lift-base junction on to
    # Ontario's name: Trump's down to the junction, Ontario's from there
    ((3285, 616), (3222, 670)),
    # s_10: one stroke forks at Little Stick's junction into Champion's line (to its diamond) and Know You Don't's
    ((2860, 1899), (2866, 1826)),
    # s_11, v4.png: one stroke from Clipper's name along the boundary to the Pinyon Express base and back up to Golden
    # Age's name: Clipper's down to the base, Golden Age's from it
    ((3063, 479), (3181, 657)),
    # s_12: one stroke from Lady of the Lake's name down to All Right's: the first bend is Lady of the Lake's (its
    # line goes on west), the rest All Right's
    ((1152, 1703), (1129, 1727)),
    # v7.png, v7p.png, c7.png: one blue line from Carbenite's name down across the Green Monster loop (where it breaks)
    # and the lifts to the Exchange junction, and on to Persistance's name: the interactive map's Persistance starts at
    # the junction (its Carbenite (Lower), listed by the report, has no line in its SVG): Carbenite's down to there
    ((1956, 619), (1811, 661)),
]
TRACED = [
    # c10.png, v11.png: the November image draws Gilt Edge's line, a short green stub from Birdseye's line under the
    # Sterling Express to its name (the October PDF has none; the interactive map draws it): traced on the image
    ('Gilt Edge', [(2994, 1120), (3008, 1116), (3023, 1111)]),
]
