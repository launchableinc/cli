from typing import Annotated, List

import typer
from junitparser import TestCase, TestSuite  # type: ignore

from smart_tests.testpath import TestPath

from . import smart_tests


def path_builder(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
    test_path = []
    if suite.name:
        test_path.append({"type": "file", "name": suite.name})

    if case.classname:
        test_path.append({"type": "class", "name": case.classname})

    if case.name:
        test_path.append({"type": "testcase", "name": case.name})

    return test_path


@smart_tests.record.tests
def record_tests(
    client,
    reports: Annotated[List[str], typer.Argument(
        help="Test report files to process"
    )],
):
    for r in reports:
        client.report(r)

    client.path_builder = path_builder
    client.run()


@smart_tests.subset
def subset(client):
    if client.base_path is None:
        raise typer.BadParameter("Please specify base path")

    for line in client.stdin():
        if len(line.strip()) and not line.startswith(">"):
            client.test_path(line.rstrip("\n"))

    client.run()


split_subset = smart_tests.CommonSplitSubsetImpls(__name__).split_subset()
