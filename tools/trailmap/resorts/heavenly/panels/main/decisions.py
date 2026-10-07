"""Naming decisions for the main panel, settled on crops, keyed by points in map px (work/heavenly/main/map.png), so
they survive a re-extraction: pdf_resort.py finds the piece through each point.

CHECKED  [((x, y), NAME)]: the piece through the point is that trail
UNNAMED  [((x, y), why)]: the piece through the point is not a trail (or not one this map names)
CUTS     [((x, y), (x, y))]: the piece through the first point carries two trails: cut it nearest the second
TRACED   [(NAME, [(x, y), ...])]: a stretch drawn along the map's own line where no piece runs
TRIMS    [((x, y), (x, y))]: the piece through the first point runs on under another line: cut it nearest the
         second and drop the part beyond

A line running on out of a label's end is that run's; an arrow ends a run's line where it leads into the next run
(Von Schmidt's upper line ends in an arrow at California Trail's square, Silver Spur's at Von Schmidt's). The crops
are in the session's scratch folder (hv/reg/...).
"""
CHECKED = [
    # hv/reg/top10.png: Skyline Trail's start, from the Sky Express top west to its label (an arrow into it)
    ((1965, 433), 'Skyline trail'),
    # hv/reg/hf_junc.png, hv/reg/H3_both.png: High Five's line forks above the Sky Deck, one branch to each lift's
    # foot (OpenStreetMap's High Five ends at the Canyon Express foot)
    ((2318, 1399), 'High Five'),
    # hv/reg/mombo.png: the two lines meeting at Mombo's square, from the slow zone and from above
    ((2644, 1325), 'Mombo'),
    # hv/reg/R8b.png: California Trail's end splits into two arrows into the Sky Deck; its line between its first two
    # labels, along the top of the Sand Dunes label (Sand Dunes is the arrow from its square down to Comet)
    ((2078, 1471), 'California Trail'),
    ((1458, 987), 'California Trail'),
    # hv/reg/comet_both.png: Comet's line from the Sand Dunes arrow down to its label
    ((1385, 1163), 'Comet'),
    # hv/reg/dip_both.png (OpenStreetMap: Big Dipper runs on past where the Dipper Returns leave it): Big Dipper's
    # line from its lower square down to Upper Dipper Return's, Lower Dipper Return's line leaving it; Nova's line
    # from Big Dipper's down to Nova's square (drawn with Orion's and Cosmic Wave's lines and their labels, the PDF's
    # drawing order)
    ((785, 1349), 'Big Dipper'),
    ((966, 1202), 'Nova'),
    # hv/reg/vs43.png, hv/reg/R6b.png (OpenStreetMap: Bonanza runs from Von Schmidt down to Comet): Bonanza's line from
    # Von Schmidt's lower square west past Silver Spur's label into Bonanza's, its stub on to Comet's line
    ((1388, 1525), 'Bonanza'),
    # hv/reg/nb.png (OpenStreetMap: Pepi's runs from the Stagecoach lift's top to the Comet lift's foot): Pepi's line
    # from the Stagecoach Express top to its square; Crossover's line below its lower square, forking to the North
    # Bowl Express top and down towards the Olympic Express
    ((946, 1735), "Pepi's"),
    ((1143, 1715), 'Crossover'),
    # hv/reg/tog_main.png, hv/reg/ss_arrow.png, hv/reg/tog_lines.png (the 2022 page's lines alone), hv/skimap/nav_vs.png
    # (an older edition's navigation map: Nevada to the Top of Gondola by Comet, then the Von Schmidt traverse),
    # hv/reg/osm_tog.png (OpenStreetMap's one-way runs: Von Schmidt from the Olympic Express top past Bonanza's start
    # and Easy Street's to California Trail; Olympic Downhill and Cloud 9 from the Olympic Express top; Silver Spur from
    # Easy Street's start to Bonanza): Von Schmidt's line from the lower label's square round the hairpin (its slow
    # zone, an arrow into the upper label's square), the lower label's west end being where Bonanza and Silver Spur
    # leave it; Silver Spur's line from Easy Street's circle (the top of the Big Easy lift) down to the lower label;
    # Olympic Downhill's line from the Olympic Express top (the lower label's east end) down towards its label (an older
    # edition prints the label at its end)
    ((1358, 1430), 'Von Schmidt'),
    ((1487, 1460), 'Silver Spur'),
    ((1543, 1505), 'Olympic Downhill'),
    ((1555, 1544), 'Olympic Downhill'),
    # hv/reg/gal.png: Comstock's line from its square (a dash, then solid) down to the Galaxy lift's foot, beside
    # Mineshaft's
    ((476, 2020), 'Comstock'),
]
UNNAMED = [
    # hv/reg/p15top.png, hv/reg/H3_both.png
    ((2459, 1306), "a blue line from below High Five's label, under the Canyon Express, down to the Sky Chute slow "
                   "zone, with no name (Double Down's line leaves it; OpenStreetMap's way here has no name either)"),
    # hv/reg/R8b.png
    ((2403, 1600), "a green arrow from the Sky Deck lodge into Maggie's slow zone, with no name"),
    ((2362, 1635), "a green arrow from the Sky Deck lodge into Maggie's slow zone, with no name"),
]
CUTS = []
TRACED = [
    # hv/reg/upb.png, hv/crops/cmpe_0x2.png: Upper Powderbowl's label, moved since the 2022 page up beside Ridge
    # Run's: the stretch along it on the 2024 image, from its square
    ('Powderbowl Upper', [(2473, 989), (2500, 1003), (2560, 1035), (2620, 1060), (2670, 1088)]),
    # hv/tr/pbr.png: Powderbowl Run's label, moved since the 2022 page under Lakeview Park: the stretch down along it on
    # the 2024 image, from its square
    ('Powderbowl Run', [(2733, 1240), (2738, 1270), (2742, 1310), (2746, 1350), (2750, 1385)]),
    # hv/tr/nbu.png: North Bowl Upper's name, printed on two lines down its cut from its square
    ('North Bowl Upper', [(1040, 1790), (1048, 1820), (1058, 1850), (1068, 1880), (1078, 1915)]),
]
TRIMS = []
