"""What Crystal Mountain's Northway inset prints, read on zoomed grid crops of it (2x the published image:
work/crystal-mountain/northway/map.png, in its px) and on a mask of its black ink (every run's line is a black stroke
there, whatever its rating). The trail-maps page shows it beside the trail map ("See NORTHWAY inset for detail"):
the Northway lift's terrain, from the Otto Bahn traverse and Jeremy's Road on the ridge down to the Northway base.
prepare.py routes each line along the painted one and pdf_resort.py builds the trail list from these.

READING[panel]: (NAME as printed, (x, y) the label's middle, symbol, [line, ...]) per printed name. symbol: the one
printed by the name. A line is points along the run's own drawn line, in order (prepare.py routes between them along
the black ink); a name with no line (a bowl, a face, cliffs) has none and becomes a marker at its label.
"""

READING = {
    'northway': [
        # the ridge: the Otto Bahn from Jeremy's Road's foot west along the gates, then down round its loop (below
        # Spook Hill) to the diamond where Lower Otto Bahn and Paradise meet; Jeremy's Road from Northway Peak to it
        ('OTTO BAHN', (660, 570), 'diamond', [[
            (810, 556), (760, 566), (620, 590), (500, 606), (400, 610), (330, 614), (335, 680), (355, 750), (400, 810),
            (450, 855), (490, 862), (525, 825), (560, 815), (600, 848), (628, 874)]]),
        ("JEREMY'S ROAD", (940, 450), 'square', [[(1160, 400), (1040, 456), (960, 498), (880, 530), (820, 552)]]),
        ('PARADISE', (720, 780), 'diamond', [[(842, 560), (832, 640), (800, 690), (760, 740), (700, 785), (650, 830),
                                             (628, 872)]]),
        # Lower Otto Bahn from that diamond down past the Northway lift to the base
        ('LOWER OTTO BAHN', (735, 960), 'diamond', [[
            (628, 878), (740, 940), (840, 995), (870, 1030), (880, 1090), (862, 1160), (880, 1220), (940, 1280),
            (1040, 1340), (1100, 1400), (1200, 1480), (1300, 1600), (1356, 1730)]]),
        # from the ridge east of the lift: Upper Northway down to Northway's diamond, Northway on to the base
        ('UPPER NORTHWAY', (1350, 620), 'diamond', [[
            (1486, 450), (1445, 548), (1360, 620), (1280, 690), (1200, 790), (1120, 870), (1050, 940), (990, 1000),
            (990, 1060), (1020, 1100), (1080, 1140), (1200, 1220), (1300, 1300), (1380, 1360), (1420, 1420),
            (1426, 1500)]]),
        ('NORTHWAY', (1400, 1600), 'diamond', [[(1424, 1520), (1420, 1600), (1400, 1680), (1370, 1780), (1300, 1830),
                                               (1200, 1850), (1120, 1865)]]),
        ('GLORY DAYS', (1540, 650), 'diamond', [[
            (1824, 420), (1720, 520), (1626, 606), (1520, 690), (1462, 760), (1430, 840), (1390, 892), (1348, 920),
            (1305, 960), (1254, 1000), (1180, 1050), (1066, 1110)]]),
        ('BRAND-X', (1890, 810), 'double-diamond', [[
            (1970, 710), (1936, 766), (1880, 840), (1760, 920), (1640, 1000), (1520, 1100), (1440, 1200), (1380, 1280),
            (1356, 1330)]]),
        ("WHIT'S END", (1070, 1510), 'diamond', [[(1072, 1450), (1076, 1600), (1080, 1750), (1080, 1840)]]),
        # west of the lift: I-5 from the main map's side to Lower Otto Bahn, Employee Housing off the ridge
        ('I-5', (725, 1275), 'diamond', [[(0, 1400), (200, 1380), (400, 1362), (600, 1356), (660, 1330), (690, 1270),
                                          (740, 1220), (800, 1160), (820, 1110)]]),
        ('EMPLOYEE HOUSING', (160, 800), 'double-diamond', [[(250, 722), (150, 800), (60, 880), (0, 940)]]),
        # printed with a symbol and no line: markers at their names
        ('SPOOK HILL', (405, 690), 'diamond', []),
        ('HORSESHOE CLIFFS', (595, 680), 'double-diamond', []),
        ('PARADISE BOWL', (930, 600), 'double-diamond', []),
        ("BRUCE'S BOWL", (1120, 495), 'double-diamond', []),
        ('PARADISE TREES', (840, 790), 'double-diamond', []),
        ('THE NOSE', (1015, 750), 'double-diamond', []),
        ('NORTHWAY BOWL', (1355, 480), 'double-diamond', []),
        ("PENNY DAWG'S", (1275, 850), 'double-diamond', []),
        ("PUCKER'S GULCH", (1540, 910), 'double-diamond', []),
        ('MORNING GLORY BOWL', (1950, 555), 'double-diamond', []),
        ('LOWER BRAND-X CLIFFS', (1780, 1175), 'double-diamond', []),
        ('NIAGRAS', (280, 985), 'double-diamond', []),
        ('O-MEADOWS', (425, 1185), 'double-diamond', []),
        ('13F', (850, 1835), 'diamond', []),
    ],
}
