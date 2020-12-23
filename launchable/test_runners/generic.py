#
# The most bare-bone versions of the test runner support
#
import click
import sys
from . import launchable


@launchable.subset
def subset(client):
    # read lines as test file names
    for t in sys.stdin:
        client.test_path(t)
    client.run()


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    # here we are implicitly assuming that test reports we read, combined with the default path builder,
    # produces test names that aligned with what `optimize_tests` function does above.
    # TODO: use a custom path builder to ensure this is always the case. This is too fragile.
    for r in reports:
        client.report(r)
    client.run()
