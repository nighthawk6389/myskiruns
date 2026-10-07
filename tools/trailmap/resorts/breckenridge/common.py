"""Shared by Breckenridge's pipeline scripts: where the repo and the working files are.

Working files (the downloaded PDF and painting, intermediate JSON, crops) go to $BRECKENRIDGE_WORK, default
work/breckenridge in the repo (git-ignored); regen.sh sets it. The scripts were scratch scripts (br_*.py) run from
their own folder; here every work file is work(name) and every repo file repo(path), with the logic unchanged.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
WORK = os.path.abspath(os.environ.get('BRECKENRIDGE_WORK', os.path.join(REPO, 'work/breckenridge')))
DATA = os.path.join(REPO, 'src/data/resorts/breckenridge')
PDF = os.path.join(WORK, 'breckenridge.pdf')  # the 2025-26 trail-map PDF (scratch: breck.pdf)
PIECES = os.path.join(DATA, 'linePolylines.json')  # the line pieces, after the cut (split_pieces.py)


def work(name):
    return os.path.join(WORK, name)


def repo(path):
    return os.path.join(REPO, path)
