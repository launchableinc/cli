import sys
import re
import click

from . import launchable
from ..testpath import TestPath


def make_test_path(cls, case) -> TestPath:
    return [{'type': 'class', 'name': cls}, {'type': 'case', 'name': case}]


@launchable.subset
def subset(client):
    # Read targets from stdin, which generally looks like //foo/bar:zot
    for label in sys.stdin:
        # handle ctest -N output
        # Test #1: FooTest.Bar -> (FooTest, Bar)
        result = re.match(r'^ *Test #\d+: ([^ ]+)$', label)
        if result:
            (cls, case) = result.group(1).split('.')
            client.test_path(make_test_path(cls, case))

    client.formatter = lambda x: x[0]['name'] + "." + x[1]['name']
    client.run()


@click.argument('report_dirs', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, report_dirs):
    for root in report_dirs:
        client.scan(root, "*.xml")
    client.run()
