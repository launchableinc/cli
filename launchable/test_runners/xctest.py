import html
import xml.etree.ElementTree as ET  # type: ignore
from typing import Annotated, List

import typer
from junitparser import TestCase, TestSuite

from ..testpath import TestPath
from . import launchable


@launchable.record.tests
def record_tests(
    client,
    reports: Annotated[List[str], typer.Argument(
        help="Test report files to process"
    )],
):

    def parse_func(p: str) -> ET.ElementTree:
        tree = ET.parse(p)
        root = tree.getroot()

        for testsuite in root.findall('testsuite'):
            for testcase in testsuite.findall('testcase'):
                failure = testcase.find('failure')
                if failure is not None:
                    # Note(Konboi): XCTest escape `"` to `&quot;` in the message, so save as unescaped text
                    message = html.unescape(failure.get('message', ''))
                    body = failure.text or ''
                    failure.text = f"{message}\n{body}"

        return tree

    def path_builder(case: TestCase, suite: TestSuite, report_path: str) -> TestPath:
        class_attr = case.classname
        [target, *rest] = class_attr.split('.')
        class_name = '/'.join(rest)
        return [
            {"type": "target", "name": target},
            {"type": "class", "name": class_name},
            {"type": "testcase", "name": case.name},
        ]

    client.junitxml_parse_func = parse_func
    client.path_builder = path_builder
    launchable.CommonRecordTestImpls.load_report_files(client=client, source_roots=reports)


@launchable.subset
def subset(client):
    if not client.is_get_tests_from_previous_sessions or not client.is_output_exclusion_rules:
        typer.secho(
            "XCTest profile only supports the subset with `--get-tests-from-previous-sessions` and `--output-exclusion-rules` options",  # noqa: E501
            fg=typer.colors.RED,
            err=True,
        )

    def formatter(test_path: TestPath) -> str:
        if len(test_path) == 0:
            return ""

        # only target case
        if len(test_path) == 1:
            return "-skip-testing:{}".format(test_path[0]['name'])

        # default target/class format
        return "-skip-testing:{}/{}".format(test_path[0]['name'], test_path[1]['name'])

    client.formatter = formatter
    client.separator = "\n"
    client.run()
