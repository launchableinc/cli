#
# The the test runner to support playwright junit and JSON report format.
# https://playwright.dev/
#
import json
from typing import Dict, Generator, List

import click
from junitparser import TestCase, TestSuite  # type: ignore

from ..commands.record.case_event import CaseEvent
from ..testpath import TestPath
from . import launchable

TEST_CASE_DELIMITER = " › "


@click.option('--json', 'json_format', help="use JSON report format", is_flag=True)
@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports, json_format):
    def path_builder(case: TestCase, suite: TestSuite,
                     report_file: str) -> TestPath:
        """
        The playwright junit report sets a file name to the name attribute in a testsuite element and the classname attribute in a testcase element. # noqa: E501
        This playwright plugin uses a testsuite attribute value.
        e.g.)
        <testsuite name="tests/demo-todo-app.spec.ts" ...>
            <testcase name="New Todo › should allow me to add todo items" classname="tests/demo-todo-app.spec.ts"></testcase>
            <testcase name="New Todo › should clear text input field when an item is added" classname="tests/demo-todo-app.spec.ts"></testcase>
        </testsuite>
        """
        filepath = suite.name
        if not filepath:
            raise click.ClickException(
                "No file name found in %s" % report_file)

        test_path = [client.make_file_path_component(filepath)]
        if case.name:
            test_path.append({"type": "testcase", "name": case.name})
        return test_path

    if json_format:
        client.parse_func = JSONReportParser(client).parse_func
    else:
        client.path_builder = path_builder

    for r in reports:
        client.report(r)

    client.run()


@launchable.subset
def subset(client):
    # read lines as test file names
    for t in client.stdin():
        client.test_path(t.rstrip("\n"))

    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()


class JSONReportParser:
    def __init__(self, client):
        self.client = client

    def parse_func(self, report_file: str) -> Generator[CaseEvent, None, None]:
        data: Dict[str, Dict]
        with open(report_file, 'r') as json_file:
            try:
                data = json.load(json_file)
            except Exception as e:
                raise Exception("Can't read JSON format report file {}. Make sure to confirm report file.".format(
                    report_file)) from e

        suites = data.get("suites", None)
        if suites is None or len(suites) == 0:
            click.echo("Can't find test results from {}. Make sure to confirm report file.".format(
                report_file), err=True)
            yield

        for s in suites:
            # The title of the root suite object contains the file name.
            test_file = s.get("title")

            for event in self._parse_suites(test_file, s, []):
                yield event

    def _parse_suites(self, test_file: str, suite: Dict[str, Dict], test_case_names: List[str] = []) -> List[CaseEvent]:
        events: List[CaseEvent] = []

        # In some cases, suites are nested.
        for s in suite.get("suites", []):
            [events.append(event) for event in self._parse_suites(test_file, s, test_case_names + [s.get("title")])]

        for spec in suite.get("specs", []):
            spec_name = spec.get("title", "")
            line_no = spec.get("line", None)
            for test in spec.get("tests", []):
                for result in test.get("results", []):
                    test_path: TestPath = [
                        self.client.make_file_path_component(test_file),
                        {"type": "testcase", "name": TEST_CASE_DELIMITER.join(test_case_names + [spec_name])}
                    ]

                    duration_msec = result.get("duration", 0)
                    status = self._case_event_status_from_str(result.get("status", ""))
                    stdout = self._parse_stdout(result.get("stdout", []))
                    stderr = self._parse_stderr(result.get("errors", []))

                    events.append(CaseEvent.create(
                        test_path=test_path,
                        duration_secs=duration_msec / 1000,  # convert msec to sec,
                        status=status,
                        stdout=stdout,
                        stderr=stderr,
                        data={"lineNumber": line_no}
                    ))

        return events

    def _case_event_status_from_str(self, status_str: str) -> int:
        if status_str == "passed":
            return CaseEvent.TEST_PASSED
        elif status_str == "failed":
            return CaseEvent.TEST_FAILED
        elif status_str == "skipped":
            return CaseEvent.TEST_SKIPPED
        else:
            return CaseEvent.TEST_PASSED

    def _parse_stdout(self, stdout: List[Dict[str, Dict]]) -> str:
        if len(stdout) == 0:
            return ""

        return "\n".join([out.get("text", "") for out in stdout])

    def _parse_stderr(self, stderr: List[Dict[str, Dict]]) -> str:
        if len(stderr) == 0:
            return ""

        return "\n".join([err.get("message", "") for err in stderr])
