import os
from typing import Any, Dict, List

import click

from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.launchable_client import LaunchableClient
from ...utils.key_value_type import normalize_key_value_types


@click.command()
@click.option(
    '--days',
    'days',
    help='How many days of test sessions in the past to be stat',
    type=int,
    default=7
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    metavar='KEY=VALUE',
    cls=KeyValueType,
    multiple=True,
)
@click.pass_context
def test_sessions(
    context: click.core.Context,
    days: int,
    flavor: List[str] = [],
):
    params: Dict[str, Any] = {'days': days, 'flavor': []}
    flavors = []
    for f in normalize_key_value_types(flavor):
        flavors.append('%s=%s' % (f[0], f[1]))

    if flavors:
        params['flavor'] = flavors
    else:
        params.pop('flavor', None)

    try:
        client = LaunchableClient(dry_run=context.obj.dry_run)
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
