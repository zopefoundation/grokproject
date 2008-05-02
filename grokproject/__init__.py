import sys
import os
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
from grokproject.utils import run_buildout

VERSIONINFO_INFO_URL = 'http://grok.zope.org/releaseinfo/current'


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

def get_boolean_value_for_option(vars, option):
    value = vars.get(option.name)
    if value is not None:
        if isinstance(option.default, bool):
            want_boolean = True
        else:
            want_boolean = False
        value = value.lower()
        if value in ('1', 'true'):
            if want_boolean:
                value = True
            else:
                value = 'true'
        elif value in ('0', 'false'):
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

def get_version_info_url(vars, option):
    value = vars.get(option.name, '')
    if value == '':
        info = urllib.urlopen(VERSIONINFO_INFO_URL).read().strip()
        value = urlparse.urljoin(VERSIONINFO_INFO_URL, info)
    return value


class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        ask_var('user', 'Name of an initial administrator user', default=NoDefault),
        ask_var('passwd', 'Password for the initial administrator user',
            default=NoDefault, should_echo=False),
        ask_var('newest', 'Check for newer versions of packages',
                default='false', should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('version_info_url',
            "The URL to a *.cfg file containing a [versions] section.",
            default='', should_ask=False, getter=get_version_info_url),
        ask_var('run_buildout', "After creating the project area "
                "bootstrap the buildout.",
                default=True, should_ask=False,
                getter=get_boolean_value_for_option),
        ]

    def check_vars(self, vars, cmd):
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)

        skipped_vars = {}
        for var in list(self.vars):
            if not var.should_ask:
                skipped_vars[var.name] = var.getter(vars, var)
                self.vars.remove(var)

        vars = super(GrokProject, self).check_vars(vars, cmd)
        for name in skipped_vars:
            vars[name] = skipped_vars[name]

        for var_name in ['user', 'passwd']:
            # Escape values that go in site.zcml.
            vars[var_name] = xml.sax.saxutils.quoteattr(vars[var_name])
        vars['app_class_name'] = vars['project'].capitalize()
        return vars

    def post(self, command, output_dir, vars):
        if vars['run_buildout']:
            os.chdir(vars['project'])
            run_buildout(command.options.verbose)


def main():
    usage = "usage: %prog [options] PROJECT"
    parser = optparse.OptionParser(usage=usage)
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
    commands = command.get_commands()
    cmd = commands['create'].load()
    runner = cmd('create')

    option_args = []
    if options.repos is not None:
        option_args.extend(['--svn-repository', options.repos])
    if not options.verbose:
        option_args.append('-q')

    # Process the options that override the interactive part of filling
    # the templates.
    extra_args = []
    for var in GrokProject.vars:
        supplied_value = getattr(options, var.name)
        if supplied_value is not None:
            extra_args.append('%s=%s' % (var.name, supplied_value))
    exit_code = runner.run(option_args + ['-t', 'grok', project]
                           + extra_args)
    sys.exit(exit_code)
