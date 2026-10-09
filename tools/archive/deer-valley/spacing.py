import json, subprocess, sys, re
W='/home/user/myskiruns/work/deer-valley'
V=json.load(open(W+'/vicomap/trails.json'))
names={re.sub(r'[^a-z0-9]','',re.sub(r'\s*\(.*?\)','',t['name']).lower()): re.sub(r'\s*\(.*?\)','',t['name']) for t in V['trails']}
for sp in sys.argv[1:]:
    subprocess.run(['python3','tools/trailmap/pdf_glyphs.py','labels',W+'/deervalley_2025-10.pdf','--glyphs',W+'/glyphs.json','--letters','tools/trailmap/resorts/deer-valley/letters.json','--out',W+'/t.json','--square','blue','--diamond','black','--circle','green','--turned','nu','--turned-hole','69','--join','13']+(['--space',sp] if sp!='-' else []),capture_output=True)
    L=json.load(open(W+'/t.json'))['labels']
    bad=[]; ok=0
    for l in L:
        k=re.sub(r'[^a-z0-9]','',l['text'].lower().replace('’',''))
        if k in names:
            want=names[k].replace("'",'’')
            if want.replace(' ','')==l['text'].replace(' ','') and want!=l['text']: bad.append((l['text'],want))
            else: ok+=1
    print(sp, ok, len(bad), bad[:40])
