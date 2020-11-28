import click
from .case_event import CaseEvent
from junitparser import JUnitXml, Failure, Error, Skipped, TestCase
from ...utils.http_client import LaunchableClient


@click.command()
@click.option(
    '--path',
    help='Test result file path',
    required=True,
    type=str,
)
@click.option(
    '--name',
    'build_number',
    help='build identifer',
    required=True,
    type=str,
    metavar='BUILD_ID'
)
def test(path, name):
    token, org, workspace = parse_token()

    xml = JUnitXml.fromfile(path)

    events = [[CaseEvent.from_case(case) for case in suite] for suite in xml]

    headers = {
        "Content-Type": "application/json",
    }

    client = LaunchableClient(token)

    payload = {events: events}
    session_path = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(
        org, workspace, name)
    res = client.request("post", session_path, data=json.dumps(
        payload).encode(), headers=headers)
    # not test yet
    session_id = res.json()['session_id']

    payload = {events: events}
    case_path = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}cases".format(
        org, workspace, name, session_id)
    res = client.request("post", case_path, data=json.dumps(
        payload).encode(), headers=headers)
