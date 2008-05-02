import os
import sys
import shutil
import tempfile
import pkg_resources
from ConfigParser import ConfigParser

HOME = os.path.expanduser('~')


def get_buildout_default_eggs_dir():
    default_cfg = os.path.join(HOME, '.buildout', 'default.cfg')
    if os.path.isfile(default_cfg):
        cfg = ConfigParser()
        cfg.read(default_cfg)
        if cfg.has_option('buildout', 'eggs-directory'):
            eggs_dir = cfg.get('buildout', 'eggs-directory').strip()
            if eggs_dir:
                return os.path.expanduser(eggs_dir)

def default_eggs_dir():
    buildout_default = get_buildout_default_eggs_dir()
    if buildout_default:
        return buildout_default
    return os.path.join(HOME, 'buildout-eggs')


def run_buildout(verbose=False):
    """Run a buildout.

    This will download zc.buildout if it's not available. Then it will
    bootstrap the buildout scripts and finally launch the buildout
    installation routine.

    Note that this function expects the buildout directory to be the
    current working directory.
    """
    extra_args = []
    if not verbose:
        extra_args.append('-q')

    try:
        import zc.buildout.buildout
    except ImportError:
        print "Downloading zc.buildout..."

        # Install buildout into a temporary location
        import setuptools.command.easy_install
        tmpdir = tempfile.mkdtemp()
        sys.path.append(tmpdir)
        setuptools.command.easy_install.main(extra_args +
                                             ['-mNxd', tmpdir, 'zc.buildout'])

        # Add downloaded buildout to PYTHONPATH by requiring it
        # through setuptools (this dance is necessary because the
        # temporary installation was done as multi-version).
        ws = pkg_resources.working_set
        ws.add_entry(tmpdir)
        ws.require('zc.buildout')

        import zc.buildout.buildout
        zc.buildout.buildout.main(extra_args + ['bootstrap'])
        shutil.rmtree(tmpdir)
    else:
        zc.buildout.buildout.main(extra_args + ['bootstrap'])

    print "Invoking zc.buildout..."
    zc.buildout.buildout.main(['-q', 'install'])
