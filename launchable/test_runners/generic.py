#
# The most bare-bone versions of the test runner support
#
import click
from . import launchable


@click.argument('tests', required=True, nargs=-1)
@launchable.optimize.tests
def optimize_tests(client, tests):
    # TODO: I think it's better to read tests from stdin
    for t in tests:
        client.test_path(t)
    client.run()


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)
    client.run()
