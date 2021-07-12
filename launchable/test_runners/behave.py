import click
from . import launchable
from xml.etree import ElementTree as ET
import os


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    def parse_func(p: str) -> ET.ElementTree:
        tree = ET.parse(p)
        for suite in tree.iter("testsuite"):
            if len(suite) == 0:
                continue

            name = suite.get('name')
            if name is None:
                continue

            suite_name = name.split('.')
            if len(suite_name) < 2:
                continue

            file_name = suite_name[0] + ".feature"
            class_name = suite_name[1]
            suite.attrib.update({"filepath": file_name})

            for case in suite:
                case.attrib.update({"classname": class_name})

        return tree

    client.junitxml_parse_func = parse_func
    client.run()


@launchable.subset
def subset(client):
    for t in client.stdin():
        if 0 < t.find(".feature"):
            paths = os.path.split(t)
            if len(paths) < 2:
                continue

            file = paths[1]
            client.test_path(file.rstrip('\n'))

    client.separator = "|"
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, seperator="|").split_subset()
