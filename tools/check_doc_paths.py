"""Every repo path the docs mention in backticks or a markdown link must exist: README.md, CLAUDE.md, docs/*.md and
the READMEs under tools/ (the archive's index aside). Prints each missing path with the docs that mention it; exits
1 if any is missing. Run it after moving or renaming a script.

    python3 tools/check_doc_paths.py [extra.md ...]
"""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PREFIX = ('src/', 'public/', 'tools/', 'scripts/', 'docs/', 'api/', 'supabase/', 'tests/', 'marketing/', '.claude/')


def main():
    os.chdir(ROOT)
    docs = (['README.md', 'CLAUDE.md'] + glob.glob('docs/*.md')
            + [d for d in glob.glob('tools/**/README.md', recursive=True) if d != 'tools/archive/README.md'] + sys.argv[1:])
    missing = {}
    for d in docs:
        text = open(d).read()
        base = os.path.dirname(d)
        for c in set(re.findall(r'`([^`\s]+)`', text)) | set(re.findall(r'\]\(([^)#\s]+)', text)):
            c = c.strip().rstrip('.,:;)')
            if c.startswith(('http', '/')) or any(ch in c for ch in '<*{$'):
                continue
            rel = os.path.normpath(os.path.join(base, c)) if c.startswith(('./', '../')) else c
            if not rel.startswith(PREFIX):
                continue  # a bare file name in a resort folder's README is relative to that folder
            rel = rel.split(':')[0]
            if not os.path.exists(rel):
                missing.setdefault(rel, set()).add(d)
    for k in sorted(missing):
        print(f'{k}  <- {", ".join(sorted(missing[k]))}')
    print(len(missing), 'missing')
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
