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
