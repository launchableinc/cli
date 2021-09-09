import click
from launchable.test_runners import launchable


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        click.echo('foo:{}'.format(r))


@launchable.subset
def subset(client):
    click.echo("Subset!")
