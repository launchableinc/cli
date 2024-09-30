from typing import Any, Dict, Sequence, Tuple

import click

from ...utils.click import KEY_VALUE
from ...utils.launchable_client import LaunchableClient


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
    type=KEY_VALUE,
    default=(),
    multiple=True,
)
@click.pass_context
def test_sessions(
    context: click.core.Context,
    days: int,
    flavor: Sequence[Tuple[str, str]] = (),
):
    params: Dict[str, Any] = {'days': days, 'flavor': []}
    flavors = []
    for f in flavor:
        flavors.append('%s=%s' % (f[0], f[1]))

    if flavors:
        params['flavor'] = flavors
    else:
        params.pop('flavor', None)

    client = LaunchableClient(app=context.obj)
    try:
        res = client.request('get', '/stats/test-sessions', params=params)
        res.raise_for_status()
        click.echo(res.text)

    except Exception as e:
        client.print_exception_and_recover(e, "Warning: the service failed to get stat.")
