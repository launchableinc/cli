import glob
import os
import traceback
import click
from junitparser import JUnitXml, TestSuite, TestCase  # type: ignore
import xml.etree.ElementTree as ET
from typing import Callable, Dict, Generator,  List, Optional
from more_itertools import ichunked
from .case_event import CaseEvent
from ...utils.http_client import LaunchableClient
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.session import parse_session
from ...testpath import TestPathComponent
from launchable.commands.helper import find_or_create_session
from http import HTTPStatus
from ...utils.click import KeyValueType
from ...utils.logger import Logger
import datetime
from dateutil.parser import parse


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
    'session',
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
    '--subset-id',
    'subsetting_id',
    help='subset_id',
    type=str,
)
@click.option(
    '--post-chunk',
    help='Post chunk',
    default=1000,
    type=int
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    cls=KeyValueType,
    multiple=True,
)
@click.pass_context
def tests(context, base_path: str, session: Optional[str], build_name: Optional[str], post_chunk: int, subsetting_id: str,
          flavor):

    if subsetting_id:
        result = get_session_and_record_start_at_from_subsetting_id(
            subsetting_id)
        session_id = result["session"]
        record_start_at = result["start_at"]
    else:
        session_id = find_or_create_session(
            context, session, build_name, flavor)

        record_start_at = get_record_start_at(build_name, session)

    logger = Logger()

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class

    class RecordTests:
        CaseEventType = Dict[str, str]
        # The most generic form of parsing, where a path to a test report
        # is turned into a generator by using CaseEvent.create()
        ParseFunc = Callable[[str], Generator[CaseEventType, None, None]]

        # A common mechanism to build ParseFunc by building JUnit XML report in-memory (or build it the usual way
        # and patch it to fix things up). This is handy as some libraries produce invalid / broken JUnit reports
        JUnitXmlParseFunc = Callable[[str], ET.Element]

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
        def parse_func(self) -> ParseFunc:
            return self._parse_func

        @parse_func.setter
        def parse_func(self, f: ParseFunc):
            self._parse_func = f

        # setter only property that sits on top of the parse_func property
        def set_junitxml_parse_func(self, f: JUnitXmlParseFunc):
            """
            Parse XML report file with the JUnit report file, possibly with the custom parser function 'f'
            that can be used to build JUnit ET.Element tree from scratch or do some patch up.

            If f=None, the default parse code from JUnitParser module is used.
            """

            def parse(report: str) -> Generator[RecordTests.CaseEventType, None, None]:
                # To understand JUnit XML format, https://llg.cubic.org/docs/junit/ is helpful
                # TODO: robustness: what's the best way to deal with broken XML file, if any?
                xml = JUnitXml.fromfile(report, f)
                if isinstance(xml, JUnitXml):
                    testsuites = [suite for suite in xml]
                elif isinstance(xml, TestSuite):
                    testsuites = [xml]
                else:
                    # TODO: what is a Pythonesque way to do this?
                    assert False

                for suite in testsuites:
                    for case in suite:
                        yield CaseEvent.from_case_and_suite(self.path_builder, case, suite, report)

            self.parse_func = parse

        junitxml_parse_func = property(None, set_junitxml_parse_func)

        @property
        def check_timestamp(self):
            return self._check_timestamp

        @check_timestamp.setter
        def check_timestamp(self, enable: bool):
            self._check_timestamp = enable

        def __init__(self):
            self.reports = []
            self.skipped_reports = []
            self.path_builder = CaseEvent.default_path_builder(base_path)
            self.junitxml_parse_func = None
            self.check_timestamp = True

        def make_file_path_component(self, filepath) -> TestPathComponent:
            """Create a single TestPathComponent from the given file path"""
            if base_path:
                filepath = os.path.relpath(filepath, start=base_path)
            return {"type": "file", "name": filepath}

        def report(self, junit_report_file: str):
            ctime = datetime.datetime.fromtimestamp(
                os.path.getctime(junit_report_file))

            if self.check_timestamp and ctime.timestamp() < record_start_at.timestamp():
                format = "%Y-%m-%d %H:%M:%S"
                logger.warning("skip: {} is too old to report. start_record_at: {} file_created_at: {}".format(
                    junit_report_file, record_start_at.strftime(format), ctime.strftime(format)))
                self.skipped_reports.append(junit_report_file)

                return

            self.reports.append(junit_report_file)

        def scan(self, base: str, pattern: str):
            """
            Starting at the 'base' path, recursively add everything that matches the given GLOB pattern

            scan('build/test-reports', '**/*.xml')
            """
            for t in glob.iglob(os.path.join(base, pattern), recursive=True):
                self.report(t)

        def run(self):
            count = 0  # count number of test cases sent
            client = LaunchableClient(test_runner=context.invoked_subcommand)

            def testcases(reports: List[str]) -> Generator[RecordTests.CaseEventType, None, None]:
                exceptions = []
                for report in reports:
                    try:
                        yield from self.parse_func(report)

                    except Exception as e:
                        exceptions.append(Exception(
                            "Failed to process a report file: {}".format(report), e))

                if len(exceptions) > 0:
                    # defer XML parsing exceptions so that we can send what we can send before we bail out
                    raise Exception(exceptions)

            # generator that creates the payload incrementally
            def payload(cases: Generator[TestCase, None, None]) -> (Dict[str, List], List[Exception]):
                nonlocal count
                cs = []
                exs = []

                while True:
                    try:
                        cs.append(next(cases))
                    except StopIteration:
                        break
                    except Exception as ex:
                        exs.append(ex)

                count += len(cs)
                return {"events": cs}, exs

            def send(payload: Dict[str, List]) -> None:
                res = client.request("post", "{}/events".format(session_id), payload=payload, compress=True)

                if res.status_code == HTTPStatus.NOT_FOUND:
                    if session:
                        build, _ = parse_session(session)
                        click.echo(click.style(
                            "Session {} was not found. Make sure to run `launchable record session --build {}` before `launchable record tests`".format(
                                session, build), 'yellow'), err=True)
                    elif build_name:
                        click.echo(click.style(
                            "Build {} was not found. Make sure to run `launchable record build --name {}` before `launchable record tests`".format(
                                build_name, build_name), 'yellow'), err=True)

                res.raise_for_status()

            try:
                tc = testcases(self.reports)

                exceptions = []
                for chunk in ichunked(tc, post_chunk):
                    p, es = payload(chunk)

                    send(p)
                    exceptions.extend(es)

                res = client.request("patch", "{}/close".format(session_id))
                res.raise_for_status()

                if len(exceptions) > 0:
                    raise Exception(exceptions)

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    traceback.print_exc()
                    return

            click.echo("Recorded {} tests".format(count))
            if count == 0:
                if len(self.skipped_reports) != 0:
                    click.echo(click.style(
                        "{} test reports were skipped because they were created before `launchable record build`.\nMake sure to run test after `launchable record build`.".format(len(self.skip_reports)), 'yellow'))
                else:
                    click.echo(click.style(
                        "Looks like tests didn't run? If not, make sure the right files/directories are passed", 'yellow'))

    context.obj = RecordTests()


# if we fail to determine the timestamp of the build, we err on the side of collecting more test reports
# than no test reports, so we use the 'epoch' timestamp
INVALID_TIMESTAMP = datetime.datetime.fromtimestamp(0)

def get_record_start_at(build_name: Optional[str], session: Optional[str]):
    """
    Determine the baseline timestamp to be used for up-to-date checks of report files.
    Only files newer than this timestamp will be collected.

    Based on the thinking that if a build doesn't exist tests couldn't have possibly run, we attempt
    to use the timestamp of a build, with appropriate fallback.
    """
    if session is None and build_name is None:
        raise click.UsageError(
            'Either --build or --session has to be specified')

    if session:
        build_name, _ = parse_session(session)

    client = LaunchableClient()
    sub_path = "builds/{}".format(build_name)

    res = client.request("get", sub_path)
    if res.status_code != 200:
        if res.status_code == 404:
            msg = "Build {} was not found. Make sure to run `launchable record build --name {}` before `launchable record tests`".format(
                build_name, build_name)
        else:
            msg = "Unable to determine the timestamp of the build {}. HTTP response code was {}".format(build_name,
                                                                                                        res.status_code)
        click.echo(click.style(msg, 'yellow'), err=True)

        # to avoid stop report command
        return INVALID_TIMESTAMP

    created_at = res.json()["createdAt"]
    Logger().debug("Build {} timestamp = {}".format(build_name, created_at))
    t = parse_launchable_timeformat(created_at)
    return t


def parse_launchable_timeformat(t: str) -> datetime.datetime:
    # e.g) "2021-04-01T09:35:47.934+00:00"
    try:
        return parse(t)
    except Exception as e:
        Logger().error("parse time error {}. time: {}".format(str(e), t))
        return INVALID_TIMESTAMP


def get_session_and_record_start_at_from_subsetting_id(subsetting_id):
    s = subsetting_id.split('/')

    # subset/{id}
    if len(s) != 2:
        raise click.UsageError(
            'Invalid subset id. like `subset/123/slice` but got {}'.format(subsetting_id))

    res = LaunchableClient().request("get", subsetting_id)
    if res.status_code != 200:
        raise click.echo(click.style("Unable to get subset information from subset id {}".format(
            subsetting_id), 'yellow'), err=True)

    build_number = res.json()["build"]["buildNumber"]
    created_at = res.json()["build"]["createdAt"]
    test_session_id = res.json()["testSession"]["id"]

    return {
        "session": "builds/{}/test_sessions/{}".format(build_number, test_session_id),
        "start_at": parse_launchable_timeformat(created_at)
    }
