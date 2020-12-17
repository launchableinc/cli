import click
import json
import os
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token


@click.command(help="Subsetting tests")
@click.argument('test_paths', required=True, nargs=-1)
@click.option(
    '--target',
    'target',
    help='subsetting target percentage 0.0-1.0',
    required=True,
    type=float,
    default=0.8,
)
@click.option(
    '--session',
    'session_id',
    help='Test session ID',
    required=True,
    type=int,
)
@click.option(
    '--source',
    help='repository district'
    'REPO_DIST like --source . ',
    metavar="REPO_NAME",
)
@click.option(
    '--name',
    'build_name',
    help='build identifier',
    required=True,
    type=str,
    metavar='BUILD_ID'
)
def test(test_paths, target, session_id, source, build_name):
    token, org, workspace = parse_token()

    test_paths = [os.path.relpath(
        path, start=source) if source else path for path in test_paths]

    try:
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "testNames": test_paths,
            "target": target,
            "session": {
                "id": session_id
            }
        }

        path = "/intake/organizations/{}/workspaces/{}/subset".format(
            org, workspace)

        client = LaunchableClient(token)
        res = client.request("post", path, data=json.dumps(
            payload).encode(), headers=headers)
        res.raise_for_status()

        subsetted_paths = res.json()["testNames"]
        click.echo(" ".join(subsetted_paths))
    except Exception as e:
        # When Error occurs, return the test name as it is passed.
        click.echo(" ".join(test_paths))
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
