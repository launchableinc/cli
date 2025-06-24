from typing import Annotated, Any, Dict, List

import typer

from ...dependency import get_application
from ...utils.launchable_client import LaunchableClient
from ...utils.typer_types import validate_key_value

app = typer.Typer(name="test-sessions", help="View test session statistics")


@app.command()
def test_sessions(
    days: Annotated[int, typer.Option(
        help="How many days of test sessions in the past to be stat"
    )] = 7,
    flavor: Annotated[List[str], typer.Option(
        help="flavors",
        metavar="KEY=VALUE"
    )] = [],
):
    app = get_application()

    # Parse flavors
    parsed_flavors = [validate_key_value(f) for f in flavor]

    params: Dict[str, Any] = {'days': days, 'flavor': []}
    flavors = []
    for f in parsed_flavors:
        flavors.append('%s=%s' % (f[0], f[1]))

    if flavors:
        params['flavor'] = flavors
    else:
        params.pop('flavor', None)

    client = LaunchableClient(app=app)
    try:
        res = client.request('get', '/stats/test-sessions', params=params)
        res.raise_for_status()
        typer.echo(res.text)

    except Exception as e:
        client.print_exception_and_recover(e, "Warning: the service failed to get stat.")
