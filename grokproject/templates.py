import sys
import os
import urllib
import urlparse
import xml.sax.saxutils
from paste.script import templates
from paste.script.templates import NoDefault
from grokproject.utils import run_buildout
from grokproject.utils import default_eggs_dir
from grokproject.utils import get_buildout_default_eggs_dir
from grokproject.utils import ask_var
from grokproject.utils import get_var
from grokproject.utils import get_boolean_value_for_option
from grokproject.utils import create_buildout_defaults_file

VERSIONINFO_INFO_URL = 'http://grok.zope.org/releaseinfo/current'


class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        ask_var('user', 'Name of an initial administrator user',
                default=NoDefault),
        ask_var('passwd', 'Password for the initial administrator user',
                default=NoDefault, should_echo=False),
        ask_var('newest', 'Check for newer versions of packages',
                default='false', should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('run_buildout', "After creating the project area "
                "bootstrap the buildout.",
                default=True, should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('eggs_dir',
                'Location where zc.buildout will look for and place packages',
                default=default_eggs_dir()),
        ]

    def check_vars(self, vars, cmd):
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)

        explicit_eggs_dir = vars.get('eggs_dir')
        # Do not ask for eggs dir when we have a default already.
        buildout_default = get_buildout_default_eggs_dir()
        if buildout_default is not None:
            var = get_var(self.vars, 'eggs_dir')
            var.should_ask = False

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

        # Handling the version.cfg file.
        info = urllib.urlopen(VERSIONINFO_INFO_URL).read().strip()
        version_info_url = urlparse.urljoin(VERSIONINFO_INFO_URL, info)
        vars['version_info_url'] = version_info_url
        version_info_file_contents = urllib.urlopen(version_info_url).read()
        vars['version_info_file_contents'] = version_info_file_contents

        if explicit_eggs_dir is None:
            vars['eggs_dir'] = os.path.expanduser(vars['eggs_dir'])
        else:
            vars['eggs_dir'] = os.path.expanduser(explicit_eggs_dir)
        if buildout_default is None:
            create_buildout_defaults_file(vars['eggs_dir'])
        buildout_default = get_buildout_default_eggs_dir()
        if vars['eggs_dir'] == buildout_default:
            vars['eggs_dir'] = ''
        else:
            vars['eggs_dir'] = (
                '# Warning: when you share this buildout.cfg with friends\n'
                '# please remove the eggs-directory line as it is hardcoded.\n'
                'eggs-directory = %s') % vars['eggs_dir']
        return vars

    def post(self, command, output_dir, vars):
        if vars['run_buildout']:
            os.chdir(vars['project'])
            run_buildout(command.options.verbose)
