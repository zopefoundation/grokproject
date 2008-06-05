import sys
import os
import urllib
import urlparse
import shutil
import tempfile
import xml.sax.saxutils
import tarfile
from paste.script import templates
from paste.script.templates import NoDefault
from grokproject.utils import run_buildout
from grokproject.utils import get_buildout_default_eggs_dir
from grokproject.utils import ask_var
from grokproject.utils import get_boolean_value_for_option
from grokproject.utils import create_buildout_default_file
from grokproject.utils import exist_buildout_default_file
from grokproject.utils import required_grok_version
from grokproject.utils import is_grok_installed
from grokproject.utils import install_grok

GROK_RELEASE_URL = 'http://grok.zope.org/releaseinfo/'

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
        ask_var('run_buildout',
                "After creating the project area, run the buildout.",
                default=True, should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('eggs_dir',
                'Location where zc.buildout will look for and place packages',
                default='', should_ask=False),
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

        # Handling the version.cfg file.
        current_info_url = GROK_RELEASE_URL + 'current'
        info = urllib.urlopen(current_info_url).read().strip()
        version_info_url = urlparse.urljoin(current_info_url, info)
        vars['version_info_url'] = version_info_url
        version_info_file_contents = urllib.urlopen(version_info_url).read()
        vars['version_info_file_contents'] = version_info_file_contents

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
        eggs_dir = vars.get('explicit_eggs_dir',
                            get_buildout_default_eggs_dir())
        if not os.path.isdir(eggs_dir):
            os.mkdir(eggs_dir)

        version = required_grok_version(vars['version_info_file_contents'])
        if not is_grok_installed(target_dir=eggs_dir, version=version):
            print "Grok is not installed. A grok tarball will be downloaded."

            tarball_name = 'grok-eggs-%s.tgz' % version
            url = GROK_RELEASE_URL + tarball_name
            print "Downloading %s ..." % url

            try:
                extraction_dir = tempfile.mkdtemp()
                filenum, temp_tarball_name = tempfile.mkstemp()
                tarball = open(temp_tarball_name, 'w')
                tarball.write(urllib.urlopen(url).read())
                tarball.close()
                print "Finished downloading."
                print "Installing eggs to %s ..." % eggs_dir

                try:
                    tf = tarfile.open(temp_tarball_name,
                                      'r:gz')
                except tarfile.ReadError, e:
                    print "ReadError: %s.  Not using tarball." % e
                else:
                    links = []
                    for name in tf.getnames():
                        tf.extract(name, extraction_dir)
                        links.append(os.path.join(extraction_dir, name))
                    tf.close()

                    result = install_grok(target_dir=eggs_dir, version=version,
                                          links=links)
                    if result is False:
                        print "Failed to install Grok with the tar ball."
                        print "Continuing with buildout instead."
            finally:
                shutil.rmtree(extraction_dir)
                os.unlink(temp_tarball_name)

        run_buildout(command.options.verbose)
