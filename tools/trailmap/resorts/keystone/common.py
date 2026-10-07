"""Shared by Keystone's pipeline scripts: where the working files and the app's data are.

Working files (the downloaded PDF and painting, the map image, intermediate JSON, crops) go to $KEYSTONE_WORK
(default work/keystone in the repo, git-ignored); the app's data is src/data/resorts/keystone/. The scripts work in
PDF points; the map image is the page's clip 0,90,1530,1080 pt rendered at 2.8 px/pt (4284x2772), and the pieces
in linePolylines.json are in percent of it."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
WORK = os.path.abspath(os.environ.get('KEYSTONE_WORK', os.path.join(REPO, 'work/keystone')))
DATA = os.path.join(REPO, 'src/data/resorts/keystone')
PDF = os.path.join(WORK, 'keystone.pdf')


def work(name):
    return os.path.join(WORK, name)


def data(name):
    return os.path.join(DATA, name)
