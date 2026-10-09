p='/home/user/myskiruns/tools/trailmap/vicomap.py'
s=open(p).read()
i=s.index('def check(a):'); j=s.index('def main():')
new='''def check(a):
    import numpy as np
    from scipy.spatial import cKDTree
    import pdf_resort as pr
    R = pr.Resort(a.resort)
    A = R.R.VICOMAP_AFFINE
    V = json.load(open(a.trails or os.path.join(pr.work_root(R.id), 'vicomap', 'trails.json')))

    def tf(p):
        return (A[0] * p[0] + A[1] * p[1] + A[2], A[3] * p[0] + A[4] * p[1] + A[5])
    vn, vp = [], []
    for t in V['trails']:
        for pl in t['lines']:
            if len(pl) > 1:
                q = dense_pts([tf(p) for p in pl], 1.0)
                vp += q
                vn += [t['name']] * len(q)
    tree = cKDTree(np.array(vp))
    pieces = R.load('pieces_cut.json')['polylines']
    names = R.load('names.json')
    only = {int(v) for v in a.only.split(',')} if a.only else None
    shown = 0
    for p in pieces:
        pid = p['id']
        if only and pid not in only:
            continue
        dense = dense_pts(R.pts_of(p), 2.0)
        cover = collections.Counter()
        for hits in tree.query_ball_point(np.array(dense), a.tol):
            for nm in {vn[k] for k in hits}:
                cover[nm] += 1
        best = [(nm, n / len(dense)) for nm, n in cover.most_common(3)]
        mine = names.get(str(pid), '?')
        top = best[0] if best else ('', 0)
        agree = mine not in ('?', '-') and top[1] >= a.share and base(top[0]) == base(mine)
        quiet = mine == '-' and top[1] < a.share
        if only or a.all or not (agree or quiet):
            shown += 1
            print(f'{pid:4d} {mine:28s} vicomap: ' + (', '.join(f'{n} {s:.0%}' for n, s in best) or '-') +
                  f'  ({round(p["lengthPx"])} px)')
    print(f'{shown} pieces shown')


'''
s=s[:i]+new+s[j:]
s=s.replace('import base64\nimport html\n','import base64\nimport collections\nimport html\n')
open(p,'w').write(s)
