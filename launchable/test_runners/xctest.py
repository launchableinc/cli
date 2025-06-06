import click
from junitparser import TestCase, TestSuite

from ..testpath import TestPath
from . import launchable


@click.argument('reports', nargs=-1, required=True)
@launchable.record.tests
def record_tests(client, reports):
    def path_builder(case: TestCase, suite: TestSuite, report_path: str) -> TestPath:
        class_attr = case.classname
        splits = class_attr.split('.')
        target = splits[0]
        class_name = '/'.join(splits[1:])
        return [
            {"type": "target", "name": target},
            {"type": "class", "name": class_name},
            {"type": "testcase", "name": case.name},
        ]

    client.path_builder = path_builder

    for r in reports:
        client.report(r)
        client.run()


@launchable.subset
def subset(client):
    if not client.is_get_tests_from_previous_sessions or not client.is_output_exclusion_rules:
        click.echo(
            click.style(
                "XCTest profile only supports the subset with `--get-tests-from-previous-sessions` and `--output-exclusion-rules` options",  # noqa: E501
                fg="red"),
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
