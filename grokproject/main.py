import sys
from paste.script import command
import optparse
from grokproject import GrokProject


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
