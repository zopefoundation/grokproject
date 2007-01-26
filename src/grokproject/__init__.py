import sys
import os.path
import optparse
from paste.script import templates, command
from paste.script.templates import var, NoDefault

class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        var('module', 'Name of an demo Python module placed into the package',
            default=NoDefault),
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
    exit_code = runner.run(extra_args + ['-t', 'grokproject', project])
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
