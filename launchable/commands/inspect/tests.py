import os
import sys
from http import HTTPStatus

import click
from tabulate import tabulate

from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient


@click.command()
@click.option(
    '--test-session-id',
    'test_session_id',
    help='test session id',
    required=True
)
def tests(test_session_id: int):
    try:
        client = LaunchableClient()
        res = client.request(
            "get", "/test_sessions/{}/events".format(test_session_id))

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(click.style(
                "Test session {} not found. Check test session ID and try again.".format(test_session_id), 'yellow'),
                err=True,
            )
            sys.exit(1)

        res.raise_for_status()
        results = res.json()
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
        click.echo(click.style(
            "Warning: failed to inspect tests", fg='yellow'),
            err=True)

        return

    header = ["Test Path",
              "Duration (sec)", "Status", "Uploaded At"]

    rows = []
    for result in results:
        if result.keys() >= {"testPath"}:
            rows.append(
                [
                    "#".join([path["type"] + "=" + path["name"]
                             for path in result["testPath"] if path.keys() >= {"type", "name"}]),
                    result.get("duration", 0.0),
                    result.get("status", ""),
                    result.get("createdAt", None),
                ]
            )

    click.echo(tabulate(rows, header, tablefmt="github", floatfmt=".2f"))
