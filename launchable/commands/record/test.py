import click
import json
from itertools import chain
import os
from junitparser import JUnitXml, Failure, Error, Skipped, TestSuite, TestCase

from .case_event import CaseEvent
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token
from ...utils.env_keys import REPORT_ERROR_KEY


@click.command()
@click.argument('xml_paths', required=True, nargs=-1)
@click.option(
    '--path',
    help='Test result file path',
    type=str
)
@click.option(
    '--name',
    'build_name',
    help='build identifier',
    required=True,
    type=str,
    metavar='BUILD_ID'
)
@click.option(
    '--source',
    help='repository district'
    'REPO_DIST like --source . ',
    default=".",
    metavar="REPO_NAME",
)
@click.option(
    '--session',
    'session_id',
    help='Test session ID',
    required=True,
    type=int,
)
def test(xml_paths, path, build_name, source, session_id):
    token, org, workspace = parse_token()

    # To understand JUnit XML format, https://llg.cubic.org/docs/junit/ is helpful
    xmls = [JUnitXml.fromfile(p) for p in xml_paths]
    testsuites = []
    for xml in xmls:
        if isinstance(xml, JUnitXml):
            testsuites += [suite for suite in xml]
        elif isinstance(xml, TestSuite):
            testsuites.append(xml)

    events = list(chain.from_iterable([CaseEvent.from_case_and_suite(case, suite, source).to_json()
                                       for case in suite] for suite in testsuites))

    headers = {
        "Content-Type": "application/json",
    }

    client = LaunchableClient(token)

    try:
        payload = {"events": events}
        print(payload)
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
