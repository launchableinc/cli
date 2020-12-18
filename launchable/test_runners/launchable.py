import click
from launchable.commands.optimize.tests import tests as optimize_tests
from launchable.commands.record.tests import tests as record_tests

def cmdname(f):
    """figure out the sub-command name from a test runner function"""

    # a.b.cde -> cde
    m = f.__module__
    return m[m.rindex('.')+1:]

def wrap(f, group):
    """
    Wraps a 'plugin' function into a click command and registers it to the given group.

    a plugin function receives the scanner object in its first argument
    """
    d = click.command(name=cmdname(f))
    cmd = d(click.pass_obj(f))
    group.add_command(cmd)
    return cmd


def test_scanner(f):
    return wrap(f, optimize_tests)

def report_scanner(f):
    return wrap(f, record_tests)
