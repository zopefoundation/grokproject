import pkg_resources
pkg_resources.require('PasteScript')

from paste.script import templates
from paste.script.templates import var

class GrokProject(templates.Template):
    _template_dir = 'template'
    summary = "A grok project"
    required_templates = []

    vars = [
        # TODO required parameters
        var('user', 'Name of an initial administrator user'),
        var('passwd', 'Password for the initial administrator user'),
        ]

def main():
    import sys
    import os.path
    from paste.script import command

    # create sandbox using paste.script
    project = sys.argv[1]  # TODO parse arguments properly
    commands = command.get_commands()
    command = commands['create'].load()
    runner = command('create')
    exit_code = runner.run(['-t', 'grokproject', project])
    # TODO exit_code

    # bootstrap the buildout
    os.chdir(project)
    bootstrap_py = os.path.join(os.getcwd(), 'bootstrap', 'bootstrap.py')
    assert os.spawnle(os.P_WAIT, sys.executable, sys.executable,
                      bootstrap_py, os.environ) == 0

    # run the buildout
    bin_buildout = os.path.join(os.getcwd(), 'bin', 'buildout')
    assert os.spawnle(os.P_WAIT, sys.executable, sys.executable, bin_buildout,
                      os.environ) == 0
