import glob
import json
import os
import traceback

import click
from junitparser import JUnitXml, TestSuite

from .case_event import CaseEvent
from ...testpath import TestPathComponent
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.gzipgen import compress
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token


@click.group()
@click.option(
    '--base',
    'base_path',
    help='(Advanced) base directory to make test names portable',
    type=click.Path(exists=True, file_okay=False),
    metavar="DIR",
)
@click.option(
    '--session',
    'session_id',
    help='Test session ID',
    # validate session_id under debug mode,
    required=os.getenv(REPORT_ERROR_KEY),
    type=str,
)
@click.pass_context
def tests(context, base_path, session_id: str):
    if not session_id:
        click.echo(
            "Session ID in --session is missing. It might be caused by Launchable API errors.", err=True)
        # intentionally exiting with zero
        return

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class
    class RecordTests:
        @property
        def path_builder(self) -> CaseEvent.TestPathBuilder:
            """
            This function, if supplied, is used to build a test path
            that uniquely identifies a test case
            """
            return self._path_builder

        @path_builder.setter
        def path_builder(self, v: CaseEvent.TestPathBuilder):
            self._path_builder = v

        def __init__(self):
            self.reports = []
            self.path_builder = CaseEvent.default_path_builder(base_path)

        def make_file_path_component(self, filepath) ->  TestPathComponent:
            """Create a single TestPathComponent from the given file path"""
            if base_path:
                filepath = os.path.relpath(filepath, start=base_path)
            return {"type": "file", "name": filepath}

        def report(self, junit_report_file: str):
            """Add one report file by its path name"""
            self.reports.append(junit_report_file)

        def scan(self, base, pattern):
            """
            Starting at the 'base' path, recursively add everything that matches the given GLOB pattern

            scan('build/test-reports', '**/*.xml')
            """
            for t in glob.iglob(os.path.join(base, pattern), recursive=True):
                self.report(t)

        def run(self):
            token, org, workspace = parse_token()

            # generator that creates the payload incrementally
            def payload():
                yield '{"events": ['
                first = True        # used to control ',' in printing

                for p in self.reports:
                    # To understand JUnit XML format, https://llg.cubic.org/docs/junit/ is helpful
                    # TODO: robustness: what's the best way to deal with broken XML file, if any?
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

                            yield json.dumps(CaseEvent.from_case_and_suite(self.path_builder, case, suite, p))
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
                res = client.request(
                    "post", "{}/events".format(session_id), data=payload, headers=headers)
                res.raise_for_status()

                print(res.status_code)

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    traceback.print_exc()

    context.obj = RecordTests()
