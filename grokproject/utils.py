import os
import sys
import shutil
import tempfile
import pkg_resources
from paste.script.templates import var
from ConfigParser import ConfigParser

HOME = os.path.expanduser('~')


class ask_var(var):

    def __init__(self, name, description,
                 default='', should_echo=True, should_ask=True,
                 getter=None):
        super(ask_var, self).__init__(
            name, description, default=default,
            should_echo=should_echo)
        self.should_ask = should_ask
        self.getter = getter
        if self.getter is None:
            self.getter = lambda x, y: self.default


def get_var(vars, name):
    for var in vars:
        if var.name == name:
            return var


def create_buildout_default_file():
    default_dir = os.path.join(HOME, '.buildout')
    if not os.path.isdir(default_dir):
        os.mkdir(default_dir)
    eggs_dir = os.path.join(default_dir, 'eggs')
    if not os.path.isdir(eggs_dir):
        os.mkdir(eggs_dir)
    default_cfg = os.path.join(HOME, '.buildout', 'default.cfg')
    if not os.path.isfile(default_cfg):
        config_file = open(default_cfg, 'w')
        contents = """[buildout]
eggs-directory = %s
""" % (eggs_dir)
        config_file.write(contents)
        config_file.close()


def get_boolean_value_for_option(vars, option):
    value = vars.get(option.name)
    if value is not None:
        if isinstance(option.default, bool):
            want_boolean = True
        else:
            want_boolean = False
        value = value.lower()
        if value in ('1', 'true', 'yes'):
            if want_boolean:
                value = True
            else:
                value = 'true'
        elif value in ('0', 'false', 'no'):
            if want_boolean:
                value = False
            else:
                value = 'false'
        else:
            print ""
            print "Error: %s should be true or false." % option.name
            sys.exit(1)
    else:
        value = option.default
    return value


def get_buildout_default_eggs_dir():
    default_cfg = os.path.join(HOME, '.buildout', 'default.cfg')
    if os.path.isfile(default_cfg):
        cfg = ConfigParser()
        cfg.read(default_cfg)
        if cfg.has_option('buildout', 'eggs-directory'):
            eggs_dir = cfg.get('buildout', 'eggs-directory').strip()
            if eggs_dir:
                return os.path.expanduser(eggs_dir)


def exist_buildout_default_file():
    default_cfg = os.path.join(HOME, '.buildout', 'default.cfg')
    return os.path.isfile(default_cfg)


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


def required_grok_version(versionfile):
    for line in versionfile.split('\n'):
        if line.startswith('grok ='):
            return line.split(' ')[-1]


def install_grok(target_dir=None, version=None, links=None):
    from zc.buildout.easy_install import install
    from zc.buildout.easy_install import MissingDistribution
    try:
        empty_index = tempfile.mkdtemp()

        try:
            install(['grok'], target_dir, newest=False,
                    versions={'grok': version}, links=links,
                    index='file://' + empty_index)
        except MissingDistribution:
            result = False
        else:
            result = True
    finally:
        shutil.rmtree(empty_index)
    return result


def is_grok_installed(target_dir=None, version=None):
    # Check if the required grok version is installed.  We do this
    # by trying to install grok in the target dir and letting
    # easy_install only look inside that same eggs dir while doing
    # that.
    result = install_grok(target_dir=target_dir, version=version,
                          links=[target_dir])
    return result
