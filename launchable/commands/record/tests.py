import glob
import json
import os
import traceback

import click
from junitparser import JUnitXml, TestSuite
import xml.etree.ElementTree as ET
from typing import Callable

from .case_event import CaseEvent
from ...testpath import TestPathComponent
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.gzipgen import compress
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.session import read_session
from ...testpath import TestPathComponent
from .session import session


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
    type=str,
)
@click.option(
    '--build',
    'build_name',
    help='build name',
    type=str,
    metavar='BUILD_NAME'
)
@click.option(
    '--debug',
    help='print request payload',
    default=False,
    is_flag=True,
)
@click.pass_context
def tests(context, base_path: str, session_id: str, build_name: str, debug: bool):
    if session_id and build_name:
        raise click.UsageError(
            'Only one of -build or -session should be specified')

    if not session_id:
        if build_name:
            session_id = read_session(build_name)
            if not session_id:
                res = context.invoke(session, build_name=build_name, save_session_file=True, print_session=False)
                session_id = read_session(build_name)
        else:
            raise click.UsageError(
                'Either --build or --session has to be specified')

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class
    class RecordTests:
        # function that returns junitparser.TestCase
        # some libraries output invalid  incorrectly format then have to fix them.
        JUnitXmlParseFunc = Callable[[str],  ET.Element]

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

        @property
        def junitxml_parse_func(self):
            return self._junitxml_parse_func

        @junitxml_parse_func.setter
        def junitxml_parse_func(self, f: JUnitXmlParseFunc):
            self._junitxml_parse_func = f

        def __init__(self):
            self.reports = []
            self.path_builder = CaseEvent.default_path_builder(base_path)
            self.junitxml_parse_func = None

        def make_file_path_component(self, filepath) -> TestPathComponent:
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
                    xml = JUnitXml.fromfile(p, self.junitxml_parse_func)
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

            def printer(f):
                for d in f:
                    print(d)
                    yield d

            payload = printer(payload()) if debug else payload()

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
                res = client.request("patch", "{}/close".format(session_id), headers=headers)
                res.raise_for_status()
            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    traceback.print_exc()

    context.obj = RecordTests()
