"""Shared final-size figure settings and the exact body typeface."""
import hashlib
import json
import os
from pathlib import Path
RUN_CACHE = Path(__file__).resolve().parents[2] / '.research-run' / 'cache'
os.environ.setdefault('MPLCONFIGDIR', str(RUN_CACHE / 'matplotlib'))
import matplotlib as mpl
from matplotlib import font_manager, style

ROOT = Path(__file__).resolve().parent
COLUMN_IN = 3.163944
TEXT_IN = 6.535444
RED = '#8E1B1E'
BLUE = '#0072B2'
INK = '#242424'
GREY = '#7B7B7B'
PALE = '#F2F0EC'
def ensure_fonts():
    """Load pinned, redistributable outline fonts without network access."""
    directory = ROOT / 'fonts'
    manifest = json.loads((directory / 'manifest.json').read_text())
    if hashlib.sha256((directory / 'LICENCE.txt').read_bytes()).hexdigest() != manifest['licence_sha256']:
        raise ValueError('The bundled font licence notice changed')
    paths = []
    for name, expected in manifest['files'].items():
        path = directory / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Bundled figure font differs from its manifest: ' + name)
        paths.append(path)
    if len(paths) != 4:
        raise ValueError('The figure typeface requires its four recorded styles')
    return paths


def apply():
    for path in ensure_fonts():
        font_manager.fontManager.addfont(path)
    style.use(ROOT / 'hyperprior.mplstyle')
    mpl.rcParams['mathtext.fontset'] = 'custom'
    mpl.rcParams['mathtext.rm'] = 'XCharter'
    mpl.rcParams['mathtext.it'] = 'XCharter:italic'
    mpl.rcParams['mathtext.bf'] = 'XCharter:bold'


def save(fig, destination):
    fig.savefig(destination, format='pdf', metadata={
        'Creator': 'HyperPrior Research', 'Author': 'HyperPrior Research',
        'CreationDate': None, 'ModDate': None})
