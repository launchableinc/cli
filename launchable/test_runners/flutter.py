import json
import pathlib
from typing import Dict, Generator, List, Optional

import click

from launchable.commands.record.case_event import CaseEvent
from launchable.testpath import FilePathNormalizer

from . import launchable

FLUTTER_FILE_EXT = "_test.dart"

FLUTTER_TEST_RESULT_SUCCESS = "success"
FLUTTER_TEST_RESULT_FAILURE = "error"


class TestCase:
    def __init__(self, id: int, name: str, is_skipped: bool = False):
        self._id: int = id
        self._name: str = name
        self._is_skipped: bool = is_skipped
        self._status: str = ""
        self._stdout: str = ""
        self._stderr: str = ""
        self._duration_sec: float = 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def status(self) -> int:  # status code see: case_event.py
        if self._is_skipped:
            return CaseEvent.TEST_SKIPPED
        elif self._status == FLUTTER_TEST_RESULT_SUCCESS:
            return CaseEvent.TEST_PASSED
        elif self._status == FLUTTER_TEST_RESULT_FAILURE:
            return CaseEvent.TEST_FAILED

        # safe fallback
        return CaseEvent.TEST_PASSED

    @status.setter
    def status(self, status: str):
        self._status = status

    @property
    def duration(self) -> float:
        return self._duration_sec

    @duration.setter
    def duration(self, duration_sec: float):
        self._duration_sec = duration_sec

    @property
    def stdout(self) -> str:
        return self._stdout

    @stdout.setter
    def stdout(self, stdout: str):
        self._stdout = stdout

    @property
    def stderr(self) -> str:
        return self._stderr

    @stderr.setter
    def stderr(self, stderr: str):
        self._stderr = stderr


class TestSuite:
    def __init__(self, id: int, platform: str, path: str):
        self._id = id
        self._platform = platform
        self._path = path
        self._test_cases: Dict[int, TestCase] = {}

    def _get_test_case(self, id: int) -> Optional[TestCase]:
        return self._test_cases.get(id)


class ReportParser:
    def __init__(self, file_path_normalizer: FilePathNormalizer):
        self.file_path_normalizer = file_path_normalizer
        self._suites: Dict[int, TestSuite] = {}

    def _get_suite(self, suite_id: int) -> Optional[TestSuite]:
        return self._suites.get(suite_id)

    def _get_test(self, test_id: int) -> Optional[TestCase]:
        if test_id is None:
            return None

        for s in self._suites.values():
            c = s._get_test_case(test_id)
            if c is not None:
                return c

        return None

    def _events(self) -> List:
        events = []
        for s in self._suites.values():
            for c in s._test_cases.values():
                events.append(CaseEvent.create(
                    test_path=[
                        {"type": "file", "name": pathlib.Path(self.file_path_normalizer.relativize(s._path)).as_posix()},
                        {"type": "testcase", "name": c.name}],
                    duration_secs=c.duration,
                    status=c.status,
                    stdout=c.stdout,
                    stderr=c.stderr,
                ))

        return events

    def parse_func(self, report_file: str) -> Generator[CaseEvent, None, None]:
        # TODO: Support cases that include information about `flutter pub get`
        # see detail: https://github.com/launchableinc/examples/actions/runs/11884312142/job/33112309450
        if not pathlib.Path(report_file).exists():
            click.echo(click.style("Error: Report file not found: {}".format(report_file), fg='red'), err=True)
            return

        with open(report_file, "r") as ndjson:
            try:
                for j in ndjson:
                    if not j.strip():
                        continue
                    try:
                        data = json.loads(j)
                        self._parse_json(data)
                    except json.JSONDecodeError:
                        click.echo(
                            click.style("Error: Invalid JSON format: {}. Skip load this line".format(j), fg='yellow'), err=True)
                        continue
            except Exception as e:
                click.echo(
                    click.style("Error: Failed to parse the report file: {} : {}".format(report_file, e), fg='red'), err=True)
                return

        for event in self._events():
            yield event

    def _parse_json(self, data: Dict):
        if not isinstance(data, Dict):
            # Note: array sometimes comes in but won't use it
            return

        data_type = data.get("type")
        if data_type is None:
            return
        elif data_type == "suite":
            suite_data = data.get("suite")
            if suite_data is None:
                # it's might be invalid suite data
                return

            suite_id = suite_data.get("id")
            if self._get_suite(suite_data.get("id")) is not None:
                # already recorded
                return

            self._suites[suite_id] = TestSuite(suite_id, suite_data.get("platform"), suite_data.get("path"))
        elif data_type == "testStart":
            test_data = data.get("test")

            if test_data is None:
                # it's might be invalid test data
                return
            if test_data.get("line") is None:
                # Still set up test case, should skip
                return

            suite_id = test_data.get("suiteID")
            suite = self._get_suite(suite_id)

            if suite_id is None or suite is None:
                click.echo(click.style(
                    "Warning: Cannot find a parent test suite (id: {}). So won't send test result of {}".format(
                        suite_id, test_data.get("name")), fg='yellow'), err=True)
                return

            test_id = test_data.get("id")
            test = self._get_test(test_id)
            if test is not None:
                # already recorded
                return

            name = test_data.get("name")
            metadata = test_data.get("metadata", {})
            is_skipped = metadata.get("skip", False)
            suite._test_cases[test_id] = TestCase(test_id, name, is_skipped)

        elif data_type == "testDone":
            test_id = data.get("testID")
            test = self._get_test(test_id)

            if test is None:
                return

            test.status = data.get("result", "success")  # safe fallback
            duration_msec = data.get("time", 0)
            test.duration = duration_msec / 1000  # to sec

        elif data_type == "error":
            test_id = data.get("testID")
            test = self._get_test(test_id)
            if test is None:
                click.echo(click.style(
                    "Warning: Cannot find a test (id: {}). So we skip update stderr".format(test_id), fg='yellow'),
                    err=True)
                return
            test.stderr += ("\n" if test.stderr else "") + data.get("error", "")

        elif data_type == "print":
            # It's difficult to identify the "Retry" case because Flutter reports it with the same test ID
            # So we won't handle it at the moment.
            test_id = data.get("testID")
            test = self._get_test(test_id)
            if test is None:
                click.echo(click.style(
                    "Warning: Cannot find a test (id: {}). So we skip update stdout".format(test_id), fg='yellow'),
                    err=True)
                return

            test.stdout += ("\n" if test.stdout else "") + data.get("message", "")

        else:
            return


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    file_path_normalizer = FilePathNormalizer(base_path=client.base_path, no_base_path_inference=client.no_base_path_inference)
    client.parse_func = ReportParser(file_path_normalizer).parse_func

    launchable.CommonRecordTestImpls.load_report_files(client=client, source_roots=reports)


subset = launchable.CommonSubsetImpls(__name__).scan_files('*.dart')
split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()
