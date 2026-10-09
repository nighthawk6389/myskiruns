"""Summarise a vicomap SVG: element ids by kind, stroke colours and widths of fill:none paths, inside/outside groups."""
import collections, re, sys
import xml.etree.ElementTree as ET
ns = '{http://www.w3.org/2000/svg}'
root = ET.parse(sys.argv[1]).getroot()
def style(el):
    return dict(kv.split(':', 1) for kv in el.get('style', '').split(';') if ':' in kv)
parent = {c: p for p in root.iter() for c in p}
def group_of(el):
    while el in parent:
        el = parent[el]
        gid = el.get('id', '')
        if '-' in gid or gid in ('map',):
            return gid
    return ''
strokes = collections.Counter()
kinds = collections.Counter()
for el in root.iter():
    tag = el.tag.replace(ns, '')
    gid = el.get('id', '')
    if gid:
        kinds[(tag, gid.partition('-')[0])] += 1
    if tag == 'path':
        st = style(el)
        if st.get('fill') == 'none' and 'stroke' in st:
            g = group_of(el)
            strokes[(st['stroke'], st.get('stroke-width'), g.partition('-')[0] if g else '-', bool(st.get('stroke-dasharray')))] += 1
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])[:40]:
    print('id', k, v)
for k, v in sorted(strokes.items(), key=lambda kv: -kv[1])[:60]:
    print('stroke', k, v)
