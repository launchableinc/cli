import os
import json
import click
from . import launchable
from junitparser import TestCase, TestSuite  # type: ignore
from launchable.testpath import TestPath


def path_builder(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
    test_path = []
    if suite.name:
        test_path.append({"type": "file", "name": suite.name})

    if case.classname:
        test_path.append({"type": "class", "name": case.classname})

    if case.name:
        test_path.append({"type": "testcase", "name": case.name})

    return test_path


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    client.path_builder = path_builder
    client.run()


@launchable.subset
def subset(client):
    if client.base_path is None:
        raise click.BadParameter("Please specify base path")

    for line in client.stdin():
        if len(line.strip()) and not line.startswith(">"):
            client.test_path(line.rstrip("\n"))

    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()
