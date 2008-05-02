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


class ask_var(var):

    def __init__(self, name, description,
                 default='', should_echo=True, should_ask=True):
        super(ask_var, self).__init__(
            name, description, default=default,
            should_echo=should_echo)
        self.should_ask = should_ask


class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        ask_var('user', 'Name of an initial administrator user', default=NoDefault),
        ask_var('passwd', 'Password for the initial administrator user',
            default=NoDefault, should_echo=False),
        ask_var('newest', 'Check for newer versions of packages',
                default='false', should_ask=False),
        ask_var('version_info_url',
            "The URL to a *.cfg file containing a [versions] section.",
            default=None, should_ask=False),
        ]

    def check_vars(self, vars, cmd):
        skipped_vars = {}
        for var in self.vars:
            if not var.should_ask:
                skipped_vars[var.name] = var.default
                self.vars.remove(var)

        vars = super(GrokProject, self).check_vars(vars, cmd)
        for name in skipped_vars:
            vars[name] = skipped_vars[name]
        extra_args = [v.split('=') for v in cmd.args if v.find('=') != -1]
        for arg in extra_args:
            name = arg[0]
            value = arg[1]
            if name in skipped_vars:
                vars[name] = value

        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)
        for var_name in ['user', 'passwd']:
            # Escape values that go in site.zcml.
            vars[var_name] = xml.sax.saxutils.quoteattr(vars[var_name])
        extends = vars.get('version_info_url')
        if extends is None:
            info = urllib.urlopen(VERSIONINFO_INFO_URL).read().strip()
            extends = urlparse.urljoin(VERSIONINFO_INFO_URL, info)
        vars['extends'] = extends
        vars['app_class_name'] = vars['project'].capitalize()

        # We want to have newest be 'false' or 'true'.
        if vars['newest'].lower() in ('1', 'true'):
            vars['newest'] = 'true'
        else:
            vars['newest'] = 'false'
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
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose",
                      default=False, help="Be verbose.")

    # Options that override the interactive part of filling the templates.
    for var in GrokProject.vars:
        option_name = '--'+var.name.replace('_', '-')
        if not parser.has_option(option_name):
            parser.add_option(
                option_name, dest=var.name,
                help=var.description)

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        return 1

    # create sandbox using paste.script
    project = args[0]
    app_class_name = project.capitalize()
    commands = command.get_commands()
    cmd = commands['create'].load()
    runner = cmd('create')

    option_args = []
    if options.repos is not None:
        option_args.extend(['--svn-repository', options.repos])
    if not options.verbose:
        option_args.append('-q')

    extra_args = []
    extra_args.append('%s=%s' % ('app_class_name', app_class_name))

    # Process the options that override the interactive part of filling
    # the templates.
    for var in GrokProject.vars:
        supplied_value = getattr(options, var.name)
        if supplied_value is not None:
            extra_args.append('%s=%s' % (var.name, supplied_value))

    exit_code = runner.run(option_args + ['-t', 'grok', project]
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
