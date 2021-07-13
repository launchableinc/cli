import click
from . import launchable
from xml.etree import ElementTree as ET


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    def parse_func(p: str) -> ET.ElementTree:
        tree = ET.parse(p)
        for suites in tree.iter("testsuites"):
            if len(suites)==0:
                continue
            root_suite = suites.find('./testsuite[@name="Root Suite"]')
            if root_suite is not None:
                filepath = root_suite.get("file")
                if filepath is not None:
                    for suite in suites:
                        suite.attrib.update({"filepath": filepath})
        return tree

    client.junitxml_parse_func = parse_func
    client.run()


@launchable.subset
def subset(client):
    # read lines as test file names
    for t in client.stdin():
        client.test_path(t.rstrip("\n"))

    client.separator = ','
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, seperator=',').split_subset()
