import re, sys, subprocess, json
def get(u):
    return subprocess.run(['curl','-s','--max-time','40','-A','Mozilla/5.0',u],capture_output=True,text=True).stdout
for aid in sys.argv[1:]:
    s=open(f'a{aid}.html').read() if False else get(f'https://skimap.org/skiareas/view/{aid}')
    title=re.search(r'<title>([^<]*)',s).group(1)
    out=[]
    for m in re.finditer(r'<figure class="figure" id="ski-map-(\d+)".*?</figure>', s, re.S):
        blk=m.group(0)
        year=re.search(r'Published in (\d{4})',blk)
        kinds=re.findall(r'badge bg-secondary">([^<]*)',blk)
        if 'downhill' not in kinds: continue
        out.append((int(year.group(1)) if year else 0, m.group(1)))
    out.sort(reverse=True)
    print('==',aid,title, [y for y,_ in out[:6]])
    for y,mid in out[:2]:
        v=get(f'https://skimap.org/skimaps/view/{mid}')
        files=sorted(set(re.findall(r'https://files\.skimap\.org/[a-z0-9]+(?:\.[a-z]+)?', v)))
        dl=re.findall(r'href="([^"]*(?:download|original|\.pdf)[^"]*)"', v)
        meta=re.findall(r'(\d+\s*x\s*\d+|[\d.]+\s*MB|application/pdf|PDF|image/jpeg)', v)
        print('  ', y, mid, 'downloads:', dl[:4], 'meta:', sorted(set(meta))[:8])
