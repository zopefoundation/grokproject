import sys
import os
import urllib
import urlparse
import xml.sax.saxutils
from paste.script import templates
from paste.script.templates import NoDefault
from grokproject.utils import run_buildout
from grokproject.utils import ask_var
from grokproject.utils import get_boolean_value_for_option
from grokproject.utils import create_buildout_default_file
from grokproject.utils import exist_buildout_default_file
from grokproject.utils import required_grok_version

GROK_RELEASE_URL = 'http://grok.zope.org/releaseinfo/'


class GrokProject(templates.Template):
    _template_dir = 'template_paste'
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
        ask_var('run_buildout',
                "After creating the project area, run the buildout.",
                default=True, should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('eggs_dir',
                'Location where zc.buildout will look for and place packages',
                default='', should_ask=False),
        ask_var('zopectl',
                "Use zopectl",
                default=False, should_ask=False,
                getter=get_boolean_value_for_option),
        ]

    def check_vars(self, vars, cmd):
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)

        explicit_eggs_dir = vars.get('eggs_dir')
        
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

        if vars['zopectl']:
            self._template_dir = 'template'
        
        # Handling the version.cfg file.
        print "Downloading info about versions..."
        current_info_url = GROK_RELEASE_URL + 'current'
        try:
            info = urllib.urlopen(current_info_url).read().strip()
        except IOError:
            print "Error: cannot download required %s" % current_info_url
            print "Server may be down.  Please try again later."
            sys.exit(1)
        version_info_url = urlparse.urljoin(current_info_url, info)
        vars['version_info_url'] = version_info_url
        try:
            version_info_file_contents = urllib.urlopen(version_info_url).read()
        except IOError:
            print "Error: cannot download required %s" % version_info_url
            print "Server may be down.  Please try again later."
            sys.exit(1)
        vars['version_info_file_contents'] = version_info_file_contents

        # Which grok version are we depending on?
        version = required_grok_version(vars['version_info_file_contents'])
        vars['grokversion'] = version

        buildout_default = exist_buildout_default_file()
        if explicit_eggs_dir:
            # Put explicit_eggs_dir in the vars; used by the post command.
            vars['explicit_eggs_dir'] = explicit_eggs_dir
            vars['eggs_dir'] = (
                '# Warning: when you share this buildout.cfg with friends\n'
                '# please remove the eggs-directory line as it is hardcoded.\n'
                'eggs-directory = %s') % explicit_eggs_dir
        elif buildout_default:
            vars['eggs-dir'] = ''
        else:
            create_buildout_default_file()

        return vars

    def post(self, command, output_dir, vars):
        if not vars['run_buildout']:
            return
        os.chdir(vars['project'])
        run_buildout(command.options.verbose)
