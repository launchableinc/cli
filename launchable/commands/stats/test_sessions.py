import click
import os
from typing import Any, Dict, Sequence, List
from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient


@click.command()
@click.option(
    '--days',
    'days',
    help='subsetting target from 0% to 100%',
    type=int,
    default=7
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    cls=KeyValueType,
    multiple=True,
)
@click.pass_context
def test_sessions(
    context: click.core.Context,
    days: int,
    flavor: List[str] = [],
):
    try:
        test_runner = context.invoked_subcommand
        params = {'days': days, 'flavor': []}
        flavors = []
        for f in flavor:
            if isinstance(f, str):
                k, v = f.replace("(", "").replace(
                    ")", "").replace("'", "").split(",")
                flavors.append('%s=%s' % (k.strip(), v.strip()))
            elif isinstance(f, Sequence):
                flavors.append('%s=%s' % (f[0], f[1]))

        if flavors:
            params['flavor'] = flavors
        else:
            del params['flavor']

        client = LaunchableClient(
            test_runner=test_runner,
            dry_run=context.obj.dry_run)
        res = client.request('get', '/stats/test-sessions', params=params)
        res.raise_for_status()
        click.echo(res.text)

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
        click.echo(click.style(
            "Warning: the service failed to get stat.", fg='yellow'),
            err=True)
