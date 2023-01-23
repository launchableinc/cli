import os
from typing import List

import click

from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
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
    # We originally wanted to write it like `params: Dict[str, Any]`, but python 3.5 does not support it,
    # so we gave an empty list in the 'flavor' key to give a type hint.
    # If we don't write this, `pip run type` will assume it is Dict[str, int],
    # and the check will not pass.
    params = {'days': days, 'flavor': []}
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
