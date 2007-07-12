import sys
import os.path
import optparse
import shutil
import tempfile
import pkg_resources
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
    exit_code = runner.run(['-t', 'grokproject', project] + extra_args)
    # TODO exit_code

    if options.no_buildout:
        return

    os.chdir(project)

    try:
        import zc.buildout.buildout
    except ImportError:
        print "Downloading zc.buildout..."

        # Install buildout into a temporary location
        import setuptools.command.easy_install
        tmpdir = tempfile.mkdtemp()
        sys.path.append(tmpdir)
        setuptools.command.easy_install.main(['-mNxd', tmpdir, 'zc.buildout'])

        # Add downloaded buildout to PYTHONPATH by requiring it
        # through setuptools (this dance is necessary because the
        # temporary installation was done as multi-version).
        ws = pkg_resources.working_set
        ws.add_entry(tmpdir)
        ws.require('zc.buildout')

        import zc.buildout.buildout
        zc.buildout.buildout.main(['bootstrap'])
        shutil.rmtree(tmpdir)
    else:
        zc.buildout.buildout.main(['bootstrap'])

    print "Invoking zc.buildout..."
    zc.buildout.buildout.main(['install'])
