import json
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
        self._id = id
        self._name = name
        self._is_skipped = is_skipped
        self._status = None
        self._stdout = ""
        self._stderr = ""
        self._duration_sec = 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def status(self) -> CaseEvent:
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
        self._test_cases: List[TestCase] = []

    def _get_test_case(self, id: int) -> Optional[TestCase]:
        if id is None:
            return

        for c in self._test_cases:
            if c.id == id:
                return c


class ReportParser:
    def __init__(self, client):
        self.client = client
        self.file_path_normalizer = FilePathNormalizer(base_path=client.base_path,
                                                       no_base_path_inference=client.no_base_path_inference)
        self._suites: List[TestSuite] = []

    def _get_suite(self, suite_id: int) -> Optional[TestSuite]:
        if suite_id is None:
            return

        for s in self._suites:
            if s._id == suite_id:
                return s

    def _get_test(self, test_id: int) -> Optional[TestCase]:
        if test_id is None:
            return

        for s in self._suites:
            for c in s._test_cases:
                if c.id == test_id:
                    return c

    def _events(self) -> List[CaseEvent]:
        events = []
        for s in self._suites:
            for c in s._test_cases:
                events.append(CaseEvent.create(
                    test_path=[{"type": "file", "name": s._path, }, {"type": "testcase", "name": c.name}],
                    duration_secs=c.duration,
                    status=c.status,
                    stdout=c.stdout,
                    stderr=c.stderr,
                ))

        return events

    def parse_func(self, report_file: str) -> Generator[CaseEvent, None, None]:
        with open(report_file, "r") as ndjson:
            for j in ndjson:
                if not j.strip():
                    continue
                data = json.loads(j)
                self._parse_json(data)

        print("come on")
        for event in self._events():
            print("event~~~",event)
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

            self._suites.append(
                TestSuite(suite_data.get("id"), suite_data.get("platform"), suite_data.get("path"))
            )
        elif data_type == "testStart":
            test_data = data.get("test")
            if test_data is None:
                # it's might be invalid test data
                return

            if test_data.get("line") is None:
                # Still set up test case
                return

            suite_id = test_data.get("suiteID")
            suite = self._get_suite(suite_id)
            if suite_id is None or suite is None:
                click.echo(click.style(
                    "Warning: Cannot find a parent test suite (id: {}). So won't send test result of {}".format(
                        suite_id, test_data.get("name")), fg='yellow'), err=True)
                return

            id = test_data.get("id")
            name = test_data.get("name")
            metadata = test_data.get("metadata", {})
            is_skipped = metadata.get("skip", False)
            suite._test_cases.append(TestCase(id, name, is_skipped))
        elif data_type == "testDone":
            test_id = data.get("testID")
            test = self._get_test(test_id)

            if test is None:
                return

            test.status = data.get("result", "success")  # safe fallback
            duration_msec = data.get("duration", 0)
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
    for r in reports:
        client.report(r)
    client.parse_func = ReportParser(client).parse_func
    client.run()


subset = launchable.CommonSubsetImpls(__name__).scan_files('*.dart')
split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()