import json, sys
# usage: sel.py out.json id1 id2 ...
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))
ids = set(int(a) for a in sys.argv[2:])
json.dump({'polylines': [p for p in d['polylines'] if p['id'] in ids]}, open(sys.argv[1], 'w'))
