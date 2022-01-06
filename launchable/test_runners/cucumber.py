import json
import os
from typing import Dict, Generator, List, Optional
from xml.etree import ElementTree as ET
import click


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
        client.parse_func = _record_tests_from_json
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
            report_file_and_test_file_map[report] = test_file
            client.report(report)
        else:
            click.echo("Cannot find test file of {}".format(report), err=True)


def _record_tests_from_json(report_file: str) -> Generator[CaseEventType, None, None]:
    # TODO: error handling
    with open(report_file, 'r') as json_file:
        data = json.load(json_file)

    for d in data:
        file_name = d.get("uri", "")
        class_name = d.get("name", "")
        for e in d.get("elements", []):
            test_case = e.get("name", "")
            steps = {}
            duration = 0
            statuses = []
            stderr = []
            for step in e.get("steps", []):
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
                status = 0
            elif "undefined" in statuses:
                status = 2
            else:
                status = 1

            test_path = [
                {"type": "file", "name": file_name},
                {"type": "class", "name": class_name},
                {"type": "tesstcase", "name": test_case},
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
