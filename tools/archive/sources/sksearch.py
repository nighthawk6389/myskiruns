import re, html, sys, subprocess
q = sys.argv[1]
s = subprocess.run(['curl', '-sS', '-L', '-m', '60', f'https://skimap.org/search/results?query={q}'], capture_output=True, text=True).stdout
for m in re.finditer(r'href="/skiareas/view/(\d+)">\s*<div class="fw-bold">([^<]*)</div>\s*<small>\s*([^<]*)</small>.*?(\d+) ski maps?', s, re.S):
    print(m.group(1), html.unescape(m.group(2)).strip(), '|', m.group(3).strip(), '|', m.group(4), 'maps')
