import json
B = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/okemo/'
idx = json.load(open(B + 'tiles/index.json'))
MY = ['t005', 't105', 't205', 't305', 't405']
tiles_of = {}
for t in idx['tiles']:
    if t['tile'] in MY:
        for i in t['ids']:
            tiles_of.setdefault(i, []).append(t['tile'])
polys = {p['id']: p['cls'] for p in json.load(open(B + 'linePolylines_v1.json'))['polylines']}

H, M, L = 'high', 'medium', 'low'
lines = [
    # Jackson Gore summit / Quantum Six terrain
    (222, 'SUNSET STRIP', H, 'from the summit down-left to the end of the SUNSET STRIP label; continues west of it as 223'),
    (221, 'TUCKERED OUT', H, 'from the summit east to the first ■TUCKERED OUT label (label ~3977,756); continues after it as 220'),
    (218, 'BIG BANG', H, 'branches off Tuckered Out below the summit, ends at the ◆◆ of BIG BANG'),
    (217, 'BIG BANG', H, 'continues after the BIG BANG label, merges into Eclipse (215) at ~3990,1160'),
    (23, 'BLACK HOLE', H, 'thin line inside the dark-grey BLACK HOLE glade band, above its label'),
    (22, 'BLACK HOLE', H, 'inside the BLACK HOLE glade band, below its label/◆◆/glade icon'),
    (212, 'VORTEX', H, 'from the summit down to the ◆ of VORTEX'),
    (211, 'VORTEX', H, 'continues after the VORTEX label, crosses the Quantum Six lift and Quantum Leap (214), ends ~3707,1008'),
    (214, 'QUANTUM LEAP', H, 'black line along the Quantum Six lift line from the summit to the ◆ of QUANTUM LEAP (~3786,1252); crosses Vortex (211) and the lift, no other label along it'),
    (213, 'QUANTUM LEAP', H, 'continues after the QUANTUM LEAP label beside the lift down to the Quantum Six bottom terminal'),
    (216, 'ECLIPSE', H, 'short piece from the foot of the Black Hole band to the ◆ of ECLIPSE (inline label; 215 continues after it)'),
    (215, 'ECLIPSE', H, 'continues after the ECLIPSE label down the east side to the slow zone ~4047,1558; Big Bang (217) merges in at ~3990,1160, no other label below'),
    (195, 'UPPER LIMELIGHT', H, 'from Sunset Strip below the summit down to the end of the UPPER LIMELIGHT label'),
    (194, 'UPPER LIMELIGHT', H, 'continues after the ◆ of UPPER LIMELIGHT to the Blue Moon / Lower Limelight junction ~3270,1025'),
    (191, 'LOWER LIMELIGHT', H, 'from the Upper Limelight / Blue Moon junction to the ■ of LOWER LIMELIGHT'),
    (190, 'LOWER LIMELIGHT', H, 'continues after the LOWER LIMELIGHT label down to the slow zone at the Quantum Six bottom terminal'),
    (197, 'WHITE LIGHTNING', H, 'branches off Upper Limelight just above its label, ends at the ◆ of WHITE LIGHTNING'),
    (196, 'WHITE LIGHTNING', H, 'continues after the WHITE LIGHTNING label, ends ~3704,1187'),
    (199, 'ROLLING THUNDER', H, 'branches off White Lightning (197), ends at the ◆◆ of ROLLING THUNDER'),
    (198, 'ROLLING THUNDER', H, 'continues after the ROLLING THUNDER label, ends ~3787,1461'),
    (25, 'SUPERNOVA', H, 'thin line inside the left arm of the dark-grey SUPERNOVA glade band (V-shaped band), down to its label'),
    (28, 'SUPERNOVA', H, 'thin line inside the right arm of the same V-shaped SUPERNOVA glade band; starts by White Lightning, joins 25 at ~3352,1090; the band has no other label'),
    (24, 'SUPERNOVA', H, 'inside the SUPERNOVA glade band below its label/◆◆/glade icon, down to ~3813,1614'),
    # Coleman Brook / Jackson Gore base
    (174, 'EXPRESSO', H, 'from the Quantum Six bottom-terminal slow zone to the ● of EXPRESSO; 173 continues after the label'),
    (168, 'FAST TRACK', H, 'from the Quantum Six bottom-terminal slow zone down to the ● of FAST TRACK (~4019,1877); Spur Line (171) joins at ~4005,1785'),
    (171, 'SPUR LINE', H, 'from the ● of SPUR LINE (label beside the Coleman Brook lift, x>4019) down to Fast Track (168)'),
    (169, 'INN BOUND', L, 'AMBIGUOUS: sits between the end of the FAST TRACK label (~4063,1965) and the end of the INN BOUND label (~4014,2013) with no junction; 168-169-170 were drawn as one PDF path. Could equally be FAST TRACK (its continuation after the label); chose INN BOUND because the yellow slow zone that carries the INN BOUND label starts exactly at the FAST TRACK label end'),
    (170, 'INN BOUND', H, 'from the ● of INN BOUND down to the Jackson Gore base by the Coleman Brook lift bottom'),
    (167, 'SOUTHERN CROSSING', H, 'short piece from the Moonshadow crossing to the ● of SOUTHERN CROSSING (Jack-a-Lope ends at that crossing)'),
    (166, 'SOUTHERN CROSSING', H, 'continues after the SOUTHERN CROSSING label past the coaster to the Jackson Gore base (~3839,2100)'),
    # Solitude side (okemo-mountain)
    (165, 'JACK-A-LOPE', H, 'from the Solitude base (junction with 163/189) to the ● of JACK-A-LOPE'),
    (164, 'JACK-A-LOPE', H, 'continues after the JACK-A-LOPE label to the crossing with Upper/Lower Moonshadow'),
    (183, 'UPPER MOONSHADOW', H, 'continues 182 (from Sidewinder) past the Rising Star branch, gap at a road, then 185 to the ■ of UPPER MOONSHADOW; no other label'),
    (185, 'UPPER MOONSHADOW', H, 'short piece ending at the ■ of UPPER MOONSHADOW'),
    (186, 'UPPER MOONSHADOW', H, 'continues after the UPPER MOONSHADOW label down to the Jack-a-Lope / Southern Crossing crossing'),
    (187, 'LOWER MOONSHADOW', H, 'short piece from that crossing to the top end of the LOWER MOONSHADOW label'),
    (184, 'LOWER MOONSHADOW', H, 'continues below the ■ of LOWER MOONSHADOW into the slow zone at the Morning Star Triple bottom'),
    (189, 'LINE DRIVE', H, 'from Jack-a-Lope at the Solitude base, beside Morning Star Triple, to the ■ of LINE DRIVE'),
    (188, 'LINE DRIVE', H, 'continues after the LINE DRIVE label into the slow zone at the Morning Star Triple bottom'),
    (178, 'RISING STAR', H, 'short piece from the Upper Moonshadow junction (182/183) to the top end of the RISING STAR label'),
    (175, 'PROMENADE', H, 'continues after the PROMENADE label (label west of the tile edge, ● ~3161,1627) to the Morning Star Triple / 163 junction'),
    (161, 'DAYBREAK', H, 'continues after the DAYBREAK label (west of the tile, ~3055,1880) to the Morning Star Triple bottom terminal slow zone'),
]
out_lines = []
seen = set()
for pid, name, conf, note in lines:
    assert pid not in seen, pid
    seen.add(pid)
    out_lines.append({'id': pid, 'mapName': name, 'color': polys[pid], 'confidence': conf,
                      'tiles': sorted(tiles_of.get(pid, [])), 'note': note})
missing = set(tiles_of) - seen
extra = seen - set(tiles_of)
assert not missing, missing
assert not extra, extra

JG, OM = 'jackson-gore', 'okemo-mountain'
labels = [
    ('SUNSET STRIP', 'circle', False, JG, [3305, 736], 'line 222 above / 223 below the label'),
    ('TUCKERED OUT', 'square', False, JG, [3977, 756], 'upper of two TUCKERED OUT labels; the second (■ ~4144,1244) is east of these tiles'),
    ('BIG BANG', 'double-diamond', False, JG, [3799, 791], 'two diamonds confirmed on a 7x crop and in the PDF vector fills'),
    ('BLACK HOLE', 'double-diamond', True, JG, [3705, 835], 'glade: dark-grey band + orange-brown tree icon; ◆◆ printed under the name (7x crop + PDF fills)'),
    ('VORTEX', 'diamond', False, JG, [3547, 835], 'single diamond (7x crop + PDF fills)'),
    ('UPPER LIMELIGHT', 'diamond', False, JG, [3350, 903], 'single diamond (7x crop + PDF fills)'),
    ('WHITE LIGHTNING', 'diamond', False, JG, [3565, 1094], 'single diamond (7x crop + PDF fills)'),
    ('ECLIPSE', 'diamond', False, JG, [3859, 1117], 'single diamond (7x crop + PDF fills)'),
    ('ROLLING THUNDER', 'double-diamond', False, JG, [3550, 1214], 'two diamonds (7x crop + PDF fills)'),
    ('SUPERNOVA', 'double-diamond', True, JG, [3474, 1256], 'glade: dark-grey V-shaped band + tree icon; ◆◆ printed under the name (7x crop + PDF fills)'),
    ('QUANTUM LEAP', 'diamond', False, JG, [3808, 1309], 'single diamond (7x crop + PDF fills); label runs beside the QUANTUM SIX lift label'),
    ('LOWER LIMELIGHT', 'square', False, JG, [3412, 1305], ''),
    ('EXPRESSO', 'circle', False, JG, [4011, 1652], 'spelled EXPRESSO; label straddles the east tile edge'),
    ('FAST TRACK', 'circle', False, JG, [4041, 1921], 'only the ● is at the east edge of t305/t405 (x~4019); text lies east of these tiles'),
    ('INN BOUND', 'circle', False, JG, [3976, 2037], ''),
    ('BRIGHT STAR BASIN', 'circle', False, JG, [4005, 2134], 'beginner area by carpets 6/7 at the Jackson Gore base; no drawn trail line'),
    ('TREE TAP', 'none-visible', False, JG, [3957, 2088], 'terrain park: orange name with an orange pill; no drawn line (no freestyle piece)'),
    ('SOUTHERN CROSSING', 'circle', False, JG, [3596, 1859], ''),
    ('JACK-A-LOPE', 'circle', False, OM, [3331, 1784], ''),
    ('UPPER MOONSHADOW', 'square', False, OM, [3423, 1612], ''),
    ('LOWER MOONSHADOW', 'square', False, OM, [3441, 1934], ''),
    ('LINE DRIVE', 'square', False, OM, [3348, 1980], ''),
    ('RISING STAR', 'circle', False, OM, [3262, 1513], 'label on the west edge of t205/t305'),
]
out_labels = [{'mapName': n, 'symbol': s, 'glade': g, 'area': a, 'labelSrc': p, 'note': note}
              for n, s, g, a, p, note in labels]
json.dump({'lines': out_lines, 'labels': out_labels}, open(B + 'tiles/result_4.json', 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(len(out_lines), 'lines', Counter(l['confidence'] for l in out_lines), len(out_labels), 'labels')
print(Counter(l['symbol'] for l in out_labels))
