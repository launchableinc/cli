import click
import json
from itertools import chain
import os
from junitparser import JUnitXml, Failure, Error, Skipped, TestCase

from .case_event import CaseEvent
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token
from ...utils.env_keys import REPORT_ERROR_KEY


@click.command()
@click.option(
    '--path',
    help='Test result file path',
    required=True,
    type=str,
    multiple=True
)
@click.option(
    '--name',
    'build_name',
    help='build identifer',
    required=True,
    type=str,
    metavar='BUILD_ID'
)
@click.option(
    '--source',
    help='repository name and repository district. please specify'
    'REPO_DIST like --source . '
    'or REPO_NAME=REPO_DIST like --source main=./main --source lib=./main/lib',
    default=".",
    metavar="REPO_NAME",
)
def test(path, build_name, source):
    token, org, workspace = parse_token()

    # To understand JUnit XML format, https://llg.cubic.org/docs/junit/ is helpful
    xmls = [JUnitXml.fromfile(p) for p in path]
    events = list(chain.from_iterable(chain.from_iterable([CaseEvent.from_case_and_suite(case, suite, source).to_json()
                                                           for case in suite] for suite in xml) for xml in xmls))

    headers = {
        "Content-Type": "application/json",
    }

    client = LaunchableClient(token)

    try:
        session_path = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(
            org, workspace, build_name)
        res = client.request("post", session_path, headers=headers)
        res.raise_for_status()

        session_id = res.json()['id']
        print("Session ID: {}".format(session_id))

        payload = {"events": events}
        case_path = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}/events".format(
            org, workspace, build_name, session_id)
        res = client.request("post", case_path, data=json.dumps(
            payload).encode(), headers=headers)
        res.raise_for_status()

        print(res.status_code)

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)
