"""adddec.py PANEL FILE "comment": record the id=NAME / id=- / id=-:why / x,y=NAME lines of FILE (# comments
ignored) with pdf_resort.py's add (ids of the last build)."""
import sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
panel, f, comment = sys.argv[1:4]
args = [l.strip() for l in open(f) if l.strip() and not l.startswith('#')]
r = pr.Resort(f'whistler-blackcomb/{panel}')
pr.add(r, comment, args)
