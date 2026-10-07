import re, html, sys, subprocess
aid = sys.argv[1]
s = subprocess.run(['curl', '-sS', '-L', '-m', '60', f'https://skimap.org/skiareas/view/{aid}'], capture_output=True, text=True).stdout
n = 0
for m in re.finditer(r'<figure class="figure" id="ski-map-(\d+)".*?</figure>', s, re.S):
    f = m.group(0)
    cap = re.search(r'<figcaption.*?</figcaption>', f, re.S).group(0)
    txt = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', cap)).split())
    print(m.group(1), txt[:160])
    n += 1
    if n >= int(sys.argv[2] if len(sys.argv) > 2 else 6):
        break
