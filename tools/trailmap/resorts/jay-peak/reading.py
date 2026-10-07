"""Jay Peak's labels as one synthetic reader result (seed_roster.py input), straight from the PDF text.

    python3 tools/trailmap/resorts/jay-peak/reading.py work/jay-peak/jay_label_spans.json work/jay-peak/reading_pdf.json

Reads labels.py's spans; writes {"labels": [...], "lines": []} in the readers' format (prompts/0-new-map.md),
every label "certain": no reader was needed. Decisions it holds (read off the PDF text and the rendered
labels, checks/sheet.py): the label-font spans that are not trails (NOT_TRAILS: lodge, hotel, first aid,
carpet and kids' centre names), the map's typo "Lower Lift Linee" read as Lower Lift Line, a label drawn
twice (halo and fill, within 40 px) kept once, glades = the names that say Glade or Woods, and Sis Boom Bah,
printed only in the Side View inset (left out of labels.py's spans), added at its inset label. Was the
scratch jay_reading.py (2026-09-30), unchanged but for its two paths.
"""
import json, math, re, sys
spans = json.load(open(sys.argv[1]))
NOT_TRAILS = {'& BASE LODGE', 'ADVENTURE', 'CENTER', 'CLIPS & REELS', 'FIRST AID', 'MOUNTAIN KIDS',
              'MOVING CARPET', 'RECREATION', 'STATESIDE HOTEL'}
FIX = {'LOWER LIFT LINEE': ('LOWER LIFT LINE', 'Lower Lift Line')}  # the map's typo
labels = []
for s in spans:
    n, printed = s['mapName'], s['printed']
    if n in NOT_TRAILS:
        continue
    n, printed = FIX.get(n, (n, printed))
    if any(l['mapName'] == n and math.dist(l['labelSrc'], s['labelSrc']) < 40 for l in labels):
        continue  # the same label drawn twice (halo + fill)
    labels.append({'mapName': n, 'printed': printed, 'symbol': s['symbol'], 'park': s['park'],
                   'glade': bool(re.search(r'GLADE|\bWOODS\b', n)), 'area': 'jay-peak',
                   'labelSrc': s['labelSrc'], 'confidence': 'certain'})
# only in the SIDE VIEW inset (PDF text 'Sis Boom' / ' Bah', diamond at 939-946,100-107)
labels.append({'mapName': 'SIS BOOM BAH', 'printed': 'Sis Boom Bah', 'symbol': 'diamond', 'park': False,
               'glade': False, 'area': 'jay-peak', 'labelSrc': [3776, 124], 'confidence': 'certain'})
json.dump({'labels': labels, 'lines': []}, open(sys.argv[2], 'w'), indent=1)
print(len(labels), 'labels,', len({l['mapName'] for l in labels}), 'names')
