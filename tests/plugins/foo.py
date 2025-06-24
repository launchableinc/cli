from typing import Annotated, List

import typer

from launchable.test_runners import launchable


@launchable.record.tests
def record_tests(
    client,
    reports: Annotated[List[str], typer.Argument(
        help="Test report files to process"
    )],
):
    for r in reports:
        typer.echo('foo:{}'.format(r))


@launchable.subset
def subset(client):
    typer.echo("Subset!")
