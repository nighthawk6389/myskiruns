"""A resort whose trail map is a vector PDF: name each line piece from the names and symbols printed on the map,
apply the decisions settled on crops, and write the inputs of the trail pipeline (seed_roster.py,
aggregate_readings.py, traces_to_reviews.py). The PDF counterpart of resorts/vail/{build,reading}.py; each
resort's regen.sh runs it between the extraction and the pipeline.

    python3 tools/trailmap/pdf_resort.py <resort>           # e.g. hunter: tools/trailmap/resorts/hunter/
    python3 tools/trailmap/pdf_resort.py <resort> build     # the auto-match and decisions only, for review crops
    python3 tools/trailmap/pdf_resort.py <resort> reading   # ... and the pipeline's inputs, not the app data
    python3 tools/trailmap/pdf_resort.py <resort> add "crop that showed it" 123=NAME 2100,1200=NAME 45=-:"why"

The resort's folder holds
  resort.py     how the map prints things: clip and scale, which text is a trail name, names printed in two parts,
                text to drop, names printed some other way (EXTRA), display spellings, glades, parks, names with
                no line, areas (resorts/hunter/resort.py lists the basic settings). Optional ones, read with getattr
                where they apply (the other resort folders use them): JOIN_GAP, MATCH_ENDS, ALONG_SHORT,
                ALONG_NEAREST, SYMBOL_CENTRE, CUT_AT_SYMBOLS, SYMBOL_OFF_LINE, LOOSE_SYMBOLS, ON_CIRCLE, SYMBOL_OF,
                DEFAULT_SYMBOL
  decisions.py  CHECKED / UNNAMED / CUTS / TRACED, all keyed by points in map px (see its docstring)
  header.txt    the comment at the top of trails.ts
  regen.sh      the extraction, then this
and reads, from work/<resort>/ (git-ignored; $<RESORT>_WORK overrides):
  pieces.json   extract_pdf_vectors.py's line pieces (percent of the map image)
  printed.json  pdf_labels.py's text labels, or pdf_glyphs.py's labels and symbols (PDF points)
  symbols.json  pdf_symbols.py's symbols (map px; leave it out to use pdf_glyphs.py's)
  map.png       the map image (for its size)
By default it then runs the pipeline into src/data/resorts/<resort>/ (pipeline() below).

Names: one label per printed name. A name drawn twice (a halo pass), a curved label also drawn one object per
letter, and an object holding two names that are also printed apart each keep one copy; resort.JOIN glues a name
printed in two parts. Each symbol goes to the nearest name end (first or last character) within SYMBOL_REACH.

Auto-match: a piece whose end lies at a name's end (beyond its first or last character, or at its symbol) takes
that name: lines run into their names (the name is printed in a gap of its own line), so this names most pieces.
Each name end takes one piece end, nearest first, preferring pieces of the symbol's colour. A piece with one end at
a name's text and the other at the next name's symbol belongs to the first: the line goes on past its label until
the next trail starts. A piece most of whose length runs along a name's characters takes it too, and so does an
unnamed piece passing under a name printed as a numbered circle (ON_CIRCLE). Then names spread along unlabelled
continuations: an end that meets exactly one other piece end of the same colour. decisions.py overrides all of
this.

Names printed in a gap of their line also get a stretch along their own characters, from the symbol (as
Whiteface's did), so the overlay runs through the label, and a trail whose label is all of its line has one.

Writes to the work folder: pieces_cut.json (pieces after CUTS, then the stretches), names.json ({id: name,
'name~' a stretch, '-' not a trail, '?' undecided}: grid_crop.py --names), assign.json, and the pipeline inputs:
  tiles/result.json       one reading: every printed name (symbol, position) and every named piece
  tiles/index.json        stub tile index (aggregate_readings.py wants the image size)
  linePolylines.json      pieces after CUTS plus TRACED stretches, with _unnamed and _traced
  trace.json              markers for names drawn on no line (glades are left to aggregate_readings.py)
  named_syms.json         every symbol with its name ([{name, t, c, r}]: symbol_audit.py --symbols)
"""
import collections
import importlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, HERE)
import seed_roster as sr  # noqa: E402

CLS = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black'}


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def line_dist(q, pts):
    if len(pts) == 1:
        return math.dist(q, pts[0])
    return min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def midpoint(pts):
    """The point halfway along a polyline: where a decision about a whole piece is recorded."""
    half, run = length(pts) / 2, 0
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        if run + d >= half:
            f = (half - run) / (d or 1)
            return (round(a[0] + f * (b[0] - a[0])), round(a[1] + f * (b[1] - a[1])))
        run += d
    return tuple(round(v) for v in pts[0])


def tid(name):
    return sr.slug(sr.norm(name))


class Resort:
    def __init__(self, rid):
        self.id = rid
        self.dir = os.path.join(HERE, 'resorts', rid)
        sys.path.insert(0, self.dir)
        self.R = importlib.import_module('resort')
        self.D = importlib.import_module('decisions')
        env = re.sub(r'\W', '_', rid.upper()) + '_WORK'
        self.work_dir = os.path.abspath(os.environ.get(env, os.path.join(REPO, 'work', rid)))
        x0, y0, x1, y1 = self.R.CLIP
        self.W, self.H = round((x1 - x0) * self.R.SCALE), round((y1 - y0) * self.R.SCALE)

    def work(self, name):
        return os.path.join(self.work_dir, name)

    def load(self, name):
        return json.load(open(self.work(name)))

    def px(self, p):
        """PDF points -> map image px."""
        x0, y0 = self.R.CLIP[:2]
        return ((p[0] - x0) * self.R.SCALE, (p[1] - y0) * self.R.SCALE)

    def pts_of(self, p):
        return [(x * self.W / 100, y * self.H / 100) for x, y in p['points']]

    def pct(self, pts):
        return [[round(100 * x / self.W, 3), round(100 * y / self.H, 3)] for x, y in pts]

    def resolve(self, P, q, tol=8):
        """The piece through point q (nearest within tol px), or None."""
        best = min(((line_dist(q, p['pt']), p['id']) for p in P), default=None)
        return best[1] if best and best[0] <= tol else None

    # ---- names ---------------------------------------------------------------------------------------------
    def names(self):
        R = self.R
        raw = self.load('printed.json')
        raw = raw['labels'] if isinstance(raw, dict) else raw  # pdf_glyphs.py: {labels, symbols}
        L = [{'text': l['text'], 'pts': [self.px(p) for p in l['pts']], 'c': self.px(l['c']), 'seq': l.get('seq', 0),
              'color': l['color'] if isinstance(l.get('color'), str) else tuple(l.get('color') or ()),
              'size': l.get('size', 0)} for l in raw if R.is_name(l)]
        near = 0.8 * R.SCALE  # px: two characters this close are one character drawn twice
        L += self.letter_runs(L)
        # one copy per printed name (a halo pass, the letters of a curved label, a recoloured copy); spaces aside
        uniq = []
        for l in sorted(L, key=lambda l: (-len(l['pts']), bool(l.get('run')), -l['text'].count(' '))):
            key = l['text'].replace(' ', '')
            if not any(u['text'].replace(' ', '') == key and math.dist(u['c'], l['c']) < near for u in uniq):
                uniq.append(l)

        def on(l, others):
            return all(any(math.dist(p, q) < near for o in others for q in o['pts']) for p in l['pts'])
        # single letters left over (a curved label also drawn whole): drop the letters
        uniq = [l for l in uniq if len(l['pts']) > 2 or not on(l, [o for o in uniq if len(o['pts']) > 2])]
        # an object holding two names that are also printed apart (TAYLOR'S RUN WHICH WAY GLADES): keep the parts
        keep = []
        for l in uniq:
            parts = [o for o in uniq if o is not l and len(o['pts']) < len(l['pts'])
                     and any(math.dist(p, q) < near for p in l['pts'] for q in o['pts'])]
            if len(parts) >= 2 and on(l, parts):
                continue
            keep.append(l)
        for parts in getattr(R, 'JOIN', []):  # a name printed in parts (two or three lines), in reading order
            for first in [l for l in keep if l['text'] == parts[0]]:
                chain = [first]
                for t in parts[1:]:
                    gap = lambda l: min(math.dist(p, q) for p in chain[-1]['pts'] for q in l['pts'])  # noqa: E731
                    nxt = min((l for l in keep if l['text'] == t and l not in chain), key=gap, default=None)
                    if nxt is None or gap(nxt) > getattr(R, 'JOIN_GAP', 8) * R.SCALE:
                        break
                    chain.append(nxt)
                if len(chain) < len(parts):
                    continue
                for l in chain:
                    keep.remove(l)
                pts = [p for l in chain for p in l['pts']]
                keep.append({'text': ' '.join(parts), 'pts': pts, 'color': chain[0].get('color'),
                             'c': (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))})
        drop = getattr(R, 'DROP', [])
        out = []
        for l in keep:
            if any(t == l['text'] and (q is None or math.dist(q, l['c']) < 40) for t, q in drop):
                continue
            out.append({'name': getattr(R, 'RENAME', {}).get(l['text'], l['text']), 'pts': l['pts'], 'c': l['c'],
                        'printed': l['text'], 'color': l.get('color')})
        for e in getattr(R, 'EXTRA', []):  # names printed some other way (another font, a sign): name, x, y
            out.append({'name': e[0], 'pts': [tuple(e[1:3])], 'c': tuple(e[1:3]), 'printed': None,
                        'symbol': e[3] if len(e) > 3 else None})
        return sorted(out, key=lambda n: (round(n['c'][1]), round(n['c'][0]), n['name']))  # a stable order

    def letter_runs(self, L):
        """A curved label is also drawn one object per letter: join consecutive single letters of one colour (by
        drawing order) into labels, with a space where the gap between two letters is well over the run's usual."""
        runs, run = [], []
        for l in sorted((l for l in L if len(l['pts']) == 1 and len(l['text'].strip()) == 1), key=lambda l: l['seq']):
            if run and (l['color'] != run[-1]['color']
                        or math.dist(l['pts'][0], run[-1]['pts'][0]) > 1.6 * (l['size'] or 4) * self.R.SCALE):
                runs.append(run)
                run = []
            run.append(l)
        runs.append(run)
        out = []
        for run in runs:
            if len(run) < 3:
                continue
            pts = [l['pts'][0] for l in run]
            text = self.spaced(pts, L) or self.guess_spaces(run)
            out.append({'text': text, 'pts': pts, 'c': (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)),
                        'seq': run[0]['seq'], 'color': run[0]['color'], 'size': run[0]['size'], 'run': True})
        return out

    def spaced(self, pts, L):
        """The text of a whole label whose characters lie on these letters, spaces included (the letters of a
        curved name are often also drawn as one object, or inside a longer one), or None."""
        near = 0.8 * self.R.SCALE
        for o in L:
            if len(o['pts']) < len(pts) or len(o['pts']) != len(o['text'].replace(' ', '')):
                continue
            idx = []
            for p in pts:
                j = min(range(len(o['pts'])), key=lambda j: math.dist(p, o['pts'][j]))
                if math.dist(p, o['pts'][j]) >= near:
                    break
                idx.append(j)
            if len(idx) == len(pts) and idx == list(range(idx[0], idx[0] + len(idx))):
                where = [i for i, ch in enumerate(o['text']) if ch != ' ']  # text index of each drawn character
                return o['text'][where[idx[0]]:where[idx[-1]] + 1]
        return None

    @staticmethod
    def guess_spaces(run):
        """Letters with no whole copy: a space where a gap is well over the run's usual one."""
        pts = [l['pts'][0] for l in run]
        gaps = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
        usual = sorted(gaps)[len(gaps) // 2]
        text = run[0]['text'].strip()
        for g, l in zip(gaps, run[1:]):
            text += (' ' if g > 1.3 * usual else '') + l['text'].strip()
        return text

    def symbols(self, names):
        """Each symbol to the nearest name end within reach (one each). Returns the named symbols and the rest."""
        if os.path.exists(self.work('symbols.json')):  # pdf_symbols.py, in map px
            syms = [{'t': s['type'], 'c': tuple(s['src']), 'r': s['sizePt'] * self.R.SCALE / 2}
                    for s in self.load('symbols.json')]
        else:  # pdf_glyphs.py's symbols, in PDF points
            syms = [{'t': s['t'], 'c': self.px(s['c']), 'r': 1.5 * self.R.SCALE}
                    for s in self.load('printed.json')['symbols']]
        joined = {' '.join(parts) for parts in getattr(self.R, 'JOIN', [])}
        used_s, used_n = set(), set()
        for q, name in getattr(self.R, 'SYMBOL_OF', []):  # a symbol printed beside its name but out of reach
            i = min(range(len(syms)), key=lambda i: math.dist(syms[i]['c'], q))
            j = next((j for j, n in enumerate(names) if n['name'] == name), None)
            if j is None or math.dist(syms[i]['c'], q) > 20:
                print('  SYMBOL_OF: no symbol or no name', q, name)
                continue
            used_s.add(i); used_n.add(j)
            names[j]['symbol'], names[j]['sym'] = syms[i]['t'], syms[i]
        cands = []
        for i, s in enumerate(syms):
            if i in used_s:
                continue
            for j, n in enumerate(names):
                if n.get('symbol') is not None or not n['printed']:
                    continue
                ends = n['pts'] if n['printed'] in joined else (n['pts'][0], n['pts'][-1])  # two lines: any end
                if getattr(self.R, 'SYMBOL_CENTRE', False):  # symbols printed above or below the middle of a name
                    ends = list(ends) + [n['c']]
                d = min(math.dist(s['c'], p) for p in ends)
                if d <= self.R.SYMBOL_REACH * self.R.SCALE:
                    cands.append((d, i, j))
        for d, i, j in sorted(cands):
            if i in used_s or j in used_n:
                continue
            used_s.add(i); used_n.add(j)
            names[j]['symbol'] = syms[i]['t']
            names[j]['sym'] = syms[i]
        for q, kind in getattr(self.R, 'SYMBOL_FIX', []):  # a symbol read differently on a crop
            s = min(syms, key=lambda s: math.dist(s['c'], q))
            if math.dist(s['c'], q) < 20:
                s['t'] = kind
                for n in names:
                    if n.get('sym') is s:
                        n['symbol'] = kind
        loose = [s for i, s in enumerate(syms) if i not in used_s]
        return syms, loose

    # ---- pieces ---------------------------------------------------------------------------------------------
    def pieces(self):
        P = self.load('pieces.json')['polylines']
        for p in P:
            p['pt'] = self.pts_of(p)
        for on, q in getattr(self.D, 'CUTS', []):  # one drawn line carrying two trails: split at q
            pid = self.resolve(P, on)
            if pid is None:
                print('  cut: no piece at', on)
                continue
            self.split(P, P[pid], q)
        return P

    @staticmethod
    def nearest_on(pts, q):
        """(distance, index of the segment's end point, the nearest point) of polyline pts to q."""
        best = (math.inf, 1, pts[0])
        for i in range(1, len(pts)):
            (ax, ay), (bx, by) = pts[i - 1], pts[i]
            dx, dy = bx - ax, by - ay
            t = max(0, min(1, ((q[0] - ax) * dx + (q[1] - ay) * dy) / ((dx * dx + dy * dy) or 1e-9)))
            c = (ax + t * dx, ay + t * dy)
            if math.dist(c, q) < best[0]:
                best = (math.dist(c, q), i, c)
        return best

    def split(self, P, p, q):
        """Cut piece p where it passes nearest q; the second part becomes a new piece (appended)."""
        _, i, c = self.nearest_on(p['pt'], q)
        first, second = p['pt'][:i] + [c], [c] + p['pt'][i:]
        p['pt'], p['points'], p['lengthPx'] = first, self.pct(first), round(length(first))
        P.append({'id': len(P), 'cls': p['cls'], 'lengthPx': round(length(second)), 'points': self.pct(second),
                  'pt': second})

    def cut_at_symbols(self, P, names):
        """Maps that print a run's symbol on (or just beside) its line, with the name after it
        (resort.CUT_AT_SYMBOLS): cut the nearest line of the symbol's colour where it passes the symbol, so the
        stretch from a symbol down to the next is one piece. Returns [(name index, the cut point)]."""
        off = getattr(self.R, 'SYMBOL_OFF_LINE', 1.5) * self.R.SCALE  # how far beside its line a symbol may sit
        at = []
        for j, n in enumerate(names):
            s = n.get('sym')
            if not s:
                continue
            want = CLS.get(n.get('symbol'))
            near = sorted((self.nearest_on(p['pt'], s['c'])[0], p['id']) for p in P if p['cls'] == want)
            if not near or near[0][0] > s['r'] + off:
                near = sorted((self.nearest_on(p['pt'], s['c'])[0], p['id']) for p in P)
                if not near or near[0][0] > s['r'] + 1.5 * self.R.SCALE:
                    continue
            p = P[near[0][1]]
            _d, _i, c = self.nearest_on(p['pt'], s['c'])
            ends = sorted((math.dist(c, p['pt'][k]), k) for k in (0, -1))
            if ends[0][0] <= s['r']:
                c = p['pt'][ends[0][1]]  # the line already ends at the symbol
            else:
                self.split(P, p, s['c'])
            at.append((j, c))
        return at

    def terminals(self, n):
        """A name's two ends: [(point, has its symbol)] for its first and last character, each pushed out
        along the text by most of a character; the symbol end is the symbol itself."""
        pts = n['pts']
        if len(pts) > 1:
            a, b = (pts[1], pts[0]), (pts[-2], pts[-1])
            pitch = length(pts) / (len(pts) - 1)
        else:
            a = b = (pts[0], pts[0])
            pitch = 0
        out = []
        for (q, e) in (a, b):
            d = math.dist(q, e) or 1
            out.append([(e[0] + 0.7 * pitch * (e[0] - q[0]) / d, e[1] + 0.7 * pitch * (e[1] - q[1]) / d), False])
        s = n.get('sym')
        if s:
            k = 0 if math.dist(s['c'], pts[0]) < math.dist(s['c'], pts[-1]) else 1
            out[k] = [s['c'], True]
        return out

    def stretch(self, n):
        """A line along a name's own characters, from its symbol: for a name printed in a gap of its line."""
        (t0, _), (t1, _) = self.terminals(n)
        return [t0] + list(n['pts']) + [t1] if len(n['pts']) > 1 else [t0, t1]

    def build(self):
        R, D = self.R, self.D
        names = self.names()
        syms, loose = self.symbols(names)
        self.names_all = names
        P = self.pieces()
        reach = R.END_REACH * R.SCALE
        two_line = set(getattr(R, 'TWO_LINE', ()))  # names printed on two lines: no stretch along them
        on_line = getattr(R, 'CUT_AT_SYMBOLS', False)
        sym_cuts = self.cut_at_symbols(P, names) if on_line else []
        cands = []  # (score, piece id, piece end, name index, name end)
        for j, n in enumerate(names):
            if not n['printed'] or on_line or not getattr(R, 'MATCH_ENDS', True):  # names on their line
                continue
            want = CLS.get(n.get('symbol'))
            for m, (t, _sym) in enumerate(self.terminals(n)):
                for p in P:
                    for k in (0, -1):
                        dd = math.dist(p['pt'][k], t)
                        if dd <= reach:
                            cands.append((dd + (0 if want in (None, p['cls']) else reach), p['id'], k, j, m))
        match = collections.defaultdict(list)  # piece id -> [(name index, name end, at its symbol)]
        used_end, used_term = set(), set()
        for sc, pid, k, j, m in sorted(cands):
            if (pid, k) in used_end or (j, m) in used_term:
                continue
            used_end.add((pid, k)); used_term.add((j, m))
            match[pid].append((j, m, self.terminals(names[j])[m][1]))
        assign = collections.defaultdict(set)
        why = {}
        for pid, ms in match.items():
            if len({names[j]['name'] for j, _m, _s in ms}) > 1:
                # one end at a name's last character (the line goes on from its label), the other at the next
                # name's symbol (where that trail starts): the line is the first name's
                plain = [x for x in ms if not x[2]]
                if len(plain) == 1:
                    ms = plain
            for j, m, at_sym in ms:
                assign[pid].add(names[j]['name'])
                why[pid] = f"{'symbol' if at_sym else 'end'} of {names[j]['name']}"
        gap = {names[j]['name'] for j, _m in used_term}  # names printed in a gap of their line
        # a piece running along a name's characters
        short = getattr(R, 'ALONG_SHORT', False)  # also names of two or three characters (T2, OZ)
        nearest = getattr(R, 'ALONG_NEAREST', False)  # names printed between parallel lines: the nearest only
        for j, n in enumerate(names):
            if len(n['pts']) < (2 if short else 4):
                continue
            hits = []
            for p in P:
                if p['id'] in assign and not why.get(p['id'], '').startswith('along'):
                    continue  # named by a name that runs into it
                ds = [line_dist(q, p['pt']) for q in n['pts']]
                close = sum(1 for d in ds if d < R.ALONG * R.SCALE)
                need = 0.6 * len(n['pts']) if len(n['pts']) >= 4 else len(n['pts'])
                if close >= need and length(p['pt']) > 0.5 * length(n['pts']):
                    hits.append((sorted(ds)[len(ds) // 2], p['id']))
            for _d, pid in sorted(hits)[:1] if nearest else hits:
                assign[pid].add(n['name'])  # several names along one piece: cut it (CUTS)
                why[pid] = f"along {n['name']}"
        # a name printed as a numbered circle on its own line (resort.ON_CIRCLE, pt: about the circle's radius;
        # Sugarloaf's key numbers): the unnamed pieces passing under the circle
        rad = getattr(R, 'ON_CIRCLE', 0) * R.SCALE
        for n in names if rad else ():
            if n['printed'] and len(n['pts']) == 1:
                for p in P:
                    if not assign.get(p['id']) and line_dist(n['c'], p['pt']) <= rad:
                        assign[p['id']].add(n['name'])
                        why[p['id']] = f"under the circle of {n['name']}"
        if on_line:
            # the piece leaving a named symbol toward its name starts that run
            for j, c in sym_cuts:
                n = names[j]
                toward = (n['c'][0] - c[0], n['c'][1] - c[1])
                best = None
                for p in P:
                    for k in (0, -1):
                        if math.dist(p['pt'][k], c) > 1.0:
                            continue
                        pts = p['pt'] if k == 0 else p['pt'][::-1]
                        ahead = next((q for q in pts if math.dist(q, c) > 6 * R.SCALE), pts[-1])
                        v = (ahead[0] - c[0], ahead[1] - c[1])
                        cos = (v[0] * toward[0] + v[1] * toward[1]) / ((math.hypot(*v) * math.hypot(*toward)) or 1)
                        if best is None or cos > best[0]:
                            best = (cos, p['id'])
                if best and best[0] > 0 and not (assign.get(best[1], set()) - {n['name']}):
                    assign[best[1]].add(n['name'])
                    why[best[1]] = f"from the symbol of {n['name']}"
        fixed = set()
        for q, name in D.CHECKED:
            pid = self.resolve(P, q)
            if pid is None:
                print('  checked point on no piece:', q, name)
                continue
            assign[pid] = {name}; why[pid] = 'checked'; fixed.add(pid)
        unnamed = {}
        for q, note in D.UNNAMED:
            pid = self.resolve(P, q)
            if pid is None:
                print('  unnamed point on no piece:', q, note)
                continue
            assign.pop(pid, None); why[pid] = 'unnamed'; fixed.add(pid); unnamed[pid] = note
        ends = [(p['pt'][k], p['id']) for p in P for k in (0, -1)]

        def neighbours(pid):
            out = []
            for k in (0, -1):
                e = P[pid]['pt'][k]
                if any(math.dist(e, c) < 1.0 for _j, c in sym_cuts):
                    continue  # a run starts at its symbol: no continuation across it
                at = {i for f, i in ends if i != pid and math.dist(f, e) < 1.0 * R.SCALE}
                if len(at) == 1:
                    out.append(next(iter(at)))
            return out
        changed = True
        while changed:
            changed = False
            for p in P:
                if assign.get(p['id']) or p['id'] in fixed:
                    continue
                ns = set()
                for nb in neighbours(p['id']):
                    if P[nb]['cls'] == p['cls'] and len(assign.get(nb, ())) == 1 and nb not in unnamed:
                        ns |= assign[nb]
                if len(ns) == 1:
                    assign[p['id']] = set(ns); why[p['id']] = 'continuation'; changed = True
        # stretches: along the names printed in a gap of their line (or whose label is all the line they have),
        # then the stretches traced on crops
        traced = {}
        glades = set(getattr(R, 'GLADES', ()))
        along = (gap | set(getattr(R, 'LABEL_LINE', ()))) - set(getattr(R, 'NO_STRETCH', ())) - glades
        for n in names:
            if n['name'] in along and n['printed'] and n['printed'] not in two_line and 'GLADE' not in n['name']:
                pts = self.stretch(n)
                pid = len(P)
                P.append({'id': pid, 'cls': CLS.get(n.get('symbol')) or self.colour_of_assign(assign, P, n['name']),
                          'lengthPx': round(length(pts)), 'points': self.pct(pts), 'pt': pts})
                assign[pid] = {n['name']}; why[pid] = 'along its printed name'; traced[pid] = 'label'
        for name, pts in getattr(D, 'TRACED', []):
            pid = len(P)
            P.append({'id': pid, 'cls': self.colour_of_assign(assign, P, name), 'lengthPx': round(length(pts)), 'points': self.pct(pts), 'pt': [tuple(q) for q in pts]})
            assign[pid] = {name}; why[pid] = 'traced along the drawn line'; traced[pid] = 'traced'
        self.P, self.names_, self.syms, self.loose = P, names, syms, loose
        self.assign = {k: v for k, v in assign.items() if v}
        self.unnamed, self.why, self.traced = unnamed, why, traced
        json.dump({'polylines': [{k: p[k] for k in ('id', 'cls', 'lengthPx', 'points')} for p in P]},
                  open(self.work('pieces_cut.json'), 'w'))
        tags = {str(p['id']): '/'.join(sorted(self.assign[p['id']])) + ('~' if p['id'] in traced else '')
                if p['id'] in self.assign else ('-' if p['id'] in unnamed else '?') for p in P}
        json.dump(tags, open(self.work('names.json'), 'w'))
        json.dump({'assign': {str(k): sorted(v) for k, v in self.assign.items()},
                   'why': {str(k): v for k, v in why.items()}, 'unnamed': {str(k): v for k, v in unnamed.items()}},
                  open(self.work('assign.json'), 'w'), indent=0)
        json.dump([{'name': n['name'], 't': n['sym']['t'], 'c': n['sym']['c'], 'r': n['sym']['r']}
                   for n in names if n.get('sym')], open(self.work('named_syms.json'), 'w'), indent=0)
        json.dump([{'c': s['c'], 't': s['t'], 'name': ''} for s in loose], open(self.work('loose_syms.json'), 'w'))
        left = [p['id'] for p in P if p['id'] not in self.assign and p['id'] not in unnamed]
        several = {k: sorted(v) for k, v in self.assign.items() if len(v) > 1}
        named = {n for v in self.assign.values() for n in v}
        print(f'{len(names)} names, {len(syms)} symbols ({len(loose)} with no name); {len(P) - len(traced)} pieces: '
              f'{len(self.assign) - len(traced)} named, {len(unnamed)} not trails, {len(left)} undecided {left}; '
              f'{sum(1 for v in traced.values() if v == "label")} stretches along names, '
              f'{sum(1 for v in traced.values() if v == "traced")} traced')
        if several:
            print('  pieces with several names:', several)
        print('  names on no line:', sorted({n["name"] for n in names} - named))
        return left, several

    def colour_of_assign(self, assign, P, name):
        """A stretch's colour: that of the trail's own pieces, else its symbol's."""
        c = collections.Counter(P[pid]['cls'] for pid, v in assign.items() if name in v)
        if c:
            return c.most_common(1)[0][0]
        n = next((n for n in self.names_all if n['name'] == name), None)
        if n and n.get('color') in ('green', 'blue', 'black'):  # a name printed in its difficulty colour
            return n['color']
        return CLS.get(n and n.get('symbol')) or 'black'

    # ---- the pipeline's inputs ---------------------------------------------------------------------------
    def reading(self):
        R = self.R
        left, several = self.build()
        assert not several, ('pieces with several names: decide each on a crop (decisions.py CHECKED)', several)
        assert not left, ('undecided pieces: decide each on a crop (decisions.py CHECKED or UNNAMED)', left)
        P, names = self.P, self.names_
        glades, parks = set(getattr(R, 'GLADES', ())), set(getattr(R, 'PARKS', ()))
        labels = []
        for n in names:
            nm = n['name']
            labels.append({'mapName': nm, 'printed': R.DISPLAY.get(nm), 'symbol': n.get('symbol'),
                           'glade': 'GLADE' in nm or nm in glades, 'park': nm in parks, 'area': R.area(n['c']),
                           'labelSrc': [round(n['c'][0]), round(n['c'][1])], 'confidence': 'certain'})
        # symbols printed with no name on a named trail's line (a change of rating): they count toward its difficulty
        loose_off = 0
        for s in self.loose:
            d, pid = min((line_dist(s['c'], p['pt']), p['id']) for p in P)
            if pid in self.assign and d <= 2 * s['r'] + 4:
                nm = next(iter(self.assign[pid]))
                labels.append({'mapName': nm, 'printed': R.DISPLAY.get(nm), 'symbol': s['t'],
                               'glade': 'GLADE' in nm or nm in glades, 'park': nm in parks, 'area': R.area(s['c']),
                               'labelSrc': [round(s['c'][0]), round(s['c'][1])], 'confidence': 'certain'})
                print(f'  {s["t"]} at {[round(v) for v in s["c"]]} (no name printed) on {nm}')
            else:
                why = getattr(R, 'LOOSE_SYMBOLS', None)
                if not why:
                    print(f'  symbol {s["t"]} at {[round(v) for v in s["c"]]} with no name, on no named line '
                          f'(nearest piece {pid}, {d:.0f} px)')
                loose_off += 1
        if loose_off and getattr(R, 'LOOSE_SYMBOLS', None):
            print(f'  {loose_off} symbols with no name on no line: {R.LOOSE_SYMBOLS}')
        # resort.DEFAULT_SYMBOL: the symbol of a name printed with none anywhere (for names with no line to colour them)
        rated = {L['mapName'] for L in labels if L.get('symbol')}
        for L in labels:
            d = getattr(R, 'DEFAULT_SYMBOL', {}).get(L['mapName'])
            if d and L['mapName'] not in rated:
                L['symbol'] = d
                print(f'  {L["mapName"]}: no symbol printed, {d} by default (resort.DEFAULT_SYMBOL)')
        traced = sorted(self.traced)
        os.makedirs(self.work('tiles'), exist_ok=True)
        lines = [{'id': pid, 'mapName': next(iter(v)), 'color': P[pid]['cls'], 'confidence': 'certain',
                  'note': 'checked on a crop' if self.why.get(pid) == 'checked' else self.why.get(pid, '')}
                 for pid, v in sorted(self.assign.items())]
        json.dump({'labels': [{k: v for k, v in L.items() if v is not None} for L in labels], 'lines': lines},
                  open(self.work('tiles/result.json'), 'w'), indent=1)
        json.dump({'zoom': 1, 'imageSize': [self.W, self.H], 'tiles': []}, open(self.work('tiles/index.json'), 'w'))
        doc = {'_source': R.SOURCE,
               '_unnamed': {str(k): v for k, v in sorted(self.unnamed.items())},
               '_traced': [str(k) for k in traced],
               'polylines': [{k: p[k] for k in ('id', 'cls', 'lengthPx', 'points')} for p in P]}
        json.dump(doc, open(self.work('linePolylines.json'), 'w'))
        drawn = {n for v in self.assign.values() for n in v}
        markers = []
        for L in labels:
            nm = L['mapName']
            if nm in drawn or L['glade'] or any(tid(nm) == m['id'] for m in markers):
                continue
            markers.append({'id': tid(nm), 'pieces': [], 'traced': [], 'confidence': 'high',
                            'note': getattr(R, 'NO_LINE', {}).get(nm, 'Named on the map with no line drawn: marker at its name')})
        json.dump({'trails': markers}, open(self.work('trace.json'), 'w'), indent=1)
        print(len(labels), 'labels,', len(lines), 'named pieces and stretches,', len(self.unnamed), 'not trails,',
              len(markers), 'markers:', ', '.join(m['id'] for m in markers))


def run(*cmd):
    import subprocess
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def pipeline(r):
    """The readings -> the app's data in src/data/resorts/<resort>/: trails.ts (seed_roster.py, with the
    resort's header.txt), linePolylines.json, trailProposals.json (aggregate_readings.py), Claude's reviews in
    trailReviews.json (traces_to_reviews.py: markers for names with no line; a person's reviews are kept, and
    Claude's unchanged ones keep their timestamps) and trailPaths.json (npm run trails:apply)."""
    R, T = r.R, 'tools/trailmap'
    D = os.path.join(REPO, 'src/data/resorts', r.id)
    os.makedirs(D, exist_ok=True)
    areas = ','.join('='.join(map(str, a)) for a in R.AREAS)
    print(run('python3', f'{T}/seed_roster.py', '--readings', r.work('tiles/result.json'), '--areas', areas,
              '--trails', f'{D}/trails.ts', '--labels', r.work('labels.json')).splitlines()[0])
    ts = open(f'{D}/trails.ts').read()
    head = ts[ts.index('// Seeded'):ts.index('export const peaks')]
    ts = ts.replace(head, open(os.path.join(r.dir, 'header.txt')).read())
    open(f'{D}/trails.ts', 'w').write(ts)
    json.dump(r.load('linePolylines.json'), open(f'{D}/linePolylines.json', 'w'))
    print(run('python3', f'{T}/aggregate_readings.py', '--tiles', r.work('tiles'), '--readings',
              r.work('tiles/result.json'), '--roster', f'{D}/trails.ts', '--polylines', f'{D}/linePolylines.json',
              '--proposals', f'{D}/trailProposals.json', '--review-data', r.work('review.json'),
              '--labels', r.work('labels.json')).strip().splitlines()[-1])
    f = f'{D}/trailReviews.json'
    d = json.load(open(f)) if os.path.exists(f) else {'reviews': {}}
    old = {k: v for k, v in d['reviews'].items() if v.get('by') == 'claude'}
    d['reviews'] = {k: v for k, v in d['reviews'].items() if v.get('by') != 'claude'}  # a person's reviews stay
    json.dump(d, open(f, 'w'), indent=1)
    if os.path.exists(r.work('recheck.json')):
        os.remove(r.work('recheck.json'))
    run('python3', f'{T}/traces_to_reviews.py', '--traces', r.work('trace.json'), '--reviews', f,
        '--recheck', r.work('recheck.json'), '--labels', r.work('labels.json'), '--image', r.work('map.png'))
    d = json.load(open(f))
    for k, v in d['reviews'].items():  # unchanged decisions keep their timestamp
        o = old.get(k)
        if v.get('by') == 'claude' and o and {**o, 'at': None} == {**v, 'at': None}:
            v['at'] = o['at']
    json.dump(d, open(f, 'w'), indent=1)
    print(run('npm', 'run', '-s', 'trails:apply', '--', '--resort', r.id).strip().splitlines()[-1])


def add(r, comment, args):
    """Record decisions in the resort's decisions.py as points: id=NAME or x,y=NAME (CHECKED), id=- or
    id=-:why (UNNAMED). Ids are those of the last build (pieces_cut.json); the piece's midpoint is stored."""
    P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
    named, unnamed = [], []
    for a in args:
        k, v = a.split('=', 1)
        q = tuple(int(float(t)) for t in k.split(',')) if ',' in k else midpoint(P[int(k)])
        if v.startswith('-'):
            unnamed.append((q, v[2:] if v.startswith('-:') else 'unnamed connector'))
        else:
            named.append((q, v))
    f = os.path.join(r.dir, 'decisions.py')
    s = open(f).read()
    for block, entries in (('CHECKED', named), ('UNNAMED', unnamed)):
        if not entries:
            continue
        i = s.index(f'{block} = [') + len(f'{block} = [')
        text = f'\n    # {comment}' + ''.join(f'\n    (({x}, {y}), {nm!r}),' for (x, y), nm in entries)
        s = s[:i] + text + s[i:]
    open(f, 'w').write(s)
    print('recorded', len(named), 'named,', len(unnamed), 'not trails')


if __name__ == '__main__':
    r = Resort(sys.argv[1])
    cmd = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if cmd == 'build':
        r.build()
    elif cmd == 'add':  # pdf_resort.py <resort> add "what showed it" 123=NAME 2100,1200=NAME 45=-:"why not"
        add(r, sys.argv[3], sys.argv[4:])
    elif cmd == 'reading':
        r.reading()
    else:
        r.reading()
        pipeline(r)
