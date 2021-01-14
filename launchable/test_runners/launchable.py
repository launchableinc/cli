import click, types, glob, os
from launchable.commands.subset import subset as subset_cmd
from launchable.commands.record.tests import tests as record_tests_cmd


def cmdname(m):
    """figure out the sub-command name from a test runner function"""

    # a.b.cde -> cde
    # xyz -> xyz
    #
    # In python module name the conventional separator is '_' but in command name,
    # it is '-', so we do replace that
    return m[m.rfind('.')+1:].replace('_','-')


def wrap(f, group, name=None):
    """
    Wraps a 'plugin' function into a click command and registers it to the given group.

    a plugin function receives the scanner object in its first argument
    """
    if not name:
        name = cmdname(f.__module__)
    d = click.command(name=name)
    cmd = d(click.pass_obj(f))
    group.add_command(cmd)
    return cmd


def subset(f): return wrap(f, subset_cmd)


record = types.SimpleNamespace()
record.tests = lambda f: wrap(f, record_tests_cmd)


class CommonRecordTestImpls:
    """
    Typical 'record tests' implementations that are reusable.
    """

    def __init__(self, module_name):
        self.cmdname = cmdname(module_name)

    def report_files(self):
        """
        Suitable for test runners that create a directory full of JUnit report files.

        'record tests' expect JUnit report/XML file names.
        """

        @click.argument('source_roots', required=True, nargs=-1)
        def record_tests(client, source_roots):
            # Accept both file names and GLOB patterns
            # Simple globs like '*.xml' can be dealt with by shell, but
            # not all shells consistently deal with advanced GLOBS like '**'
            # so it's worth supporting it here.
            for root in source_roots:
                match = False
                for t in glob.iglob(root, recursive=True):
                    match = True
                    if os.path.isdir(t):
                        client.scan(t, "*.xml")
                    else:
                        client.report(t)

                if not match:
                    # By following the shell convention, if the file doesn't exist or GLOB doesn't match anything,
                    # raise it as an error. Note this can happen for reasons other than a configuration error.
                    # For example, if a build catastrophically failed and no tests got run.
                    click.echo("No matches found: " % root, err=True)
                    # intentionally exiting with zero
                    return

            client.run()

        return wrap(record_tests, record_tests_cmd, self.cmdname)
