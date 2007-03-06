import sys
import os.path
import optparse
import ConfigParser
from paste.script import templates, command
from paste.script.templates import var, NoDefault

class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        var('module', 'Name of a demo Python module placed into the package',
            default='app.py'),
        var('user', 'Name of an initial administrator user', default=NoDefault),
        var('passwd', 'Password for the initial administrator user',
            default=NoDefault),
        ]

    def check_vars(self, vars, cmd):
        vars = super(GrokProject, self).check_vars(vars, cmd)
        module = vars['module']
        if '.' in module:
            if module.endswith('.py'):
                vars['module'] = module[:-3]
            else:
                raise command.BadCommand('Bad module name: %s' % module)
        return vars

    def post(self, command, output_dir, vars):
        if 'zope3' in vars:
            # This means the user supplied the --with-zope3 parameter
            # and has a pre-installed Zope 3 lying around.  Let's edit
            # buildout.cfg so that it doesn't download Zope 3 but uses
            # the existing one.
            buildout_cfg = os.path.join(os.path.abspath(output_dir),
                                        'buildout.cfg')
            cfg = ConfigParser.ConfigParser()
            cfg.read(buildout_cfg)

            # remove 'zope3' from the list of parts as we don't have
            # to build Zope 3 anymore
            parts = cfg.get('buildout', 'parts').split()
            parts.remove('zope3')
            cfg.set('buildout', 'parts', ' '.join(parts))

            # add a 'location' attribute to the 'zope3' section that
            # points to the Zope 3 installation.  For clarity, we also
            # remove all other things from the section.
            for name in cfg.options('zope3'):
                cfg.remove_option('zope3', name)
            cfg.set('zope3', 'location', vars['zope3'])

            cfg.write(open(buildout_cfg, 'w'))

def main():
    usage = "usage: %prog [options] PROJECT"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--no-buildout', action="store_true", dest="no_buildout",
                      default=False, help="Only create project area, do not "
                      "bootstrap the buildout.")
    parser.add_option('--svn-repository', dest="repos", default=None,
                      help="Import project to given repository location (this "
                      "will also create the standard trunk/ tags/ branches/ "
                      "hierarchy)")
    parser.add_option('--with-zope3', dest="zope3", default=None,
                      help="Location of an existing Zope 3 installation. If "
                      "provided, grokproject will not download and install "
                      "Zope 3 itself.")
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        return 1

    # create sandbox using paste.script
    project = args[0]
    commands = command.get_commands()
    cmd = commands['create'].load()
    runner = cmd('create')

    extra_args = []
    if options.repos is not None:
        extra_args.extend(['--svn-repository', options.repos])
    if options.zope3 is not None:
        zope3 = os.path.expanduser(options.zope3)
        # TODO do some sanity checks here to see if the directory
        # actually exists and is a Zope 3 installation

        # add the path to the Zope 3 installation to the variables so
        # that the template has access to it.
        extra_args.append('zope3=%s' % zope3)
    exit_code = runner.run(['-t', 'grokproject', project] + extra_args)
    # TODO exit_code

    if options.no_buildout:
        return

    # bootstrap the buildout
    os.chdir(project)
    bootstrap_py = os.path.join(os.getcwd(), 'bootstrap', 'bootstrap.py')
    assert os.spawnle(os.P_WAIT, sys.executable, sys.executable,
                      bootstrap_py, os.environ) == 0

    # run the buildout
    bin_buildout = os.path.join(os.getcwd(), 'bin', 'buildout')
    assert os.spawnle(os.P_WAIT, sys.executable, sys.executable, bin_buildout,
                      os.environ) == 0
