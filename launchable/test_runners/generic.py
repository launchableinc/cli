#
# The most bare-bone versions of the test runner support
#
import click
import sys
from . import launchable


@launchable.optimize.tests
def optimize_tests(client):
    for t in sys.stdin:
        client.test_path(t)
    client.run()


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)
    client.run()
