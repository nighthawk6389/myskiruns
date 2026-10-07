import json, math
F=[json.loads(l.strip().rstrip(',')) for l in open('okemo_runs.jsonl')]
lat0, lon0 = 43.405, -72.745
kx = 111320*math.cos(math.radians(lat0)); ky = 110540
def ne(lon, lat): return ((lat-lat0)*ky, (lon-lon0)*kx)
runs = {}
for f in F:
    n = f['properties'].get('name')
    if f['geometry']['type'] == 'LineString':
        runs.setdefault(n, []).append([ne(c[0], c[1]) + (c[2] if len(c) > 2 else 0,) for c in f['geometry']['coordinates']])
def solve(A, b):
    # least squares via normal equations (3 unknowns)
    n = len(A[0])
    M = [[sum(A[k][i]*A[k][j] for k in range(len(A))) for j in range(n)] for i in range(n)]
    v = [sum(A[k][i]*b[k] for k in range(len(A))) for i in range(n)]
    # gaussian elimination
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]; v[i], v[p] = v[p], v[i]
        for r in range(n):
            if r != i:
                f = M[r][i]/M[i][i]
                M[r] = [a - f*c for a, c in zip(M[r], M[i])]; v[r] -= f*v[i]
    return [v[i]/M[i][i] for i in range(n)]
def fit(ctrl):
    A = [[n, e, 1] for (n, e), _ in ctrl]
    cx = solve(A, [m[0] for _, m in ctrl]); cy = solve(A, [m[1] for _, m in ctrl])
    f = lambda n, e: (cx[0]*n + cx[1]*e + cx[2], cy[0]*n + cy[1]*e + cy[2])
    for (n, e), m in ctrl:
        p = f(n, e); print('  resid', round(p[0]-m[0]), round(p[1]-m[1]))
    return f
