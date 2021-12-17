import glob
from launchable.utils.authentication import get_org_workspace
import os
import traceback
import click
from junitparser import JUnitXml, TestSuite, TestCase  # type: ignore
import xml.etree.ElementTree as ET
from typing import Callable, Dict, Generator, List, Optional, Tuple
from more_itertools import ichunked
from .case_event import CaseEvent, CaseEventType
from ...utils.http_client import LaunchableClient
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.session import parse_session, read_build
from ...testpath import TestPathComponent, FilePathNormalizer
from ..helper import find_or_create_session
from http import HTTPStatus
from ...utils.click import KeyValueType
from ...utils.logger import Logger
import datetime
from dateutil.parser import parse
from tabulate import tabulate


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
    metavar='BUILD_NAME',
    hidden=True,
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
@click.option(
    "--no_base_path_inference",
    "no_base_path_inference",
    help="""Do not guess the base path to relativize the test file paths.

    By default, if the test file paths are absolute file paths, it automatically
    guesses the repository root directory and relativize the paths. With this
    option, the command doesn't do this guess work.

    If --base_path is specified, the absolute file paths are relativized to the
    specified path irrelevant to this option. Use it if the guessed base path is
    incorrect.
    """,
    is_flag=True
)
@click.pass_context
def tests(context, base_path: str, session: Optional[str], build_name: Optional[str], post_chunk: int, subsetting_id: str,
          flavor, no_base_path_inference):
    file_path_normalizer = FilePathNormalizer(
        base_path, no_base_path_inference=no_base_path_inference)

    if subsetting_id:
        result = get_session_and_record_start_at_from_subsetting_id(
            subsetting_id)
        session_id = result["session"]
        record_start_at = result["start_at"]
    else:
        session_id = find_or_create_session(
            context, session, build_name, flavor)
        build_name = read_build()
        record_start_at = get_record_start_at(session_id)

    logger = Logger()

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class

    class RecordTests:
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

            def parse(report: str) -> Generator[CaseEventType, None, None]:
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

        def __init__(self, dry_run=False):
            self.reports = []
            self.skipped_reports = []
            self.path_builder = CaseEvent.default_path_builder(
                file_path_normalizer)
            self.junitxml_parse_func = None
            self.check_timestamp = True
            self.base_path = base_path
            self.dry_run = dry_run

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
            client = LaunchableClient(test_runner=context.invoked_subcommand,
                                      dry_run=context.obj.dry_run)

            def testcases(reports: List[str]) -> Generator[CaseEventType, None, None]:
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
            def payload(cases: Generator[TestCase, None, None]) -> Tuple[Dict[str, List], List[Exception]]:
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
                res = client.request(
                    "post", "{}/events".format(session_id), payload=payload, compress=True)

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

            def recorded_result() -> Tuple[int, int, int, float]:
                test_count = 0
                success_count = 0
                fail_count = 0
                duration = float(0)

                for tc in testcases(self.reports):
                    test_count += 1
                    status = tc.get("status")
                    if status == 0:
                        fail_count += 1
                    elif status == 1:
                        success_count += 1
                    duration += float(tc.get("duration") or 0)  # sec

                return test_count, success_count, fail_count, duration/60   # sec to min

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

            if count == 0:
                if len(self.skipped_reports) != 0:
                    click.echo(click.style(
                        "{} test reports were skipped because they were created before `launchable record build` was run.\nMake sure to run tests after running `launchable record build`.".format(len(self.skipped_reports)), 'yellow'))
                    return
                else:
                    click.echo(click.style(
                        "Looks like tests didn't run? If not, make sure the right files/directories are passed", 'yellow'))
                    return

            build_name, test_session_id = parse_session(session_id)
            org, workspace = get_org_workspace()

            file_count = len(self.reports)
            test_count, success_count, fail_count, duration = recorded_result()

            click.echo(
                "Launchable recorded tests for build {} (test session {}) to workspace {}/{} from {} files:\n".format(build_name, test_session_id, org, workspace, file_count))

            header = ["Files found", "Tests found", "Tests passed",
                      "Tests failed", "Total duration (min)"]

            rows = [[file_count, test_count,
                     success_count, fail_count, "{:0.4f}".format(duration)]]
            click.echo(tabulate(rows, header, tablefmt="github"))

            click.echo(
                "\nRun `launchable inspect tests --test-session-id {}` to view uploaded test results".format(test_session_id))

    context.obj = RecordTests(dry_run=context.obj.dry_run)


# if we fail to determine the timestamp of the build, we err on the side of collecting more test reports
# than no test reports, so we use the 'epoch' timestamp
INVALID_TIMESTAMP = datetime.datetime.fromtimestamp(0)


def get_record_start_at(session: Optional[str]):
    """
    Determine the baseline timestamp to be used for up-to-date checks of report files.
    Only files newer than this timestamp will be collected.

    Based on the thinking that if a build doesn't exist tests couldn't have possibly run, we attempt
    to use the timestamp of a build, with appropriate fallback.
    """
    if session is None:
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
        raise click.UsageError(click.style("Unable to get subset information from subset id {}".format(
            subsetting_id), 'yellow'), err=True)

    build_number = res.json()["build"]["buildNumber"]
    created_at = res.json()["build"]["createdAt"]
    test_session_id = res.json()["testSession"]["id"]

    return {
        "session": "builds/{}/test_sessions/{}".format(build_number, test_session_id),
        "start_at": parse_launchable_timeformat(created_at)
    }
