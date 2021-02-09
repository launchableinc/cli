import os
import traceback

import click
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token


@click.command()
@click.option(
    '--session',
    'session_id',
    help='Test session ID',
    type=str,
    required=True,
)
def session(session_id: str):
    token, org, workspace = parse_token()

    headers = {
        "Content-Type": "application/json",
    }

    client = LaunchableClient(token)
    try:
        res = client.request(
            "patch", "{}/close".format(session_id), headers=headers)
        res.raise_for_status()
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            traceback.print_exc()
