from typing import Annotated, List

import typer

from smart_tests.test_runners import smart_tests


@smart_tests.record.tests
def record_tests(
    client,
    reports: Annotated[List[str], typer.Argument(
        help="Test report files to process"
    )],
):
    for r in reports:
        typer.echo(f'foo:{r}')


@smart_tests.subset
def subset(client):
    typer.echo("Subset!")
