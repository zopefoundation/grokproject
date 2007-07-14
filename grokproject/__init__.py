from zopeproject.script import create_project
from paste.script.templates import Template, var

class GrokApp(Template):
    _template_dir = 'template'
    summary = 'Package that contains a Grok application'
    required_templates = ['zope_deploy']

    vars = [
        var('module', 'Name of a demo Python module placed into the package',
            default='app.py')
        ]

    def check_vars(self, vars, cmd):
        vars = super(GrokApp, self).check_vars(vars, cmd)
        module = vars['module']
        if '.' in module:
            if module.endswith('.py'):
                vars['module'] = module[:-3]
            else:
                raise command.BadCommand('Bad module name: %s' % module)
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)
        return vars

def main():
    create_project('grok_app')
