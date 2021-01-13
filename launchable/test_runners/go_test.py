import sys
import click
from . import launchable

@launchable.subset
def subset(client):
    for case in sys.stdin:
        # Avoid last line such as `ok      github.com/launchableinc/rocket-car-gotest      0.268s`
        if not ' ' in case:
            client.test_path([{'type': 'testcase', 'name': case.rstrip('\n')}])

    client.formatter = lambda x: "^{}$".format(x[0]['name'])
    client.separator = '|'
    client.run()


@click.argument('source_roots', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, source_roots):
    for root in source_roots:
        client.scan(root, "*.xml")
    client.run()
