import click
import json
import os
from junitparser import JUnitXml, TestSuite

from .case_event import CaseEvent
from ...utils.http_client import LaunchableClient
from ...utils.gzipgen import compress
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
def tests(xml_paths, path, build_name, source, session_id):
    token, org, workspace = parse_token()

    # generator that creates the payload incrementally
    def payload():
        yield '{"events":['
        first = True        # use to control ',' in printing

        for p in xml_paths:
            # To understand JUnit XML format, https://llg.cubic.org/docs/junit/ is helpful
            # TODO: robustness: what's the best way to deal with brokeen XML file, if any?
            xml = JUnitXml.fromfile(p)

            if isinstance(xml, JUnitXml):
                testsuites = [suite for suite in xml]
            elif isinstance(xml, TestSuite):
                testsuites = [xml]
            else:
                # TODO: what is a Pythonesque way to do this?
                assert False

            for suite in testsuites:
                for case in suite:
                    if not first:
                        yield ','
                    first = False

                    yield json.dumps(CaseEvent.from_case_and_suite(case, suite, source).to_json())
        yield ']}'

    # TODO: this probably should be a flag
    if True:
        # generator adapter that prints the content
        def printer(f):
            for d in f:
                print(d)
                yield d
        payload = printer(payload())

    # str -> bytes then gzip compress
    payload = (s.encode() for s in payload)
    payload = compress(payload)

    headers = {
        "Content-Type": "application/json",
        "Content-Encoding": "gzip",
    }

    client = LaunchableClient(token)

    try:
        case_path = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}/events".format(
            org, workspace, build_name, session_id)
        res = client.request("post", case_path, data=payload, headers=headers)
        res.raise_for_status()

        print(res.status_code)

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)


# for backward compatibility
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
@click.pass_context
def test(ctx, xml_paths, path, build_name, source, session_id):
    ctx.forward(tests)
