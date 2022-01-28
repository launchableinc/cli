import json
import os
import pathlib
from typing import Dict, Generator, List, Optional
from xml.etree import ElementTree as ET
import click

from launchable.testpath import FilePathNormalizer


from ..commands.record.case_event import CaseEvent, CaseEventType
from . import launchable
from pathlib import Path
from copy import deepcopy


subset = launchable.CommonSubsetImpls(__name__).scan_files('*_feature')
split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()


REPORT_FILE_PREFIX = "TEST-"


@click.option('--json', 'json_format', help="use JSON report format", is_flag=True)
@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports, json_format):
    if json_format:
        for r in reports:
            client.report(r)
        client.parse_func = JSONReportParser(client).parse_func
    else:
        report_file_and_test_file_map = {}
        _record_tests_from_xml(client, reports, report_file_and_test_file_map)

        def parse_func(report: str) -> ET.ElementTree:
            tree = ET.parse(report)
            for case in tree.findall("testcase"):
                case.attrib["file"] = str(
                    report_file_and_test_file_map[report])

            return tree

        client.junitxml_parse_func = parse_func

    client.run()


def _record_tests_from_xml(client, reports, report_file_and_test_file_map: Dict[str, str]):
    base_path = client.base_path if client.base_path else os.getcwd()
    for report in reports:
        if REPORT_FILE_PREFIX not in report:
            click.echo(
                "{} was load skipped because it doesn't look like a report file.".format(report), err=True)
            continue

        test_file = _find_test_file_from_report_file(base_path, report)
        if test_file:
            report_file_and_test_file_map[report] = str(test_file)
            client.report(report)
        else:
            click.echo("Cannot find test file of {}".format(report), err=True)


class JSONReportParser:
    """
        client: launchable.RecordTests
    """

    def __init__(self, client):
        self.client = client
        self.file_path_normalizer = FilePathNormalizer(
            base_path=client.base_path, no_base_path_inference=client.no_base_path_inference)

    def parse_func(self, report_file: str) -> Generator[CaseEventType, None, None]:
        """
        example of JSON format report
        [
        {
            "uri": "features/foo/is_it_friday_yet.feature",
            "id": "is-it-friday-yet?",
            "keyword": "Feature",
            "name": "Is it Friday yet?",
            "description": "  Everybody wants to know when it's Friday",
            "line": 1,
            "elements": [
            {
                "id": "is-it-friday-yet?;today-is-or-is-not-friday;;2",
                "keyword": "Scenario Outline",
                "name": "Today is or is not Friday",
                "description": "",
                "line": 11,
                "type": "scenario",
                "steps": [
                {
                    "keyword": "Given ",
                    "name": "today is \"Friday\"",
                    "line": 5,
                    "match": {
                    "location": "features/step_definitions/stepdefs.rb:12"
                    },
                    "result": {
                    "status": "passed",
                    "duration": 101000
                    }
                },
                {
                    "keyword": "When ",
                    "name": "I ask whether it's Friday yet",
                    "line": 6,
                    "match": {
                    "location": "features/step_definitions/stepdefs.rb:24"
                    },
                    "result": {
                    "status": "passed",
                    "duration": 11000
                    }
                },
                {
                    "keyword": "Then ",
                    "name": "I should be told \"TGIF\"",
                    "line": 7,
                    "match": {
                    "location": "features/step_definitions/stepdefs.rb:28"
                    },
                    "result": {
                    "status": "passed",
                    "duration": 481000
                    }
                }
                ]
            }
        ]
        """
        with open(report_file, 'r') as json_file:
            try:
                data = json.load(json_file)
            except Exception as e:
                raise Exception("Can't read JSON format report file {}. Make sure to confirm report file.".format(
                    report_file)) from e

        if len(data) == 0:
            click.echo("Can't find test reports from {}. Make sure to confirm report file.".format(
                report_file), err=True)

        for d in data:
            file_name = d.get("uri", "")
            class_name = d.get("name", "")
            for element in d.get("elements", []):
                test_case = element.get("name", "")
                steps = {}
                duration = 0
                statuses = []
                stderr = []
                for step in element.get("steps", []):
                    steps[step.get("keyword", "").strip()] = step.get(
                        "name", "").strip()
                    result = step.get("result", None)

                    if result:
                        # duration's unit is nano sec
                        # ref: https://github.com/cucumber/cucumber-ruby/blob/main/lib/cucumber/formatter/json.rb#L222
                        duration = duration + result.get("duration", 0)
                        statuses.append(result.get("status"))
                        if result.get("error_message", None):
                            stderr.append(result["error_message"])

                if "failed" in statuses:
                    status = CaseEvent.TEST_FAILED
                elif "undefined" in statuses:
                    status = CaseEvent.TEST_SKIPPED
                else:
                    status = CaseEvent.TEST_PASSED

                test_path = [
                    {"type": "file", "name": pathlib.Path(
                        self.file_path_normalizer.relativize(file_name)).as_posix()},
                    {"type": "class", "name": class_name},
                    {"type": "testcase", "name": test_case},
                ]

                for k in steps:
                    test_path.append({"type": k, "name": steps[k]})

                yield CaseEvent.create(test_path, duration / 1000/1000 / 1000, status, None, "\n".join(stderr), None, None)


def _find_test_file_from_report_file(base_path: str, report: str) -> Optional[Path]:
    """
    Find test file from cucumber report file path format
    e.g) Test-features-foo-hoge.xml -> features/foo/hoge.feature or features/foo-hoge.feature
    """

    report_file = os.path.basename(report)
    report_file = report_file.lstrip(REPORT_FILE_PREFIX)
    report_file = os.path.splitext(report_file)[0]

    list = _create_file_candidate_list(report_file)
    for l in list:
        f = Path(base_path, l + ".feature")
        if f.exists():
            return f

    return None


def _create_file_candidate_list(file: str) -> List[str]:
    list = [""]
    for c in file:
        if c == "-":
            l = len(list)
            list += deepcopy(list)
            for i in range(l):
                list[i] += '-'
            for i in range(l, len(list)):
                list[i] += '/'
        else:
            for i in range(len(list)):
                list[i] += c

    return list
