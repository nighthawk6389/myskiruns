"""Copper Mountain: the paths the scripts in this folder share (imported by each of them; no logic).

HERE is this folder (the hand-made inputs: letters.json, decisions.py, header.txt), REPO the repository root,
W the working folder ($COPPER_MOUNTAIN_WORK, default work/copper-mountain in the repo, git-ignored: the PDF and
every intermediate file), PDF the trail-map PDF in it, DATA the app's data folder for the resort.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
W = os.path.abspath(os.environ.get('COPPER_MOUNTAIN_WORK', os.path.join(REPO, 'work/copper-mountain')))
PDF = os.path.join(W, 'copper.pdf')
DATA = os.path.join(REPO, 'src/data/resorts/copper-mountain')


def work(name):
    """A file in the working folder."""
    return os.path.join(W, name)
