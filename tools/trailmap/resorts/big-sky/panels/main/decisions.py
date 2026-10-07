"""Naming decisions for the main panel, settled on crops, keyed by points in map px
(work/big-sky/main/map.png), so they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on under another line: cut it nearest the
         second and drop the part beyond
"""
CHECKED = [
    # bs/sym/main/off_0.png, bs/c_mred.png (tools/trailmap/symbol_audit.py): Mr. Ed's line starts at its circle, 18 px
    # above where Mr. K's stroke ends (see CUTS)
    ((1981, 1464), 'Mr. Ed'),
    # bs/c_mr2.png, bs/osm_mr_21.png, bs/c_woa.png, bs/osm_woa_30.png (OpenStreetMap's runs): Swift Bear's line from
    # Middle River's circle east to its own circle (OpenStreetMap's Swift Bear leaves Middle River); White Otter
    # Access's line on along its name to the White Otter lift's foot (see CUTS)
    ((2320, 1996), 'Swift Bear'),
    ((2200, 1625), 'White Otter Access'),
    # bs/aud/main (the per-trail audit sheets), bs/c_lm.png, bs/c_lmp.png, bs/c_amb3.png (OpenStreetMap's runs): Lobo Meadows' line from its double square on down past where Chuck's Run leaves to Lobo (OpenStreetMap's Lobo Meadows; it was taken for Chuck's Run's continuation)
    ((2225, 949), 'Lobo Meadows'),
    # bs/mu6-mu12.png, bs/c164b.png, bs/c170c.png, bs/c178p.png, bs/c100.png, bs/c51p.png, bs/c49.png, bs/c121.png, bs/c149.png, bs/c_gul2.png, bs/c3f.png, bs/c_pbj2.png, bs/c300.png, bs/c303.png, bs/osm_m6_*.png, bs/osm_m8_67.png (OpenStreetMap's runs): Chuckles' line on west of its double square and down to K1 Return (OpenStreetMap's Chuckles); Lost Frontier's line from its name's end down past its diamond to Powder River; White Wing's wide line up past where Blue Moon leaves it to the top; Blue Moon's line on below its name to SA Road; Pine Marten's line from Trapline's fork to where they meet again; Cron's line along its name; the Gullies Traverse from the tram's top to its double diamond above The Gullies (named on the insets); The Gullies' six numbered chutes; Trident's middle prong; PB & J Way's blue upper part through its double square; the pink top of Outlook Way from Take a Bough's end; Cabin Access's line on past its name to the Montage
    ((538, 1109), 'Chuckles'),
    ((2905, 1417), 'LOST FRONTIER'),
    ((2691, 977), 'White Wing'),
    ((2702, 1464), 'Blue Moon'),
    ((3834, 1503), 'Pine Marten'),
    ((3313, 677), "Cron's"),
    ((3255, 553), 'GULLIES TRAVERSE'),
    ((3202, 655), 'The Gullies'),
    ((3210, 605), 'The Gullies'),
    ((3189, 593), 'The Gullies'),
    ((3168, 600), 'The Gullies'),
    ((3134, 605), 'The Gullies'),
    ((3217, 672), 'The Gullies'),
    ((3549, 693), 'Trident'),
    ((4491, 1454), 'PB & J Way (Upper)'),
    ((280, 1190), 'Outlook Way'),
    ((166, 1125), 'Cabin Access'),
    # bs/mu1-mu4.png, bs/m_sp2.png, bs/m_cas2.png, bs/m_wo.png, bs/m_ybr.png (OpenStreetMap's runs, the PDF's drawing order): Plenty Coup's line from the east to the Cascade lift's top and on into its own (OpenStreetMap's Plenty Coup); Chief Gull's loop through its circle; White Otter Access's line through its circle and name; the lines beside the Tweener and Homer pomas and the Pull-up tow (the report's Tweener Poma Line, Homer Poma Line and Pull Up Tow Line); Wolf's line on below the road (drawn right before Wolf's); Natawista's, Diamond Hitch's and Twin Tunnels' lines on below their names to the Pony Express base; Gator Way's line through its name; Mr. K's line down to Mr. Ed's circle (OpenStreetMap's Mr. K); Sacajawea's line from the Andesite summit down to its name (OpenStreetMap's Sacajawea)
    ((2315, 1881), 'Plenty Coup'),
    ((2425, 1716), 'Chief Gull'),
    ((2329, 1589), 'White Otter Access'),
    ((312, 893), 'Tweener Poma Line'),
    ((549, 980), 'Wolf'),
    ((2899, 1711), 'Natawista'),
    ((2586, 1602), 'Diamond Hitch'),
    ((2515, 1620), 'Twin Tunnels'),
    ((378, 1008), 'Gator Way'),
    ((2040, 1435), 'Mr. K'),
    ((1285, 914), 'Sacajawea'),
    ((104, 921), 'Homer Poma Line'),
    ((455, 903), 'Pull Up Tow Line'),
]
UNNAMED = [
    # bs/c_mr2.png, bs/c_woa.png (see CUTS)
    ((2420, 1970), "a pink access line from Swift Bear's circle up to the houses, with no name"),
    ((2268, 1500), 'a pink link from Lone Wolf down across Bozeman Trail to White Otter Access, with no name'),
    # bs/aud/main (the per-trail audit sheets), bs/c_lm.png, bs/c_lmp.png, bs/c_amb3.png (OpenStreetMap's runs): Lobo Meadows' line from its double square on down past where Chuck's Run leaves to Lobo (OpenStreetMap's Lobo Meadows; it was taken for Chuck's Run's continuation)
    ((1519, 1238), "a blue link from where Ambush Meadows ends (and Ambush Glades starts) to Ambush's line at its double square, with no name"),
    # bs/mu6-mu12.png, bs/c164b.png, bs/c170c.png, bs/c178p.png, bs/c100.png, bs/c51p.png, bs/c49.png, bs/c121.png, bs/c149.png, bs/c_gul2.png, bs/c3f.png, bs/c_pbj2.png, bs/c300.png, bs/c303.png, bs/osm_m6_*.png, bs/osm_m8_67.png (OpenStreetMap's runs): Chuckles' line on west of its double square and down to K1 Return (OpenStreetMap's Chuckles); Lost Frontier's line from its name's end down past its diamond to Powder River; White Wing's wide line up past where Blue Moon leaves it to the top; Blue Moon's line on below its name to SA Road; Pine Marten's line from Trapline's fork to where they meet again; Cron's line along its name; the Gullies Traverse from the tram's top to its double diamond above The Gullies (named on the insets); The Gullies' six numbered chutes; Trident's middle prong; PB & J Way's blue upper part through its double square; the pink top of Outlook Way from Take a Bough's end; Cabin Access's line on past its name to the Montage
    ((1314, 1426), 'a blue link from War Dance west to Elk Park Ridge, with no name or symbol'),
    ((1714, 1396), "a blue link from Tippy's Tumble's double square east across the Ramcharger lift to Ambush, with no name"),
    ((2604, 1099), 'a green link from White Wing east across Magic Meadows to Blue Moon, with no name'),
    ((2034, 1581), "the thin green line from the Explorer gondola's foot on through a circle printed with no name to White Wing"),
    ((2400, 1310), "a thin green link from Secret Meadow down past Wolf Pup Park's features to Lone Wolf, with no name"),
    ((3854, 2089), "a green run-out along the Madison base from Cinnabar's line to the lifts, with no name"),
    ((1376, 1082), "a blue link from the first aid at the Thunder Wolf lift's top down past Mad Wolf's start to Silverknife, with no name"),
    ((4004, 1073), "a blue loop off Horseshoe down to Old Faithful's top and back, with no name"),
    ((1207, 1066), "a short blue cut-off between Ponderosa and Bighorn (OpenStreetMap's Big Horn Cut-Off, not on the map or the trail report)"),
    ((3220, 827), 'a black traverse between the tops of Jack Creek and Rock Creek under their triple diamonds, with no name'),
    ((2976, 880), "a black traverse from the Headwaters lift's top east to Alder Gulch and Cold Spring, with no name"),
    # bs/mu1-mu4.png, bs/m_bb0.png, bs/m_cas2.png, bs/m_60.png, bs/m_lw0.png, bs/m_sp2.png
    ((1500, 1584), "a blue run-out from where Colter's Hell meets Mine Shaft east to the Mountain Village (Bear Back Line leaves it along the Bear Back lift), with no name; its square is the only mark on it"),
    ((479, 989), "a 14 pt bit of pink access line below the road at the Pull-up tow's foot, with no name"),
    ((2178, 1873), "a pink link from the White Otter lift's foot to the Cascade lift's top, with no name"),
    ((2118, 1840), "a pink link from the White Otter lift's foot to the Cascade lift's top, with no name"),
    ((2131, 1706), "a pink line beside the White Otter lift from its top to its foot (OpenStreetMap's White Otter, not on the trail report), with no name on the map"),
    ((3075, 1420), "a blue link from Powder River's line across the road down to Cinnabar's, with no name"),
    ((3058, 1397), "a blue link from Powder River's line across the road down to Cinnabar's, with no name"),
    ((1946, 1648), 'a pink stub at the Mountain Village first-aid station, with no name'),
    ((2091, 1474), "a thin green line from the Explorer gondola's foot down beside Chet's Knob to a circle printed with no name"),
    ((2048, 1513), "a thin green line from the Explorer gondola's foot down beside Chet's Knob to a circle printed with no name"),
    ((1331, 835), "the arrow from the label EVERETT'S 8,800 to the lodge"),
    ((359, 927), "part of the Spanish Peaks Mountain Club's logo"),
]
CUTS = [
    # bs/c127a.png, bs/c127c.png, bs/c239.png, bs/c38a.png, bs/c214.png, bs/c214c.png, bs/c296.png, bs/osm_m7_*.png,
    # bs/topo_*.png (OpenStreetMap's runs and how they meet), bs/c69b.png, bs/c104.png: one line carrying two runs,
    # cut where the second starts:
    # Stillwater Traverse down to the Lone Tree lift's foot, where Meriwether (and Lone Creek Gully) starts
    ((3305, 1053), (3368, 1196)),
    # Rips down to where Great Falls' line joins it, then Great Falls Gully past its diamond (Oxbow leaves there)
    ((3916, 871), (3842, 833)),
    # Lazy Jack from the first aid down to where both Powder Rivers and Bearcat Gully join it, Cinnabar on to the
    # Madison base (OpenStreetMap's Lazy Jack ends at Powder River, its Cinnabar starts there)
    ((3202, 1515), (3025, 1257)),
    # Trapline from its diamond down its left branch to where Pine Marten's line (the right branch) meets it: Lower
    # Trapline goes on to the left there, Pine Marten down past its name (OpenStreetMap's runs)
    ((4109, 1842), (3860, 1573)),
    # Colter's Hell down to its bend, where the blue run-out leaves and Mine Shaft's diamond is
    ((1427, 1477), (1437, 1558)),
    # Alpine Meadows down its name and round the bend to where Stacey's Way meets it, Hideaway on east past its name
    ((2745, 1679), (2842, 1768)),
    # K1 Return west to where Take a Bough's line crosses it (and its circle is), Clubhouse Loop on round the
    # clubhouse (OpenStreetMap's K1 Return ends at Take a Bough, its Clubhouse Loop starts there)
    ((689, 1118), (390, 1118)),
    # Calamity Jane's upper label and its lower one: the lower part from the lower one's double square, where Huntley
    # Hollow leaves
    ((2303, 1022), (2186, 1132)),
    # a pink line from Middle River's circle east past Swift Bear's circle up to the houses: Swift Bear's start, then
    # an access line; a pink line from Lone Wolf down across Bozeman Trail to White Otter Access's line and on along
    # its name: a link, then White Otter Access
    ((2405, 1978), (2361, 1992)),
    ((2268, 1500), (2247, 1599)),
    # Mr. K's stroke runs on past Mr. Ed's circle to its name: Mr. Ed from the circle
    ((2040, 1440), (1989, 1459)),
]
TRIMS = [
    # bs/c_sac4.png, bs/c_lw4.png (bs/overlaps.py: lines lying along another): Sacajawea's thin line runs from the
    # Everett's first aid under Yellow Brick Road's wide one before leaving it along its name; Lone Wolf's thin line
    # runs its last stretch inside White Wing's wide one
    ((1100, 975), (1239, 937)),
    ((2260, 1405), (2447, 1336)),
]
TRACED = [
]
