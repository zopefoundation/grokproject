import sys
import os.path
import optparse
import shutil
import tempfile
import pkg_resources
import urllib
import urlparse
import xml.sax.saxutils
from paste.script import templates, command
from paste.script.templates import var, NoDefault

VERSIONINFO_INFO_URL = 'http://grok.zope.org/releaseinfo/current'

class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        var('user', 'Name of an initial administrator user', default=NoDefault),
        var('passwd', 'Password for the initial administrator user',
            default=NoDefault),
        var('eggs_dir', 'Location where zc.buildout will look for and place '
            'packages', default=os.path.expanduser('~/buildout-eggs')),
        ]

    def check_vars(self, vars, cmd):
        vars = super(GrokProject, self).check_vars(vars, cmd)
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)
        for var_name in ['user', 'passwd']:
            # Esacpe values that go in site.zcml.
            vars[var_name] = xml.sax.saxutils.quoteattr(vars[var_name])
        vars['eggs_dir'] = os.path.expanduser(vars['eggs_dir'])
        return vars

def main():
    usage = "usage: %prog [options] PROJECT"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--no-buildout', action="store_true", dest="no_buildout",
                      default=False, help="Only create project area, do not "
                      "bootstrap the buildout.")
    parser.add_option('--svn-repository', dest="repos", default=None,
                      help="Import project to given repository location (this "
                      "will also create the standard trunk/ tags/ branches/ "
                      "hierarchy).")
    parser.add_option('--newer', action="store_true", dest="newest",
                      default=False, help="Check for newer versions of packages.")
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose",
                      default=False, help="Be verbose.")
    parser.add_option(
        '--version-info-url', dest="version_info_url", default=None,
        help="The URL to a *.cfg file containing a [versions] section.")

    # Options that override the interactive part of filling the templates.
    for var in GrokProject.vars:
        parser.add_option(
            '--'+var.name.replace('_', '-'), dest=var.name,
            help=var.description)

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        return 1

    # create sandbox using paste.script
    project = args[0]
    commands = command.get_commands()
    cmd = commands['create'].load()
    runner = cmd('create')

    option_args = []
    if options.repos is not None:
        option_args.extend(['--svn-repository', options.repos])
    if not options.verbose:
        option_args.append('-q')

    extra_args = []
    if options.newest:
        extra_args.append('newest=true')
    else:
        extra_args.append('newest=false')

    # Process the options that override the interactive part of filling
    # the templates.
    for var in GrokProject.vars:
        supplied_value = getattr(options, var.name)
        if supplied_value is not None:
            extra_args.append('%s=%s' % (var.name, supplied_value))

    version_info_url = options.version_info_url
    if not version_info_url:
        info = urllib.urlopen(VERSIONINFO_INFO_URL).read().strip()
        version_info_url = urlparse.urljoin(VERSIONINFO_INFO_URL, info)
    extra_args.append('extends=' + version_info_url)
    exit_code = runner.run(option_args + ['-t', 'grokproject', project]
                           + extra_args)
    # TODO exit_code

    if options.no_buildout:
        return

    os.chdir(project)

    extra_args = []
    if not options.verbose:
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
